from PySide6.QtGui import QColor
from mir_commander.ui.utils.opengl.utils import color_to_id, id_to_color


def test_color_to_id():
    assert color_to_id(QColor(255, 0, 0)) == 0xFF0000
    assert color_to_id(QColor(0, 0, 0)) == 0
    assert color_to_id(QColor(255, 255, 255)) == 0xFFFFFF
    assert color_to_id(QColor(0, 255, 0)) == 0x00FF00
    assert color_to_id(QColor(0, 0, 255)) == 0x0000FF


def test_id_to_color():
    assert id_to_color(0xFF0000) == (1.0, 0.0, 0.0, 1.0)
