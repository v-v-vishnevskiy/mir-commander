from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QMouseEvent, QPixmap
from PySide6.QtWidgets import QColorDialog, QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QVBoxLayout, QWidget

from mir_commander.ui.utils.opengl.utils import color_to_qcolor
from mir_commander.ui.utils.widget import GroupBox, PushButton

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class ColorButton(QFrame):
    def __init__(self, parent: QWidget, color: QColor = QColor("#FFFF00")):
        super().__init__(parent)
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
        self.setFixedSize(20, 20)
        self.setStyleSheet(f"QFrame {{ border: 1px solid black; background-color: {color.name()}; }}")
        self._color = color

    @property
    def color(self) -> QColor:
        return self._color

    def setColor(self, color: QColor):
        self._color = color
        self.setStyleSheet(f"QFrame {{ border: 1px solid black; background-color: {color.name()}; }}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        color = QColorDialog.getColor(
            initial=self._color, parent=self, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        self.setStyleSheet(f"QFrame {{ border: 1px solid black; background-color: {color.name()}; }}")
        self._color = color


class VolumeCube(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(self.tr("Volume Cube Surfaces"))

        self._settings = parent

        self._value = QDoubleSpinBox()
        self._value.setRange(-1000.0, 1000.0)
        self._value.setSingleStep(0.01)
        self._value.setDecimals(5)
        self._value.setValue(0.0)

        # Value layout
        value_layout = QGridLayout()

        self._color_button = ColorButton(parent=parent)

        add_button = PushButton(PushButton.tr("Add"), parent)
        add_button.clicked.connect(self.add_button_clicked_handler)

        self._surface_combo_box = QComboBox()
        self._surface_combo_box.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self._surface_combo_box.setDisabled(True)

        self._remove_button = PushButton(PushButton.tr("Remove"), parent)
        self._remove_button.setDisabled(True)
        self._remove_button.clicked.connect(self.remove_button_clicked_handler)

        value_layout.addWidget(self._value, 0, 0)
        value_layout.addWidget(self._color_button, 0, 1)
        value_layout.addWidget(add_button, 0, 2)
        value_layout.addWidget(self._surface_combo_box, 1, 0, 1, 2)
        value_layout.addWidget(self._remove_button, 1, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(value_layout)
        self.setLayout(self.main_layout)

    def update_values(self, viewer: "MolecularStructureViewer"):
        self._value.setValue(0)
        self._color_button.setColor(color_to_qcolor(viewer.visualizer._style.current.surface_color))

    def apply_settings(self, viewers: list["MolecularStructureViewer"]):
        value = self._value.value()
        color = (
            self._color_button.color.redF(),
            self._color_button.color.greenF(),
            self._color_button.color.blueF(),
            self._color_button.color.alphaF(),
        )
        for viewer in viewers:
            viewer.visualizer.add_volume_cube_surface(value=value, color=color)

    def add_button_clicked_handler(self):
        value = self._value.value()
        color = (
            self._color_button.color.redF(),
            self._color_button.color.greenF(),
            self._color_button.color.blueF(),
            self._color_button.color.alphaF(),
        )
        for viewer in self._settings.viewers:
            viewer.visualizer.add_volume_cube_surface(value=value, color=color)

        pixmap = QPixmap(20, 20)
        pixmap.fill(self._color_button.color)
        index = self._surface_combo_box.findText(str(value))
        if index == -1:
            self._surface_combo_box.addItem(pixmap, str(value))
            self._surface_combo_box.setCurrentText(str(value))
        else:
            self._surface_combo_box.setItemIcon(index, pixmap)

        self._surface_combo_box.setDisabled(False)
        self._remove_button.setDisabled(False)

    def remove_button_clicked_handler(self):
        if self._surface_combo_box.count() == 0:
            return

        value = self._surface_combo_box.currentText()
        for viewer in self._settings.viewers:
            viewer.visualizer.remove_volume_cube_surface(value=float(value))
        self._surface_combo_box.removeItem(self._surface_combo_box.currentIndex())

        if self._surface_combo_box.count() == 0:
            self._surface_combo_box.setDisabled(True)
            self._remove_button.setDisabled(True)
