from typing import TypeVar

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class BaseViewer:
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    settings: type[QWidget] | None = None


T = TypeVar("T")


class BaseViewerSettings[T: BaseViewer](QWidget):
    def __init__(self):
        super().__init__()

        self._active_viewer: None | T = None
        self._all_viewers: list[T] = []

    def viewers(self, only_active: bool) -> list[T]:
        if only_active:
            return [self._active_viewer]
        else:
            return self._all_viewers

    def set_active_viewer(self, viewer: T):
        self._active_viewer = viewer

    def set_all_viewers(self, viewers: list[T]):
        self._all_viewers = viewers

    def __del__(self):
        self._active_viewer = None
        self._all_viewers.clear()
