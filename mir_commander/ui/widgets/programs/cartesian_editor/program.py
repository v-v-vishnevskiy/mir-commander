from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFrame, QHeaderView, QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import PushButton, TableView, Translator, VBoxLayout
from mir_commander.utils.chem import atomic_number_to_symbol, symbol_to_atomic_number


class AtomicCoordinatesTableView(TableView):
    def __init__(self, cartesian_editor: "CartesianEditor", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cartesian_editor = cartesian_editor

        self._model = QStandardItemModel(parent=self)
        self.setModel(self._model)

        self._model.setHorizontalHeaderLabels(["Symbol", "X", "Y", "Z"])

        self._model.itemChanged.connect(self._on_item_changed)

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(TableView.SelectionMode.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self._atomic_coordinates: AtomicCoordinates | None = None

    def _on_item_changed(self, item: QStandardItem):
        """Handle item changes in the table."""
        updated_data = self.save_data()
        self._cartesian_editor.item.core_item.data = updated_data
        self._cartesian_editor.send_item_changed_signal()

    def _create_symbol_item(self, symbol: str) -> QStandardItem:
        item = QStandardItem(symbol)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _create_coordinate_item(self, value: float) -> QStandardItem:
        item = QStandardItem(f"{value:.6f}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item

    def _add_atom_row(self, atomic_num: int, x: float, y: float, z: float):
        symbol = atomic_number_to_symbol(atomic_num)
        symbol_item = self._create_symbol_item(symbol)
        x_item = self._create_coordinate_item(x)
        y_item = self._create_coordinate_item(y)
        z_item = self._create_coordinate_item(z)
        self._model.appendRow([symbol_item, x_item, y_item, z_item])

    def load_data(self, atomic_coordinates: AtomicCoordinates):
        self._atomic_coordinates = atomic_coordinates
        self._model.blockSignals(True)
        self._model.removeRows(0, self._model.rowCount())

        n_atoms = len(atomic_coordinates.atomic_num)
        for i in range(n_atoms):
            self._add_atom_row(
                atomic_coordinates.atomic_num[i],
                atomic_coordinates.x[i],
                atomic_coordinates.y[i],
                atomic_coordinates.z[i],
            )
        self._model.blockSignals(False)

    def _extract_row_data(self, row: int) -> tuple[int, float, float, float] | None:
        symbol_item = self._model.item(row, 0)
        x_item = self._model.item(row, 1)
        y_item = self._model.item(row, 2)
        z_item = self._model.item(row, 3)

        if not (symbol_item and x_item and y_item and z_item):
            return None

        try:
            symbol = symbol_item.text()
            atomic_num = symbol_to_atomic_number(symbol)
            x = float(x_item.text())
            y = float(y_item.text())
            z = float(z_item.text())
            return atomic_num, x, y, z
        except (ValueError, KeyError):
            return None

    def save_data(self) -> AtomicCoordinates:
        """Extract data from table and return as AtomicCoordinates."""
        atomic_num_list = []
        x_list = []
        y_list = []
        z_list = []

        for row in range(self._model.rowCount()):
            row_data = self._extract_row_data(row)
            if row_data:
                atomic_num, x, y, z = row_data
                atomic_num_list.append(atomic_num)
                x_list.append(x)
                y_list.append(y)
                z_list.append(z)

        return AtomicCoordinates(atomic_num=atomic_num_list, x=x_list, y=y_list, z=z_list)


class CartesianEditor(ProgramWindow):
    name = Translator.tr("Cartesian editor")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        central_widget = QWidget()
        layout = VBoxLayout()

        self._atomic_coordinates_table_view = AtomicCoordinatesTableView(self)

        layout.addWidget(self._atomic_coordinates_table_view, stretch=1)
        layout.addWidget(PushButton("Add"))

        match self.item.core_item.data:
            case AtomicCoordinates():
                self._atomic_coordinates_table_view.load_data(self.item.core_item.data)

        central_widget.setLayout(layout)
        self.setWidget(central_widget)

        self.update_window_title()

        self.setMinimumSize(350, 300)
        self.resize(350, 300)

    def update_window_title(self):
        title = self.item.text()
        parent_item = self.item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.setWindowTitle(title)
        self.setWindowIcon(self.item.icon())
