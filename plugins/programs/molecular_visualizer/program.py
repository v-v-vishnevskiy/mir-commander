import logging
from typing import Any, cast

from PIL import Image, ImageCms
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from mir_commander.api.data_structures import AtomicCoordinates, VolumeCube
from mir_commander.api.program import MessageChannel, NodeChangedAction, UINode
from mir_commander.ui.sdk.opengl.utils import Color4f
from mir_commander.ui.sdk.widget import TR
from mir_commander.utils.text import sanitize_filename

from ..node_changed_actions import (
    AtomicCoordinatesAddAtomAction,
    AtomicCoordinatesNewPositionAction,
    AtomicCoordinatesNewSymbolAction,
    AtomicCoordinatesRemoveAtomsAction,
    AtomicCoordinatesSwapAtomsIndicesAction,
)
from ..program import BaseProgram
from .config import Config
from .visualizer import Visualizer

logger = logging.getLogger("UI.Programs.MolecularVisualizer")


class Program(BaseProgram):
    config: Config

    def __init__(self, all: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all = all

        self._atomic_coordinates_nodes: list[UINode] = []
        self._volume_cube_nodes: list[UINode] = []

        self.visualizer = Visualizer(program=self, title=self.node.text(), config=self.config)

        match self.node.project_node.data:
            case VolumeCube():
                self._volume_cube_nodes.append(self.node)
                self.visualizer.set_volume_cube(self.node.project_node.data)

        self._molecule_index = 0
        self._draw_node = self.node
        self._set_draw_node()
        self.visualizer.set_atomic_coordinates(self._get_draw_node_atomic_coordinates())
        self.visualizer.coordinate_axes_adjust_length()

    def _get_node(self, node_id: int) -> UINode:
        for nodes_list in [self._atomic_coordinates_nodes, self._volume_cube_nodes]:
            for node in nodes_list:
                if node.id == node_id:
                    return node
        raise ValueError(f"Node with id {node_id} not found")

    @property
    def _node_full_name(self) -> str:
        names = [self._draw_node.text()]
        parent_node = self._draw_node.parent()
        while parent_node:
            names.append(parent_node.text())
            parent_node = parent_node.parent()
        return "/".join(reversed(names))

    def _atomic_coordinates_node(self, index: int, parent: UINode, counter: int = -1) -> tuple[bool, int, UINode]:
        """
        Finds node with `AtomicCoordinates` data structure
        """

        index = max(0, index)
        last_node = parent
        if not parent.hasChildren() and parent.project_node.type == "atomic_coordinates":
            return True, 0, last_node
        else:
            for i in range(parent.rowCount()):
                node = cast(UINode, parent.child(i))
                if node.project_node.type == "atomic_coordinates":
                    last_node = node
                    counter += 1
                    if index == counter:
                        return True, counter, node
                elif self._all and node.hasChildren():
                    found, counter, last_node = self._atomic_coordinates_node(index, node, counter)
                    if found:
                        return found, counter, last_node
            return False, counter, last_node

    def _set_draw_node(self):
        _, self._molecule_index, self._draw_node = self._atomic_coordinates_node(self._molecule_index, self.node)
        self._atomic_coordinates_nodes = [self._draw_node]

    def _get_draw_node_atomic_coordinates(self) -> list[tuple[int, AtomicCoordinates]]:
        match self._draw_node.project_node.data:
            case AtomicCoordinates():
                return [(self._draw_node.id, self._draw_node.project_node.data)]
            case _:
                return []

    def set_prev_atomic_coordinates(self):
        if self._molecule_index > 0:
            self._molecule_index -= 1
            self._set_draw_node()
            self.update_window_title_signal.emit(self.get_title())
            self.visualizer.set_atomic_coordinates(self._get_draw_node_atomic_coordinates())

    def set_next_atomic_coordinates(self):
        self._molecule_index += 1
        node = self._draw_node
        self._set_draw_node()
        if node != self._draw_node:
            self.update_window_title_signal.emit(self.get_title())
            self.visualizer.set_atomic_coordinates(self._get_draw_node_atomic_coordinates())

    def save_image(
        self, filename: str, width: int, height: int, bg_color: Color4f | None = None, crop_to_content: bool = False
    ):
        filename = filename.replace("%n", sanitize_filename(self._node_full_name))
        try:
            image = self.visualizer.render_to_image(width, height, bg_color, crop_to_content)
            profile = ImageCms.createProfile("sRGB")
            Image.fromarray(image).save(filename, icc_profile=ImageCms.ImageCmsProfile(profile).tobytes())
            self.send_message_signal.emit(MessageChannel.CONSOLE, TR.tr("{} saved successfully").format(filename))
        except Exception as e:
            txt = TR.tr("Error saving image {}").format(filename)
            logger.error(f"{txt}: {e}")
            self.send_message_signal.emit(MessageChannel.CONSOLE, txt)

    def get_title(self) -> str:
        return self._node_full_name

    def get_icon(self) -> QIcon:
        return self._draw_node.icon()

    def update_control_panel_event(self, key: str, data: dict[str, Any]):
        match key:
            case "view.rotate_scene":
                self.visualizer.rotate_scene(**data)
            case "view.scale_scene":
                self.visualizer.scale_scene(**data)
            case "view.set_scene_rotation":
                self.visualizer.set_scene_rotation(**data)
            case "view.set_scene_scale":
                self.visualizer.set_scene_scale(**data)
            case "atom_labels.set_symbol_visible":
                self.visualizer.set_atom_symbol_visible(**data)
            case "atom_labels.set_number_visible":
                self.visualizer.set_atom_number_visible(**data)
            case "atom_labels.set_size":
                self.visualizer.set_label_size_for_all_atoms(**data)
            case "atom_labels.set_offset":
                self.visualizer.set_label_offset_for_all_atoms(**data)
            case "atom_labels.toggle_visibility_for_all_atoms":
                self.visualizer.toggle_labels_visibility_for_all_atoms(**data)
            case "atom_labels.toggle_visibility_for_selected_atoms":
                self.visualizer.toggle_labels_visibility_for_selected_atoms(**data)
            case "volume_cube.add_isosurface":
                self.visualizer.add_volume_cube_isosurface(**data)
            case "volume_cube.set_isosurface_color":
                self.visualizer.set_volume_cube_isosurface_color(**data)
            case "volume_cube.set_isosurface_visible":
                self.visualizer.set_volume_cube_isosurface_visible(**data)
            case "volume_cube.remove_isosurface":
                self.visualizer.remove_volume_cube_isosurface(**data)
            case "image.save":
                self.save_image(**data)
            case "coordinate_axes.set_visible":
                self.visualizer.set_coordinate_axes_visible(**data)
            case "coordinate_axes.set_labels_visible":
                self.visualizer.set_coordinate_axes_labels_visible(**data)
            case "coordinate_axes.set_both_directions":
                self.visualizer.set_coordinate_axes_both_directions(**data)
            case "coordinate_axes.set_to_center":
                self.visualizer.set_coordinate_axes_center(**data)
            case "coordinate_axes.set_length":
                self.visualizer.set_coordinate_axes_length(**data)
            case "coordinate_axes.set_thickness":
                self.visualizer.set_coordinate_axes_thickness(**data)
            case "coordinate_axes.set_font_size":
                self.visualizer.set_coordinate_axes_font_size(**data)
            case "coordinate_axes.set_color":
                self.visualizer.set_coordinate_axis_color(**data)
            case "coordinate_axes.set_label_color":
                self.visualizer.set_coordinate_axis_label_color(**data)
            case "coordinate_axes.set_text":
                self.visualizer.set_coordinate_axis_text(**data)
            case "coordinate_axes.adjust_length":
                self.visualizer.coordinate_axes_adjust_length(**data)
            case _:
                logger.error("Unknown key: %s", key)

    def node_changed_event(self, node_id: int, action: NodeChangedAction):
        try:
            data = self._get_node(node_id).project_node.data
        except ValueError:
            return

        match data:
            case AtomicCoordinates():
                match action:
                    case AtomicCoordinatesAddAtomAction():
                        self.visualizer.build_molecule(node_id)
                    case AtomicCoordinatesNewSymbolAction():
                        self.visualizer.update_atomic_number(node_id, action.atom_index)
                    case AtomicCoordinatesNewPositionAction():
                        self.visualizer.update_atom_position(node_id, action.atom_index)
                    case AtomicCoordinatesRemoveAtomsAction():
                        self.visualizer.remove_atoms(node_id, action.atom_indices)
                    case AtomicCoordinatesSwapAtomsIndicesAction():
                        self.visualizer.swap_atoms_indices(node_id, action.atom_index_1, action.atom_index_2)
                    case _:
                        logger.warning("Unknown action: %s", action)

    def get_widget(self) -> QWidget:
        return self.visualizer
