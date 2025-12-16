from PySide6.QtCore import QCoreApplication

from mir_commander.api.plugin import Metadata, Plugin
from mir_commander.api.program import ProgramDetails, ProgramPlugin

from .src.cartesian_editor.config import Config as CartesianEditorConfig
from .src.cartesian_editor.control_panel import ControlPanel as CartesianEditorControlPanel
from .src.cartesian_editor.program import Program as CartesianEditorProgram
from .src.molecular_visualizer.config import Config as MolecularVisualizerConfig
from .src.molecular_visualizer.control_panel import ControlPanel as MolecularVisualizerControlPanel
from .src.molecular_visualizer.program import Program as MolecularVisualizerProgram


def register_plugins() -> list[Plugin]:
    return [
        ProgramPlugin(
            id="cartesian_editor",
            metadata=Metadata(
                name=QCoreApplication.translate("builtin.cartesian_editor", "Cartesian editor"),
                version=(1, 0, 0),
                description="Editor for atomic coordinates.",
                publisher="mircmd",
            ),
            details=ProgramDetails(
                config_class=CartesianEditorConfig,
                program_class=CartesianEditorProgram,
                control_panel_class=CartesianEditorControlPanel,
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
                publisher="mircmd",
            ),
            details=ProgramDetails(
                config_class=MolecularVisualizerConfig,
                program_class=MolecularVisualizerProgram,
                control_panel_class=MolecularVisualizerControlPanel,
                supported_node_types=[
                    "builtin.atomic_coordinates",
                    "builtin.atomic_coordinates_group",
                    "builtin.volume_cube",
                ],
                is_default_for_node_type=["builtin.atomic_coordinates", "builtin.volume_cube"],
            ),
        ),
    ]
