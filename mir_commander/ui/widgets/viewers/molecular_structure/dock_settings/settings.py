from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from mir_commander.ui.utils.widget import CheckBox
from mir_commander.ui.widgets.viewers.base import BaseViewerSettings

from .labels import Labels

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Settings(BaseViewerSettings):
    def __init__(self):
        super().__init__()

        self._apply_for_all = False

        # "Apply for all" checkbox
        self.apply_for_all_checkbox = CheckBox(CheckBox.tr("Apply for all"), self)
        self.apply_for_all_checkbox.setChecked(self._apply_for_all)
        self.apply_for_all_checkbox.toggled.connect(self.apply_for_all_checkbox_toggled_handler)

        self.labels = Labels(self)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.apply_for_all_checkbox)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.labels)
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def set_active_viewer(self, viewer: "MolecularStructureViewer"):
        super().set_active_viewer(viewer)
        self.labels.update_values(viewer)

    @property
    def viewers(self) -> list["MolecularStructureViewer"]:
        return super().viewers(only_active=False if self._apply_for_all else True)

    @Slot(bool)
    def apply_for_all_checkbox_toggled_handler(self, checked: bool):
        self._apply_for_all = checked

        if checked:
            self.labels.apply_settings(self.viewers)
