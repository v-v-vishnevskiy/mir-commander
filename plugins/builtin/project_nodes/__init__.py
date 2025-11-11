from mir_commander.api.plugin import Metadata, Plugin
from mir_commander.api.project_node import ProjectNodeDetails, ProjectNodePlugin

from . import atomic_coordinates, atomic_coordinates_group, molecule, unex, volume_cube


def register_plugins() -> list[Plugin]:
    return [
        ProjectNodePlugin(
            id="atomic_coordinates",
            metadata=Metadata(
                name="Atomic Coordinates",
                version=(1, 0, 0),
                description="Core project node",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProjectNodeDetails(type=atomic_coordinates.TYPE, icon_path=atomic_coordinates.ICON_PATH),
        ),
        ProjectNodePlugin(
            id="atomic_coordinates_group",
            metadata=Metadata(
                name="Atomic Coordinates Group",
                version=(1, 0, 0),
                description="Core project node",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProjectNodeDetails(
                type=atomic_coordinates_group.TYPE, icon_path=atomic_coordinates_group.ICON_PATH
            ),
        ),
        ProjectNodePlugin(
            id="molecule",
            metadata=Metadata(
                name="Molecule",
                version=(1, 0, 0),
                description="Core project node",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProjectNodeDetails(type=molecule.TYPE, icon_path=molecule.ICON_PATH),
        ),
        ProjectNodePlugin(
            id="unex",
            metadata=Metadata(
                name="UNEX",
                version=(1, 0, 0),
                description="Core project node",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProjectNodeDetails(type=unex.TYPE, icon_path=unex.ICON_PATH),
        ),
        ProjectNodePlugin(
            id="volume_cube",
            metadata=Metadata(
                name="Volume Cube",
                version=(1, 0, 0),
                description="Core project node",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ProjectNodeDetails(type=volume_cube.TYPE, icon_path=volume_cube.ICON_PATH),
        ),
    ]
