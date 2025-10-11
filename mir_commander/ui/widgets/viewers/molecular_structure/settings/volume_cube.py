from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from mir_commander.ui.utils.opengl.utils import Color4f, color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.utils.widget import CheckBox, GroupBox, PushButton

from ..entities import VolumeCubeIsosurfaceGroup

if TYPE_CHECKING:
    from .settings import Settings


class VisibilityButton(QCheckBox):
    def __init__(self, parent: QWidget, settings: "Settings", id: int, checked: bool):
        super().__init__(parent)
        self._id = id
        self._settings = settings
        self.setStyleSheet(
            "QCheckBox::indicator { width: 20px; height: 20px; }"
            "QCheckBox::indicator:unchecked { image: url(:/icons/general/square.png); }"
            "QCheckBox::indicator:checked { image: url(:/icons/general/visibility.png); }"
        )
        self.setChecked(checked)
        self.toggled.connect(self.toggled_handler)

    def toggled_handler(self, checked: bool):
        kwargs = {"apply_to_children": True}
        if checked:
            kwargs["apply_to_parents"] = True

        for viewer in self._settings.viewers:
            viewer.visualizer.set_node_visible(self._id, checked, **kwargs)
        self._settings.volume_cube.update_values()


class DeleteButton(QPushButton):
    def __init__(self, parent: QWidget, settings: "Settings", id: int):
        super().__init__(parent)
        self._id = id
        self._settings = settings
        self.setStyleSheet("QPushButton { border: none;}")
        self.setIcon(QIcon(":/icons/general/delete.png"))
        self.clicked.connect(self.clicked_handler)

    def clicked_handler(self):
        for viewer in self._settings.viewers:
            viewer.visualizer.remove_node(self._id)
        self._settings.volume_cube.update_values()


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


class IsosurfacesTreeView(QTreeView):
    def __init__(self, parent: "Settings"):
        super().__init__(parent)
        self._settings = parent

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.setIconSize(QSize(20, 20))
        self._model = QStandardItemModel(parent=self)
        self.setModel(self._model)
        self.setDisabled(True)
        self.setIndentation(20)

    def _get_icon(self, color: Color4f) -> QPixmap:
        pixmap = QPixmap(20, 20)
        pixmap.fill(color4f_to_qcolor(color))
        return pixmap

    def add_isosurface_group(self, group: VolumeCubeIsosurfaceGroup):
        root_item = self._model.invisibleRootItem()

        text = "/".join((str(s.value) for s in group.isosurfaces))
        group_text_item = QStandardItem(text)
        group_text_item.setEditable(False)
        group_color_item = QStandardItem()
        group_visibility_item = QStandardItem()
        group_delete_item = QStandardItem()
        if len(group.isosurfaces) > 1:
            for isosurface in group.isosurfaces:
                isosurface_text_item = QStandardItem(str(isosurface.value))
                isosurface_text_item.setEditable(False)
                isosurface_color_item = QStandardItem()
                isosurface_color_item.setIcon(self._get_icon(isosurface.color))
                isosurface_visibility_item = QStandardItem()
                isosurface_delete_item = QStandardItem()
                group_text_item.appendRow(
                    [
                        isosurface_text_item,
                        isosurface_color_item,
                        isosurface_visibility_item,
                        isosurface_delete_item,
                    ]
                )
                v = VisibilityButton(self, self._settings, isosurface.id, isosurface.visible)
                self.setIndexWidget(self._model.indexFromItem(isosurface_visibility_item), v)
                d = DeleteButton(self, self._settings, isosurface.id)
                self.setIndexWidget(self._model.indexFromItem(isosurface_delete_item), d)
        else:
            group_color_item.setIcon(self._get_icon(group.isosurfaces[0].color))

        root_item.appendRow([group_text_item, group_color_item, group_visibility_item, group_delete_item])
        v = VisibilityButton(self, self._settings, group.id, group.visible)
        self.setIndexWidget(self._model.indexFromItem(group_visibility_item), v)
        d = DeleteButton(self, self._settings, group.id)
        self.setIndexWidget(self._model.indexFromItem(group_delete_item), d)

        self.setDisabled(False)
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)

    def load(self, groups: list[VolumeCubeIsosurfaceGroup]):
        self._model.clear()
        self.setDisabled(True)
        for group in groups:
            self.add_isosurface_group(group)
        self.expandAll()


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

        self._isosurfaces_tree_view = IsosurfacesTreeView(parent)

        value_layout.addWidget(self._value, 0, 0)
        value_layout.addWidget(self._color_button_1, 0, 1)
        value_layout.addWidget(add_button, 0, 2)
        value_layout.addWidget(self._both_sides_checkbox, 1, 0)
        value_layout.addWidget(self._color_button_2, 1, 1)
        value_layout.addWidget(self._isosurfaces_tree_view, 2, 0, 1, 3)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(value_layout)
        self.setLayout(self.main_layout)

    def update_values(self):
        groups = []
        for viewer in self._settings.viewers:
            groups.extend(viewer.visualizer.get_volume_cube_isosurface_groups())
        self._isosurfaces_tree_view.load(groups)

    def add_button_clicked_handler(self):
        value = self._value.value()

        items = [(value, qcolor_to_color4f(self._color_button_1.color))]
        if self._both_sides_checkbox.isChecked() and value != 0.0:
            items.append((value * -1, qcolor_to_color4f(self._color_button_2.color)))

        ids = []
        for viewer in self._settings.viewers:
            ids.append(viewer.visualizer.add_volume_cube_isosurface_group(items=items))

        self.update_values()

    def _both_sides_checkbox_toggled_handler(self, checked: bool):
        self._color_button_2.setEnabled(checked)
