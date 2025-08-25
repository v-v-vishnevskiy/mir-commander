from typing import Any, Generic, TypeVar, get_args

from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from ..widget import Menu
from .viewer import Viewer

T = TypeVar("T", bound=Viewer)


class ViewerMenu(Generic[T], Menu):
    _type_T: Any

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    def __init__(self, title: str, parent: QWidget, mdi_area: QMdiArea):
        super().__init__(title, parent)
        self._mdi_area = mdi_area

    @property
    def active_viewer(self) -> T:
        return self._mdi_area.activeSubWindow()

    def update_state(self, window: None | QMdiSubWindow):
        if window and type(window) is self._type_T:
            self.set_enabled_actions(True)
        else:
            self.set_enabled_actions(False)
