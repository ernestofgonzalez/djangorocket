import ast
import os
import logging


class DjangoManageManager:
    def __init__(self, manage_path=None):
        """
        Initialize the DjangoManageManager with the path to the manage.py file.

        Args:
            manage_path (str, optional): The path to the Django manage.py file. Defaults to None.
        """
        possible_paths = [
            manage_path,
            os.path.join(os.getcwd(), "manage.py"),
            os.path.join(os.getcwd(), "src", "manage.py"),
        ]

        for path in possible_paths:
            if os.path.isfile(path):
                self.manage_path = path
                return

        raise FileNotFoundError("manage.py not found in the current directory or src subdirectory.")

    def get_default_settings_module(self):
        """
        Retrieve the value set in the os.environ.setdefault('DJANGO_SETTINGS_MODULE', ...) line.

        Returns:
            str: The value of the default settings module.
        """
        with open(self.manage_path, "r") as file:
            for line in file:
                if "os.environ.setdefault('DJANGO_SETTINGS_MODULE'" in line or \
                   'os.environ.setdefault("DJANGO_SETTINGS_MODULE"' in line:
                    # Extract the value set for DJANGO_SETTINGS_MODULE
                    return line.split(",")[-1].strip().strip(")").strip('"').strip("'")
        raise ValueError("DJANGO_SETTINGS_MODULE not found in manage.py")


class DjangoSettingsManager:
    def __init__(self, settings_path):
        """
        Initialize the DjangoSettingsManager with the path to the settings.py file.

        Args:
            settings_path (str): The path to the Django settings.py file.
        """
        if not os.path.isfile(settings_path):
            raise FileNotFoundError(f"Settings file not found: {settings_path}")
        self.settings_path = settings_path
        self.tree = self._load_ast()
        self.logger = logging.getLogger(__name__)

    def _load_ast(self):
        """
        Parse the settings.py file into an AST.

        Returns:
            ast.Module: The parsed AST of the settings.py file.
        """
        with open(self.settings_path, "r") as file:
            return ast.parse(file.read())

    def _write_ast(self):
        """
        Write the modified AST back to the settings.py file.
        """
        with open(self.settings_path, "w") as file:
            file.write(ast.unparse(self.tree))

    def _find_installed_apps_node(self):
        """
        Find the AST node for the INSTALLED_APPS variable.

        Returns:
            ast.List: The AST node representing the INSTALLED_APPS list.
        """
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "INSTALLED_APPS":
                        if isinstance(node.value, ast.List):
                            return node.value
        raise ValueError("INSTALLED_APPS not found in settings.py")

    def add_app(self, app_name):
        """
        Add an app to the INSTALLED_APPS setting in the Django settings file.

        Args:
            app_name (str): The name of the app to add.
        """
        installed_apps_node = self._find_installed_apps_node()

        # Check if the app is already in the list
        for element in installed_apps_node.elts:
            if isinstance(element, ast.Constant) and element.value == app_name:
                self.logger.warning(f"App '{app_name}' is already in INSTALLED_APPS.")
                return

        # Add the app to the list
        installed_apps_node.elts.append(ast.Constant(value=app_name))
        self._write_ast()
        self.logger.info(f"App '{app_name}' added to INSTALLED_APPS.")

    def remove_app(self, app_name):
        """
        Remove an app from the INSTALLED_APPS setting in the Django settings file.

        Args:
            app_name (str): The name of the app to remove.
        """
        installed_apps_node = self._find_installed_apps_node()

        # Remove the app from the list
        new_elements = [
            element
            for element in installed_apps_node.elts
            if not (isinstance(element, ast.Constant) and element.value == app_name)
        ]

        if len(new_elements) == len(installed_apps_node.elts):
            self.logger.warning(f"App '{app_name}' is not in INSTALLED_APPS.")
            return

        installed_apps_node.elts = new_elements
        self._write_ast()
        self.logger.info(f"App '{app_name}' removed from INSTALLED_APPS.")