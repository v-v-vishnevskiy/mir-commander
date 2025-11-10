from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QSizePolicy, QWidget

from mir_commander.api.program import ControlElement, ControlPanel
from mir_commander.ui.sdk.widget import CheckBox, DockWidget, GroupVBoxLayout


class _ControlComponents(QWidget):
    def __init__(
        self,
        elements: list[ControlElement],
        allows_apply_for_all: bool,
        apply_for_all_value: bool,
        apply_for_all_handler: Callable[[bool], None],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred))

        self.group_layout = GroupVBoxLayout()

        if allows_apply_for_all:
            _apply_for_all_checkbox = CheckBox(CheckBox.tr("Apply for all"))
            _apply_for_all_checkbox.setStyleSheet("QCheckBox { border: 0px; }")
            _apply_for_all_checkbox.setChecked(apply_for_all_value)
            _apply_for_all_checkbox.toggled.connect(apply_for_all_handler)
            self.group_layout.addSpacing(10)
            self.group_layout.addWidget(_apply_for_all_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.group_layout.addSpacing(10)

        for control_element in elements:
            self.group_layout.add_widget(control_element.title, control_element.widget, control_element.visible)
        self.group_layout.addStretch(1)

        self.setLayout(self.group_layout)


class ProgramControlPanelDock(DockWidget):
    """
    The program's control panel dock widget.

    A single instance of this class is used for showing widgets with settings for the program.
    """

    def __init__(self, control_panel: ControlPanel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.control_panel = control_panel

        self._apply_for_all = False

        self._visible = True

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._container = _ControlComponents(
            control_panel.get_control_elements(),
            control_panel.allows_apply_for_all(),
            self._apply_for_all,
            self._apply_for_all_handler,
            parent=self,
        )
        self._scroll_area.setWidget(self._container)

        self.setMinimumWidth(350)

        self.visibilityChanged.connect(self._visibility_changed_handler)

        self.setWidget(self._scroll_area)

    def _apply_for_all_handler(self, checked: bool):
        self._apply_for_all = checked

    @property
    def apply_for_all(self) -> bool:
        return self._apply_for_all

    def hide(self):
        visible = self._visible
        super().hide()
        self._visible = visible

    def restore_visibility(self):
        if self._visible:
            self.show()
        else:
            self.hide()

    def _visibility_changed_handler(self, visible: bool):
        self._visible = visible
