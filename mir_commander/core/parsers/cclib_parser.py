import logging
import pprint
from pathlib import Path

import cclib
import numpy as np
from cclib.io import ccread

from ..errors import LoadFileError
from ..models import AtomicCoordinates, AtomicCoordinatesGroup, Item, Molecule
from .consts import babushka_priehala

logger = logging.getLogger(__name__)


def load_cclib(path: Path, logs: list) -> Molecule:
    """
    Import data from file using cclib, build and populate a respective tree of items.
    Here also is implemented logic on how to visualize by default the imported items.
    We mark them for a possible automatic visualization and for expanding of the tree branches.
    Whether this will be actually done is decided in the upper context.
    Also returned is a list of messages, which can be printed later.
    """

    # Use here cclib for parsing files
    # Note, we do not handle multijob files explicitly!
    # cclib is currently on the way to implement this possibility by returning
    # lists of data from ccread.
    # So currently we just fill in our project tree as is, but in the future
    # we will split project to independent jobs.
    logs.append(f"cclib {cclib.__version__}")

    kwargs = {"future": True}
    data = ccread(path, **kwargs)
    if data is None:
        logger.error("cclib cannot determine the format of file: %s", path)
        raise LoadFileError()

    if hasattr(data, "metadata"):
        logs.append(pprint.pformat(data.metadata, compact=True))

    result = Item(
        name=path.parts[-1], 
        data=Molecule(n_atoms=data.natom, atomic_num=data.atomnos), 
        metadata={"type": "cclib"},
    )

    if hasattr(data, "charge"):
        result.data.charge = data.charge
    if hasattr(data, "mult"):
        result.data.multiplicity= data.mult

    # If we have coordinates of atoms.
    # This is actually expected to be always true
    if hasattr(data, "atomcoords"):
        cshape = np.shape(data.atomcoords)  # Number of structure sets is in cshape[0]

        if hasattr(data, "optdone"):
            # optdone is here a list due to the experimental feature in cclib turned on by the future option above
            # Take here the first converged structure
            if (len(data.optdone) > 0):  
                xyz_idx = data.optdone[0]
                xyz_title = "Optimized XYZ"
            else:
                # Take simply the last structure in the list but note that it is not (fully) optimized
                xyz_idx = cshape[0] - 1
                xyz_title = "Unoptimized final XYZ"
        else:
            # This may be a single point calculation
            # or a kind of trajectory (multi-xyz file) without any other infos.
            # Take the last structure
            xyz_idx = cshape[0] - 1
            xyz_title = "Final coordinates"

        # Add a set of representative Cartesian coordinates directly to the molecule
        at_coord_item = Item(
            name=xyz_title,
            data=AtomicCoordinates(
                atomic_num=result.data.atomic_num,
                x=data.atomcoords[xyz_idx][:, 0],
                y=data.atomcoords[xyz_idx][:, 1],
                z=data.atomcoords[xyz_idx][:, 2],
            ),
            metadata={babushka_priehala: True}
        )
        result.items.append(at_coord_item)

        # If we have multiple sets of coordinates
        if cshape[0] > 1:
            # If this was an optimization
            if hasattr(data, "optstatus"):
                optcg_item = Item(name="Optimization", data=AtomicCoordinatesGroup())
                result.items.append(optcg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    atcoods_data = AtomicCoordinates(
                        atomic_num=result.data.atomic_num,
                        x=data.atomcoords[i][:, 0], 
                        y=data.atomcoords[i][:, 1], 
                        z=data.atomcoords[i][:, 2],
                    )
                    csname = "Step {}".format(i + 1)
                    if data.optstatus[i] & data.OPT_NEW:
                        csname += ", new"
                    if data.optstatus[i] & data.OPT_DONE:
                        csname += ", done"
                    if data.optstatus[i] & data.OPT_UNCONVERGED:
                        csname += ", unconverged"
                    optcg_item.items.append(Item(name=csname, data=atcoods_data))
            # Otherwise this is an undefined set of coordinates
            else:
                molcg_item = Item(name="Coordinates", data=AtomicCoordinatesGroup())
                result.items.append(molcg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    atcoods_data = AtomicCoordinates(
                        atomic_num=result.data.atomic_num, 
                        x=data.atomcoords[i][:, 0], 
                        y=data.atomcoords[i][:, 1], 
                        z=data.atomcoords[i][:, 2],
                    )
                    csname = "Set {}".format(i + 1)
                    molcg_item.items.append(Item(name=csname, data=atcoods_data))

    # If there was an energy scan along some geometrical parameter(s)
    if hasattr(data, "scancoords"):
        cshape = np.shape(data.scancoords)  # Number of structure sets is in cshape[0]
        if cshape[0] > 0:
            scancg_item = Item(name="Scan", data=AtomicCoordinatesGroup())
            result.items.append(scancg_item)
            # Adding sets of atomic coordinates to the group
            for i in range(0, cshape[0]):
                atcoods_data = AtomicCoordinates(
                    atomic_num=result.data.atomic_num, 
                    x=data.scancoords[i][:, 0], 
                    y=data.scancoords[i][:, 1], 
                    z=data.scancoords[i][:, 2],
                )
                csname = "Step {}".format(i + 1)
                scancg_item.items.append(Item(name=csname, data=atcoods_data))

    return result
