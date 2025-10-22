import logging
from typing import TYPE_CHECKING, Callable, cast

from PIL import Image, ImageCms
from PySide6.QtCore import QPoint
from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

from mir_commander.core.models import AtomicCoordinates
from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.opengl.errors import Error, NodeNotFoundError, NodeParentError
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.models import cone, cylinder, sphere
from mir_commander.ui.utils.opengl.opengl_widget import OpenGLWidget
from mir_commander.ui.utils.opengl.resource_manager import (
    FragmentShader,
    ShaderProgram,
    VertexArrayObject,
    VertexShader,
)
from mir_commander.ui.utils.opengl.text_overlay import TextOverlay
from mir_commander.ui.utils.opengl.utils import Color4f, compute_face_normals, compute_smooth_normals, normalize_color
from mir_commander.ui.utils.widget import TR
from mir_commander.utils.chem import symbol_to_atomic_number
from mir_commander.utils.message_channel import MessageChannel

from . import shaders
from .build_bonds_dialog import BuildBondsDialog
from .config import AtomLabelType
from .consts import VAO_CONE_RESOURCE_NAME, VAO_CYLINDER_RESOURCE_NAME, VAO_SPHERE_RESOURCE_NAME
from .control_panel import ControlPanel
from .entities import VolumeCubeIsosurfaceGroup
from .errors import CalcError
from .graphics_nodes import Axis, BaseGraphicsNode, CoordinateAxes, Molecule, Molecules, VolumeCube
from .save_image_dialog import SaveImageDialog
from .style import Style

if TYPE_CHECKING:
    from .program import MolecularVisualizer

logger = logging.getLogger("MoleculeStructureViewer.Visualizer")


