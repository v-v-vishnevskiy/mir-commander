from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QIcon, QMouseEvent, QResizeEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QColorDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
)

from mir_commander.ui.utils.opengl.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.utils.widget import CheckBox, GroupBox, PushButton, StandardItem, TreeView

from ..entities import VolumeCubeIsosurfaceGroup

if TYPE_CHECKING:
    from .settings import Settings


class ColorButton(QPushButton):
    def __init__(self, color: QColor, settings: "Settings", id: int):
        super().__init__()
        self._color = color
        self._id = id
        self._settings = settings
        self._set_style_sheet(color)
        self.clicked.connect(self.clicked_handler)

    def _set_style_sheet(self, color: QColor):
        self.setStyleSheet(
            f"QPushButton {{ border: 1px solid black; margin: 1px;background-color: {color.name(QColor.NameFormat.HexArgb)}; }}"
        )

    def clicked_handler(self):
        color = QColorDialog.getColor(
            initial=self._color,
            parent=self,
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel
            | QColorDialog.ColorDialogOption.DontUseNativeDialog,
        )
        if color.isValid():
            self._set_style_sheet(color)
            for viewer in self._settings.viewers:
                viewer.visualizer.set_node_color_by_id(self._id, qcolor_to_color4f(color))
            self._settings.volume_cube.update_values()


class VisibilityButton(QPushButton):
    def __init__(self, settings: "Settings", id: int, visible: bool):
        super().__init__()
        self._id = id
        self._visible = visible
        self._settings = settings
        self.setStyleSheet("QPushButton { border: none; }")
        self.setIcon(QIcon(":/icons/general/eye.png" if visible else ":/icons/general/square.png"))
        self.clicked.connect(self.clicked_handler)

    def clicked_handler(self):
        self._visible = not self._visible
        kwargs = {"apply_to_children": True}
        if self._visible:
            kwargs["apply_to_parents"] = True

        for viewer in self._settings.viewers:
            viewer.visualizer.set_node_visible(self._id, self._visible, **kwargs)
        self._settings.volume_cube.update_values()


class DeleteButton(QPushButton):
    def __init__(self, settings: "Settings", id: int):
        super().__init__()
        self._id = id
        self._settings = settings
        self.setStyleSheet("QPushButton { border: none; }")
        self.setIcon(QIcon(":/icons/general/delete.png"))
        self.clicked.connect(self.clicked_handler)

    def clicked_handler(self):
        for viewer in self._settings.viewers:
            viewer.visualizer.remove_node(self._id)
        self._settings.volume_cube.update_values()


