from .utils import ProjectNodePlugin


class VolumeCube(ProjectNodePlugin):
    def get_type(self) -> str:
        return "volume_cube"

    def get_name(self) -> str:
        return "Volume Cube"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/volume_cube.png"

    def get_default_program_name(self) -> str:
        return "molecular_visualizer"

    def get_program_names(self) -> list[str]:
        return []
