from typing import Generic, TypeVar

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from mir_commander.api.program import Program

T = TypeVar("T", bound=Program)


class ControlBlock(Generic[T], QWidget):
    def update_values(self, program: T):
        raise NotImplementedError


class BaseProgram(Program):
    def get_title(self) -> str:
        names = [self.node.text()]
        parent_node = self.node.parent()
        while parent_node:
            names.append(parent_node.text())
            parent_node = parent_node.parent()
        return "/".join(reversed(names))

    def get_icon(self) -> QIcon:
        return self.node.icon()
