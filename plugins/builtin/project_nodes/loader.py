from mir_commander.api.plugin import Metadata, Plugin
from mir_commander.api.project_node import ProjectNodeDetails, ProjectNodePlugin


def register_plugins() -> list[Plugin]:
    return [
        ProjectNodePlugin(
            id="atomic_coordinates",
            metadata=Metadata(
                name="Atomic Coordinates",
                version=(1, 0, 0),
                description="Core project node",
                publisher="mircmd",
            ),
            details=ProjectNodeDetails(
                type="atomic_coordinates", icon_path=":/builtin/resources/icons/atomic_coordinates.png"
            ),
        ),
        ProjectNodePlugin(
            id="atomic_coordinates_group",
            metadata=Metadata(
                name="Atomic Coordinates Group",
                version=(1, 0, 0),
                description="Core project node",
                publisher="mircmd",
            ),
            details=ProjectNodeDetails(
                type="atomic_coordinates_group", icon_path=":/builtin/resources/icons/atomic_coordinates_group.png"
            ),
        ),
        ProjectNodePlugin(
            id="molecule",
            metadata=Metadata(
                name="Molecule",
                version=(1, 0, 0),
                description="Core project node",
                publisher="mircmd",
            ),
            details=ProjectNodeDetails(type="molecule", icon_path=":/builtin/resources/icons/molecule.png"),
        ),
        ProjectNodePlugin(
            id="unex",
            metadata=Metadata(
                name="UNEX",
                version=(1, 0, 0),
                description="Core project node",
                publisher="mircmd",
            ),
            details=ProjectNodeDetails(type="unex", icon_path=":/builtin/resources/icons/unex.png"),
        ),
        ProjectNodePlugin(
            id="volume_cube",
            metadata=Metadata(
                name="Volume Cube",
                version=(1, 0, 0),
                description="Core project node",
                publisher="mircmd",
            ),
            details=ProjectNodeDetails(type="volume_cube", icon_path=":/builtin/resources/icons/volume_cube.png"),
        ),
    ]
