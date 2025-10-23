from typing import TYPE_CHECKING

from pydantic import BaseModel
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMdiSubWindow

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.widget import Translator, TrString
from mir_commander.ui.widgets.docks.project_dock.item_changed_actions import ItemChangedAction

from .program_control_panel import ProgramControlPanel

if TYPE_CHECKING:
    from mir_commander.ui.widgets.docks.project_dock.items import TreeItem


class ProgramWindow(QMdiSubWindow):
    _id_counter = 0

    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    item_changed_signal = Signal(int, int, ItemChangedAction)  # item_id, program_id, action
    control_panel_cls: type[ProgramControlPanel] | None = None
    name: TrString

    def __init__(
        self, item: "TreeItem", app_config: AppConfig, control_panel: ProgramControlPanel | None, *args, **kwargs
    ):
        ProgramWindow._id_counter += 1
        self._id = ProgramWindow._id_counter

        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.item = item
        self.app_config = app_config
        self.control_panel = control_panel
        self.update_window_title(self.item)

    @property
    def id(self) -> int:
        return self._id

    @classmethod
    def get_name(cls) -> str:
        return Translator.translate(cls.name)

    @property
    def item_name(self) -> str:
        name = self.item.text()
        parent_item = self.item.parent()
        while parent_item:
            name = parent_item.text() + "/" + name
            parent_item = parent_item.parent()
        return name

    def update_window_title(self, item: "TreeItem"):
        self.setWindowTitle(self.item_name)
        self.setWindowIcon(item.icon())

    def contains_item(self, item_id: int) -> bool:
        """Checks if the program window contains an item with the specified identifier."""
        return self.item.id == item_id

    def get_config(self) -> BaseModel:
        raise NotImplementedError("This method should be implemented in the subclass")

    def send_item_changed_signal(self, action: None | ItemChangedAction = None):
        self.item_changed_signal.emit(self.item.id, self._id, action)

    def item_changed_event(self, item_id: int, action: None | ItemChangedAction):
        raise NotImplementedError("This method should be implemented in the subclass")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, item={self.item})"
