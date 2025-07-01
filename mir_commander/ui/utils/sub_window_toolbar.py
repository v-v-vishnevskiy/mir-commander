from typing import Any, Generic, TypeVar, get_args

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from mir_commander.ui.config import Toolbars

from .widget import ToolBar

T = TypeVar("T", bound=QWidget)


class SubWindowToolBar(Generic[T], ToolBar):
    _type_T: Any

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    def __init__(self, title: str, parent: QWidget, mdi_area: QMdiArea, config: Toolbars):
        super().__init__(title, parent)
        self._mdi_area = mdi_area

        icon_size = config.icon_size
        self.setIconSize(QSize(icon_size, icon_size))

        self.setup_actions()
        self.set_enabled(False)

    @property
    def widget(self) -> T:
        return self._mdi_area.activeSubWindow().widget()

    def setup_actions(self):
        raise NotImplementedError()

    def set_enabled(self, flag: bool):
        for action in self.actions():
            action.setEnabled(flag)

    def update_state(self, window: None | QMdiSubWindow):
        if window and type(window.widget()) is self._type_T:
            self.set_enabled(True)
        else:
            self.set_enabled(False)
