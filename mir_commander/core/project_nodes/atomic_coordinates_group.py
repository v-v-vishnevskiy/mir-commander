from .utils import BaseProjectNode


class AtomicCoordinatesGroupNode(BaseProjectNode):
    def get_type(self) -> str:
        return "atomic_coordinates_group"

    def get_name(self) -> str:
        return "Atomic Coordinates Group"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/atomic_coordinates_group.png"

    def get_default_program_name(self) -> str:
        return "molecular_visualizer"

    def get_program_names(self) -> list[str]:
        return []
