from mir_commander.plugin_system.file_exporter import FileExporterPlugin
from mir_commander.plugin_system.metadata import Metadata


class BaseExporter(FileExporterPlugin):
    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self.get_name(),
            version=(1, 0, 0),
            description="Core exporter",
            author="Mir Commander",
            email="info@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )
