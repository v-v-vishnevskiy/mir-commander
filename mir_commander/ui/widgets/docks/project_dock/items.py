from typing import TYPE_CHECKING, Callable

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core import models
from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import Action, Menu
from mir_commander.ui.widgets.programs.cartesian_editor.program import CartesianEditor
from mir_commander.ui.widgets.programs.molecular_visualizer.program import MolecularVisualizer

if TYPE_CHECKING:
    from .tree_view import TreeView


class TreeItem(QStandardItem):
    _id_counter = 0

    default_program: type[ProgramWindow] | None = None
    programs: list[type[ProgramWindow]] = []
    child: Callable[..., "TreeItem"]

    def __init__(self, item: models.Item):
        TreeItem._id_counter += 1
        self._id = TreeItem._id_counter

        super().__init__(item.name)

        self._core_item = item

        self.setEditable(False)
        self._set_icon()
        self._load_data()

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))

    @property
    def id(self) -> int:
        return self._id

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, TreeItem):
            return f"{parent.path}.{part}"
        else:
            return part

    @property
    def core_item(self) -> models.Item:
        return self._core_item

    def _load_data(self):
        for item in self._core_item.items:
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

        export_item_action = Action(
            text=Action.tr("Export..."), parent=result, triggered=lambda: tree_view.export_item(self)
        )
        result.addAction(export_item_action)

        if self.default_program:

            def trigger(viewer: type[QWidget]) -> Callable[[], None]:
                return lambda: tree_view.view_item.emit(self, viewer, {})

            open_with_menu = Menu(Menu.tr("Open With"))
            for viewer in [self.default_program] + self.programs:
                action = Action(text=viewer.get_name(), parent=open_with_menu, triggered=trigger(viewer))
                open_with_menu.addAction(action)
            result.addMenu(open_with_menu)

        if self.hasChildren():
            result.addSeparator()
            view_structures_menu = Menu(Menu.tr("View Structures"), result)
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_Child"),
                    parent=view_structures_menu,
                    triggered=lambda: tree_view.view_item.emit(self, MolecularVisualizer, {"all": False}),
                )
            )
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_All"),
                    parent=view_structures_menu,
                    triggered=lambda: tree_view.view_item.emit(self, MolecularVisualizer, {"all": True}),
                )
            )
            result.addMenu(view_structures_menu)

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, name={self.text()})"


class Container(TreeItem):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(TreeItem):
    pass


class Unex(TreeItem):
    pass


class VolumeCube(TreeItem):
    default_program = MolecularVisualizer

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/volume-cube.png"))


class AtomicCoordinatesGroup(TreeItem):
    default_program = MolecularVisualizer

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(TreeItem):
    default_program = MolecularVisualizer
    programs = [CartesianEditor]

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
