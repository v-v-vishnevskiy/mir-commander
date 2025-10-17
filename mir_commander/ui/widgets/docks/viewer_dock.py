from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QWidget

from mir_commander.ui.utils.viewer.viewer import Viewer
from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings

from .base import BaseDock


class ViewerDock(BaseDock):
    """The viewer's dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently active viewer in the mdi area.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Viewer"), parent)

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.setMinimumWidth(350)

        self._viewer_settings_widgets: dict[type, ViewerSettings] = {}
        self._all_viewers: dict[type, list[Viewer]] = defaultdict(list)

        self.setWidget(self._scroll_area)

    def add_viewer_settings_widget(self, viewer: type[Viewer]) -> ViewerSettings | None:
        if viewer.settings is None:
            return None

        if viewer not in self._viewer_settings_widgets:
            self._viewer_settings_widgets[viewer] = viewer.settings()
        return self._viewer_settings_widgets[viewer]

    def set_viewer_settings_widget(self, viewer: None | Viewer):
        viewer_cls = viewer.__class__
        if viewer_cls in self._viewer_settings_widgets:
            settings = self._viewer_settings_widgets[viewer_cls]
            settings.set_all_viewers(self._all_viewers[viewer_cls])
            settings.set_active_viewer(viewer)
            self._scroll_area.setWidget(settings)

        if (viewer is not None and viewer.settings is None) or not self._all_viewers:
            self._scroll_area.takeWidget()

    def update_viewers_list(self, viewers: list[Viewer]):
        self._all_viewers.clear()
        for viewer in viewers:
            if viewer not in self._viewer_settings_widgets:
                self._all_viewers[viewer.__class__].append(viewer)

        # remove viewer's settings that are not in the list of viewers
        for viewer_cls in list(self._viewer_settings_widgets.keys()):
            if viewer_cls not in self._all_viewers:
                self._viewer_settings_widgets.pop(viewer_cls)

    def __del__(self):
        self._viewer_settings_widgets.clear()
        self._all_viewers.clear()
