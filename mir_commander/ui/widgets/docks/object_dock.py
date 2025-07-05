from PySide6.QtWidgets import QWidget

from .base import BaseDock


class ObjectDock(BaseDock):
    """The object dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently chosen object in the project tree.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Object"), parent)
