from PySide6.QtGui import QContextMenuEvent, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core.models import AtomicCoordinates, VolumeCube
from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer import Viewer

from .config import MolecularStructureViewerConfig
from .context_menu import ContextMenu
from .settings.settings import Settings
from .visualizer import Visualizer


class MolecularStructureViewer(Viewer):
    settings = Settings

    def __init__(
        self,
        parent: QWidget,
        item: QStandardItem,
        app_config: AppConfig,
        all: bool = False,
    ):
        super().__init__(parent=parent, item=item, app_config=app_config)

        self._config = app_config.project_window.widgets.viewers.molecular_structure

        self._all = all

        self.visualizer = Visualizer(parent=self, title=item.text(), app_config=app_config)
        self.visualizer.message_channel.connect(self.long_msg_signal.emit)

        match item.data().data:
            case VolumeCube():
                self.visualizer.set_volume_cube(item.data().data)
                self.visualizer.add_volume_cube_isosurface_group(
                    [(0.05, (1.0, 1.0, 0.0, 0.5)), (-0.05, (1.0, 0.0, 1.0, 0.5))]
                )
                self.visualizer.add_volume_cube_isosurface_group([(0.01, (0.0, 1.0, 1.0, 0.5))])

        self._molecule_index = 0
        self._draw_item = item
        self._set_draw_item()
        self.visualizer.add_atomic_coordinates(self._draw_item.data().data)

        self._context_menu = ContextMenu(parent=self, app_config=app_config)

        self.setWidget(self.visualizer)

        self.update_window_title()

        self.setMinimumSize(self._config.min_size[0], self._config.min_size[1])
        self.resize(self._config.size[0], self._config.size[1])

    def get_config(self) -> MolecularStructureViewerConfig:
        return self._config

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._context_menu.exec(event.globalPos())

    def update_window_title(self):
        title = self._draw_item.text()
        parent_item = self._draw_item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.visualizer.set_title(title)
        self.setWindowTitle(title)
        self.setWindowIcon(self._draw_item.icon())

    def _atomic_coordinates_item(
        self, index: int, parent: QStandardItem, counter: int = -1
    ) -> tuple[bool, int, QStandardItem]:
        """
        Finds item with `AtomicCoordinates` data structure
        """

        index = max(0, index)
        last_item = parent
        if not parent.hasChildren() and isinstance(parent.data().data, AtomicCoordinates):
            return True, 0, last_item
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
            self.visualizer.set_atomic_coordinates(self._draw_item.data().data)

    def set_next_atomic_coordinates(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            self.visualizer.set_atomic_coordinates(self._draw_item.data().data)
