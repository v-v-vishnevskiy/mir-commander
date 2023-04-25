from typing import TYPE_CHECKING

from PySide6.QtCore import QDir, QModelIndex, Qt, Slot
from PySide6.QtGui import QMoveEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QListView, QPushButton, QVBoxLayout

from mir_commander.utils.widget import Translator

if TYPE_CHECKING:
    from mir_commander.application import Application


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


class RecentProjects(Translator, QDialog):
    """Dialog with information about the program."""

    def __init__(self, app: "Application"):
        super().__init__(None)
        self.app = app

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.setLayout(layout)
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self.recent = ListView(self)
        self.recent.setMouseTracking(True)
        self.recent.setModel(QStandardItemModel(self))

        self.pb_open_project = QPushButton()
        self.pb_cancel = QPushButton()

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.pb_open_project)
        buttons.addWidget(self.pb_cancel)

        layout.addWidget(self.recent)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.retranslate_ui()

    def show(self):
        self.load_data()
        super().show()

    def load_data(self):
        self.clear_data()
        root = self.recent.model().invisibleRootItem()
        for project in self.app.recent_projects.recent:
            item = QStandardItem(f"{project.title}\n{project.path}")
            item.project_path = project.path
            item.setEditable(False)
            root.appendRow(item)

    def clear_data(self):
        root = self.recent.model().invisibleRootItem()
        root.removeRows(0, root.rowCount())

    def setup_connections(self):
        self.recent.clicked.connect(self.recent_open)
        self.pb_open_project.clicked.connect(self.pb_open_clicked)
        self.pb_cancel.clicked.connect(self.reject)

    @Slot()
    def recent_open(self, index: QModelIndex):
        item = self.recent.model().itemFromIndex(index)
        if self.app.open_project(item.project_path):
            self.hide()

    @Slot()
    def pb_open_clicked(self, *args, **kwargs):
        dialog = QFileDialog(self, self.tr("Open Project"), QDir.homePath())
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            if self.app.open_project(dialog.selectedFiles()[0]):
                self.hide()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Recent Projects"))
        self.pb_open_project.setText(self.tr("Open"))
        self.pb_cancel.setText(self.tr("Cancel"))
