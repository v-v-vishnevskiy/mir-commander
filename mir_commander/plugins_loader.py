import importlib.util
import logging
import sys
from pathlib import Path
from typing import Callable

from mir_commander.api.plugin_registry import PluginRegistry
from mir_commander.core.plugin_registry_adapter import plugin_registry

logger = logging.getLogger("PluginsLoader")


def load_from_directory(plugins_dir: Path):
    """
    Load plugins from a directory.

    Scans all subdirectories and imports __init__.py from each.
    Each __init__.py should have a register_plugins(registry) function.

    Args:
        plugins_dir: Path to directory containing plugin subdirectories
    """
    if not plugins_dir.exists():
        logger.debug("Plugins directory does not exist: %s", plugins_dir)
        return

    if not plugins_dir.is_dir():
        logger.warning("Plugins path is not a directory: %s", plugins_dir)
        return

    # Add plugins directory to sys.path temporarily
    plugins_dir_str = str(plugins_dir.absolute())
    if plugins_dir_str not in sys.path:
        sys.path.insert(0, plugins_dir_str)

    try:
        # Iterate through subdirectories
        for subdir in plugins_dir.iterdir():
            if not subdir.is_dir():
                continue

            if subdir.name.startswith("_") or subdir.name.startswith("."):
                continue

            init_file = subdir / "__init__.py"
            if not init_file.exists():
                logger.debug("Skipping directory without __init__.py: %s", subdir.name)
                continue

            try:
                module_name = subdir.name
                logger.info("Loading plugin from directory: %s", module_name)

                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, init_file)
                if spec is None or spec.loader is None:
                    logger.error("Failed to load spec for plugin: %s", module_name)
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Call register_plugins function if it exists
                if hasattr(module, "register_plugins"):
                    register_func: Callable[[PluginRegistry], None] = getattr(module, "register_plugins")
                    if callable(register_func):
                        register_func(plugin_registry)
                        logger.info("Successfully loaded plugin: %s", module_name)
                    else:
                        logger.error("register_plugins in '%s' is not callable", module_name)
                else:
                    logger.warning("Plugin directory '%s' has no `register_plugins` function", module_name)

            except Exception as e:
                logger.error("Failed to load plugin from '%s': %s", subdir.name, e, exc_info=True)

    finally:
        # Remove plugins directory from sys.path
        if plugins_dir_str in sys.path:
            sys.path.remove(plugins_dir_str)


def startup(plugins_dir: Path):
    """
    Load all external plugins.

    Loads plugins from:
    1. Python entry points (installed packages)
    2. Plugins directory (if provided)

    Args:
        plugins_dir: path to directory containing plugin files
    """
    logger.info("Loading external plugins...")

    # Load from plugins directory
    load_from_directory(plugins_dir)

    logger.info("External plugins loading completed")
