from typing import TYPE_CHECKING, List

from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtGui import QIcon, QMoveEvent, QResizeEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QListView,
    QStackedLayout,
    QTabWidget,
    QVBoxLayout,
)

from mir_commander.utils.widget import Translator
from mir_commander.widgets.settings.category import Category
from mir_commander.widgets.settings.general import General
from mir_commander.widgets.settings.project import Project

if TYPE_CHECKING:
    from mir_commander.main_window import MainWindow


class Settings(Translator, QDialog):
    """Main dialog of the setting window.

    Inherits Translator, since we have here UI elements,
    which may be translated on the fly.
    """

    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)
        self._config = parent.project.config.nested("widgets.settings_window")
        self.global_settings = parent.app.settings
        self.project_settings = parent.project.settings
        self._settings = [self.global_settings, self.project_settings]
        self._categories: List[Category] = []

        self.setup_ui()
        self.setup_data()
        self.retranslate_ui()
        self.setup_connections()

        self._load_settings()

    def show(self):
        for item in self._categories:
            item.setup_data()
        super().show()

    def setup_ui(self):
        """Creation of UI elements of the main Setting dialog."""

        self.setWindowIcon(QIcon(":/icons/general/settings.png"))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        main_layout = QVBoxLayout(self)

        layout = QHBoxLayout()
        self.categories = QListView(self)
        self.categories.setFixedWidth(150)
        self.categories.setModel(QStandardItemModel(self))

        self.area = QStackedLayout()

        layout.addWidget(self.categories)
        layout.addLayout(self.area)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)

        main_layout.addLayout(layout)
        main_layout.addWidget(self.buttons)

        self.setLayout(main_layout)

    def setup_data(self):
        """Generation of particular pages (as tab widgets) with controls for settings."""

        self.category_items = [
            {"title": self.tr("Project"), "tabs": [(Project, "")]},
            {"title": self.tr("General"), "tabs": [(General, "")]},
        ]

        root = self.categories.model().invisibleRootItem()
        for i, section in enumerate(self.category_items):
            # Setup self.categories
            item = QStandardItem()
            item.setEditable(False)
            item.position = i
            root.appendRow(item)

            # setup self.area
            tabwidget = QTabWidget()
            tabwidget.setTabBarAutoHide(True)
            for tab in section["tabs"]:
                category = tab[0](self)
                self._categories.append(category)
                tabwidget.addTab(category, "")
            self.area.addWidget(tabwidget)

        self.categories.setCurrentIndex(root.child(0).index())
        self.area.setCurrentIndex(0)

    def setup_connections(self):
        """Establish connections for the Ok, Cancel,... etc. buttons."""

        self.categories.clicked.connect(self.category_changed)
        for i in range(self.area.count()):
            self.area.widget(i).currentChanged.connect(self.tab_changed)

        self.buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self.restore_defaults_clicked
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_clicked)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.cancel_clicked)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.ok_clicked)
        self.global_settings.set_changed_callback(self.changed_settings)
        self.project_settings.set_changed_callback(self.changed_settings)

    @Slot()
    def category_changed(self, index: QModelIndex):
        item = self.categories.model().itemFromIndex(index)
        self.area.setCurrentIndex(item.position)
        self._config["current_category"] = item.position
        self._config["current_tab"] = self.area.currentWidget().currentIndex()

    @Slot()
    def tab_changed(self, index: int):
        self._config["current_tab"] = index

    @Slot()
    def restore_defaults_clicked(self, button: QAbstractButton):
        for item in self._settings:
            item.load_defaults()
            for category_item in self._categories:
                category_item.setup_data()

    @Slot()
    def apply_clicked(self, button: QAbstractButton):
        for item in self._settings:
            item.apply()

    @Slot()
    def cancel_clicked(self, button: QAbstractButton):
        for item in self._settings:
            item.clear()
            item.apply(all=True)
        self.reject()

    @Slot()
    def ok_clicked(self, button: QAbstractButton):
        for item in self._settings:
            item.write()
            item.apply()
        self.accept()

    def _load_settings(self):
        pos = self._config["pos"]
        size = self._config["size"]
        if pos and size:
            self.setGeometry(pos[0], pos[1], size[0], size[1])

        current_category = self._config["current_category"] or 0
        if current_category:
            item = self.categories.model().invisibleRootItem().child(current_category)
            if item:
                index = item.index()
                self.categories.setCurrentIndex(index)
                self.area.setCurrentIndex(current_category)

            current_tab = self._config["current_tab"] or 0
            if current_tab:
                self.area.currentWidget().setCurrentIndex(current_tab)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Settings"))
        root = self.categories.model().invisibleRootItem()
        for i, item in enumerate(self.category_items):
            root.child(i).setText(self.tr(item["title"]))
            for j, tab in enumerate(item["tabs"]):
                self.area.widget(i).setTabText(j, self.tr(tab[1]))

    def changed_settings(self):
        value = any((item.has_changes for item in self._settings))
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(value)

    def moveEvent(self, event: QMoveEvent):
        self._config["pos"] = [event.pos().x(), event.pos().y()]

    def resizeEvent(self, event: QResizeEvent):
        self._config["size"] = [event.size().width(), event.size().height()]

    def closeEvent(self, *args, **kwargs):
        for item in self._settings:
            item.clear()
            item.apply(all=True)
