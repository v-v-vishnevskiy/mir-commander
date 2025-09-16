from typing import Any, cast

from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtGui import QIcon, QMoveEvent, QResizeEvent, QStandardItemModel
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QStackedLayout, QVBoxLayout, QWidget

from mir_commander.core.config import ProjectConfig
from mir_commander.ui.config import AppConfig, ApplyCallbacks
from mir_commander.ui.utils.widget import Dialog, ListView, PushButton, StandardItem, TabWidget

from .base import BasePage
from .general_page import General
from .project_page import Project


class SettingsDialog(Dialog):
    """Main dialog of the setting window.

    Inherits Translator, since we have here UI elements,
    which may be translated on the fly.
    """

    def __init__(
        self,
        parent: QWidget,
        app_apply_callbacks: ApplyCallbacks,
        mw_apply_callbacks: ApplyCallbacks,
        app_config: AppConfig,
        project_config: ProjectConfig,
    ):
        super().__init__(parent)

        self.app_apply_callbacks = app_apply_callbacks
        self.mw_apply_callbacks = mw_apply_callbacks

        self.app_config = app_config
        self.project_config = project_config

        self._config = self.app_config.settings
        self._pages: list[BasePage] = []
        self._pages_model = QStandardItemModel(self)

        self.setWindowTitle(self.tr("Settings"))
        self.setWindowIcon(QIcon(":/icons/general/settings.png"))
        self.setMinimumSize(800, 600)

        self.setup_ui()
        self.setup_data()
        self.setup_connections()

        self._load_settings()

    def show(self):
        for page in self._pages:
            page.setup_data()
        super().show()

    def setup_ui(self):
        """Creation of UI elements of the main Setting dialog."""

        main_layout = QVBoxLayout(self)

        layout = QHBoxLayout()
        self.pages = ListView(self)
        self.pages.setFixedWidth(150)
        self.pages.setModel(self._pages_model)

        self.area = QStackedLayout()

        layout.addWidget(self.pages)
        layout.addLayout(self.area)

        self.pb_restore_defaults = PushButton(PushButton.tr("Restore Defaults"))
        self.pb_restore_defaults.setMinimumWidth(70)
        self.pb_apply = PushButton(PushButton.tr("Apply"))
        self.pb_apply.setMinimumWidth(70)
        self.pb_apply.setEnabled(True)
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

        page_items: list[dict[str, Any]] = [
            {"title": StandardItem.tr("Project"), "tabs": [(Project, "")]},
            {"title": StandardItem.tr("General"), "tabs": [(General, "")]},
        ]

        root = self._pages_model.invisibleRootItem()
        for i, section in enumerate(page_items):
            # Setup self.categories
            item = StandardItem(section["title"])
            item.setEditable(False)
            item.setData({"position": i})
            root.appendRow(item)

            # setup self.area
            tabwidget = TabWidget()
            tabwidget.setTabBarAutoHide(True)
            for tab in section["tabs"]:
                page = tab[0](parent=self, app_config=self.app_config, project_config=self.project_config)
                self._pages.append(page)
                tabwidget.addTab(page, tab[1])
            self.area.addWidget(tabwidget)

        self.pages.setCurrentIndex(root.child(0).index())
        self.area.setCurrentIndex(0)

    def setup_connections(self):
        """Establish connections for the Ok, Cancel,... etc. buttons."""

        self.pages.clicked.connect(self.page_changed)
        for i in range(self.area.count()):
            widget = cast(TabWidget, self.area.widget(i))
            widget.currentChanged.connect(self.tab_changed)

        self.pb_restore_defaults.clicked.connect(self.restore_defaults_clicked)
        self.pb_apply.clicked.connect(self.apply_clicked)
        self.pb_cancel.clicked.connect(self.cancel_clicked)
        self.pb_ok.clicked.connect(self.ok_clicked)

    @Slot()
    def page_changed(self, index: QModelIndex):
        item = self._pages_model.itemFromIndex(index)
        self.area.setCurrentIndex(item.data()["position"])
        self._config.current_page = item.data()["position"]
        self._config.current_tab = cast(TabWidget, self.area.currentWidget()).currentIndex()

    @Slot()
    def tab_changed(self, index: int):
        self._config.current_tab = index

    @Slot()
    def restore_defaults_clicked(self, _: QAbstractButton):
        for page in self._pages:
            page.restore_defaults()

    @Slot()
    def apply_clicked(self, _: QAbstractButton):
        self.app_apply_callbacks.run()
        self.mw_apply_callbacks.run()

    @Slot()
    def cancel_clicked(self, _: QAbstractButton):
        for page in self._pages:
            page.cancel()
        self.app_apply_callbacks.run()
        self.mw_apply_callbacks.run()
        self.reject()

    @Slot()
    def ok_clicked(self, _: QAbstractButton):
        self.app_apply_callbacks.run()
        self.mw_apply_callbacks.run()
        self.app_config.dump()
        self.project_config.dump()
        for page in self._pages:
            page.backup_data()
        self.accept()

    def _load_settings(self):
        pos = self._config.pos
        size = self._config.size
        if pos and size:
            self.setGeometry(pos[0], pos[1], size[0], size[1])

        current_page = self._config.current_page
        if current_page:
            item = self._pages_model.invisibleRootItem().child(current_page)
            if item:
                index = item.index()
                self.pages.setCurrentIndex(index)
                self.area.setCurrentIndex(current_page)

            current_tab = self._config.current_tab
            if current_tab:
                cast(TabWidget, self.area.currentWidget()).setCurrentIndex(current_tab)

    def moveEvent(self, event: QMoveEvent):
        self._config.pos = [event.pos().x(), event.pos().y()]

    def resizeEvent(self, event: QResizeEvent):
        self._config.size = [event.size().width(), event.size().height()]

    def closeEvent(self, *args, **kwargs):
        for page in self._pages:
            page.cancel()
