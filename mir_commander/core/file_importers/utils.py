from pathlib import Path

from mir_commander.api.file_importer import FileImporterPlugin
from mir_commander.api.metadata import Metadata


class BaseImporter(FileImporterPlugin):
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
            name=self.get_name(),
            version=(1, 0, 0),
            description="Core importer",
            author="Mir Commander",
            email="support@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )
