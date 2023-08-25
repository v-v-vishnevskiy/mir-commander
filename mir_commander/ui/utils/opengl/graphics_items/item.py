import logging
from typing import Union

from OpenGL.GL import glMultMatrixf, glPopMatrix, glPushMatrix
from PySide6.QtGui import QMatrix4x4

logger = logging.getLogger(__name__)


class Item:
    def __init__(self, parent: Union[None, "Item"] = None):
        self.__parent: Union[None, "Item"] = None
        self.__children: set["Item"] = set()
        if parent is not None:
            self.set_parent(parent)
        self.transform = QMatrix4x4()

    def _paint(self):
        raise NotImplementedError()

    def set_parent(self, item: "Item"):
        if not issubclass(type(item), Item):
            logger.error(f"1Invalid item type: {item.__class__.__name__}")
            return

        if self.__parent is not None:
            self.__parent.__children.remove(self)
        item.__children.add(self)
        self.__parent = item

    def remove_parent(self):
        if self.__parent is not None:
            self.__parent.__children.remove(self)
        self.__parent = None

    def paint(self):
        glPushMatrix()
        glMultMatrixf(self.transform.data())
        self._paint()
        for item in self.__children:
            item.paint()
        glPopMatrix()
