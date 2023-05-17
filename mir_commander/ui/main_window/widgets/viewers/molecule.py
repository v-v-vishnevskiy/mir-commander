import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph import Vector

from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS
from mir_commander.default_config import CONFIG

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


AT_RAD = CONFIG["widgets"]["viewers"]["molecule"]["atoms"]["radius"]  # type: ignore
COLOR = CONFIG["widgets"]["viewers"]["molecule"]["atoms"]["color"]  # type: ignore


@dataclass
class MoleculeStruct:
    atoms: List[gl.GLMeshItem]
    center: Vector
    radius: float


class Molecule(gl.GLViewWidget):
    def __init__(self, item: "Item"):
        super().__init__(None)
        self.item = item
        self.__molecule_index = 0
        self._molecule: Union[None, MoleculeStruct] = None

        self.setMinimumSize(175, 131)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
        self._build_molecules()
        self.draw()

    def _build_molecules(self):
        self.__molecule_index, ds = self.__atomic_coordinates(self.__molecule_index, self.item)
        if ds:
            self._build_molecule(ds)

    def _build_molecule(self, ds: AtomicCoordinatesDS):
        distance = 0
        atoms = []
        for i, atomic_num in enumerate(ds.atomic_num):
            mesh_data = gl.MeshData.sphere(20, 20, AT_RAD[atomic_num])
            mesh_item = gl.GLMeshItem(
                meshdata=mesh_data, smooth=True, shader="shaded", color=self.hex_to_float(COLOR[atomic_num])
            )
            mesh_item.translate(ds.x[i], ds.y[i], ds.z[i])
            atoms.append(mesh_item)

            d = ds.x[i] ** 2 + ds.y[i] ** 2 + ds.z[i] ** 2
            if d > distance:
                distance = d

        pos = Vector(np.sum(ds.x) / ds.x.size, np.sum(ds.y) / ds.y.size, np.sum(ds.z) / ds.z.size)

        self._molecule = MoleculeStruct(atoms, pos, math.sqrt(distance))

    def draw(self):
        self.clear()
        if self._molecule:
            for atom in self._molecule.atoms:
                self.addItem(atom)
            self.setCameraPosition(pos=self._molecule.center, distance=self._molecule.radius * 3.5)

    def hex_to_float(self, value: int) -> Tuple[float, float, float, float]:
        return (((value & 0xFF0000) >> 15) / 256, ((value & 0xFF00) >> 7) / 256, (value & 0xFF) / 256, 1.0)

    def __atomic_coordinates(
        self, index: int, parent: "Item", counter: int = -1
    ) -> Tuple[int, Optional[AtomicCoordinatesDS]]:
        last_ac_data = None
        for i in range(parent.rowCount()):
            data = parent.child(i).data()
            if isinstance(data, AtomicCoordinatesDS):
                last_ac_data = data
                counter += 1
                if index == counter:
                    return counter, data
            elif parent.child(i).hasChildren():
                return self.__atomic_coordinates(index, parent.child(i), counter)
        return counter, last_ac_data
