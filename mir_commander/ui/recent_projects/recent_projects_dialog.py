from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QDir, QModelIndex, Qt, Slot
from PySide6.QtGui import QMoveEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QListView, QMessageBox, QVBoxLayout

from mir_commander.consts import DIR
from mir_commander.core import Project
from mir_commander.core.errors import LoadProjectError
from mir_commander.ui.utils.widget import Dialog as BaseDialog, PushButton

from .config import ProjectConfig, RecentProjectsConfig

if TYPE_CHECKING:
    from mir_commander.ui.application import Application


class ListView(QListView):
    def mouseMoveEvent(self, event: QMoveEvent) -> None:
        index = self.indexAt(event.pos())
        item = self.model().itemFromIndex(index)
        if item:
            self.setCurrentIndex(index)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.clearSelection()
            self.setCursor(Qt.CursorShape.ArrowCursor)


class RecentProjectsDialog(BaseDialog):
    """Dialog with information about the program."""

    def __init__(self, app: "Application"):
        super().__init__(None)
        self.app = app
        self._config: RecentProjectsConfig = RecentProjectsConfig.load(DIR.HOME_CONFIG / "recent_projects.yaml")
        self.add_opened = self._config.add_opened
        self.add_recent = self._config.add_recent
        self.remove_opened = self._config.remove_opened
        self.remove_recent = self._config.remove_recent

        self.setup_ui()
        self.setup_signals()

        self.setWindowTitle(self.tr("Recent Projects"))

    def setup_ui(self):
        self.error = QMessageBox(self)
        self.error.setIcon(QMessageBox.Icon.Critical)

        layout = QVBoxLayout()

        self.setLayout(layout)
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self.recent = ListView(self)
        self.recent.setMouseTracking(True)
        self.recent.setModel(QStandardItemModel(self))

        self.pb_open_project = PushButton(PushButton.tr("Open"), self)
        self.pb_cancel = PushButton(PushButton.tr("Cancel"), self)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.pb_open_project)
        buttons.addWidget(self.pb_cancel)

        layout.addWidget(self.recent)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def show(self):
        self.load_data()
        super().show()

    def load_data(self):
        self.clear_data()
        root = self.recent.model().invisibleRootItem()
        for project in self._config.recent:
            msg = ""
            if not project.exists:
                msg = " (unavailable)"
            item = QStandardItem(f"{project.name}{msg}\n{project.path}")
            item.project_path = project.path
            item.setEditable(False)
            root.appendRow(item)

    def clear_data(self):
        root = self.recent.model().invisibleRootItem()
        root.removeRows(0, root.rowCount())

    def setup_signals(self):
        self.recent.clicked.connect(self.recent_open)
        self.pb_open_project.clicked.connect(self.pb_open_clicked)
        self.pb_cancel.clicked.connect(self.reject)

    @property
    def opened(self) -> list[ProjectConfig]:
        return self._config.opened

    @Slot()
    def recent_open(self, index: QModelIndex):
        item = self.recent.model().itemFromIndex(index)
        if item.isEnabled():
            self._open_project(item.project_path)

    @Slot()
    def pb_open_clicked(self, *args, **kwargs):
        dialog = QFileDialog(self, self.tr("Open Project"), QDir.homePath())
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            self._open_project(Path(dialog.selectedFiles()[0]))

    def _open_project(self, path: Path):
        try:
            self.app.open_project(path, raise_exc=True)
            self.hide()
        except LoadProjectError as e:
            self.error.setText(e.__class__.__name__)
            self.error.setInformativeText(str(e))
            self.error.show()
