from typing import Callable, cast

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFrame, QHeaderView, QPushButton, QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import TableView, Translator, VBoxLayout
from mir_commander.utils.chem import all_symbols, atomic_number_to_symbol, symbol_to_atomic_number


class TableItem(QStandardItem):
    def __init__(self, *args, index: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self._index = index

    @property
    def idx(self) -> int:
        return self._index

    def set_index(self, index: int):
        self._index = index

    def validate(self) -> bool:
        return True

    def reset(self):
        pass

    def set_valid_state(self, valid: bool):
        self.model().blockSignals(True)
        if valid:
            self.setForeground(QColor(0, 0, 0))
        else:
            self.setForeground(QColor(255, 0, 0))
        self.model().blockSignals(False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(index={self.idx}, text={self.text()})"


class TagItem(TableItem):
    def __init__(self, tag: int, row_count_fn: Callable[[], int], *args, **kwargs):
        super().__init__(str(tag), *args, **kwargs)

        self._row_count_fn = row_count_fn

    @property
    def value(self) -> int:
        return int(self.text())

    def validate(self) -> bool:
        try:
            if 0 < self.value <= self._row_count_fn() - 1:
                valid = True
            else:
                valid = False
        except ValueError:
            valid = False
        self.set_valid_state(valid)
        return valid


class SymbolItem(TableItem):
    @property
    def atomic_number(self) -> int:
        return symbol_to_atomic_number(self.text())

    def reset(self):
        self.setText("")
        self.set_valid_state(True)

    def validate(self) -> bool:
        valid = self.text() in all_symbols()
        self.set_valid_state(valid)
        return valid


class FloatItem(TableItem):
    def __init__(self, value: float, *args, **kwargs):
        super().__init__(f"{value:.6f}", *args, **kwargs)
        self.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    @property
    def value(self) -> float:
        return float(self.text())

    def reset(self):
        self.setText(f"{0.0:.6f}")
        self.set_valid_state(True)

    def validate(self) -> bool:
        try:
            self.value
            valid = True
        except ValueError:
            valid = False
        self.set_valid_state(valid)
        return valid


class FloatItemX(FloatItem): ...


class FloatItemY(FloatItem): ...


class FloatItemZ(FloatItem): ...


class AtomicCoordinatesTableView(TableView):
    def __init__(self, cartesian_editor: "CartesianEditor", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cartesian_editor = cartesian_editor

        self._all_symbols = all_symbols()

        self._model = QStandardItemModel(parent=self)
        self.setModel(self._model)

        self._model.setHorizontalHeaderLabels(["Tag", "Symbol", "X", "Y", "Z"])
        self._model.itemChanged.connect(self._on_item_changed)

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(TableView.SelectionMode.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)

        self._raw_data = AtomicCoordinates()

        self._init_new_atom_row()

    def _get_item(self, row: int, column: int = 0) -> TableItem:
        return cast(TableItem, self._model.item(row, column))

    def _init_new_atom_row(self):
        self._new_atom_plus_item = QStandardItem()
        self._new_atom_plus_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._new_atom_symbol_item = SymbolItem("", index=-1)
        self._new_atom_x_item = FloatItem(0.0, index=-1)
        self._new_atom_y_item = FloatItem(0.0, index=-1)
        self._new_atom_z_item = FloatItem(0.0, index=-1)

        self._plus_button = QPushButton(QIcon(":/icons/general/plus.png"), "")
        self._plus_button.setIconSize(QSize(16, 16))
        self._plus_button.setEnabled(False)
        self.setStyleSheet("QPushButton { border: none; }")
        self._plus_button.clicked.connect(self._add_new_atom_button_clicked_handler)

    def _reset_new_atom_row(self):
        self._plus_button.setEnabled(False)
        self._new_atom_symbol_item.reset()
        self._new_atom_x_item.reset()
        self._new_atom_y_item.reset()
        self._new_atom_z_item.reset()

    def _on_item_changed(self, item: QStandardItem):
        """Handle item changes in the table."""

        if not isinstance(item, TableItem):
            return

        if item in [self._new_atom_symbol_item, self._new_atom_x_item, self._new_atom_y_item, self._new_atom_z_item]:
            if self._is_valid_values_for_new_atom_row():
                self._plus_button.setEnabled(True)
            else:
                self._plus_button.setEnabled(False)
            return

        if not item.validate():
            return

        match item:
            case SymbolItem():
                self._raw_data.atomic_num[item.idx] = item.atomic_number
            case FloatItemX():
                self._raw_data.x[item.idx] = item.value
            case FloatItemY():
                self._raw_data.y[item.idx] = item.value
            case FloatItemZ():
                self._raw_data.z[item.idx] = item.value
            case TagItem():
                self._model.blockSignals(True)
                self._apply_new_tag(item)
                self._model.blockSignals(False)

        self._cartesian_editor.send_item_changed_signal()

    def _apply_new_tag(self, item: TagItem):
        index_1 = item.idx
        index_2 = item.value - 1

        row_1 = self._model.indexFromItem(item).row()
        row_2 = 0
        for row in range(self._model.rowCount() - 1):
            if self._get_item(row, 0).idx == index_2:
                row_2 = row
                break

        # swap the tag text
        self._get_item(row_2, 0).setText(str(index_1 + 1))

        # swap the index of the items
        for column in range(self._model.columnCount()):
            self._get_item(row_1, column).set_index(index_2)
            self._get_item(row_2, column).set_index(index_1)

        # swap the data in core item
        data = self._raw_data
        data.atomic_num[index_1], data.atomic_num[index_2] = data.atomic_num[index_2], data.atomic_num[index_1]
        data.x[index_1], data.x[index_2] = data.x[index_2], data.x[index_1]
        data.y[index_1], data.y[index_2] = data.y[index_2], data.y[index_1]
        data.z[index_1], data.z[index_2] = data.z[index_2], data.z[index_1]

    def _is_valid_values_for_new_atom_row(self) -> bool:
        return (
            self._new_atom_symbol_item.validate()
            and self._new_atom_x_item.validate()
            and self._new_atom_y_item.validate()
            and self._new_atom_z_item.validate()
        )

    def _add_new_atom_button_clicked_handler(self):
        if not self._is_valid_values_for_new_atom_row():
            return

        symbol = self._new_atom_symbol_item.text()
        x = float(self._new_atom_x_item.text())
        y = float(self._new_atom_y_item.text())
        z = float(self._new_atom_z_item.text())

        # add the new atom row to the table
        self._add_atom_row(self._model.rowCount(), symbol, x, y, z, append=False)

        # update the data in core item
        self._raw_data.atomic_num.append(symbol_to_atomic_number(symbol))
        self._raw_data.x.append(x)
        self._raw_data.y.append(y)
        self._raw_data.z.append(z)
        self._cartesian_editor.send_item_changed_signal()

        self._model.blockSignals(True)
        self._reset_new_atom_row()
        self._model.blockSignals(False)

    def _add_atom_row(self, tag: int, symbol: str, x: float, y: float, z: float, append: bool = True):
        tag_item = TagItem(tag, self._model.rowCount, index=tag - 1)
        symbol_item = SymbolItem(symbol, index=tag - 1)
        x_item = FloatItemX(x, index=tag - 1)
        y_item = FloatItemY(y, index=tag - 1)
        z_item = FloatItemZ(z, index=tag - 1)
        if append:
            self._model.appendRow([tag_item, symbol_item, x_item, y_item, z_item])
        else:
            self._model.insertRow(self._model.rowCount() - 1, [tag_item, symbol_item, x_item, y_item, z_item])

    def _add_new_atom_row(self):
        self._model.appendRow(
            [
                self._new_atom_plus_item,
                self._new_atom_symbol_item,
                self._new_atom_x_item,
                self._new_atom_y_item,
                self._new_atom_z_item,
            ]
        )
        self.setIndexWidget(self._model.indexFromItem(self._new_atom_plus_item), self._plus_button)

    def load_data(self, atomic_coordinates: AtomicCoordinates):
        self._raw_data = atomic_coordinates
        self._model.blockSignals(True)
        self._model.removeRows(0, self._model.rowCount())

        n_atoms = len(atomic_coordinates.atomic_num)
        for i in range(n_atoms):
            self._add_atom_row(
                i + 1,
                atomic_number_to_symbol(atomic_coordinates.atomic_num[i]),
                atomic_coordinates.x[i],
                atomic_coordinates.y[i],
                atomic_coordinates.z[i],
            )
        self._add_new_atom_row()
        self._reset_new_atom_row()
        self._model.blockSignals(False)


class CartesianEditor(ProgramWindow):
    name = Translator.tr("Cartesian editor")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        central_widget = QWidget()
        layout = VBoxLayout()

        self._atomic_coordinates_table_view = AtomicCoordinatesTableView(self)

        layout.addWidget(self._atomic_coordinates_table_view, stretch=1)

        match self.item.core_item.data:
            case AtomicCoordinates():
                self._atomic_coordinates_table_view.load_data(self.item.core_item.data)

        central_widget.setLayout(layout)
        self.setWidget(central_widget)

        self.setMinimumSize(350, 300)
        self.resize(350, 300)
