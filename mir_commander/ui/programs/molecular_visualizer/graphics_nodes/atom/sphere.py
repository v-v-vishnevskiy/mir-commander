from typing import TYPE_CHECKING

from PySide6.QtGui import QVector3D

from mir_commander.ui.sdk.opengl.scene import NodeType
from mir_commander.ui.sdk.opengl.utils import Color4f

from ...consts import VAO_SPHERE_RESOURCE_NAME
from ..base import BaseGraphicsNode

if TYPE_CHECKING:
    from .atom import Atom


class Sphere(BaseGraphicsNode):
    parent: "Atom"

    def __init__(self, radius: float, color: Color4f, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.OPAQUE, picking_visible=True))
        self.set_scale(QVector3D(radius, radius, radius))
        self.set_color(color)
        self.set_model(VAO_SPHERE_RESOURCE_NAME)
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
        atom = self.parent
        return f"Atom: {atom.element_symbol}{atom.index + 1}"

    def toggle_selection(self) -> bool:
        return self.parent.toggle_selection()
