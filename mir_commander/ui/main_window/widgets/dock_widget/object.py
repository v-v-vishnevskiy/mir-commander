from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config


class Object(DockWidget):
    """The object dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently chosen object in the project tree.
    """

    default_area = Qt.RightDockWidgetArea

    def __init__(self, parent: QWidget, config: Config):
        super().__init__(self.tr("Object"), config, parent)
