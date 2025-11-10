from .utils import ProjectNodePlugin


class AtomicCoordinates(ProjectNodePlugin):
    def _get_name(self) -> str:
        return "Atomic Coordinates"

    def _get_version(self) -> tuple[int, int, int]:
        return (1, 0, 0)

    def get_type(self) -> str:
        return "atomic_coordinates"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/atomic_coordinates.png"
