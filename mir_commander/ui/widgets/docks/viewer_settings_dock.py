from collections import defaultdict

from PySide6.QtWidgets import QWidget

from mir_commander.ui.widgets.viewers.base import BaseViewer

from .base import BaseDock


class ViewerSettingsDock(BaseDock):
    """The viewer settings dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently active viewer in the mdi area.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Viewer Settings"), parent)
        self.setMinimumWidth(200)

        self._viewer_settings_widgets: dict[type[BaseViewer], BaseViewer] = {}
        self._all_viewers: dict[type[BaseViewer], list[BaseViewer]] = defaultdict(list)

    def add_viewer_settings_widget(self, viewer: type[BaseViewer]):
        if viewer not in self._viewer_settings_widgets:
            self._viewer_settings_widgets[viewer] = viewer.settings() if viewer.settings is not None else None

    def set_viewer_settings_widget(self, viewer: None | BaseViewer):
        viewer_cls = viewer.__class__
        if viewer_cls in self._viewer_settings_widgets:
            settings = self._viewer_settings_widgets[viewer_cls]
            settings.set_active_viewer(viewer)
            settings.set_all_viewers(self._all_viewers[viewer_cls])
            self.setWidget(settings)
        else:
            self.setWidget(None)

    def update_viewers_list(self, viewers: list[BaseViewer]):
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
