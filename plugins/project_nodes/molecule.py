from .utils import ProjectNodePlugin


class Molecule(ProjectNodePlugin):
    def _get_name(self) -> str:
        return "Molecule"

    def _get_version(self) -> tuple[int, int, int]:
        return (1, 0, 0)

    def get_type(self) -> str:
        return "molecule"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/molecule.png"
