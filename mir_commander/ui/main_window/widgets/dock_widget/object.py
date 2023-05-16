from typing import TYPE_CHECKING

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Object(DockWidget):
    """The object dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently chosen object in the project tree.
    """

    def __init__(self, parent: "MainWindow", config: Config):
        super().__init__(self.tr("Object"), config, parent)
