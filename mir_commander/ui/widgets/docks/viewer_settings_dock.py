from PySide6.QtWidgets import QWidget

from .base import BaseDock


class ViewerSettingsDock(BaseDock):
    """The viewer settings dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently active viewer in the mdi area.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Viewer Settings"), parent)
        self.setMinimumWidth(200)
