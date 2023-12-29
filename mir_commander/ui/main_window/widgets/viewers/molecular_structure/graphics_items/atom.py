from OpenGL.GL import GLuint
from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.graphics_items import MeshItem
from mir_commander.ui.utils.opengl.mesh import Sphere
from mir_commander.ui.utils.opengl.shader import ShaderProgram
from mir_commander.ui.utils.opengl.utils import Color4f


class Atom(MeshItem):
    def __init__(
        self,
        mesh_data: Sphere,
        index_num: int,
        atomic_num: int,
        element_symbol: str,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_shader: ShaderProgram,
    ):
        super().__init__(mesh_data, color=color)
        self.position = position
        self.radius = radius
        self.index_num = index_num
        self.atomic_num = atomic_num
        self.element_symbol = element_symbol
        self.selected_shader = selected_shader
        self.cloaked = False  # if `True` do not draw this atom and its bonds. Also see `Bond.paint` method
        self.selected = False
        self._under_cursor = False

        self._compute_transform()

    def _compute_transform(self):
        self.transform.setToIdentity()
        self.transform.translate(self.position)

        radius = self.radius
        if self._under_cursor:
            radius *= 1.15

        self.transform.scale(radius, radius, radius)

    @property
    def shader(self) -> GLuint:
        if self.selected:
            return self.selected_shader.program
        return super().shader

    def paint(self):
        if not self.cloaked:
            super().paint()

    def set_under_cursor(self, value: bool):
        if self._under_cursor != value:
            self._under_cursor = value
            self._compute_transform()

    def set_radius(self, radius: float):
        self.radius = radius
        self._compute_transform()

    def set_position(self, position: QVector3D):
        self.position = position
        self._compute_transform()

    def cross_with_line_test(self, point: QVector3D, direction: QVector3D) -> bool:
        if not self.cloaked:
            return self.position.distanceToLine(point, direction) <= self.radius
        return False

    def toggle_selection(self):
        self.selected = not self.selected
        return self.selected
