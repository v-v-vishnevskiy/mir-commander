from typing import TYPE_CHECKING, Generic, TypeVar

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from .viewer import Viewer

T = TypeVar("T", bound="Viewer")


class ViewerSettings(Generic[T], QWidget):
    def __init__(self):
        super().__init__()

        self._active_viewer: None | T = None
        self._all_viewers: list[T] = []

    def get_viewers(self, only_active: bool) -> list[T]:
        if only_active:
            return [self._active_viewer] if self._active_viewer is not None else []
        else:
            return self._all_viewers

    def set_active_viewer(self, viewer: T):
        self._active_viewer = viewer

    def set_all_viewers(self, viewers: list[T]):
        self._all_viewers = viewers

    def __del__(self):
        self._active_viewer = None
        self._all_viewers.clear()


class EmptyViewerSettings(ViewerSettings):
    pass
