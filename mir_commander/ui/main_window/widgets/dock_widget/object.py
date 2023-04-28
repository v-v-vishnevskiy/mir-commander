from PySide6.QtCore import QT_TRANSLATE_NOOP
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget


class Object(DockWidget):
    """The object dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently chosen object in the project tree.
    """

    def __init__(self, parent: QWidget):
        super().__init__(QT_TRANSLATE_NOOP("DockNames", "Object"), parent)
