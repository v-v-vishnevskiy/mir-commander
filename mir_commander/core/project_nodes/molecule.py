from pydantic import Field

from mir_commander.plugin_system.project_node import ProjectNodeDataPlugin, ProjectNodePlugin


class MoleculeData(ProjectNodeDataPlugin):
    n_atoms: int = 0
    atomic_num: list[int] = []
    charge: int = 0
    multiplicity: int = 1
    contribution: float = Field(default=0.0, description="Contribution in mixtures in fraction of unit [0, 1]")


class MoleculeNode(ProjectNodePlugin):
    def get_type(self) -> str:
        return "molecule"

    def get_name(self) -> str:
        return "Molecule"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/molecule.png"

    def get_model_class(self) -> type[MoleculeData]:
        return MoleculeData

    def get_default_program_name(self) -> None | str:
        return None

    def get_program_names(self) -> list[str]:
        return []
