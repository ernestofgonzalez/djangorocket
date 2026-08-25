"""Collision-proofing for project creation and ``make bootstrap``.

Several DjangoRocket projects must be able to coexist on one machine. The real
``djangorocket init`` console script guarantees that by de-duplicating the
identifiers a second project would otherwise share with the first:

  * the project **directory** is kebab-cased and de-duplicated on disk
    (``my-project``, ``my-project-1``, ...); the Python package inside stays
    snake_case;
  * the generated ``docker-compose.yml`` -- what ``make bootstrap`` /
    ``docker compose up`` consume -- namespaces the compose project and its
    named volumes under that unique directory name, so bootstrapping a second
    project never attaches to or clobbers the first's containers/data;
  * ``init`` also skips a name whose data volumes already exist in Docker, even
    when the directory does not (a previous project was removed but its volumes
    lingered).

Like ``test_add_command.py`` these drive the real console script and run in the
normal ``pytest`` invocation (they need no venv). They never start containers,
so they need no free host ports; the Docker-volume check skips when Docker is
unavailable.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _djangorocket_cli():
    """Locate the installed ``djangorocket`` console script (or skip)."""
    found = shutil.which("djangorocket")
    if found:
        return found
    candidate = Path(sys.executable).parent / "djangorocket"
    return str(candidate) if candidate.exists() else None


def _init(project_name, cwd):
    """Run ``djangorocket init`` via the real console script in ``cwd``.

    ``init`` prompts for the project name, so feed it on stdin.
    """
    cli = _djangorocket_cli()
    if cli is None:
        pytest.skip("djangorocket console script not found")
    return subprocess.run(
        [cli, "init"],
        cwd=str(cwd),
        input="{0}\n".format(project_name),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _docker_daemon_available():
    if shutil.which("docker") is None:
        return False
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def _compose(project_dir, *args):
    """Run ``docker compose <args>`` inside a generated project directory."""
    return subprocess.run(
        ["docker", "compose", *args],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )


def _env_value(project_dir, key):
    for line in (project_dir / ".env").read_text().splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()
    return None


def _docker_identity(project_dir):
    """(compose project name, {volume names}) declared in the generated compose."""
    name = None
    volumes = set()
    for line in (project_dir / "docker-compose.yml").read_text().splitlines():
        if line.startswith("name:"):  # top-level compose project name
            name = line.split(":", 1)[1].strip()
        else:
            stripped = line.strip()
            if stripped.startswith("name:") and "_data" in stripped:  # a volume name
                volumes.add(stripped.split(":", 1)[1].strip())
    return name, volumes


def test_init_dedupes_project_directory(tmp_path):
    """Repeated ``init`` never collides: my-project, my-project-1, my-project-2."""
    for _ in range(3):
        result = _init("Collision Check", tmp_path)
        assert result.returncode == 0, result.stdout

    dirs = sorted(p.name for p in tmp_path.iterdir() if p.is_dir())
    assert dirs == ["collision-check", "collision-check-1", "collision-check-2"], dirs

    # Every project keeps a valid snake_case Python package regardless of the
    # kebab-cased (and possibly suffixed) directory it lives in.
    for name in dirs:
        assert (tmp_path / name / "src" / "collision_check" / "settings.py").is_file()


def test_bootstrap_projects_get_isolated_docker_resources(tmp_path):
    """Two projects render disjoint compose project + volume names.

    This is what makes ``make bootstrap`` collision-proof: bringing up the
    second project's stack cannot reuse the first's containers or write into its
    Postgres/Redis volumes.
    """
    _init("Bootstrap Iso", tmp_path)
    _init("Bootstrap Iso", tmp_path)

    first = tmp_path / "bootstrap-iso"
    second = tmp_path / "bootstrap-iso-1"
    assert first.is_dir() and second.is_dir()

    name_a, volumes_a = _docker_identity(first)
    name_b, volumes_b = _docker_identity(second)

    assert name_a == "bootstrap-iso"
    assert name_b == "bootstrap-iso-1"
    assert name_a != name_b

    assert volumes_a == {"bootstrap-iso_postgres_data", "bootstrap-iso_redis_data"}
    assert volumes_b == {"bootstrap-iso-1_postgres_data", "bootstrap-iso-1_redis_data"}
    # No shared volume -> the two projects can never clobber each other's data.
    assert volumes_a.isdisjoint(volumes_b)


def test_init_avoids_existing_docker_volume(tmp_path):
    """``init`` skips a name whose Postgres data volume already exists in Docker."""
    if shutil.which("docker") is None:
        pytest.skip("docker not available")

    base = "volume-dedup"
    volume = "{0}_postgres_data".format(base)
    created = subprocess.run(
        ["docker", "volume", "create", volume],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        pytest.skip("docker volume create failed (daemon down?): {0}".format(created.stderr))

    try:
        result = _init("Volume Dedup", tmp_path)
        assert result.returncode == 0, result.stdout

        # The directory "volume-dedup" is free on disk, but its data volume
        # exists, so init must move on rather than reuse that volume.
        existing = sorted(p.name for p in tmp_path.iterdir() if p.is_dir())
        assert not (tmp_path / base).exists(), existing
        assert (tmp_path / "{0}-1".format(base)).is_dir(), existing
    finally:
        subprocess.run(["docker", "volume", "rm", volume], capture_output=True, text=True)


@pytest.mark.e2e
def test_two_projects_run_postgres_and_redis_concurrently(tmp_path):
    """Two generated projects boot Postgres + Redis at the same time.

    This is the end-to-end proof that ``make bootstrap`` is collision-proof: each
    project gets free host ports (in .env, read by compose), a unique compose
    project name and its own named volumes, so the second stack comes up while
    the first is still running -- impossible with the old hardcoded 5432/6379.
    """
    if not _docker_daemon_available():
        pytest.skip("docker daemon not available")

    assert _init("Concurrent A", tmp_path).returncode == 0
    assert _init("Concurrent B", tmp_path).returncode == 0
    first = tmp_path / "concurrent-a"
    second = tmp_path / "concurrent-b"
    assert first.is_dir() and second.is_dir()

    # Distinct host ports were assigned to each project.
    assert _env_value(first, "POSTGRES_PORT") != _env_value(second, "POSTGRES_PORT")
    assert _env_value(first, "REDIS_PORT") != _env_value(second, "REDIS_PORT")

    try:
        up_first = _compose(first, "up", "-d", "--wait")
        assert up_first.returncode == 0, up_first.stderr or up_first.stdout
        # The second stack must come up while the first is still running.
        up_second = _compose(second, "up", "-d", "--wait")
        assert up_second.returncode == 0, up_second.stderr or up_second.stdout

        # All four containers run concurrently (unique compose project names).
        running = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True
        ).stdout
        for name in (
            "concurrent-a-postgres-1",
            "concurrent-a-redis-1",
            "concurrent-b-postgres-1",
            "concurrent-b-redis-1",
        ):
            assert name in running, running

        # Data isolation: a table written to A's Postgres is invisible in B's.
        db_a = _env_value(first, "POSTGRES_DB")
        db_b = _env_value(second, "POSTGRES_DB")
        assert db_a != db_b
        _compose(
            first, "exec", "-T", "postgres",
            "psql", "-U", "postgres", "-d", db_a, "-c", "CREATE TABLE marker (id int);",
        )
        seen_in_a = _compose(
            first, "exec", "-T", "postgres", "psql", "-U", "postgres", "-d", db_a,
            "-tAc", "SELECT to_regclass('public.marker') IS NOT NULL;",
        )
        seen_in_b = _compose(
            second, "exec", "-T", "postgres", "psql", "-U", "postgres", "-d", db_b,
            "-tAc", "SELECT to_regclass('public.marker') IS NOT NULL;",
        )
        assert seen_in_a.stdout.strip() == "t", seen_in_a.stdout
        assert seen_in_b.stdout.strip() == "f", seen_in_b.stdout
    finally:
        _compose(first, "down", "-v")
        _compose(second, "down", "-v")
