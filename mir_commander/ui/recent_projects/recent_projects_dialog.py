from pathlib import Path

from PySide6.QtCore import QDir, QModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QMoveEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QListView, QVBoxLayout

from mir_commander.utils.consts import DIR
from ..utils.widget import Dialog as BaseDialog, PushButton

from .config import ProjectConfig, RecentProjectsConfig


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

    open_project = Signal(Path, bool)

    def __init__(self):
        super().__init__(None)
        self._config: RecentProjectsConfig = RecentProjectsConfig.load(DIR.HOME_CONFIG / "recent_projects.yaml")
        self.add_opened = self._config.add_opened
        self.add_recent = self._config.add_recent
        self.remove_opened = self._config.remove_opened
        self.remove_recent = self._config.remove_recent

        self._setup_ui()
        self._setup_signals()

        self.setWindowTitle(self.tr("Recent Projects"))

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.setLayout(layout)
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self._recent = ListView(self)
        self._recent.setMouseTracking(True)
        self._recent.setModel(QStandardItemModel(self))

        self._pb_open_project = PushButton(PushButton.tr("Open"), self)
        self._pb_cancel = PushButton(PushButton.tr("Cancel"), self)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self._pb_open_project)
        buttons.addWidget(self._pb_cancel)

        layout.addWidget(self._recent)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def _load_data(self):
        self._clear_data()
        root = self._recent.model().invisibleRootItem()
        for project in self._config.recent:
            msg = ""
            if not project.exists:
                msg = " (unavailable)"
            item = QStandardItem(f"{project.name}{msg}\n{project.path}")
            item.project_path = project.path
            item.setEditable(False)
            root.appendRow(item)

    def _clear_data(self):
        root = self._recent.model().invisibleRootItem()
        root.removeRows(0, root.rowCount())

    def _setup_signals(self):
        self._recent.clicked.connect(self._recent_open)
        self._pb_open_project.clicked.connect(self._pb_open_clicked)
        self._pb_cancel.clicked.connect(self.reject)

    def show(self):
        self._load_data()
        super().show()

    @property
    def opened(self) -> list[ProjectConfig]:
        return self._config.opened

    @Slot()
    def _recent_open(self, index: QModelIndex):
        item = self._recent.model().itemFromIndex(index)
        if item.isEnabled():
            self.open_project.emit(item.project_path)

    @Slot()
    def _pb_open_clicked(self, *args, **kwargs):
        dialog = QFileDialog(self, self.tr("Open Project"), QDir.homePath())
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            self._open_project(Path(dialog.selectedFiles()[0]))
