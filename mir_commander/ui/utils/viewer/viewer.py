from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiSubWindow, QWidget


class Viewer(QMdiSubWindow):
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    settings: type[QWidget] | None = None

    def __init__(self, parent: QWidget, item: QStandardItem):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.item = item
