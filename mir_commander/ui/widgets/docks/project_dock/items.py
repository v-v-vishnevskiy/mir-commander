from typing import TYPE_CHECKING, Callable

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core import models
from mir_commander.ui.utils.viewer import Viewer
from mir_commander.ui.utils.widget import Action, Menu
from mir_commander.ui.widgets.viewers.molecular_structure.viewer import MolecularStructureViewer
from mir_commander.ui.widgets.viewers.molecular_structure_editor.widget import MolecularStructureEditor

if TYPE_CHECKING:
    from .tree_view import TreeView


class TreeItem(QStandardItem):
    default_viewer: type[Viewer] | None = None
    viewers: list[type[Viewer]] = []

    def __init__(self, data: models.Item):
        super().__init__(data.name)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self._load_data()

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, TreeItem):
            return f"{parent.path}.{part}"
        else:
            return part

    def _load_data(self):
        data: models.Item = self.data()

        for item in data.items:
            if type(item.data) is models.AtomicCoordinates:
                self.appendRow(AtomicCoordinates(item))
            elif type(item.data) is models.AtomicCoordinatesGroup:
                self.appendRow(AtomicCoordinatesGroup(item))
            elif type(item.data) is models.Molecule:
                self.appendRow(Molecule(item))
            elif type(item.data) is models.Unex:
                self.appendRow(Unex(item))
            elif type(item.data) is models.VolumeCube:
                self.appendRow(VolumeCube(item))
            else:
                self.appendRow(Container(item))

    def build_context_menu(self, tree_view: "TreeView") -> Menu | None:
        result = Menu()

        import_file_action = Action(
            text=Action.tr("Import File"), parent=result, triggered=lambda: tree_view.import_file(self)
        )
        result.addAction(import_file_action)

        if self.default_viewer:

            def trigger(viewer: type[QWidget]) -> Callable[[], None]:
                return lambda: tree_view.view_item.emit(self, viewer, {})

            open_with_menu = Menu(Menu.tr("Open With"))
            for viewer in [self.default_viewer] + self.viewers:
                action = Action(text=viewer.get_name(), parent=open_with_menu, triggered=trigger(viewer))
                open_with_menu.addAction(action)
            result.addMenu(open_with_menu)

        result.addSeparator()
        view_structures_menu = Menu(Menu.tr("View Structures"), result)
        view_structures_menu.addAction(
            Action(
                text=Action.tr("VS_Child"),
                parent=view_structures_menu,
                triggered=lambda: tree_view.view_item.emit(self, MolecularStructureViewer, {"all": False}),
            )
        )
        view_structures_menu.addAction(
            Action(
                text=Action.tr("VS_All"),
                parent=view_structures_menu,
                triggered=lambda: tree_view.view_item.emit(self, MolecularStructureViewer, {"all": True}),
            )
        )

        result.addMenu(view_structures_menu)

        return result


class Container(TreeItem):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(TreeItem):
    pass


class Unex(TreeItem):
    pass


class VolumeCube(TreeItem):
    default_viewer = MolecularStructureViewer

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/volume-cube.png"))


class AtomicCoordinatesGroup(TreeItem):
    default_viewer = MolecularStructureViewer

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(TreeItem):
    default_viewer = MolecularStructureViewer
    viewers = [MolecularStructureEditor]

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
