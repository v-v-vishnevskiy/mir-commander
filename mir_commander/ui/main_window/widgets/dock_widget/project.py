from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QSize
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class TreeView(QTreeView):
    def __init__(self, parent: QWidget, config: Config):
        super().__init__(parent)
        self._config = config

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.setIconSize(self._icon_size())
        self.doubleClicked.connect(self._tree_item_double_clicked)

    def _icon_size(self) -> QSize:
        value = self._config["icon_size"]
        if value > 32 or value < 16:
            value = 20
        return QSize(value, value)

    def _tree_item_double_clicked(self, index: QModelIndex):
        item = self.model().itemFromIndex(index)
        mdi_area = self.parent().mdi_area
        for sub_window in mdi_area.subWindowList():
            if id(sub_window.widget().item) == id(item):
                mdi_area.setActiveSubWindow(sub_window)
                break
        else:
            if viewer := item.viewer():
                mdi_area.addSubWindow(viewer)
                viewer.show()
            else:
                self.setExpanded(index, not self.isExpanded(index))


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "MainWindow", config: Config):
        super().__init__(self.tr("Project"), config, parent)
        self._tree = TreeView(self, self.global_config.nested("widgets.docks.project.tree"))
        self.setWidget(self._tree)

    def set_model(self, model: QStandardItemModel):
        self._tree.setModel(model)
