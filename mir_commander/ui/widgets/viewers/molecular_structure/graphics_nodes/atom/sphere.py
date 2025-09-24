from typing import TYPE_CHECKING, cast

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode

if TYPE_CHECKING:
    from .atom import Atom


class Sphere(BaseGraphicsNode):
    def __init__(self, parent: "Atom", model_name: str, radius: float, color: Color4f):
        super().__init__(parent=parent, node_type=NodeType.OPAQUE, visible=True, picking_visible=True)
        self.set_scale(QVector3D(radius, radius, radius))
        self.set_color(color)
        self.set_model(model_name)
        self.set_shader("default")

        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(QVector3D(radius, radius, radius))

    def set_under_cursor(self, value: bool):
        if value:
            radius = self._radius * 1.15
        else:
            radius = self._radius
        self.set_scale(QVector3D(radius, radius, radius))

    def get_text(self) -> str:
        atom = cast("Atom", self._parent)
        return f"Atom: {atom.element_symbol}{atom.index_num + 1}"

    def toggle_selection(self) -> bool:
        atom = cast("Atom", self._parent)
        return atom.toggle_selection()
