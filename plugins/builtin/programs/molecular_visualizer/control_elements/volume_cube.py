from time import monotonic_ns
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QIcon, QResizeEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QDoubleSpinBox, QPushButton

from mir_commander.core.graphics.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.sdk.widget import (
    CheckBox,
    ColorButton,
    GridLayout,
    PushButton,
    StandardItem,
    TreeView,
    VBoxLayout,
)

from ...program import ControlBlock
from ..entities import VolumeCubeIsosurfaceGroup

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class VisibilityButton(QPushButton):
    def __init__(self, control_panel: "ControlPanel", id: int, visible: bool):
        super().__init__()
        self._id = id
        self._visible = visible
        self._control_panel = control_panel
        self.setStyleSheet("QPushButton { border: none; }")
        self.setIcon(QIcon(":/core/icons/eye.png" if visible else ":/core/icons/square.png"))
        self.clicked.connect(self._clicked_handler)

    def _clicked_handler(self):
        self._visible = not self._visible
        data = {"id": self._id, "visible": self._visible, "apply_to_children": True}
        if self._visible:
            data["apply_to_parents"] = True

        self._control_panel.program_action_signal.emit("volume_cube.set_isosurface_visible", data)


class DeleteButton(QPushButton):
    def __init__(self, control_panel: "ControlPanel", id: int):
        super().__init__(QIcon(":/core/icons/delete.png"), "")
        self._id = id
        self._control_panel = control_panel
        self.setStyleSheet("QPushButton { border: none; }")
        self.clicked.connect(self._clicked_handler)

    def _clicked_handler(self):
        self._control_panel.program_action_signal.emit("volume_cube.remove_isosurface", {"id": self._id})


class IsosurfacesTreeView(TreeView):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()
        self._control_panel = control_panel

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

        def color_changed_handler(id: int):
            return lambda color: self._color_changed_handler(id, color)

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
                c = ColorButton(color4f_to_qcolor(isosurface.color))
                c.color_changed.connect(color_changed_handler(isosurface.id))
                self.setIndexWidget(self._model.indexFromItem(isosurface_color_item), c)
                v = VisibilityButton(self._control_panel, isosurface.id, isosurface.visible)
                self.setIndexWidget(self._model.indexFromItem(isosurface_visibility_item), v)
                d = DeleteButton(self._control_panel, isosurface.id)
                self.setIndexWidget(self._model.indexFromItem(isosurface_delete_item), d)
        else:
            c = ColorButton(color4f_to_qcolor(group.isosurfaces[0].color))
            c.color_changed.connect(color_changed_handler(group.isosurfaces[0].id))
            self.setIndexWidget(self._model.indexFromItem(group_color_item), c)
        v = VisibilityButton(self._control_panel, group.id, group.visible)
        self.setIndexWidget(self._model.indexFromItem(group_visibility_item), v)
        d = DeleteButton(self._control_panel, group.id)
        self.setIndexWidget(self._model.indexFromItem(group_delete_item), d)

    def _color_changed_handler(self, id: int, color: QColor):
        self._control_panel.program_action_signal.emit(
            "volume_cube.set_isosurface_color", {"id": id, "color": qcolor_to_color4f(color)}
        )

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


class VolumeCube(ControlBlock):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        self._value = QDoubleSpinBox()
        self._value.setRange(-1000.0, 1000.0)
        self._value.setSingleStep(0.01)
        self._value.setDecimals(5)
        self._value.setValue(0.05)

        # Value layout
        value_layout = GridLayout()

        self._color_button_1 = ColorButton(color=QColor(255, 0, 0, a=200))
        self._color_button_2 = ColorButton(color=QColor(0, 0, 255, a=200))
        self._color_button_2.setEnabled(False)

        add_button = PushButton(PushButton.tr("Add"))
        add_button.clicked.connect(self.add_button_clicked_handler)

        self._inverse_checkbox = CheckBox(CheckBox.tr("Inverse"))
        self._inverse_checkbox.setChecked(False)
        self._inverse_checkbox.toggled.connect(self._inverse_checkbox_toggled_handler)

        self._isosurfaces_tree_view = IsosurfacesTreeView(self._control_panel)

        value_layout.addWidget(self._value, 0, 0)
        value_layout.addWidget(self._color_button_1, 0, 1)
        value_layout.addWidget(add_button, 0, 2)
        value_layout.addWidget(self._inverse_checkbox, 1, 0)
        value_layout.addWidget(self._color_button_2, 1, 1)
        value_layout.addWidget(self._isosurfaces_tree_view, 2, 0, 1, 3)

        self.main_layout = VBoxLayout()
        self.main_layout.addLayout(value_layout)
        self.setLayout(self.main_layout)

    def update_values(self, program: "Program"):
        self._isosurfaces_tree_view.load(program.visualizer.get_volume_cube_isosurface_groups())
        self.setDisabled(program.visualizer.is_empty_volume_cube_scalar_field())

    def add_button_clicked_handler(self):
        self._control_panel.program_action_signal.emit(
            "volume_cube.add_isosurface",
            {
                "value": self._value.value(),
                "color_1": qcolor_to_color4f(self._color_button_1.color),
                "color_2": qcolor_to_color4f(self._color_button_2.color),
                "inverse": self._inverse_checkbox.isChecked(),
                "unique_id": monotonic_ns(),
            },
        )

    def _inverse_checkbox_toggled_handler(self, checked: bool):
        self._color_button_2.setEnabled(checked)
