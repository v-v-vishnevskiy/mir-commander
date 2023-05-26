from PySide6.QtCore import QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent

from mir_commander.ui.main_window.widgets.viewers.molecule import Molecule


class AtomicCoordinates(Molecule):
    def _set_draw_item(self):
        self._draw_item = self.item

    def _key_press_handler(self, event: QKeyEvent) -> bool:
        ctrl_up = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Up),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Up),
        }
        ctrl_down = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Down),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Down),
        }
        if event.keyCombination() in ctrl_up:  # Ctrl + Up
            self._set_prev_style()
        elif event.keyCombination() in ctrl_down:  # Ctrl + Down
            self._set_next_style()
        else:
            # No match
            return False  # not processed
        return True  # processed
