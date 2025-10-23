from typing import TYPE_CHECKING, Generic, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QSizePolicy, QWidget

from mir_commander.ui.utils.widget import CheckBox, DockWidget, GroupVBoxLayout

if TYPE_CHECKING:
    from .program_window import ProgramWindow

T = TypeVar("T", bound="ProgramWindow")


class _Container(QWidget):
    def __init__(
        self,
        control_panel: "ProgramControlPanel",
        apply_for_all_checkbox: bool = False,
        apply_for_all_value: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred))

        self.group_layout = GroupVBoxLayout()

        if apply_for_all_checkbox:
            _apply_for_all_checkbox = CheckBox(CheckBox.tr("Apply for all"))
            _apply_for_all_checkbox.setStyleSheet("QCheckBox { border: 0px; }")
            _apply_for_all_checkbox.setChecked(apply_for_all_value)
            _apply_for_all_checkbox.toggled.connect(control_panel.set_apply_for_all)
            self.group_layout.addSpacing(10)
            self.group_layout.addWidget(_apply_for_all_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.group_layout.addSpacing(10)

        self.setLayout(self.group_layout)


class ProgramControlPanel(Generic[T], DockWidget):
    """The program window's dock widget.

    A single instance of this class is used for showing widgets
    with settings for the currently active program in the mdi area.
    """

    def __init__(self, apply_for_all_checkbox: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._apply_for_all = False

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._container = _Container(self, apply_for_all_checkbox, self._apply_for_all, parent=self)
        self._scroll_area.setWidget(self._container)

        self.setMinimumWidth(350)

        self._last_active_program: None | T = None
        self._opened_programs: list[T] = []

        self.setWidget(self._scroll_area)

    @property
    def layout(self) -> GroupVBoxLayout:  # type: ignore[override]
        return self._container.group_layout

    @property
    def last_active_program(self) -> T | None:
        return self._last_active_program

    @property
    def opened_programs(self) -> list[T]:
        if self._apply_for_all:
            return self._opened_programs
        else:
            return [self._last_active_program] if self._last_active_program is not None else []

    def set_apply_for_all(self, checked: bool):
        self._apply_for_all = checked

    def update_values(self, program: T):
        """Update the values of the settings for the active program."""
        pass

    def set_opened_programs(self, programs: list[T]):
        self._opened_programs = programs
        if len(programs) > 0:
            self.show()
            self._container.show()
        else:
            self._last_active_program = None
            self.hide()
            self._container.hide()

    def set_active_program(self, program: T):
        if program != self._last_active_program:
            self._last_active_program = program
            apply_for_all = self._apply_for_all
            self._apply_for_all = False
            self.update_values(program)
            self._apply_for_all = apply_for_all

    def __del__(self):
        self._last_active_program = None
        self._opened_programs.clear()
