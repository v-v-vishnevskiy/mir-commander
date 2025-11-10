from mir_commander.api.plugin_registry import PluginRegistry

from .atomic_coordinates import AtomicCoordinates
from .atomic_coordinates_group import AtomicCoordinatesGroup
from .molecule import Molecule
from .unex import Unex
from .volume_cube import VolumeCube


def register_plugins(registry: PluginRegistry):
    registry.register_project_node(AtomicCoordinates())
    registry.register_project_node(AtomicCoordinatesGroup())
    registry.register_project_node(Molecule())
    registry.register_project_node(Unex())
    registry.register_project_node(VolumeCube())