class IsosurfacesTreeView(TreeView):
    def __init__(self, settings: "Settings"):
        super().__init__()
        self._settings = settings

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self._model = QStandardItemModel(parent=self)
        self.setModel(self._model)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setIndentation(20)
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setStyleSheet(
            "QTreeView::item:hover { background: #DDDDDD; } QTreeView::item { height: 20px; padding: 0px; margin: 0px; }"
        )
        self.header().setMinimumSectionSize(20)

    def add_isosurface_group(self, group: VolumeCubeIsosurfaceGroup):
        root_item = self._model.invisibleRootItem()

        if len(group.isosurfaces) < 2:
            if group.isosurfaces[0].inverted:
                text = StandardItem.tr("{} (inverted)").format(group.value)
            else:
                text = StandardItem.tr("{} (original)").format(group.value)
        else:
            text = str(group.value)  # type: ignore[assignment]

        group_text_item = StandardItem(text)
        group_text_item.setEditable(False)
        group_color_item = QStandardItem()
        group_visibility_item = QStandardItem()
        group_delete_item = QStandardItem()
        root_item.appendRow([group_text_item, group_color_item, group_visibility_item, group_delete_item])

        if len(group.isosurfaces) > 1:
            for isosurface in group.isosurfaces:
                isosurface_text_item = (
                    StandardItem(StandardItem.tr("inverted"))
                    if isosurface.inverted
                    else StandardItem(StandardItem.tr("original"))
                )
                isosurface_text_item.setEditable(False)
                isosurface_color_item = QStandardItem()
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
                c = ColorButton(color4f_to_qcolor(isosurface.color), self._settings, isosurface.id)
                self.setIndexWidget(self._model.indexFromItem(isosurface_color_item), c)
                v = VisibilityButton(self._settings, isosurface.id, isosurface.visible)
                self.setIndexWidget(self._model.indexFromItem(isosurface_visibility_item), v)
                d = DeleteButton(self._settings, isosurface.id)
                self.setIndexWidget(self._model.indexFromItem(isosurface_delete_item), d)
        else:
            c = ColorButton(color4f_to_qcolor(group.isosurfaces[0].color), self._settings, group.isosurfaces[0].id)
            self.setIndexWidget(self._model.indexFromItem(group_color_item), c)
        v = VisibilityButton(self._settings, group.id, group.visible)
        self.setIndexWidget(self._model.indexFromItem(group_visibility_item), v)
        d = DeleteButton(self._settings, group.id)
        self.setIndexWidget(self._model.indexFromItem(group_delete_item), d)

    def load(self, groups: list[VolumeCubeIsosurfaceGroup]):
        self._model.clear()
        for group in groups:
            self.add_isosurface_group(group)
        self.expandAll()

    def resizeEvent(self, event: QResizeEvent):
        self.setColumnWidth(0, event.size().width() - 20 - 32 - 24)
        self.setColumnWidth(1, 20)
        self.setColumnWidth(2, 32)
        self.setColumnWidth(3, 24)
        super().resizeEvent(event)


class ColorButtonNewIsosurface(QFrame):
    def __init__(self, color: QColor):
        super().__init__()
        self.setFixedSize(20, 20)
        self._color = color
        self.set_color(self._color)

    @property
    def color(self) -> QColor:
        return self._color

    def set_color(self, color: QColor):
        self._color = color
        self.set_style_sheet(color, self.isEnabled())

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
            initial=self._color,
            parent=self,
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel
            | QColorDialog.ColorDialogOption.DontUseNativeDialog,
        )
        if color.isValid():
            self.set_color(color)


class VolumeCube(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Volume Cube Isosurfaces"), parent=parent)

        self._settings = parent

        self._value = QDoubleSpinBox()
        self._value.setRange(-1000.0, 1000.0)
        self._value.setSingleStep(0.01)
        self._value.setDecimals(5)
        self._value.setValue(0.05)

        # Value layout
        value_layout = QGridLayout()

        self._color_button_1 = ColorButtonNewIsosurface(color=QColor(255, 0, 0, a=50))
        self._color_button_2 = ColorButtonNewIsosurface(color=QColor(0, 0, 255, a=50))
        self._color_button_2.setEnabled(False)

        add_button = PushButton(PushButton.tr("Add"))
        add_button.clicked.connect(self.add_button_clicked_handler)

        self._both_sides_checkbox = CheckBox(CheckBox.tr("Inverse"))
        self._both_sides_checkbox.setChecked(False)
        self._both_sides_checkbox.toggled.connect(self._both_sides_checkbox_toggled_handler)

        self._isosurfaces_tree_view = IsosurfacesTreeView(self._settings)

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
        is_empty_scalar_field = True
        for viewer in self._settings.viewers:
            groups.extend(viewer.visualizer.get_volume_cube_isosurface_groups())
            is_empty_scalar_field = is_empty_scalar_field and viewer.visualizer.is_empty_volume_cube_scalar_field()
        self._isosurfaces_tree_view.load(groups)
        self.setDisabled(is_empty_scalar_field)

    def add_button_clicked_handler(self):
        value = self._value.value()

        for viewer in self._settings.viewers:
            viewer.visualizer.add_volume_cube_isosurface(
                value,
                qcolor_to_color4f(self._color_button_1.color),
                qcolor_to_color4f(self._color_button_2.color),
                self._both_sides_checkbox.isChecked(),
            )

        self.update_values()

    def _both_sides_checkbox_toggled_handler(self, checked: bool):
        self._color_button_2.setEnabled(checked)
