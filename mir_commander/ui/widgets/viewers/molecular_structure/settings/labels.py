from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from mir_commander.ui.utils.widget import GroupBox, Label

from .utils import add_slider

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class Labels(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(self.tr("Labels"))

        self._settings = parent

        sliders_layout = QGridLayout()

        self._size_slider, self._size_double_spinbox = add_slider(
            layout=sliders_layout,
            row=0,
            text=Label.tr("Size:"),
            min_value=1,
            max_value=100,
            single_step=1,
            default_value=1,
            factor=1,
            decimals=0,
        )
        self._size_slider.valueChanged.connect(self._size_slider_value_changed_handler)
        self._size_double_spinbox.valueChanged.connect(self._size_double_spinbox_value_changed_handler)

        self._offset_slider, self._offset_double_spinbox = add_slider(
            layout=sliders_layout,
            row=1,
            text=Label.tr("Offset:"),
            min_value=1.01,
            max_value=5.0,
            single_step=0.1,
            default_value=1.01,
            factor=100,
            decimals=2,
        )
        self._offset_slider.valueChanged.connect(self._offset_slider_value_changed_handler)
        self._offset_double_spinbox.valueChanged.connect(self._offset_double_spinbox_value_changed_handler)

        main_layout = QVBoxLayout()
        main_layout.addLayout(sliders_layout)
        self.setLayout(main_layout)

    def _size_slider_value_changed_handler(self, i: int):
        self._size_double_spinbox.setValue(i)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_label_size_for_all_atoms(size=i)

    def _size_double_spinbox_value_changed_handler(self, value: int):
        self._size_slider.setValue(value)

    def _offset_slider_value_changed_handler(self, i: int):
        self._offset_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_label_offset_for_all_atoms(offset=i / 100)

    def _offset_double_spinbox_value_changed_handler(self, value: float):
        self._offset_slider.setValue(int(value * 100))

    def update_values(self, viewer: "MolecularStructureViewer"):
        visualizer = viewer.visualizer
        self._size_slider.setValue(visualizer.config.atom_label.size)
        self._size_double_spinbox.setValue(visualizer.config.atom_label.size)

        self._offset_slider.setValue(int(visualizer.config.atom_label.offset * 100))
        self._offset_double_spinbox.setValue(visualizer.config.atom_label.offset)
