from abc import abstractmethod
from pathlib import Path

from mir_commander.api.file_importer import FileImporterPlugin
from mir_commander.api.metadata import Metadata
from mir_commander.api.plugin import PluginDependency


class BaseImporter(FileImporterPlugin):
    @abstractmethod
    def _get_name(self) -> str: ...

    @abstractmethod
    def _get_version(self) -> tuple[int, int, int]: ...

    def load_lines(self, path: Path, n: int) -> list[str]:
        lines = []
        with path.open("r") as input_file:
            for i, line in enumerate[str](input_file):
                lines.append(line)
                if i >= n:
                    break
        return lines

    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self._get_name(),
            version=self._get_version(),
            description="Core importer",
            author="Mir Commander",
            contacts="https://mircmd.com",
            license="MirCommander",
        )

    def get_dependencies(self) -> list[PluginDependency]:
        return []
