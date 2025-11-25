from PySide6.QtCore import QCoreApplication

from mir_commander.api.file_exporter import DefaultProperty, FileExporterDetails, FileExporterPlugin, TextParam
from mir_commander.api.plugin import Metadata, Plugin

from .src.xyz_exporter import write


def register_plugins() -> list[Plugin]:
    return [
        FileExporterPlugin(
            id="file_exporter_xyz",
            metadata=Metadata(
                name="XYZ",
                version=(1, 0, 0),
                description="XYZ file exporter",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=FileExporterDetails(
                supported_node_types=["builtin.atomic_coordinates"],
                extensions=["xyz"],
                format_params_config=[
                    TextParam(
                        id="title",
                        label=QCoreApplication.translate("builtin.file_exporter_xyz", "Title"),
                        default=DefaultProperty(value="node.full_name"),
                        required=False,
                    )
                ],
                write_function=write,
            ),
        )
    ]
