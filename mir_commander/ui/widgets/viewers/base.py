from PySide6.QtCore import Signal


class BaseViewer:
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
