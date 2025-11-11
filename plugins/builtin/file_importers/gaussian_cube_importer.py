from pathlib import Path

import numpy as np

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.data_structures.volume_cube import VolumeCube
from mir_commander.api.file_importer import ImportFileError
from mir_commander.api.project_node_schema import ActionType
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1 as Node
from mir_commander.core.chemistry import BOHR2ANGSTROM


def _parse_nx(data: str) -> tuple[int, list[float]]:
    d = data.split()
    nx = int(d[0])
    x_vec = [float(x) for x in d[1:]]
    return nx, x_vec


def read(path: Path, logs: list[str]) -> Node:
    """
    Import data from Gaussian cube file in format:
    Comment line 1
    Comment line 2
    N_atom Ox Oy Oz [nval]  # number of atoms, followed by the coordinates of the origin and optional number of values
                            # per voxel
    N1 vx1 vy1 vz1          # number of grids along each axis, followed by the step size in x/y/z direction.
    N2 vx2 vy2 vz2          # ...
    N3 vx3 vy3 vz3          # ...
    Atom1 Z1 x y z          # Atomic number, charge, and coordinates of the atom
    ...                     # ...
    AtomN ZN x y z          # ...
    [DSET_IDS]              # Data set identifiers if number of atoms above is negative
    Data on grids           # (N1*N2) lines of records, each line has N3 elements
                            # But actually this may be in free format, just value-by-value.

    References for the format:
    http://paulbourke.net/dataformats/cube/
    https://h5cube-spec.readthedocs.io/en/latest/cubeformat.html
    http://gaussian.com/cubegen/
    """

    logs.append("Gaussian cube format.")

    comment_1 = ""
    comment_2 = ""
    box_origin: list[float] = []
    steps_number: list[int] = []
    steps_size: list[list[float]] = []

    dset_ids = False

    atom_atomic_num = []
    atom_coord_x = []
    atom_coord_y = []
    atom_coord_z = []

    with path.open("r") as f:
        comment_1 = f.readline()
        comment_2 = f.readline()
        data = f.readline().split()

        if int(data[0]) > 0:
            if len(data) > 4:
                if int(data[4]) > 1:
                    raise ImportFileError(f"Unsupported number of data values per voxel {int(data[4])} in cube file.")
        elif int(data[0]) < 0:
            dset_ids = True

        natm = abs(int(data[0]))
        box_origin = [float(x) for x in data[1:]]

        nx, xvec = _parse_nx(f.readline())
        steps_number.append(nx)
        steps_size.append(xvec)

        nx, xvec = _parse_nx(f.readline())
        steps_number.append(nx)
        steps_size.append(xvec)

        nx, xvec = _parse_nx(f.readline())
        steps_number.append(nx)
        steps_size.append(xvec)

        for _ in range(natm):
            d = f.readline().split()
            atom_atomic_num.append(int(d[0]))
            atom_coord_x.append(float(d[2]) * BOHR2ANGSTROM)
            atom_coord_y.append(float(d[3]) * BOHR2ANGSTROM)
            atom_coord_z.append(float(d[4]) * BOHR2ANGSTROM)

        if dset_ids:
            d = f.readline().split()
            if int(d[0]) != 1:
                raise ImportFileError(f"Unsupported number of identifiers per voxel {int(data[4])} in cube file.")

        rest_data = f.read()

    result = Node(
        name=path.name,
        type="builtin.volume_cube",
        data=VolumeCube(
            comment1=comment_1,
            comment2=comment_2,
            box_origin=box_origin,
            steps_number=steps_number,
            steps_size=steps_size,
            cube_data=np.array([float(x) for x in rest_data.split()]).reshape(steps_number),
        ),
        actions=[ActionType.OPEN],
    )

    # Add the set of Cartesian coordinates directly to the cube
    at_coord_item = Node(
        name="CubeMol",
        type="builtin.atomic_coordinates",
        data=AtomicCoordinates(atomic_num=atom_atomic_num, x=atom_coord_x, y=atom_coord_y, z=atom_coord_z),
    )
    result.nodes.append(at_coord_item)

    return result
