import os
import tempfile
import unittest
from djangorocket.django import DjangoSettingsManager

class TestDjangoSettingsManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary settings.py file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        self.temp_file.write(b"INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth']\n")
        self.temp_file.close()
        self.manager = DjangoSettingsManager(self.temp_file.name)

    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def test_add_app(self):
        self.manager.add_app("my_new_app")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertIn("'my_new_app'", content)

    def test_add_existing_app(self):
        self.manager.add_app("django.contrib.admin")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertEqual(content.count("django.contrib.admin"), 1)

    def test_remove_app(self):
        self.manager.remove_app("django.contrib.auth")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertNotIn("django.contrib.auth", content)

    def test_remove_nonexistent_app(self):
        self.manager.remove_app("nonexistent_app")
        with open(self.temp_file.name, "r") as file:
            content = file.read()
        self.assertIn("django.contrib.admin", content)
        self.assertIn("django.contrib.auth", content)
