from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import os
import io

VERSION = "1.0.0a1"


def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


class CustomBuildCommand(build_py):
    """Custom build command to zip templates before building the package."""

    def run(self):
        # Run the zip_templates.py script
        script_path = os.path.join(os.path.dirname(__file__), "tools", "zip_templates.py")
        if os.path.exists(script_path):
            print("Running zip_templates.py to zip all templates...")
            subprocess.check_call(["python", script_path])
        else:
            print(f"Error: Script not found at {script_path}")
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Continue with the standard build process
        super().run()


setup(
    name="djangorocket",
    description="CLI tool to add applications and UI templates to any Django website.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ernesto González",
    version=VERSION,
    license="Apache License, Version 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "click-default-group>=1.2.3",
        "cookiecutter",
    ],
    entry_points={
        'console_scripts': [
            'djangorocket = djangorocket.cli:main',
        ]
    },
    url="https://github.com/ernestofgonzalez/djangorocket",
    project_urls={
        "Documentation": "https://djangorocket.com/",
        "Changelog": "https://djangorocket.com/changelog.html",
        "Source code": "https://github.com/ernestofgonzalez/djangorocket",
        "Issues": "https://github.com/ernestofgonzalez/djangorocket/issues",
        "CI": "https://github.com/ernestofgonzalez/djangorocket/actions",
    },
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
    ],
    cmdclass={
        "build_py": CustomBuildCommand,
    },
)