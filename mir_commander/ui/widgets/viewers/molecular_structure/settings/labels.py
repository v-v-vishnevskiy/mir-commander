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

        self.size_slider, self.size_double_spinbox = add_slider(
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
        self.size_slider.valueChanged.connect(self.size_slider_value_changed_handler)
        self.size_double_spinbox.valueChanged.connect(self.size_double_spinbox_value_changed_handler)

        self.offset_slider, self.offset_double_spinbox = add_slider(
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
        self.offset_slider.valueChanged.connect(self.offset_slider_value_changed_handler)
        self.offset_double_spinbox.valueChanged.connect(self.offset_double_spinbox_value_changed_handler)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(sliders_layout)
        self.setLayout(self.main_layout)

    def update_values(self, viewer: "MolecularStructureViewer"):
        self.size_slider.setValue(viewer.visualizer.config.atom_label.size)
        self.size_double_spinbox.setValue(viewer.visualizer.config.atom_label.size)

        self.offset_slider.setValue(int(viewer.visualizer.config.atom_label.offset * 100))
        self.offset_double_spinbox.setValue(viewer.visualizer.config.atom_label.offset)

    def apply_settings(self, viewers: list["MolecularStructureViewer"]):
        for viewer in viewers:
            viewer.visualizer.set_label_size_for_all_atoms(size=self.size_slider.value())
            viewer.visualizer.set_label_offset_for_all_atoms(offset=self.offset_slider.value() / 100)

    def size_slider_value_changed_handler(self, i: int):
        self.size_double_spinbox.setValue(i)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_label_size_for_all_atoms(size=i)

    def size_double_spinbox_value_changed_handler(self, value: int):
        self.size_slider.setValue(value)

    def offset_slider_value_changed_handler(self, i: int):
        self.offset_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_label_offset_for_all_atoms(offset=i / 100)

    def offset_double_spinbox_value_changed_handler(self, value: float):
        self.offset_slider.setValue(int(value * 100))
