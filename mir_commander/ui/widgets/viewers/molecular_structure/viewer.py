from typing import Optional

from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer import Viewer

from .atomic_coordinates_viewer import AtomicCoordinatesViewer
from .dock_settings.settings import Settings


class MolecularStructureViewer(Viewer):
    settings = Settings

    def __init__(self, parent: QWidget, item: QStandardItem, app_config: AppConfig, all: bool = False):
        super().__init__(parent=parent, item=item, app_config=app_config)

        self._all = all

        self._molecule_index = 0
        self._draw_item = item
        self._set_draw_item()

        self.ac_viewer = AtomicCoordinatesViewer(
            parent=self,
            atomic_coordinates=self._draw_item.data().data,
            app_config=app_config,
            title=self._draw_item.text(),
        )
        self.setWidget(self.ac_viewer)

        self.update_window_title()

        config = app_config.project_window.widgets.viewers.molecular_structure
        self.setMinimumSize(config.min_size[0], config.min_size[1])
        self.resize(config.size[0], config.size[1])

    def update_window_title(self):
        title = self._draw_item.text()
        parent_item = self._draw_item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.ac_viewer.set_title(title)
        self.setWindowTitle(title)
        self.setWindowIcon(self._draw_item.icon())

    def _atomic_coordinates_item(
        self, index: int, parent: QStandardItem, counter: int = -1
    ) -> tuple[bool, int, Optional[QStandardItem]]:
        """
        Finds item with `AtomicCoordinates` data structure
        """
        index = max(0, index)
        last_item = None
        if not parent.hasChildren() and isinstance(parent.data().data, AtomicCoordinates):
            return True, 0, parent
        else:
            for i in range(parent.rowCount()):
                item = parent.child(i)
                if isinstance(item.data().data, AtomicCoordinates):
                    last_item = item
                    counter += 1
                    if index == counter:
                        return True, counter, item
                elif self._all and item.hasChildren():
                    found, counter, last_item = self._atomic_coordinates_item(index, item, counter)
                    if found:
                        return found, counter, last_item
            return False, counter, last_item

    def _set_draw_item(self):
        _, self._molecule_index, self._draw_item = self._atomic_coordinates_item(self._molecule_index, self.item)

    def set_prev_atomic_coordinates(self):
        if self._molecule_index > 0:
            self._molecule_index -= 1
            self._set_draw_item()
            self.update_window_title()
            self.ac_viewer.set_atomic_coordinates(self._draw_item.data().data)

    def set_next_atomic_coordinates(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            self.ac_viewer.set_atomic_coordinates(self._draw_item.data().data)
