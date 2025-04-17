import os
import tempfile
import unittest

from djangorocket.django import DjangoSettingsManager

class DjangoSettingsManagerTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary settings file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        self.temp_file.write(b"INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth']\n")
        self.temp_file.close()
        self.manager = DjangoSettingsManager(self.temp_file.name)

    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def test_add_app(self):
        # Test adding a new app
        self.manager.add_app("project.auth")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertIn("'project.auth'", content)

    def test_add_existing_app(self):
        # Test adding an app that already exists
        self.manager.add_app("django.contrib.admin")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertEqual(content.count("'django.contrib.admin'"), 1)
