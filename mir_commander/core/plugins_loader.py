import importlib.util
import logging
import sys
from pathlib import Path
from typing import Callable

from mir_commander.api.plugin import Plugin

from .plugins_registry import plugins_registry

logger = logging.getLogger("PluginsLoader")


def load_from_directory(plugins_dir: Path, skip_authors: list[str] = []):
    """
    Load plugins from a directory.

    Scans author directories and plugin subdirectories within them.
    Each plugin's __init__.py should have a register_plugins(registry) function.

    Structure: plugins_dir -> author -> plugin_name -> __init__.py

    Args:
        plugins_dir: Path to directory containing author subdirectories
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
        # Iterate through author directories
        for author_dir in plugins_dir.iterdir():
            if author_dir.name in skip_authors:
                logger.debug("Skipping author: %s", author_dir.name)
                continue

            if not author_dir.is_dir():
                continue

            if author_dir.name.startswith("_") or author_dir.name.startswith("."):
                continue

            # Iterate through plugin directories within author directory
            for plugin_dir in author_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue

                if plugin_dir.name.startswith("_") or plugin_dir.name.startswith("."):
                    continue

                init_file = plugin_dir / "__init__.py"
                if not init_file.exists():
                    logger.debug("Skipping directory without __init__.py: %s/%s", author_dir.name, plugin_dir.name)
                    continue

                try:
                    module_name = f"{author_dir.name}.{plugin_dir.name}"

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
                        register_func: Callable[[], list[Plugin]] = getattr(module, "register_plugins")
                        if callable(register_func):
                            try:
                                for plugin in register_func():
                                    plugins_registry.register_plugin(plugin, author_dir.name)
                            except Exception as e:
                                logger.error("Failed to register plugins from '%s': %s", module_name, e)
                        else:
                            logger.error("register_plugins in '%s' is not callable", module_name)
                    else:
                        logger.error("Plugin directory '%s' has no `register_plugins` function", module_name)

                except Exception as e:
                    logger.error(
                        "Failed to load plugin from '%s/%s': %s", author_dir.name, plugin_dir.name, e, exc_info=True
                    )

    finally:
        # Remove plugins directory from sys.path
        if plugins_dir_str in sys.path:
            sys.path.remove(plugins_dir_str)
