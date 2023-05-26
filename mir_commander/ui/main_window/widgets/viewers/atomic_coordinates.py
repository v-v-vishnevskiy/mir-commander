from mir_commander.ui.main_window.widgets.viewers.molecule import Molecule


class AtomicCoordinates(Molecule):
    def _set_draw_item(self):
        self._draw_item = self.item

    def _draw_next_item(self):
        pass

    def _draw_prev_item(self):
        pass
