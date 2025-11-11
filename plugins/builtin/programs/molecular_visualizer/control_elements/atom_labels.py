from typing import TYPE_CHECKING

from mir_commander.ui.sdk.widget import CheckBox, GridLayout, HBoxLayout, Label, PushButton

from ...program import ControlBlock
from .utils import add_slider

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class AtomLabels(ControlBlock["Program"]):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        layout = GridLayout()

        layout.addWidget(Label(Label.tr("Show:"), self), 0, 0)

        checkbox_layout = HBoxLayout()

        self._symbol_visible_checkbox = CheckBox(CheckBox.tr("Symbol"))
        self._symbol_visible_checkbox.setChecked(True)
        self._symbol_visible_checkbox.toggled.connect(self._symbol_visible_checkbox_handler)
        checkbox_layout.addWidget(self._symbol_visible_checkbox)

        checkbox_layout.addSpacing(5)

        self._number_visible_checkbox = CheckBox(CheckBox.tr("Number"))
        self._number_visible_checkbox.setChecked(True)
        self._number_visible_checkbox.toggled.connect(self._number_visible_checkbox_handler)
        checkbox_layout.addWidget(self._number_visible_checkbox)

        layout.addLayout(checkbox_layout, 0, 1)

        self._size_slider, self._size_double_spinbox = add_slider(
            layout=layout,
            row=2,
            text=Label.tr("Size:"),
            min_value=1,
            max_value=100,
            single_step=1,
            factor=1,
            decimals=0,
        )
        self._size_slider.valueChanged.connect(self._size_slider_value_changed_handler)
        self._size_double_spinbox.valueChanged.connect(self._size_double_spinbox_value_changed_handler)

        self._offset_slider, self._offset_double_spinbox = add_slider(
            layout=layout,
            row=3,
            text=Label.tr("Offset:"),
            min_value=1.01,
            max_value=5.0,
            single_step=0.1,
            factor=100,
            decimals=2,
        )
        self._offset_slider.valueChanged.connect(self._offset_slider_value_changed_handler)
        self._offset_double_spinbox.valueChanged.connect(self._offset_double_spinbox_value_changed_handler)

        layout.addWidget(Label(Label.tr("Toggle:"), self), 4, 0)

        toggle_layout = HBoxLayout()

        self._toggle_all_button = PushButton(PushButton.tr("All"))
        self._toggle_all_button.clicked.connect(self._toggle_all_button_clicked_handler)
        toggle_layout.addWidget(self._toggle_all_button)

        toggle_layout.addSpacing(5)

        self._toggle_selected_button = PushButton(PushButton.tr("Selected"))
        self._toggle_selected_button.clicked.connect(self._toggle_selected_button_clicked_handler)
        toggle_layout.addWidget(self._toggle_selected_button)

        layout.addLayout(toggle_layout, 4, 1, 1, 2)

        self.setLayout(layout)

    def _symbol_visible_checkbox_handler(self, value: bool):
        self._control_panel.program_action_signal.emit("atom_labels.set_symbol_visible", {"value": value})

    def _number_visible_checkbox_handler(self, value: bool):
        self._control_panel.program_action_signal.emit("atom_labels.set_number_visible", {"value": value})

    def _size_slider_value_changed_handler(self, i: int):
        self._size_double_spinbox.setValue(i)
        self._control_panel.program_action_signal.emit("atom_labels.set_size", {"value": i})

    def _size_double_spinbox_value_changed_handler(self, value: int):
        self._size_slider.setValue(value)

    def _offset_slider_value_changed_handler(self, i: int):
        self._offset_double_spinbox.setValue(i / 100)
        self._control_panel.program_action_signal.emit("atom_labels.set_offset", {"value": i / 100})

    def _offset_double_spinbox_value_changed_handler(self, value: float):
        self._offset_slider.setValue(int(value * 100))

    def _toggle_all_button_clicked_handler(self):
        self._control_panel.program_action_signal.emit("atom_labels.toggle_visibility_for_all_atoms", {})

    def _toggle_selected_button_clicked_handler(self):
        self._control_panel.program_action_signal.emit("atom_labels.toggle_visibility_for_selected_atoms", {})

    def update_values(self, program: "Program"):
        self._size_slider.setValue(program.config.atom_label.size)
        self._size_double_spinbox.setValue(program.config.atom_label.size)

        self._offset_slider.setValue(int(program.config.atom_label.offset * 100))
        self._offset_double_spinbox.setValue(program.config.atom_label.offset)

        self._symbol_visible_checkbox.setChecked(program.config.atom_label.symbol_visible)
        self._number_visible_checkbox.setChecked(program.config.atom_label.number_visible)
