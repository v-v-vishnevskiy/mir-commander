from pathlib import Path

from mir_commander.plugin_system.file_importer import FileImporter


class BaseImporter(FileImporter):
    def load_lines(self, path: Path, n: int) -> list[str]:
        lines = []
        with path.open("r") as input_file:
            for i, line in enumerate[str](input_file):
                lines.append(line)
                if i >= n:
                    break
        return lines
