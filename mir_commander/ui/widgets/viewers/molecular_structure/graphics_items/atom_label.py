from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode


class AtomLabel(SceneNode):
    def __init__(self, position: QVector3D):
        super().__init__(transparent=True, picking_visible=False)
        self.translate(QVector3D(0.0, 0.0, 1.0))
        self.set_scale(QVector3D(0.5, 0.5, 0.5))
        self.set_model("square")
        self.set_shader("text")
        self.set_texture("atom")
