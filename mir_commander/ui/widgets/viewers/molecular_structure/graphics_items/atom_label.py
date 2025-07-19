from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode


class AtomLabel(SceneNode):
    def __init__(self, element_symbol: str, index_num: int, position: QVector3D):
        super().__init__(transparent=True, picking_visible=False)
        self.set_scale(QVector3D(0.4, 0.4, 0.4))
        self.set_model("square")
        self.set_shader("text")
        self.set_texture(f"atom_{element_symbol}")
