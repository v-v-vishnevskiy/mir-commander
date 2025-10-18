from typing import TYPE_CHECKING, Generic, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget

from mir_commander.ui.utils.widget import CheckBox, GroupVBoxLayout

if TYPE_CHECKING:
    from .program_window import ProgramWindow

T = TypeVar("T", bound="ProgramWindow")


class ProgramControlPanel(Generic[T], QWidget):
    def __init__(self, apply_for_all_checkbox: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred))

        self._active_viewer: None | T = None
        self._all_viewers: list[T] = []

        # "Apply for all" checkbox
        self._apply_for_all = False

        self._layout = GroupVBoxLayout()

        if apply_for_all_checkbox:
            self._apply_for_all_checkbox = CheckBox(CheckBox.tr("Apply for all"))
            self._apply_for_all_checkbox.setStyleSheet("QCheckBox { border: 0px; }")
            self._apply_for_all_checkbox.setChecked(self._apply_for_all)
            self._apply_for_all_checkbox.toggled.connect(self._apply_for_all_checkbox_toggled_handler)
            self._layout.addSpacing(10)
            self._layout.addWidget(self._apply_for_all_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._layout.addSpacing(10)

        self.setLayout(self._layout)

    @property
    def active_viewer(self) -> T | None:
        return self._active_viewer

    @property
    def viewers(self) -> list[T]:
        if self._apply_for_all:
            return self._all_viewers
        else:
            return [self._active_viewer] if self._active_viewer is not None else []

    @property
    def layout(self) -> GroupVBoxLayout:  # type: ignore[override]
        return self._layout

    def _apply_for_all_checkbox_toggled_handler(self, checked: bool):
        self._apply_for_all = checked

    def set_active_viewer(self, viewer: T):
        self._active_viewer = viewer
        if self._active_viewer is not None:
            apply_for_all = self._apply_for_all
            self._apply_for_all = False
            self.update_values(self._active_viewer)
            self._apply_for_all = apply_for_all

    def update_values(self, viewer: T):
        """Update the values of the settings for the active viewer."""
        pass

    def set_all_viewers(self, viewers: list[T]):
        self._all_viewers = viewers

    def __del__(self):
        self._active_viewer = None
        self._all_viewers.clear()
