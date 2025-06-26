from typing import TYPE_CHECKING

from .base import BaseDock

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class ObjectDock(BaseDock):
    """The object dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently chosen object in the project tree.
    """

    def __init__(self, parent: "MainWindow"):
        super().__init__(self.tr("Object"), parent)
