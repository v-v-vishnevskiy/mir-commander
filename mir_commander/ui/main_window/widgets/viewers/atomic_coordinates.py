from mir_commander.ui.main_window.widgets.viewers.molecule import Molecule


class AtomicCoordinates(Molecule):
    def _build_molecules(self):
        self._build_molecule(self.item.data())

    def _key_press_handler(self, *args, **kwargs) -> bool:
        return False
