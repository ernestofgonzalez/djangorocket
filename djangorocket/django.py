import ast
import os
import logging
from pathlib import Path


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

    def _find_base_dir_node(self):
        """
        Find the definition of BASE_DIR in the settings.py file.

        Returns:
            ast.Name or None: The AST node representing BASE_DIR, or None if not found.
        """
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "BASE_DIR":
                        return node.value
        return None

    def _count_path_steps_from_file(self, node):
        """
        Count how many directory levels above the settings file an AST node points to.

        Recognizes the two common ways a Django ``settings.py`` derives a path
        from ``__file__``:

          * ``Path(__file__).resolve().parent[...]`` - each ``.parent`` climbs
            one level (``.resolve()``/``.absolute()`` are treated as no-ops);
          * ``os.path.dirname(...)`` nested around ``os.path.abspath(__file__)``
            - each ``os.path.dirname(...)`` climbs one level.

        Args:
            node (ast.AST): The AST node to inspect.

        Returns:
            int or None: The number of levels above the settings file, or None
            if the node does not derive a path from ``__file__``.
        """
        # Base case: __file__ resolves to the settings file itself (0 levels up).
        if isinstance(node, ast.Name) and node.id == "__file__":
            return 0

        # Attribute access without a call, e.g. ``.parent`` on a pathlib.Path.
        if isinstance(node, ast.Attribute):
            inner = self._count_path_steps_from_file(node.value)
            if inner is None:
                return None
            return inner + 1 if node.attr == "parent" else inner

        # Calls: Path(...), X.resolve(), os.path.dirname(...), os.path.abspath(...)
        if isinstance(node, ast.Call):
            func = node.func
            # Method / os.path call, e.g. Path(__file__).resolve() or
            # os.path.dirname(...).
            if isinstance(func, ast.Attribute):
                if func.attr in ("resolve", "absolute"):
                    return self._count_path_steps_from_file(func.value)
                if func.attr == "abspath" and node.args:
                    return self._count_path_steps_from_file(node.args[0])
                if func.attr == "dirname" and node.args:
                    inner = self._count_path_steps_from_file(node.args[0])
                    return None if inner is None else inner + 1
                return None
            # Plain call, e.g. Path(__file__).
            if isinstance(func, ast.Name) and func.id == "Path" and node.args:
                return self._count_path_steps_from_file(node.args[0])
            return None

        return None

    def _resolve_base_dir(self, node):
        """
        Resolve the value of BASE_DIR from its AST node.

        Handles both a literal path (``BASE_DIR = "/path/to/project"``) and the
        idioms that compute it relative to the settings file, e.g. the Django
        default ``BASE_DIR = Path(__file__).resolve().parent.parent``.

        Args:
            node (ast.AST or None): The AST node assigned to BASE_DIR.

        Returns:
            str or None: The resolved directory path, or None if it cannot be
            determined.
        """
        if node is None:
            return None

        # Literal path, e.g. BASE_DIR = "/path/to/project".
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError, SyntaxError):
            pass

        # Path computed from this settings file, e.g. Path(__file__).parent.parent.
        steps = self._count_path_steps_from_file(node)
        if steps is not None:
            base = Path(self.settings_path).resolve()
            for _ in range(steps):
                base = base.parent
            return str(base)

        return None

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

    def get_templates_dirs(self):
        """
        Retrieve the raw string values of directories specified in the TEMPLATES["DIRS"] setting.

        Returns:
            list: A list of raw string directory paths.
        """
        # Find and resolve the BASE_DIR definition
        base_dir_node = self._find_base_dir_node()
        base_dir = self._resolve_base_dir(base_dir_node)

        # Find the TEMPLATES node
        templates_node = self._find_templates_node()

        # Extract the DIRS key and compute raw string values
        for key, value in zip(templates_node.keys, templates_node.values):
            if isinstance(key, ast.Constant) and key.value == "DIRS":
                if isinstance(value, ast.List):
                    raw_dirs = []
                    for element in value.elts:
                        if isinstance(element, ast.Call) and isinstance(element.func, ast.Attribute):
                            # Handle os.path.join(BASE_DIR, ...)
                            if element.func.attr == "join" and len(element.args) > 1:
                                if isinstance(element.args[0], ast.Name) and element.args[0].id == "BASE_DIR":
                                    if base_dir is None:
                                        raise ValueError("BASE_DIR is not defined in settings.py")
                                    joined_path = os.path.join(base_dir, *[ast.literal_eval(arg) for arg in element.args[1:]])
                                    raw_dirs.append(joined_path)
                        elif isinstance(element, ast.Constant):
                            # Handle plain string paths
                            raw_dirs.append(ast.literal_eval(element))
                    return raw_dirs

        raise ValueError("DIRS key not found in TEMPLATES setting or is not a list.")

    def get_templates_dir(self):
        """
        Retrieve the primary templates directory from TEMPLATES["DIRS"].

        Returns:
            str: The first directory configured in TEMPLATES["DIRS"].

        Raises:
            ValueError: If no template directories are configured.
        """
        templates_dirs = self.get_templates_dirs()
        if not templates_dirs:
            raise ValueError("No template directories are configured in TEMPLATES['DIRS'].")
        return templates_dirs[0]