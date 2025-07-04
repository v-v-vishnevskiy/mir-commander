from PySide6.QtGui import QMatrix4x4

from .camera import Camera
from .graphics_items.item import Item


class Scene(Item):
    def __init__(self, camera: Camera):
        super().__init__()
        self._camera = camera

        self.add_item = self.add_child
        self.remove_item = self.remove_child

    @property
    def get_transform(self) -> QMatrix4x4:
        return self._camera.view_matrix * super().get_transform

    def paint_self(self):
        pass
