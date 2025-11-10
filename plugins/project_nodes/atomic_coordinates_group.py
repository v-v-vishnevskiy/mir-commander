from .utils import ProjectNodePlugin


class AtomicCoordinatesGroup(ProjectNodePlugin):
    def _get_name(self) -> str:
        return "Atomic Coordinates Group"

    def _get_version(self) -> tuple[int, int, int]:
        return (1, 0, 0)

    def get_type(self) -> str:
        return "atomic_coordinates_group"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/atomic_coordinates_group.png"
