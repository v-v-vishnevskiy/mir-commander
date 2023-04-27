from typing import Optional

from PySide6.QtGui import QIcon, QStandardItem

from mir_commander.data_structures.base import DataStructure


class Item(QStandardItem):
    def __init__(self, title: str, icon: str = "", data: Optional[DataStructure] = None):
        if icon:
            super().__init__(QIcon(icon), title)
        else:
            super().__init__(title)
        self.setData(data)
