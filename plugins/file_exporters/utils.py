from abc import abstractmethod

from mir_commander.api.file_exporter import FileExporterPlugin
from mir_commander.api.metadata import Metadata
from mir_commander.api.plugin import PluginDependency


class BaseExporter(FileExporterPlugin):
    @abstractmethod
    def _get_name(self) -> str: ...

    @abstractmethod
    def _get_version(self) -> tuple[int, int, int]: ...

    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self._get_name(),
            version=self._get_version(),
            description="Core exporter",
            author="Mir Commander",
            email="support@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )

    def get_dependencies(self) -> list[PluginDependency]:
        return []
