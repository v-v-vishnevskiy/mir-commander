from .utils import ProjectNodePlugin


class Molecule(ProjectNodePlugin):
    def get_type(self) -> str:
        return "molecule"

    def get_name(self) -> str:
        return "Molecule"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/molecule.png"

    def get_default_program_name(self) -> None | str:
        return None

    def get_program_names(self) -> list[str]:
        return []
