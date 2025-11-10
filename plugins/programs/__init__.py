from mir_commander.api.plugin_registry import PluginRegistry

from .cartesian_editor import CartesianEditor
from .molecular_visualizer import MolecularVisualizer


def register_plugins(registry: PluginRegistry):
    registry.register_program(MolecularVisualizer())
    registry.register_program(CartesianEditor())
