from mir_commander.api.file_exporter import FileExporterPlugin
from mir_commander.api.metadata import Metadata


class BaseExporter(FileExporterPlugin):
    def get_metadata(self) -> Metadata:
        return Metadata(
            name=self.get_name(),
            version=(1, 0, 0),
            description="Core exporter",
            author="Mir Commander",
            email="support@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )
