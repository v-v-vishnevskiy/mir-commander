from PySide6.QtCore import QModelIndex, QSettings, Slot
from PySide6.QtGui import QIcon, QMoveEvent, QResizeEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QHBoxLayout, QListView, QStackedLayout, QTabWidget

from mir_commander.widgets.settings.general import General


class Settings(QDialog):
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    SETTINGS_GROUP = "SettingsWindow"

    def __init__(self, parent, settings: QSettings):
        super().__init__(parent)
        self.settings = settings

        self.setup_ui()
        self.setup_data()
        self.setup_connections()

        self._restore_settings()

    def setup_ui(self):
        self.setWindowTitle(self.tr("Settings"))
        self.setWindowIcon(QIcon(":/icons/general/settings.png"))
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)

        layout = QHBoxLayout(self)

        self.categories = QListView(self)
        self.categories.setFixedWidth(150)
        self.categories.setModel(QStandardItemModel(self))

        self.area = QStackedLayout(self)

        layout.addWidget(self.categories)
        layout.addLayout(self.area)

        self.setLayout(layout)

    def setup_data(self):
        self.category_items = [
            {"title": self.tr("General"), "tabs": [(General, self.tr(""))]},
            {"title": self.tr("Test"), "tabs": [(General, self.tr("123")), (General, self.tr("456"))]},
        ]

        root = self.categories.model().invisibleRootItem()
        for i, section in enumerate(self.category_items):
            # Setup self.current_category
            item = QStandardItem(section["title"])
            item.setEditable(False)
            item.position = i
            root.appendRow(item)

            # setup self.area
            tabwidget = QTabWidget()
            tabwidget.setTabBarAutoHide(True)
            for tab in section["tabs"]:
                tabwidget.addTab(tab[0](self, self.settings), tab[1])
            self.area.addWidget(tabwidget)

        self.categories.setCurrentIndex(root.child(0).index())
        self.area.setCurrentIndex(0)

    def setup_connections(self):
        self.categories.clicked.connect(self.category_changed)
        for i in range(self.area.count()):
            self.area.widget(i).currentChanged.connect(self.tab_changed)

    @Slot()
    def category_changed(self, index: QModelIndex):
        item = self.categories.model().itemFromIndex(index)
        self.area.setCurrentIndex(item.position)
        self.settings.setValue(f"{self.SETTINGS_GROUP}/current_category", item.position)
        self.settings.setValue(f"{self.SETTINGS_GROUP}/current_tab", self.area.currentWidget().currentIndex())

    @Slot()
    def tab_changed(self, index: int):
        self.settings.setValue(f"{self.SETTINGS_GROUP}/current_tab", index)

    def _restore_settings(self):
        pos = self.settings.value(f"{self.SETTINGS_GROUP}/pos")
        size = self.settings.value(f"{self.SETTINGS_GROUP}/size")
        if pos and size:
            self.setGeometry(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

        current_category = int(self.settings.value(f"{self.SETTINGS_GROUP}/current_category", 0))
        if current_category:
            index = self.categories.model().invisibleRootItem().child(current_category).index()
            self.categories.setCurrentIndex(index)
            self.area.setCurrentIndex(current_category)

            current_tab = int(self.settings.value(f"{self.SETTINGS_GROUP}/current_tab", 0)) or 1
            if current_tab:
                self.area.currentWidget().setCurrentIndex(current_tab)

    def moveEvent(self, event: QMoveEvent):
        self.settings.setValue(f"{self.SETTINGS_GROUP}/pos", [event.pos().x(), event.pos().y()])

    def resizeEvent(self, event: QResizeEvent):
        self.settings.setValue(f"{self.SETTINGS_GROUP}/size", [event.size().width(), event.size().height()])
