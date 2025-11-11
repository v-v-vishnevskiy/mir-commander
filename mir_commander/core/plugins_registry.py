import logging
from collections import defaultdict
from typing import Generic, TypeVar

from pydantic import BaseModel

from mir_commander.api.file_exporter import FileExporterPlugin
from mir_commander.api.file_importer import FileImporterPlugin
from mir_commander.api.plugin import Plugin
from mir_commander.api.program import ProgramPlugin
from mir_commander.api.project_node import ProjectNodePlugin

from .errors import PluginDisabledError, PluginNotFoundError, PluginRegistrationError

logger = logging.getLogger("Core.PluginsRegistry")

_plugin_types_map = {FileImporterPlugin, FileExporterPlugin, ProgramPlugin, ProjectNodePlugin}


T = TypeVar("T", bound=Plugin)


class PluginItem(BaseModel, Generic[T]):
    enabled: bool
    id: str
    plugin: T


class _PluginsRepository(Generic[T]):
    def __init__(self):
        self._plugins: dict[str, PluginItem[T]] = {}

    def _validate_plugin(self, plugin: T, author: str):
        if plugin.__class__ not in _plugin_types_map:
            raise PluginRegistrationError("Invalid plugin type")

        plugin_id = f"{author}.{plugin.id}"
        if plugin_id in self._plugins:
            raise PluginRegistrationError("Plugin already registered")

    def register(self, plugin: T, author: str):
        self._validate_plugin(plugin, author)
        plugin_id = f"{author}.{plugin.id}"
        self._plugins[plugin_id] = PluginItem[T](enabled=True, id=plugin_id, plugin=plugin)

    def get(self, plugin_id: str) -> T:
        try:
            plugin = self._plugins[plugin_id]
            if plugin.enabled is False:
                raise PluginDisabledError()
            return plugin.plugin
        except KeyError:
            raise PluginNotFoundError()

    def get_all(self) -> list[PluginItem[T]]:
        return list[PluginItem[T]](self._plugins.values())

    def set_enabled(self, plugin_id: str, enabled: bool):
        try:
            self._plugins[plugin_id].enabled = enabled
        except KeyError:
            raise PluginNotFoundError()


class PluginsRegistry:
    def __init__(self):
        self._plugins: dict[type[Plugin], _PluginsRepository] = defaultdict(lambda: _PluginsRepository())

    @property
    def file_importer(self) -> _PluginsRepository[FileImporterPlugin]:
        return self._plugins[FileImporterPlugin]

    @property
    def file_exporter(self) -> _PluginsRepository[FileExporterPlugin]:
        return self._plugins[FileExporterPlugin]

    @property
    def program(self) -> _PluginsRepository[ProgramPlugin]:
        return self._plugins[ProgramPlugin]

    @property
    def project_node(self) -> _PluginsRepository[ProjectNodePlugin]:
        return self._plugins[ProjectNodePlugin]

    def register_plugin(self, plugin: Plugin, author: str):
        try:
            self._plugins[plugin.__class__].register(plugin, author)
        except PluginRegistrationError as e:
            logger.error("Failed to register plugin `%s`: %s", plugin.__class__.__name__, e)
            return


plugins_registry = PluginsRegistry()