class Visualizer(OpenGLWidget):
    parent: Callable[[], "MolecularVisualizer"]  # type: ignore[assignment]

    def __init__(self, title: str, app_config: AppConfig, control_panel: ControlPanel | None, *args, **kwargs):
        kwargs["keymap"] = Keymap(app_config.project_window.widgets.programs.molecular_visualizer.keymap.model_dump())
        super().__init__(*args, **kwargs)

        self._title = title
        self._app_config = app_config
        self._control_panel = control_panel
        self._config = app_config.project_window.widgets.programs.molecular_visualizer
        self.config = self._config.model_copy(deep=True)

        self._style = Style(self._config)

        self._node_under_cursor: BaseGraphicsNode | None = None

        self._main_node = self.resource_manager.current_scene.main_node
        self._coordinate_axes = CoordinateAxes(parent=self._main_node)
        self._molecules = Molecules(parent=self._main_node)
        self._volume_cube = VolumeCube(parent=self._main_node, resource_manager=self.resource_manager)

        self._under_cursor_overlay = TextOverlay(
            parent=self,
            config=self._style.current.under_cursor_text_overlay,
        )
        self._under_cursor_overlay.hide()

        self.message_channel = MessageChannel()

    def init_actions(self):
        super().init_actions()
        self.action_handler.add_action("toggle_node_selection", False, self.toggle_node_selection_under_cursor)

    def init_shaders(self):
        super().init_shaders()
        self.resource_manager.add_shader(
            ShaderProgram(
                "atom_label", VertexShader(shaders.vertex.ATOM_LABEL), FragmentShader(shaders.fragment.ATOM_LABEL)
            )
        )

    def init_opengl(self):
        super().init_opengl()

        self.set_background_color(normalize_color(self._style.current.background.color))

        # Add VAOs to resource manager
        self.resource_manager.add_vertex_array_object(self._get_sphere_vao())
        self.resource_manager.add_vertex_array_object(self._get_cone_vao())
        self.resource_manager.add_vertex_array_object(self._get_cylinder_vao())

        max_radius = self._molecules.get_max_molecule_radius()
        self.projection_manager.orthographic_projection.set_view_bounds(max_radius + max_radius * 0.10)

        current_fov = self._style.current.projection.perspective.fov
        self.set_perspective_projection_fov(current_fov)
        fov_factor = current_fov / 45.0
        self.projection_manager.perspective_projection.set_near_far_plane(
            max_radius / fov_factor,
            8 * max_radius / fov_factor,
        )
        self.set_projection_mode(self._style.current.projection.mode)

        self.resource_manager.current_camera.reset_to_default()
        self.resource_manager.current_camera.set_position(QVector3D(0, 0, 3 * max_radius / fov_factor))

    @property
    def coordinate_axes(self) -> CoordinateAxes:
        return self._coordinate_axes

    def scale_scene(self, value: float):
        super().scale_scene(value)
        if self.hasFocus() and self._control_panel is not None:
            self._control_panel.view.update_values(self.parent())

    def rotate_scene(self, pitch: float, yaw: float, roll: float):
        super().rotate_scene(pitch, yaw, roll)
        if self.hasFocus() and self._control_panel is not None:
            self._control_panel.view.update_values(self.parent())

    def coordinate_axes_adjust_length(self):
        self._coordinate_axes.set_length(self._molecules.max_coordinate + 1.0)
        self.update()

    def set_coordinate_axes_thickness(self, value: float):
        self._coordinate_axes.set_thickness(value)
        self.update()

    def set_coordinate_axes_length(self, value: float):
        self._coordinate_axes.set_length(value)
        self.update()

    def set_coordinate_axes_font_size(self, value: int):
        self._coordinate_axes.set_font_size(value)
        self.update()

    def set_coordinate_axes_visible(self, value: bool):
        self._coordinate_axes.set_visible(value)
        self.update()

    def set_coordinate_axes_labels_visible(self, value: bool):
        self._coordinate_axes.set_labels_visible(value)
        self.update()

    def set_coordinate_axes_both_directions(self, value: bool):
        self._coordinate_axes.set_both_directions(value)
        self.update()

    def set_coordinate_axes_center(self, value: bool):
        if value:
            self._coordinate_axes.set_position(self._molecules.center)
        else:
            self._coordinate_axes.set_position(QVector3D(0.0, 0.0, 0.0))
        self.update()

    def set_coordinate_axis_label_color(self, axis: str, color: Color4f):
        self._get_axis_by_name(axis).set_label_color(color)
        self.update()

    def set_coordinate_axis_color(self, axis: str, color: Color4f):
        self._get_axis_by_name(axis).set_color(color)
        self.update()

    def set_coordinate_axis_text(self, axis: str, text: str):
        self._get_axis_by_name(axis).set_text(text)
        self.update()

    def set_atomic_coordinates(self, atomic_coordinates: list[tuple[int, AtomicCoordinates]]):
        self._molecules.clear()
        for tree_item_id, data in atomic_coordinates:
            self._add_atomic_coordinates(tree_item_id, data)
        self._main_node.set_position(-self._molecules.center)
        self.update()

    def add_atomic_coordinates(self, tree_item_id: int, data: AtomicCoordinates):
        self._add_atomic_coordinates(tree_item_id, data)
        self._main_node.set_position(-self._molecules.center)
        self.update()

    def build_molecule(self, tree_item_id: int):
        try:
            molecule = self._get_molecule(tree_item_id)
            molecule.build()
            self._main_node.set_position(-self._molecules.center)
            self.update()
        except (ValueError, IndexError) as e:
            logger.error("Failed to add new atom: %s", e)

    def update_atomic_number(self, tree_item_id: int, atom_index: int):
        try:
            molecule = self._get_molecule(tree_item_id)
            molecule.update_atomic_number(atom_index)
            self.update()
        except (ValueError, IndexError) as e:
            logger.error("Failed to set atomic number: %s", e)

    def remove_atoms(self, tree_item_id: int, indices: list[int]):
        try:
            self._get_molecule(tree_item_id).remove_atoms(indices)
            self._main_node.set_position(-self._molecules.center)
            self.update()
        except ValueError as e:
            logger.error("Failed to remove atoms: %s", e)

    def swap_atoms_indices(self, tree_item_id: int, index_1: int, index_2: int):
        try:
            self._get_molecule(tree_item_id).swap_atoms_indices(index_1, index_2)
            self.update()
        except ValueError as e:
            logger.error("Failed to swap atoms: %s", e)

    def _get_molecule(self, tree_item_id: int) -> Molecule:
        for molecule in self._molecules.children:
            if molecule.tree_item_id == tree_item_id:
                return molecule
        raise ValueError(f"Molecule with tree_item_id {tree_item_id} not found")

    def _get_axis_by_name(self, name: str) -> Axis:
        if name == "x":
            return self._coordinate_axes.x
        elif name == "y":
            return self._coordinate_axes.y
        elif name == "z":
            return self._coordinate_axes.z
        raise ValueError(f"Invalid axis name: {name}")

    def _add_atomic_coordinates(self, tree_item_id: int, data: AtomicCoordinates):
        Molecule(
            tree_item_id=tree_item_id,
            atomic_coordinates=data,
            geom_bond_tolerance=self._config.geom_bond_tolerance,
            style=self._style.current,
            atom_label_config=self._config.atom_label,
            parent=self._molecules,
        )

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        self.makeCurrent()
        self._volume_cube.set_volume_cube(volume_cube)
        self.update()

    def add_volume_cube_isosurface(
        self, value: float, color_1: Color4f, color_2: Color4f = (1.0, 1.0, 1.0, 0.2), inverse: bool = False
    ):
        self.makeCurrent()
        result = self._volume_cube.add_isosurface(value, color_1, color_2, inverse)
        self.update()
        return result

    def get_volume_cube_isosurface_groups(self) -> list[VolumeCubeIsosurfaceGroup]:
        return self._volume_cube.isosurface_groups

    def is_empty_volume_cube_scalar_field(self) -> bool:
        return self._volume_cube.is_empty_scalar_field

    def set_title(self, title: str):
        self._title = title

    def toggle_node_selection_under_cursor(self):
        try:
            node = cast(BaseGraphicsNode, self.node_under_cursor())
            node.toggle_selection()
            self.update()
        except (NodeNotFoundError, NodeParentError):
            # NodeParentError is raised when node has no parent
            pass

    def new_cursor_position(self, x: int, y: int):
        self._handle_node_under_cursor(x, y)

    def _get_sphere_vao(self) -> VertexArrayObject:
        logger.debug("Initializing sphere mesh data")

        mesh_quality = self._config.quality.mesh
        stacks, slices = int(sphere.min_stacks * mesh_quality), int(sphere.min_slices * mesh_quality)
        tmp_vertices = sphere.get_vertices(stacks=stacks, slices=slices)
        faces = sphere.get_faces(stacks=stacks, slices=slices)
        vertices = sphere.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_smooth_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(VAO_SPHERE_RESOURCE_NAME, vertices, normals)

    def _get_cone_vao(self) -> VertexArrayObject:
        logger.debug("Initializing cone mesh data")

        mesh_quality = self._config.quality.mesh
        slices = int(cone.min_slices * (mesh_quality * 2))
        tmp_vertices = cone.get_vertices(stacks=1, slices=slices, radius=1.0, length=1.0, cap=True)
        faces = cone.get_faces(stacks=1, slices=slices, cap=True)
        vertices = cone.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_smooth_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(VAO_CONE_RESOURCE_NAME, vertices, normals)

    def _get_cylinder_vao(self) -> VertexArrayObject:
        logger.debug("Initializing cylinder mesh data")

        mesh_quality = self._config.quality.mesh
        slices = int(cylinder.min_slices * (mesh_quality * 2))
        tmp_vertices = cylinder.get_vertices(stacks=1, slices=slices, radius=1.0, length=1.0, caps=False)
        faces = cylinder.get_faces(stacks=1, slices=slices, caps=False)
        vertices = cylinder.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_smooth_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(VAO_CYLINDER_RESOURCE_NAME, vertices, normals)

    def _handle_node_under_cursor(self, x: int, y: int):
        if self._node_under_cursor is not None:
            self._node_under_cursor.set_under_cursor(False)

        try:
            node_under_cursor = cast(BaseGraphicsNode, self.node_under_cursor())
            node_under_cursor.set_under_cursor(True)
            self._node_under_cursor = node_under_cursor

            if text := node_under_cursor.get_text():
                self._under_cursor_overlay.set_text(text)
                size = self._under_cursor_overlay.size()
                self._under_cursor_overlay.set_position(QPoint(x, y - size.height()))
                self._under_cursor_overlay.show()
            else:
                self._under_cursor_overlay.set_text("")
                self._under_cursor_overlay.hide()
        except NodeNotFoundError:
            if self._node_under_cursor is not None:
                self._node_under_cursor.set_under_cursor(False)
                self._node_under_cursor = None
            self._under_cursor_overlay.set_text("")
            self._under_cursor_overlay.hide()
        self.update()

    def save_img_action_handler(self):
        dlg = SaveImageDialog(
            self,
            int(self.size().width() * self.devicePixelRatio()),
            int(self.size().height() * self.devicePixelRatio()),
            self._title,
        )
        if dlg.exec():
            save_flag = True
            if dlg.img_file_path.exists():
                ret = QMessageBox.warning(
                    self,
                    self.tr("Save image"),
                    self.tr("The file already exists:")
                    + f"\n{dlg.img_file_path}\n"
                    + self.tr("Do you want to overwrite it?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if ret != QMessageBox.StandardButton.Yes:
                    save_flag = False

            if save_flag:
                image = None
                try:
                    bg_color = (0.0, 0.0, 0.0, 0.0) if dlg.transparent_bg else None
                    image = self.render_to_image(dlg.img_width, dlg.img_height, bg_color, dlg.crop_to_content)
                except Error as e:
                    message_box = QMessageBox(
                        QMessageBox.Icon.Critical,
                        self.tr("Error image rendering"),
                        self.tr("Cannot create image."),
                        QMessageBox.StandardButton.Close,
                    )
                    message_box.setDetailedText(str(e))
                    message_box.exec()

                if image is not None:
                    try:
                        profile = ImageCms.createProfile("sRGB")
                        Image.fromarray(image).save(
                            str(dlg.img_file_path), icc_profile=ImageCms.ImageCmsProfile(profile).tobytes()
                        )
                        self.parent().short_msg_signal.emit(TR.tr("Image saved"))
                    except Exception as e:
                        logger.error("Could not save image: %s", e)
                        if isinstance(e, OSError):
                            message = self.tr("The path does not exist or is write-protected.")
                        elif isinstance(e, ValueError):
                            message = self.tr("The output format could not be determined.")
                        else:
                            message = self.tr("Error saving image")

                        QMessageBox.critical(
                            self,
                            self.tr("Save image"),
                            self.tr("Could not save image:") + f"\n{dlg.img_file_path}\n" + message,
                        )

    def set_next_style(self):
        if self._style.set_next_style():
            self._molecules.set_style(self._style.current)
            self._under_cursor_overlay.set_config(self._style.current.under_cursor_text_overlay, skip_position=True)
            self.update()

    def set_prev_style(self):
        if self._style.set_prev_style():
            self._molecules.set_style(self._style.current)
            self._under_cursor_overlay.set_config(self._style.current.under_cursor_text_overlay, skip_position=True)
            self.update()

    def select_all_atoms(self):
        for molecule in self._molecules.children:
            molecule.select_all_atoms()
        self.update()

    def unselect_all_atoms(self):
        for molecule in self._molecules.children:
            molecule.unselect_all_atoms()
        self.update()

    def select_toggle_all_atoms(self):
        for molecule in self._molecules.children:
            molecule.select_toggle_all_atoms()
        self.update()

    def cloak_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.cloak_selected_atoms()
        self.update()

    def cloak_not_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.cloak_not_selected_atoms()
        self.update()

    def cloak_h_atoms(self):
        for molecule in self._molecules.children:
            molecule.cloak_h_atoms()
        self.update()

    def cloak_not_selected_h_atoms(self):
        for molecule in self._molecules.children:
            molecule.cloak_not_selected_h_atoms()
        self.update()

    def cloak_toggle_h_atoms(self):
        for molecule in self._molecules.children:
            molecule.cloak_toggle_h_atoms()
        self.update()

    def uncloak_all_atoms(self):
        for molecule in self._molecules.children:
            molecule.uncloak_all_atoms()
        self.update()

    def _cloak_atoms_by_atnum(self, atomic_num: int):
        for molecule in self._molecules.children:
            molecule.cloak_atoms_by_atnum(atomic_num)
        self.update()

    def cloak_atoms_by_atnum(self):
        el_symbol, ok = QInputDialog.getText(
            self, self.tr("Cloak atoms by type"), self.tr("Enter element symbol:"), QLineEdit.EchoMode.Normal, ""
        )
        if ok:
            try:
                self._cloak_atoms_by_atnum(symbol_to_atomic_number(el_symbol))
            except ValueError:
                QMessageBox.critical(
                    self,
                    self.tr("Cloak atoms by type"),
                    self.tr("Invalid element symbol!"),
                    buttons=QMessageBox.StandardButton.Ok,
                )

    def calc_auto_lastsel_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_auto_lastsel_atoms())
        except CalcError as e:
            QMessageBox.critical(
                self, self.tr("Auto geometrical parameter"), str(e), buttons=QMessageBox.StandardButton.Ok
            )

    def calc_distance_last2sel_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_distance_last2sel_atoms())
        except CalcError as e:
            QMessageBox.critical(self, self.tr("Interatomic distance"), str(e), buttons=QMessageBox.StandardButton.Ok)

    def calc_angle_last3sel_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_angle_last3sel_atoms())
        except CalcError as e:
            QMessageBox.critical(self, self.tr("Angle"), str(e), buttons=QMessageBox.StandardButton.Ok)

    def calc_torsion_last4sel_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_torsion_last4sel_atoms())
        except CalcError as e:
            QMessageBox.critical(self, self.tr("Torsion angle"), str(e), buttons=QMessageBox.StandardButton.Ok)

    def calc_oop_last4sel_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_oop_last4sel_atoms())
        except CalcError as e:
            QMessageBox.critical(self, self.tr("Out-of-plane angle"), str(e), buttons=QMessageBox.StandardButton.Ok)

    def calc_all_parameters_selected_atoms(self):
        try:
            self.message_channel.send(self._molecules.calc_all_parameters_selected_atoms())
        except CalcError as e:
            QMessageBox.critical(self, self.tr("All parameters"), str(e), buttons=QMessageBox.StandardButton.Ok)

    def toggle_bonds_for_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.toggle_bonds_for_selected_atoms()
        self.update()

    def add_bonds_for_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.add_bonds_for_selected_atoms()
        self.update()

    def remove_bonds_for_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.remove_bonds_for_selected_atoms()
        self.update()

    def rebuild_bonds(self, tol: float = -2.0):
        for molecule in self._molecules.children:
            molecule.set_geom_bond_tolerance(tol)
        self.update()

    def rebuild_bonds_default(self):
        self.rebuild_bonds(self.config.geom_bond_tolerance)

    def rebuild_bonds_dynamic(self):
        current_tol = []
        for molecule in self._molecules.children:
            current_tol.append(molecule._geom_bond_tolerance)

        # TODO: get current geom bond tolerance from molecules
        dlg = BuildBondsDialog(self.config.geom_bond_tolerance, self)
        if not dlg.exec():
            for i, molecule in enumerate(self._molecules.children):
                molecule.set_geom_bond_tolerance(current_tol[i])
            self.update()

    def atom_labels_show_for_all_atoms(self):
        self._config.atom_label.visible = True
        for molecule in self._molecules.children:
            molecule.show_labels_for_all_atoms()
        self.update()

    def atom_labels_hide_for_all_atoms(self):
        self._config.atom_label.visible = False
        for molecule in self._molecules.children:
            molecule.hide_labels_for_all_atoms()
        self.update()

    def atom_labels_show_for_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.show_labels_for_selected_atoms()
        self.update()

    def atom_labels_hide_for_selected_atoms(self):
        for molecule in self._molecules.children:
            molecule.hide_labels_for_selected_atoms()
        self.update()

    def atom_labels_set_type(self, value: AtomLabelType):
        self.config.atom_label.type = value
        for molecule in self._molecules.children:
            molecule.set_label_type_for_all_atoms(value)
        self.update()

    def set_label_size_for_all_atoms(self, size: int):
        self.config.atom_label.size = size
        for molecule in self._molecules.children:
            molecule.set_label_size_for_all_atoms(size)
        self.update()

    def set_label_offset_for_all_atoms(self, offset: float):
        self.config.atom_label.offset = offset
        for molecule in self._molecules.children:
            molecule.set_label_offset_for_all_atoms(offset)
        self.update()
