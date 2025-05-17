from typing import TYPE_CHECKING, Any, Generic, TypeVar, get_args

from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.utils.widget import Menu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


T = TypeVar("T", bound=QWidget)


class SubWindowMenu(Generic[T], Menu):
    _type_T: Any

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    def __init__(self, title: str, parent: "MainWindow"):
        super().__init__(title, parent)
        self._mdi_area = parent.mdi_area

    @property
    def widget(self) -> T:
        return self._mdi_area.activeSubWindow().widget()

    def update_state(self, window: None | QMdiSubWindow):
        if window and type(window.widget()) is self._type_T:
            self.set_enabled_actions(True)
        else:
            self.set_enabled_actions(False)
