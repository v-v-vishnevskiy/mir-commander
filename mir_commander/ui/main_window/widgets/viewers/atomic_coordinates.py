from mir_commander.ui.main_window.widgets.viewers.molecule import Molecule


class AtomicCoordinates(Molecule):
    def _set_draw_item(self):
        self._draw_item = self.item

    def _key_press_handler(self, *args, **kwargs) -> bool:
        return False
