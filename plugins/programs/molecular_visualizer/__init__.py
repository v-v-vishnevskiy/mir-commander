from mir_commander.api.metadata import Metadata
from mir_commander.api.plugin import PluginDependency
from mir_commander.api.program import ProgramPlugin

from .config import Config
from .control_panel import ControlPanel
from .program import Program


class MolecularVisualizer(ProgramPlugin):
    def get_metadata(self) -> Metadata:
        return Metadata(
            name="Molecular visualizer",
            version=(1, 0, 0),
            description="Can visualize atomic coordinates and volume cubes.",
            author="Mir Commander",
            email="support@mircmd.com",
            url="https://mircmd.com",
            license="MirCommander",
        )

    def get_id(self) -> str:
        return "molecular_visualizer"

    def get_config_class(self) -> type[Config]:
        return Config

    def get_program_class(self) -> type[Program]:
        return Program

    def get_control_panel_class(self) -> type[ControlPanel]:
        return ControlPanel

    def get_supported_node_types(self) -> list[str]:
        return ["atomic_coordinates", "atomic_coordinates_group", "volume_cube"]

    def is_default_for_node_type(self) -> list[str]:
        return ["atomic_coordinates", "volume_cube"]

    def get_dependencies(self) -> list[PluginDependency]:
        return []
