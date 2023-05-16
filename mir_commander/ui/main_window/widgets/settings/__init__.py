from typing import TYPE_CHECKING, List

from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtGui import QIcon, QMoveEvent, QResizeEvent, QStandardItemModel
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QStackedLayout, QVBoxLayout

from mir_commander.ui.main_window.widgets.settings.category import Category
from mir_commander.ui.main_window.widgets.settings.general import General
from mir_commander.ui.main_window.widgets.settings.project import Project
from mir_commander.ui.utils.widget import Dialog, ListView, PushButton, StandardItem, TabWidget

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Settings(Dialog):
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

        self.setWindowTitle(self.tr("Settings"))
        self.setWindowIcon(QIcon(":/icons/general/settings.png"))
        self.setMinimumSize(800, 600)

        self.setup_ui()
        self.setup_data()
        self.setup_connections()

        self._load_settings()

    def show(self):
        for item in self._categories:
            item.setup_data()
        super().show()

    def setup_ui(self):
        """Creation of UI elements of the main Setting dialog."""

        main_layout = QVBoxLayout(self)

        layout = QHBoxLayout()
        self.categories = ListView(self)
        self.categories.setFixedWidth(150)
        self.categories.setModel(QStandardItemModel(self))

        self.area = QStackedLayout()

        layout.addWidget(self.categories)
        layout.addLayout(self.area)

        self.pb_restore_defaults = PushButton(PushButton.tr("Restore Defaults"))
        self.pb_restore_defaults.setMinimumWidth(70)
        self.pb_apply = PushButton(PushButton.tr("Apply"))
        self.pb_apply.setMinimumWidth(70)
        self.pb_apply.setEnabled(False)
        self.pb_cancel = PushButton(PushButton.tr("Cancel"))
        self.pb_cancel.setMinimumWidth(70)
        self.pb_ok = PushButton(PushButton.tr("Ok"))
        self.pb_ok.setMinimumWidth(70)

        buttons = QHBoxLayout()
        buttons.addWidget(self.pb_restore_defaults)
        buttons.addWidget(self.pb_apply)
        buttons.addStretch(1)
        buttons.addWidget(self.pb_cancel)
        buttons.addWidget(self.pb_ok)

        main_layout.addLayout(layout)
        main_layout.addLayout(buttons)

        self.setLayout(main_layout)

    def setup_data(self):
        """Generation of particular pages (as tab widgets) with controls for settings."""

        self.category_items = [
            {"title": StandardItem.tr("Project"), "tabs": [(Project, "")]},
            {"title": StandardItem.tr("General"), "tabs": [(General, "")]},
        ]

        root = self.categories.model().invisibleRootItem()
        for i, section in enumerate(self.category_items):
            # Setup self.categories
            item = StandardItem(section["title"])
            item.setEditable(False)
            item.position = i
            root.appendRow(item)

            # setup self.area
            tabwidget = TabWidget()
            tabwidget.setTabBarAutoHide(True)
            for tab in section["tabs"]:
                category = tab[0](self)
                self._categories.append(category)
                tabwidget.addTab(category, tab[1])
            self.area.addWidget(tabwidget)

        self.categories.setCurrentIndex(root.child(0).index())
        self.area.setCurrentIndex(0)

    def setup_connections(self):
        """Establish connections for the Ok, Cancel,... etc. buttons."""

        self.categories.clicked.connect(self.category_changed)
        for i in range(self.area.count()):
            self.area.widget(i).currentChanged.connect(self.tab_changed)

        self.pb_restore_defaults.clicked.connect(self.restore_defaults_clicked)
        self.pb_apply.clicked.connect(self.apply_clicked)
        self.pb_cancel.clicked.connect(self.cancel_clicked)
        self.pb_ok.clicked.connect(self.ok_clicked)
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
            item.apply()
            item.write()
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

    def changed_settings(self):
        value = any((item.has_changes for item in self._settings))
        self.pb_apply.setEnabled(value)

    def moveEvent(self, event: QMoveEvent):
        self._config["pos"] = [event.pos().x(), event.pos().y()]

    def resizeEvent(self, event: QResizeEvent):
        self._config["size"] = [event.size().width(), event.size().height()]

    def closeEvent(self, *args, **kwargs):
        for item in self._settings:
            item.clear()
            item.apply(all=True)
