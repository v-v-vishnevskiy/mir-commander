from PySide6.QtGui import QIcon

from mir_commander.api.program import Program as ProgramApi


class Program(ProgramApi):
    def get_title(self) -> str:
        names = [self.node.text()]
        parent_node = self.node.parent()
        while parent_node:
            names.append(parent_node.text())
            parent_node = parent_node.parent()
        return "/".join(reversed(names))

    def get_icon(self) -> QIcon:
        return self.node.icon()
