from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QMouseEvent, QPixmap
from PySide6.QtWidgets import QColorDialog, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QVBoxLayout, QWidget

from mir_commander.ui.utils.widget import CheckBox, GroupBox, PushButton

if TYPE_CHECKING:
    from .settings import Settings


class ColorButton(QFrame):
    def __init__(self, parent: QWidget, color: QColor):
        super().__init__(parent)
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
        self.setFixedSize(20, 20)
        self._color = color
        self.set_color(self._color)

    @property
    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        self._color = color
        enabled = self.isEnabled()
        self.set_style_sheet(self._color, enabled)

    def set_style_sheet(self, color: QColor, enabled: bool):
        color = color if enabled else QColor(128, 128, 128, a=128)
        border_color = "black" if enabled else "gray"
        self.setStyleSheet(
            f"QFrame {{ border: 1px solid {border_color}; background-color: {color.name(QColor.NameFormat.HexArgb)}; }}"
        )

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.set_style_sheet(self._color, enabled)

    def mouseReleaseEvent(self, event: QMouseEvent):
        color = QColorDialog.getColor(
            initial=self._color, parent=self, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.set_color(color)


class VolumeCube(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(self.tr("Volume Cube Isosurfaces"))

        self._settings = parent

        self._value = QDoubleSpinBox()
        self._value.setRange(-1000.0, 1000.0)
        self._value.setSingleStep(0.01)
        self._value.setDecimals(5)
        self._value.setValue(0.0)

        # Value layout
        value_layout = QGridLayout()

        self._color_button_1 = ColorButton(parent=parent, color=QColor(255, 255, 0, a=128))
        self._color_button_2 = ColorButton(parent=parent, color=QColor(0, 70, 255, a=128))
        self._color_button_2.setEnabled(False)

        add_button = PushButton(PushButton.tr("Add"), parent)
        add_button.clicked.connect(self.add_button_clicked_handler)

        self._both_sides_checkbox = CheckBox(CheckBox.tr("Both-signed"), parent)
        self._both_sides_checkbox.setChecked(False)
        self._both_sides_checkbox.toggled.connect(self._both_sides_checkbox_toggled_handler)

        self._surface_combo_box = QComboBox()
        self._surface_combo_box.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self._surface_combo_box.setDisabled(True)

        self._remove_button = PushButton(PushButton.tr("Remove"), parent)
        self._remove_button.setDisabled(True)
        self._remove_button.clicked.connect(self.remove_button_clicked_handler)

        value_layout.addWidget(self._value, 0, 0)
        value_layout.addWidget(self._color_button_1, 0, 1)
        value_layout.addWidget(add_button, 0, 2)
        value_layout.addWidget(self._both_sides_checkbox, 1, 0)
        value_layout.addWidget(self._color_button_2, 1, 1)
        value_layout.addWidget(self._surface_combo_box, 2, 0, 1, 2)
        value_layout.addWidget(self._remove_button, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(value_layout)
        self.setLayout(self.main_layout)

    def add_button_clicked_handler(self):
        value = self._value.value()
        if self._both_sides_checkbox.isChecked():
            str_value = f"{value} / {value * -1}"
        else:
            str_value = str(value)

        color_1 = (
            self._color_button_1.color.redF(),
            self._color_button_1.color.greenF(),
            self._color_button_1.color.blueF(),
            self._color_button_1.color.alphaF(),
        )
        color_2 = (
            self._color_button_2.color.redF(),
            self._color_button_2.color.greenF(),
            self._color_button_2.color.blueF(),
            self._color_button_2.color.alphaF(),
        )
        for viewer in self._settings.viewers:
            viewer.visualizer.add_volume_cube_isosurface(value=value, color=color_1)
            if self._both_sides_checkbox.isChecked():
                viewer.visualizer.add_volume_cube_isosurface(value=value * -1, color=color_2)

        pixmap = QPixmap(20, 20)
        pixmap.fill(self._color_button_1.color)
        index = self._surface_combo_box.findText(str_value)
        if index == -1:
            data = [value, value * -1] if self._both_sides_checkbox.isChecked() else [value]
            self._surface_combo_box.addItem(pixmap, str_value, userData=data)
            self._surface_combo_box.setCurrentText(str_value)
        else:
            self._surface_combo_box.setItemIcon(index, pixmap)

        self._surface_combo_box.setDisabled(False)
        self._remove_button.setDisabled(False)

    def _both_sides_checkbox_toggled_handler(self, checked: bool):
        self._color_button_2.setEnabled(checked)

    def remove_button_clicked_handler(self):
        if self._surface_combo_box.count() == 0:
            return

        index = self._surface_combo_box.currentIndex()
        data = self._surface_combo_box.itemData(index)
        for viewer in self._settings.viewers:
            for value in data:
                viewer.visualizer.remove_volume_cube_isosurface(value=value)
        self._surface_combo_box.removeItem(self._surface_combo_box.currentIndex())

        if self._surface_combo_box.count() == 0:
            self._surface_combo_box.setDisabled(True)
            self._remove_button.setDisabled(True)
