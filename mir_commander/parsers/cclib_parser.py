import logging
import pprint
from pathlib import Path

import cclib
import numpy as np
from cclib.io import ccread

from mir_commander import errors
from mir_commander.data_structures.molecule import Molecule, AtomicCoordinates
from mir_commander.ui.utils import item

from .utils import ItemParametrized

logger = logging.getLogger(__name__)


def load_cclib(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from file using cclib, build and populate a respective tree of items.
    Here also is implemented logic on how to visualize by default the imported items.
    We mark them for a possible automatic visualization and for expanding of the tree branches.
    Whether this will be actually done is decided in the upper context.
    Also returned is a list of messages, which can be printed later.
    """
    flagged_items = []
    messages = []

    # Use here cclib for parsing files
    # Note, we do not handle multijob files explicitly!
    # cclib is currently on the way to implement this possibility by returning
    # lists of data from ccread.
    # So currently we just fill in our project tree as is, but in the future
    # we will split project to independent jobs.
    messages.append("cclib {}".format(cclib.__version__))

    kwargs = {}
    kwargs["future"] = True
    data = ccread(path, **kwargs)
    if data is None:
        msg = "cclib cannot determine the format of file"
        logger.error(f"{msg}: {path}")
        raise errors.LoadFileError(msg, f"{msg}: {path}")

    if hasattr(data, "metadata"):
        messages.append(pprint.pformat(data.metadata, compact=True))

    moldata = Molecule(data.natom, data.atomnos)
    if hasattr(data, "charge"):
        moldata.charge = data.charge
    if hasattr(data, "mult"):
        moldata.multiplicity = data.mult
    molitem = item.Molecule(path.parts[1], moldata)
    molitem.file_path = path

    # If we have coordinates of atoms.
    # This is actually expected to be always true
    if hasattr(data, "atomcoords"):
        cshape = np.shape(data.atomcoords)  # Number of structure sets is in cshape[0]

        if hasattr(data, "optdone"):
            if (
                len(data.optdone) > 0
            ):  # optdone is here a list due to the experimental feature in cclib turned on by the future option above
                # Take here the first converged structure
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
        at_coord_data = AtomicCoordinates(
            moldata.atomic_num,
            data.atomcoords[xyz_idx][:, 0],
            data.atomcoords[xyz_idx][:, 1],
            data.atomcoords[xyz_idx][:, 2],
        )
        at_coord_item = item.AtomicCoordinates(xyz_title, at_coord_data)
        molitem.appendRow(at_coord_item)

        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})
        flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

        # If we have multiple sets of coordinates
        if cshape[0] > 1:
            # If this was an optimization
            if hasattr(data, "optstatus"):
                optcg_item = item.AtomicCoordinatesGroup("Optimization")
                molitem.appendRow(optcg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    atcoods_data = AtomicCoordinates(
                        moldata.atomic_num, data.atomcoords[i][:, 0], data.atomcoords[i][:, 1], data.atomcoords[i][:, 2]
                    )
                    csname = "Step {}".format(i + 1)
                    if data.optstatus[i] & data.OPT_NEW:
                        csname += ", new"
                    if data.optstatus[i] & data.OPT_DONE:
                        csname += ", done"
                    if data.optstatus[i] & data.OPT_UNCONVERGED:
                        csname += ", unconverged"
                    optcg_item.appendRow(item.AtomicCoordinates(csname, atcoods_data))
            # Otherwise this is an undefined set of coordinates
            else:
                molcg_item = item.AtomicCoordinatesGroup("Coordinates")
                molitem.appendRow(molcg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    atcoods_data = AtomicCoordinates(
                        moldata.atomic_num, data.atomcoords[i][:, 0], data.atomcoords[i][:, 1], data.atomcoords[i][:, 2]
                    )
                    csname = "Set {}".format(i + 1)
                    molcg_item.appendRow(item.AtomicCoordinates(csname, atcoods_data))

    # If there was an energy scan along some geometrical parameter(s)
    if hasattr(data, "scancoords"):
        cshape = np.shape(data.scancoords)  # Number of structure sets is in cshape[0]
        if cshape[0] > 0:
            scancg_item = item.AtomicCoordinatesGroup("Scan")
            molitem.appendRow(scancg_item)
            # Adding sets of atomic coordinates to the group
            for i in range(0, cshape[0]):
                atcoods_data = AtomicCoordinates(
                    moldata.atomic_num, data.scancoords[i][:, 0], data.scancoords[i][:, 1], data.scancoords[i][:, 2]
                )
                csname = "Step {}".format(i + 1)
                scancg_item.appendRow(item.AtomicCoordinates(csname, atcoods_data))

    return molitem, flagged_items, messages
