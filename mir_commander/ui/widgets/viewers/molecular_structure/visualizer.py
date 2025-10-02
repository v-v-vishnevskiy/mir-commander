import logging
from typing import cast

from PySide6.QtCore import QPoint
from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.opengl.errors import Error, NodeNotFoundError, NodeParentError
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.models import cylinder, sphere
from mir_commander.ui.utils.opengl.opengl_widget import OpenGLWidget
from mir_commander.ui.utils.opengl.resource_manager import (
    FragmentShader,
    ShaderProgram,
    VertexArrayObject,
    VertexShader,
)
from mir_commander.ui.utils.opengl.text_overlay import TextOverlay
from mir_commander.ui.utils.opengl.utils import Color4f, compute_face_normals, compute_vertex_normals, normalize_color
from mir_commander.ui.utils.viewer import Viewer
from mir_commander.ui.utils.widget import TR
from mir_commander.utils.chem import symbol_to_atomic_number
from mir_commander.utils.message_channel import MessageChannel

from . import shaders
from .build_bonds_dialog import BuildBondsDialog
from .config import AtomLabelType
from .consts import VAO_CYLINDER_RESOURCE_NAME, VAO_SPHERE_RESOURCE_NAME
from .errors import CalcError
from .graphics_nodes import BaseGraphicsNode, Molecule, Molecules, RootNode, VolumeCube
from .save_image_dialog import SaveImageDialog
from .style import Style

logger = logging.getLogger("MoleculeStructureViewer.Visualizer")


class Visualizer(OpenGLWidget):
    def __init__(self, parent: QWidget, title: str, app_config: AppConfig):
        super().__init__(
            parent=parent,
            keymap=Keymap(app_config.project_window.widgets.viewers.molecular_structure.keymap.model_dump()),
        )

        self._app_config = app_config
        self._config = app_config.project_window.widgets.viewers.molecular_structure
        self.config = self._config.model_copy(deep=True)
        self._title = title

        self._style = Style(self._config)

        self._node_under_cursor: BaseGraphicsNode | None = None

        self._root_node = RootNode(root_node=self.resource_manager.current_scene.root_node)
        self._molecules = Molecules(parent=self._root_node)
        self._volume_cube = VolumeCube(parent=self._root_node, resource_manager=self.resource_manager)

        self._under_cursor_overlay = TextOverlay(
            parent=self,
            config=self._style.current.under_cursor_text_overlay,
        )
        self._under_cursor_overlay.hide()

        self.message_channel = MessageChannel()

    @property
    def volume_cube_isosurfaces(self) -> list[tuple[float, Color4f]]:
        return self._volume_cube.isosurfaces

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

    def initializeGL(self):
        super().initializeGL()

        self.set_background_color(normalize_color(self._style.current.background.color))

        # Add VAOs to resource manager
        self.resource_manager.add_vertex_array_object(self._get_sphere_vao())
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

    def set_atomic_coordinates(self, atomic_coordinates: list[AtomicCoordinates]):
        self._molecules.clear()
        for item in atomic_coordinates:
            self._add_atomic_coordinates(item)
        self._root_node.set_translation(-self._molecules.center)
        self.update()

    def add_atomic_coordinates(self, atomic_coordinates: AtomicCoordinates):
        self._add_atomic_coordinates(atomic_coordinates)
        self._root_node.set_translation(-self._molecules.center)
        self.update()

    def _add_atomic_coordinates(self, atomic_coordinates: AtomicCoordinates):
        Molecule(
            parent=self._molecules,
            atomic_coordinates=atomic_coordinates,
            geom_bond_tolerance=self._config.geom_bond_tolerance,
            style=self._style.current,
            atom_label_config=self._config.atom_label,
        )

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        self._volume_cube.set_volume_cube(volume_cube)
        self.update()

    def add_volume_cube_isosurface(self, value: float, color: Color4f):
        self._volume_cube.add_isosurface(value, color)
        self.update()

    def remove_volume_cube_isosurface(self, value: float):
        self._volume_cube.remove_isosurface(value)
        self.update()

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
            normals = compute_vertex_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(VAO_SPHERE_RESOURCE_NAME, vertices, normals)

    def _get_cylinder_vao(self) -> VertexArrayObject:
        logger.debug("Initializing cylinder mesh data")

        mesh_quality = self._config.quality.mesh
        slices = int(cylinder.min_slices * (mesh_quality * 2))
        tmp_vertices = cylinder.get_vertices(stacks=1, slices=slices, radius=1.0, length=1.0, caps=False)
        faces = cylinder.get_faces(stacks=1, slices=slices, caps=False)
        vertices = cylinder.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_vertex_normals(vertices)
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
        dlg = SaveImageDialog(self, self.size().width(), self.size().height(), self._title)
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
                    image = self.render_to_image(dlg.img_width, dlg.img_height, dlg.transparent_bg, dlg.crop_to_content)
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
                    if image.save(str(dlg.img_file_path)):
                        parent = cast(Viewer, self.parent())
                        parent.short_msg_signal.emit(TR.tr("Image saved"))
                    else:
                        QMessageBox.critical(
                            self,
                            self.tr("Save image"),
                            self.tr("Could not save image:")
                            + f"\n{dlg.img_file_path}\n"
                            + self.tr("The path does not exist or is write-protected."),
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
        for molecule in self._molecules.children:
            molecule.show_labels_for_all_atoms()
        self.update()

    def atom_labels_hide_for_all_atoms(self):
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
