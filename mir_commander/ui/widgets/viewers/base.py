from PySide6.QtCore import Signal


class BaseViewer:
    short_msg = Signal(str)
    long_msg = Signal(str)
