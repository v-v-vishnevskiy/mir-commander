from PySide6.QtCore import QCoreApplication

from mir_commander.api.plugin import Metadata, Plugin
from mir_commander.api.program import ProgramDetails, ProgramPlugin

from . import cartesian_editor, molecular_visualizer


def register_plugins() -> list[Plugin]:
    return [
        ProgramPlugin(
            id="cartesian_editor",
            metadata=Metadata(
                name=QCoreApplication.translate("builtin.cartesian_editor", "Cartesian editor"),
                version=(1, 0, 0),
                description="Editor for atomic coordinates.",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProgramDetails(
                config_class=cartesian_editor.Config,
                program_class=cartesian_editor.Program,
                control_panel_class=cartesian_editor.ControlPanel,
                supported_node_types=["builtin.atomic_coordinates"],
                is_default_for_node_type=[],
            ),
        ),
        ProgramPlugin(
            id="molecular_visualizer",
            metadata=Metadata(
                name=QCoreApplication.translate("builtin.molecular_visualizer", "Molecular visualizer"),
                version=(1, 0, 0),
                description="Can visualize atomic coordinates and volume cubes.",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProgramDetails(
                config_class=molecular_visualizer.Config,
                program_class=molecular_visualizer.Program,
                control_panel_class=molecular_visualizer.ControlPanel,
                supported_node_types=[
                    "builtin.atomic_coordinates",
                    "builtin.atomic_coordinates_group",
                    "builtin.volume_cube",
                ],
                is_default_for_node_type=["builtin.atomic_coordinates", "builtin.volume_cube"],
            ),
        ),
    ]
