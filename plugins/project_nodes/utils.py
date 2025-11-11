from abc import abstractmethod

from mir_commander.api.metadata import Metadata
from mir_commander.api.plugin import PluginDependency
from mir_commander.api.project_node import ProjectNodePlugin as BaseProjectNodePlugin


class ProjectNodePlugin(BaseProjectNodePlugin):
    @abstractmethod
    def _get_name(self) -> str: ...

    @abstractmethod
    def _get_version(self) -> tuple[int, int, int]: ...

    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self._get_name(),
            version=self._get_version(),
            description="Core project node",
            author="Mir Commander",
            contacts="https://mircmd.com",
            license="MirCommander",
        )

    def get_dependencies(self) -> list[PluginDependency]:
        return []
