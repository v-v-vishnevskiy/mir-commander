from PySide6.QtGui import QMatrix4x4


class Item:
    def __init__(self):
        self.visible = True
        self.transform = QMatrix4x4()

    def clear(self):
        pass

    def paint(self):
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.__class__.__name__
