from .utils import ProjectNodePlugin


class VolumeCube(ProjectNodePlugin):
    def _get_name(self) -> str:
        return "Volume Cube"

    def _get_version(self) -> tuple[int, int, int]:
        return (1, 0, 0)

    def get_type(self) -> str:
        return "volume_cube"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/volume_cube.png"
