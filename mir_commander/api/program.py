from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Iterable, TypeVar

from pydantic import BaseModel, Field
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from .plugin import Details, Plugin
from .project_node_schema import ProjectNodeSchema


class WindowSizeConfig(BaseModel):
    min_width: int = Field(default=50, ge=50, description="Minimum width")
    min_height: int = Field(default=50, ge=50, description="Minimum height")
    width: int = Field(default=300, ge=50, description="Width")
    height: int = Field(default=300, ge=50, description="Height")


class ProgramConfig(BaseModel):
    window_size: WindowSizeConfig = WindowSizeConfig()


class NodeChangedAction(BaseModel): ...


class ProgramError(Exception): ...


class UINode(QStandardItem):
    @property
    def id(self) -> int:
        raise NotImplementedError

    @property
    def project_node(self) -> ProjectNodeSchema:
        raise NotImplementedError


class MessageChannel(Enum):
    CONSOLE = "console"
    STATUS = "status"


class Program(QObject):
    send_message_signal = Signal(MessageChannel, str)
    node_changed_signal = Signal(int, NodeChangedAction)
    update_control_panel_signal = Signal(dict)
    update_window_title_signal = Signal(str)

    def __init__(self, node: UINode, config: ProgramConfig):
        super().__init__()
        self.node = node
        self.config = config

    def node_changed_event(self, node_id: int, action: NodeChangedAction):
        raise NotImplementedError

    def action_event(self, action: str, data: dict[str, Any], instance_index: int):
        raise NotImplementedError

    def get_title(self) -> str:
        raise NotImplementedError

    def get_icon(self) -> QIcon:
        raise NotImplementedError

    def get_widget(self) -> QWidget:
        raise NotImplementedError


T_WIDGET = TypeVar("T_WIDGET", bound=QWidget)


@dataclass
class ControlBlock(Generic[T_WIDGET]):
    title: str
    widget: T_WIDGET
    expanded: bool = Field(default=True, description="Whether the block is expanded by default")


T_PROGRAM = TypeVar("T_PROGRAM", bound=Program)


class ControlPanel(Generic[T_PROGRAM], QObject):
    program_action_signal = Signal(str, dict)

    def allows_apply_for_all(self) -> bool:
        raise NotImplementedError

    def get_blocks(self) -> Iterable[ControlBlock]:
        raise NotImplementedError

    def update_event(self, program: T_PROGRAM, data: dict[Any, Any]):
        raise NotImplementedError


class ProgramDetails(Details):
    config_class: type[ProgramConfig]
    program_class: type[Program]
    control_panel_class: type[ControlPanel]
    supported_node_types: list[str] = Field(default_factory=list, description="Supported node types")
    is_default_for_node_type: list[str] = Field(default_factory=list, description="Is default for node type")


class ProgramPlugin(Plugin):
    details: ProgramDetails
