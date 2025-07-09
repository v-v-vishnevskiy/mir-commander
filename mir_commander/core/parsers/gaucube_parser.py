import logging
from pathlib import Path
import numpy as np

from mir_commander.utils import consts
from ..errors import LoadFileError
from ..models import AtomicCoordinates, Item, VolCube
from .consts import babushka_priehala

logger = logging.getLogger("Parsers.GauCubeParser")

def is_gaucube(path: Path) -> bool:
    if path.suffix == ".cube":
        return True
    else:
        return False


def parse_nx(data: str) -> tuple[int, list[float]]:
    d = data.split()
    nx = int(d[0])
    x_vec = [float(x) for x in d[1:]]
    return nx, x_vec


def load_gaucube(path: Path, logs: list) -> Item:
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

    logger.info("Parsing Gaussian cube file ...")

    logs.append("Gaussian cube format.")

    vcub = VolCube()

    dset_ids = False

    atom_atomic_num = []
    atom_coord_x = []
    atom_coord_y = []
    atom_coord_z = []

    with path.open("r") as f:
        vcub.comment1 = f.readline()
        vcub.comment2 = f.readline()
        data = f.readline().split()

        if int(data[0]) > 0:
            if len(data) > 4:
                if int(data[4]) > 1:
                    raise LoadFileError(f"Unsupported number of data values per voxel {int(data[4])} in cube file.")
        elif int(data[0]) < 0:
            dset_ids = True

        natm = abs(int(data[0]))
        vcub.box_origin = [float(x) for x in data[1:]]

        nx, xvec = parse_nx(f.readline())
        vcub.steps_number.append(nx)
        vcub.steps_size.append(xvec)

        nx, xvec = parse_nx(f.readline())
        vcub.steps_number.append(nx)
        vcub.steps_size.append(xvec)

        nx, xvec = parse_nx(f.readline())
        vcub.steps_number.append(nx)
        vcub.steps_size.append(xvec)

        for ia in range(natm):
            d = f.readline().split()
            atom_atomic_num.append(int(d[0]))
            atom_coord_x.append(float(d[2])*consts.BOHR2ANGSTROM)
            atom_coord_y.append(float(d[3])*consts.BOHR2ANGSTROM)
            atom_coord_z.append(float(d[4])*consts.BOHR2ANGSTROM)

        if dset_ids:
            d = f.readline().split()
            if int(d[0]) != 1:
                raise LoadFileError(f"Unsupported number of identifiers per voxel {int(data[4])} in cube file.")

        data = f.read()

    vcub.cube_data = np.array([float(x) for x in data.split()]).reshape([vcub.steps_number[0], vcub.steps_number[1], vcub.steps_number[2]])

    result = Item(name=path.name, data=vcub, metadata={"type": "volcube", babushka_priehala: True})
    
    # Add the set of Cartesian coordinates directly to the cube
    at_coord_item = Item(
        name="CubeMol",
        data=AtomicCoordinates(
            atomic_num=atom_atomic_num,
            x=atom_coord_x,
            y=atom_coord_y,
            z=atom_coord_z,
        ),
        metadata={babushka_priehala: True}
    )
    result.items.append(at_coord_item)

    return result

