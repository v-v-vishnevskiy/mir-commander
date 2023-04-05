from typing import List

from PySide6.QtCore import QModelIndex, QSettings, Slot
from PySide6.QtGui import QIcon, QMoveEvent, QResizeEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDialog, QHBoxLayout, QStackedLayout, QTreeView

from mir_commander.widgets.settings.general import General

SECTIONS = [{"title": "General", "widget": General}]


class Settings(QDialog):
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self, parent, settings: QSettings):
        super().__init__(parent)
        self.settings = settings

        self.setWindowTitle(self.tr("Settings"))
        self.setWindowIcon(QIcon(":/icons/general/settings.png"))

        layout = QHBoxLayout(self)

        self.area = QStackedLayout()
        self.tree = self.sections()

        layout.addWidget(self.tree)
        layout.addLayout(self.area)

        self.setLayout(layout)

        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)

        self._restore_settings()

    @Slot()
    def show_section(self, index: QModelIndex):
        item = self.tree.model().itemFromIndex(index)
        self.area.setCurrentIndex(item.widget_index)
        self.settings.setValue("PreferencesWindow/section", [str(i) for i in item.section_path])

    def sections(self) -> QTreeView:
        tree = QTreeView(self)
        tree.setFixedWidth(200)
        tree.setHeaderHidden(True)
        model = QStandardItemModel(self)
        tree.setModel(model)

        root = model.invisibleRootItem()
        self._fill_tree(root, SECTIONS, [])

        tree.setCurrentIndex(root.child(0).index())
        self.area.setCurrentIndex(0)

        tree.clicked.connect(self.show_section)

        return tree

    def _fill_tree(self, root: QStandardItem, sections: list, parent: List[int]):
        for i, section in enumerate(sections):
            item = QStandardItem(self.tr(section["title"]))
            index = self.area.addWidget(section["widget"](self, self.settings))
            item.widget_index = index
            item.section_path = parent + [i]
            root.appendRow(item)
            self._fill_tree(item, section.get("children", []), parent + [i])

    def _restore_settings(self):
        pos = self.settings.value("PreferencesWindow/pos")
        size = self.settings.value("PreferencesWindow/size")
        if pos and size:
            self.setGeometry(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

        section = [int(item) for item in self.settings.value("PreferencesWindow/section", [])]
        if section:
            item = self._item(self.tree.model().invisibleRootItem(), section)
            if item:
                self.tree.setCurrentIndex(item.index())
                self.area.setCurrentIndex(item.widget_index)

    def _item(self, item: QStandardItem, path: List[int]) -> QStandardItem:
        if path:
            nested = item.child(path[0])
            if nested:
                return self._item(nested, path[1:])
        else:
            return item

    def moveEvent(self, event: QMoveEvent):
        self.settings.setValue("PreferencesWindow/pos", [event.pos().x(), event.pos().y()])

    def resizeEvent(self, event: QResizeEvent):
        self.settings.setValue("PreferencesWindow/size", [event.size().width(), event.size().height()])
