from typing import Any, Generic, TypeVar, get_args

from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from .widget import Menu


T = TypeVar("T", bound=QWidget)


class SubWindowMenu(Generic[T], Menu):
    _type_T: Any

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    def __init__(self, title: str, parent: QWidget, mdi_area: QMdiArea):
        super().__init__(title, parent)
        self._mdi_area = mdi_area

    @property
    def widget(self) -> T:
        return self._mdi_area.activeSubWindow().widget()

    def update_state(self, window: None | QMdiSubWindow):
        if window and type(window.widget()) is self._type_T:
            self.set_enabled_actions(True)
        else:
            self.set_enabled_actions(False)
