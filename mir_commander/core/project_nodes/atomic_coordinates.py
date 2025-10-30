from mir_commander.plugin_system.project_node import ProjectNodeDataPlugin, ProjectNodePlugin


class AtomicCoordinatesData(ProjectNodeDataPlugin):
    """
    Class of atomic positions defined as Cartesian coordinates.

    We need this separately because a molecule may have multiple sets of
    geometries, for example as a result of optimization,
    (multidimensional) scans, IRC scans, etc.
    Thus, the basic properties of atoms, common for all possible geometries,
    are collected in the Molecule instance and only the different sets of
    geometries are in separate instances of AtomicCoordinates.
    Note, in a similar manner we may design a class for Z-matrices, etc.
    """

    atomic_num: list[int] = []
    x: list[float] = []  # Cartesian coordinates X [A]
    y: list[float] = []  # Cartesian coordinates Y [A]
    z: list[float] = []  # Cartesian coordinates Z [A]


class AtomicCoordinatesNode(ProjectNodePlugin):
    def get_type(self) -> str:
        return "atomic_coordinates"

    def get_name(self) -> str:
        return "Atomic Coordinates"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/atomic_coordinates.png"

    def get_model_class(self) -> type[AtomicCoordinatesData]:
        return AtomicCoordinatesData

    def get_default_program_name(self) -> str:
        return "molecular_visualizer"

    def get_program_names(self) -> list[str]:
        return ["cartesian_editor"]
