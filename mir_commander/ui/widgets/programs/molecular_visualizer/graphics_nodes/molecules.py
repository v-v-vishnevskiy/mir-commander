from math import fabs

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType

from ..config import Style
from ..errors import CalcError
from .molecule import Molecule


class Molecules(Node):
    children: list[Molecule]  # type: ignore[assignment]

    def __init__(self, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

    @property
    def center(self) -> QVector3D:
        length = len(self.children)
        if length == 0:
            return QVector3D(0, 0, 0)

        x = []
        y = []
        z = []
        for molecule in self.children:
            x.append(molecule.center.x())
            y.append(molecule.center.y())
            z.append(molecule.center.z())
        return QVector3D(sum(x) / length, sum(y) / length, sum(z) / length)

    @property
    def max_coordinate(self) -> float:
        result = 0.0
        for molecule in self.children:
            for atom in molecule.atom_items:
                result = max([result, fabs(atom.position.x()), fabs(atom.position.y()), fabs(atom.position.z())])
        return result

    def num_molecules(self) -> int:
        return len(self.children)

    def get_max_molecule_radius(self) -> float:
        if len(self.children) == 0:
            return 0.0
        return max(molecule.radius for molecule in self.children)

    def set_style(self, style: Style):
        for molecule in self.children:
            molecule.set_style(style)

    def _calc_func(self, calc_func: str) -> str:
        if len(self.children) == 0:
            raise CalcError("No molecules found!")

        if len(self.children) == 1:
            return getattr(next(iter(self.children)), calc_func)()

        output = []
        errors = 0
        error = None
        for molecule in self.children:
            try:
                fn = getattr(molecule, calc_func)
                output.append(f"{molecule.name}: {fn()}")
            except CalcError as e:
                error = e
                errors += 1

        if errors == len(self.children) and error is not None:
            raise error

        return "\n".join(output)

    def calc_auto_lastsel_atoms(self) -> str:
        return self._calc_func("calc_auto_lastsel_atoms")

    def calc_distance_last2sel_atoms(self) -> str:
        return self._calc_func("calc_distance_last2sel_atoms")

    def calc_angle_last3sel_atoms(self) -> str:
        return self._calc_func("calc_angle_last3sel_atoms")

    def calc_torsion_last4sel_atoms(self) -> str:
        return self._calc_func("calc_torsion_last4sel_atoms")

    def calc_oop_last4sel_atoms(self) -> str:
        return self._calc_func("calc_oop_last4sel_atoms")

    def calc_all_parameters_selected_atoms(self) -> str:
        return self._calc_func("calc_all_parameters_selected_atoms")

    def set_atom_symbol_visible(self, value: bool):
        for molecule in self.children:
            molecule.set_atom_symbol_visible(value)

    def set_atom_number_visible(self, value: bool):
        for molecule in self.children:
            molecule.set_atom_number_visible(value)

    def toggle_labels_visibility_for_selected_atoms(self):
        all_visible = True
        for molecule in self.children:
            if not molecule.is_all_labels_visible_for_selected_atoms:
                all_visible = False
                break

        if all_visible:
            for molecule in self.children:
                molecule.hide_labels_for_selected_atoms()
        else:
            for molecule in self.children:
                molecule.show_labels_for_selected_atoms()

    def toggle_labels_visibility_for_all_atoms(self) -> bool:
        all_visible = True
        for molecule in self.children:
            if not molecule.is_all_labels_visible:
                all_visible = False
                break

        if all_visible:
            for molecule in self.children:
                molecule.hide_labels_for_all_atoms()
        else:
            for molecule in self.children:
                molecule.show_labels_for_all_atoms()

        return not all_visible  # return True if all labels are set visible, False otherwise
