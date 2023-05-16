from typing import TYPE_CHECKING

import pyqtgraph.opengl as gl

if TYPE_CHECKING:
    from mir_commander.utils.item import Molecule as MoleculeItem


class Molecule(gl.GLViewWidget):
    def __init__(self, parent, item: "MoleculeItem"):
        super().__init__(parent)
        self.item = item

        self.setMinimumSize(175, 131)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
