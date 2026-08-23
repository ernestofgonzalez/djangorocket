import os
import tempfile
import unittest
from pathlib import Path

from djangorocket.django import DjangoSettingsManager

class DjangoSettingsManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        return super().setUp()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
        return super().tearDown()
    
    def _init_manager(self, settings_content):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        self.temp_file.write(settings_content.encode("utf-8"))
        self.temp_file.close()
        manager = DjangoSettingsManager(self.temp_file.name)
        return manager

    def test_add_app(self):
        # Test adding a new app
        settings_content = """
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth']
"""
        manager = self._init_manager(settings_content)

        manager.add_app("project.auth")

        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertIn("'project.auth'", content)

    def test_add_existing_app(self):
        # Test adding an app that already exists
        settings_content = """
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth']
"""
        manager = self._init_manager(settings_content)

        with self.assertLogs(level='INFO') as log:
            manager.add_app("django.contrib.admin")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertEqual(content.count("'django.contrib.admin'"), 1)
        self.assertIn("App 'django.contrib.admin' is already in INSTALLED_APPS.", log.output[0])

    def test_get_templates_dirs_with_base_dir(self):
        # Test when BASE_DIR and TEMPLATES["DIRS"] are properly defined
        settings_content = """
BASE_DIR = "/path/to/project"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"), "/absolute/path"],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        dirs = manager.get_templates_dirs()
        self.assertEqual(dirs, ["/path/to/project/templates", "/absolute/path"])

    def test_get_templates_dirs_with_plain_strings(self):
        # Test when TEMPLATES["DIRS"] contains plain string paths
        settings_content = """
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["/plain/path", "/another/plain/path"],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        dirs = manager.get_templates_dirs()
        self.assertEqual(dirs, ["/plain/path", "/another/plain/path"])

    def test_get_templates_dirs_without_base_dir(self):
        # Test when BASE_DIR is not defined
        settings_content = """
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        with self.assertRaises(ValueError) as context:
            manager.get_templates_dirs()
        self.assertEqual(str(context.exception), "BASE_DIR is not defined in settings.py")

    def test_get_templates_dirs_without_dirs_key(self):
        # Test when TEMPLATES["DIRS"] is not defined
        settings_content = """
BASE_DIR = "/path/to/project"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        with self.assertRaises(ValueError) as context:
            manager.get_templates_dirs()
        self.assertEqual(str(context.exception), "DIRS key not found in TEMPLATES setting or is not a list.")

    def test_get_templates_dirs_with_empty_dirs(self):
        # Test when TEMPLATES["DIRS"] is an empty list
        settings_content = """
BASE_DIR = "/path/to/project"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        dirs = manager.get_templates_dirs()
        self.assertEqual(dirs, [])

    def test_get_templates_dirs_with_path_based_base_dir(self):
        # Test the Django default: BASE_DIR computed from __file__ via pathlib.
        settings_content = """
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        base_dir = str(Path(self.temp_file.name).resolve().parent.parent)
        self.assertEqual(
            manager.get_templates_dirs(), [os.path.join(base_dir, "templates")]
        )

    def test_get_templates_dirs_with_os_path_dirname_base_dir(self):
        # Test the older idiom: nested os.path.dirname around os.path.abspath.
        settings_content = """
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        base_dir = str(Path(self.temp_file.name).resolve().parent.parent)
        self.assertEqual(
            manager.get_templates_dirs(), [os.path.join(base_dir, "templates")]
        )

    def test_get_templates_dir_returns_first(self):
        # get_templates_dir() returns the primary (first) configured directory.
        settings_content = """
BASE_DIR = "/path/to/project"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"), "/absolute/path"],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        self.assertEqual(manager.get_templates_dir(), "/path/to/project/templates")

    def test_get_templates_dir_without_dirs_raises(self):
        # get_templates_dir() raises when no directories are configured.
        settings_content = """
BASE_DIR = "/path/to/project"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
"""
        manager = self._init_manager(settings_content)

        with self.assertRaises(ValueError) as context:
            manager.get_templates_dir()
        self.assertEqual(
            str(context.exception),
            "No template directories are configured in TEMPLATES['DIRS'].",
        )
