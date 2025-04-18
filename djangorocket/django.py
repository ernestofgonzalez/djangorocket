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

        if manage_path is not None:
            if os.path.isfile(manage_path):
                self.manage_path = manage_path
                return
            
            raise FileNotFoundError("manage.py not found in the passed `manage_path`.")
    
        default_manage_module = [
            os.path.join(os.getcwd(), "manage.py"),
            os.path.join(os.getcwd(), "src", "manage.py"),
        ]

        for module in default_manage_module:
            if os.path.isfile(module):
                self.manage_path = module
                return

        raise FileNotFoundError("manage.py not found in the current directory or src subdirectory.")

    def get_default_settings_module(self):
        """
        Retrieve the value set in the os.environ.setdefault('DJANGO_SETTINGS_MODULE', ...) line.

        Returns:
            str: The value of the default settings module.
        """
        with open(self.manage_path, "r") as file:
            tree = ast.parse(file.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value
                if (
                    isinstance(func.func, ast.Attribute)
                    and func.func.attr == "setdefault"
                    and isinstance(func.func.value, ast.Attribute)
                    and func.func.value.attr == "environ"
                    and len(func.args) == 2
                    and isinstance(func.args[0], ast.Constant)
                    and func.args[0].value == "DJANGO_SETTINGS_MODULE"
                ):
                    if isinstance(func.args[1], ast.Constant):
                        return func.args[1].value

        raise ValueError("DJANGO_SETTINGS_MODULE not found in manage.py")
    
    def get_settings_path(self):
        """
        Get the file path of the settings.py file based on the settings module.

        Returns:
            str: The absolute path to the settings.py file.

        Raises:
            FileNotFoundError: If the settings.py file does not exist.
        """
        settings_module = self.get_default_settings_module()
        manage_dir = os.path.dirname(self.manage_path)

        settings_rel_path = settings_module.replace(".", os.sep) + ".py"

        settings_path = os.path.join(manage_dir, settings_rel_path)

        if not os.path.isfile(settings_path):
            raise FileNotFoundError(f"Settings file not found: {settings_path}")

        return settings_path


class DjangoSettingsManager:
    def __init__(self, settings_path=None):
        """
        Initialize the DjangoSettingsManager with the path to the settings.py file.

        Args:
            settings_path (str): The path to the Django settings.py file.
        """
        if settings_path is not None:
            if not os.path.isfile(settings_path):
                raise FileNotFoundError(f"Settings file not found: {settings_path}")
        else:    
            manage_module = DjangoManageManager()
            settings_path = manage_module.get_settings_path()
            
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

    def _find_templates_node(self):
        """
        Find the AST node for the TEMPLATES variable.

        Returns:
            ast.Dict: The AST node representing the TEMPLATES dictionary.
        """
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TEMPLATES":
                        if isinstance(node.value, ast.List) and len(node.value.elts) > 0:
                            first_element = node.value.elts[0]
                            if isinstance(first_element, ast.Dict):
                                return first_element
        raise ValueError("TEMPLATES dictionary not found in settings.py")

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