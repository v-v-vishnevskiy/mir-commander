from typing import TYPE_CHECKING

from PIL import Image, ImageCms
from PySide6.QtGui import QContextMenuEvent

from mir_commander.core.models import AtomicCoordinates, VolumeCube
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import Translator

from .config import MolecularVisualizerConfig
from .context_menu import ContextMenu
from .control_panel import ControlPanel
from .visualizer import Visualizer

if TYPE_CHECKING:
    from mir_commander.ui.widgets.docks.project_dock.items import TreeItem


class MolecularVisualizer(ProgramWindow):
    name = Translator.tr("Molecular visualizer")
    control_panel_cls = ControlPanel
    control_panel: ControlPanel

    def __init__(self, all: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._config = self.app_config.project_window.widgets.programs.molecular_visualizer

        self._all = all

        self.visualizer = Visualizer(
            parent=self, title=self.item.text(), app_config=self.app_config, control_panel=self.control_panel
        )
        self.visualizer.message_channel.connect(self.long_msg_signal.emit)

        match self.item.core_item.data:
            case VolumeCube():
                self.visualizer.set_volume_cube(self.item.core_item.data)

        self._molecule_index = 0
        self._draw_item = self.item
        self._set_draw_item()
        self.visualizer.set_atomic_coordinates(self._get_draw_item_atomic_coordinates())
        self.visualizer.coordinate_axes_adjust_length()

        self._context_menu = ContextMenu(parent=self, app_config=self.app_config)

        self.setWidget(self.visualizer)

        self.update_window_title()

        self.setMinimumSize(self._config.min_size[0], self._config.min_size[1])
        self.resize(self._config.size[0], self._config.size[1])

    def get_config(self) -> MolecularVisualizerConfig:
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
        self, index: int, parent: "TreeItem", counter: int = -1
    ) -> tuple[bool, int, "TreeItem"]:
        """
        Finds item with `AtomicCoordinates` data structure
        """

        index = max(0, index)
        last_item = parent
        if not parent.hasChildren() and isinstance(parent.core_item.data, AtomicCoordinates):
            return True, 0, last_item
        else:
            for i in range(parent.rowCount()):
                item = parent.child(i)
                if isinstance(item.core_item.data, AtomicCoordinates):
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

    def _get_draw_item_atomic_coordinates(self) -> list[AtomicCoordinates]:
        match self._draw_item.core_item.data:
            case AtomicCoordinates():
                return [self._draw_item.core_item.data]
            case _:
                return []

    def set_prev_atomic_coordinates(self):
        if self._molecule_index > 0:
            self._molecule_index -= 1
            self._set_draw_item()
            self.update_window_title()
            self.visualizer.set_atomic_coordinates(self._get_draw_item_atomic_coordinates())

    def set_next_atomic_coordinates(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if item != self._draw_item:
            self.update_window_title()
            self.visualizer.set_atomic_coordinates(self._get_draw_item_atomic_coordinates())

    def save_image(
        self, filename: str, width: int, height: int, bg_color: Color4f | None = None, crop_to_content: bool = False
    ):
        image = self.visualizer.render_to_image(width, height, bg_color, crop_to_content)
        profile = ImageCms.createProfile("sRGB")
        Image.fromarray(image).save(filename, icc_profile=ImageCms.ImageCmsProfile(profile).tobytes())
