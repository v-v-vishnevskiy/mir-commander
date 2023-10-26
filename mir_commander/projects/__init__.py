import logging
import os
import pprint
import re

import cclib
import numpy as np
from cclib.io import ccread

from mir_commander import consts, exceptions
from mir_commander.data_structures import molecule as ds_molecule
from mir_commander.projects.base import ItemParametrized, Project
from mir_commander.projects.molecule import Molecule
from mir_commander.projects.temporary import Temporary
from mir_commander.ui.utils import item
from mir_commander.utils.config import Config

logger = logging.getLogger(__name__)

IMPORT_FORMAT_UNKNOWN = 0
IMPORT_FORMAT_UNEX = 1


def import_file_unex(path: str) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from UNEX file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items = []
    messages = []

    with open(path, "r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                messages.append(line.strip())

    molitem = item.Molecule(os.path.split(path)[1], None)
    molitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    return molitem, flagged_items, messages


def import_file_cclib(path: str) -> tuple[item.Item, list[dict], list[str]]:
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
        raise exceptions.LoadFile(msg, f"{msg}: {path}")

    if hasattr(data, "metadata"):
        messages.append(pprint.pformat(data.metadata, compact=True))

    moldata = ds_molecule.Molecule(data.natom, data.atomnos)
    if hasattr(data, "charge"):
        moldata.charge = data.charge
    if hasattr(data, "mult"):
        moldata.multiplicity = data.mult
    molitem = item.Molecule(os.path.split(path)[1], moldata)
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
        atcoods_data = ds_molecule.AtomicCoordinates(
            moldata.atomic_num,
            data.atomcoords[xyz_idx][:, 0],
            data.atomcoords[xyz_idx][:, 1],
            data.atomcoords[xyz_idx][:, 2],
        )
        arcoords_item = item.AtomicCoordinates(xyz_title, atcoods_data)
        molitem.appendRow(arcoords_item)

        flagged_items.append({"itempar": ItemParametrized(arcoords_item, {"maximize": True}), "view": True})
        flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

        # If we have multiple sets of coordinates
        if cshape[0] > 1:
            # If this was an optimization
            if hasattr(data, "optstatus"):
                optcg_item = item.AtomicCoordinatesGroup("Optimization")
                molitem.appendRow(optcg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    atcoods_data = ds_molecule.AtomicCoordinates(
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
                    atcoods_data = ds_molecule.AtomicCoordinates(
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
                atcoods_data = ds_molecule.AtomicCoordinates(
                    moldata.atomic_num, data.scancoords[i][:, 0], data.scancoords[i][:, 1], data.scancoords[i][:, 2]
                )
                csname = "Step {}".format(i + 1)
                scancg_item.appendRow(item.AtomicCoordinates(csname, atcoods_data))

    return molitem, flagged_items, messages


def import_file(path: str) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from file,
    return tree of items, list of flagged items and list of messages
    """
    unexver_validator = re.compile(r"^([0-9]+).([0-9]+)-([0-9]+)-([a-z0-9]+)$")  # For example 1.7-33-g5a83887
    file_format = IMPORT_FORMAT_UNKNOWN
    line_number_limit = 10
    with open(path, "r") as input_file:
        for line_number, line in enumerate(input_file):
            if "UNEX" in line and line_number == 0:
                unexver_match = unexver_validator.match(line.split()[1])
                if unexver_match:
                    file_format = IMPORT_FORMAT_UNEX
                    break
            if line_number > line_number_limit:  # line_number starts at 0.
                break

    if file_format == IMPORT_FORMAT_UNEX:
        project_root_item, flagged_items, messages = import_file_unex(path)
    else:
        project_root_item, flagged_items, messages = import_file_cclib(path)

    return project_root_item, flagged_items, messages


def load_project(path: str) -> tuple[Project, list[str]]:
    """
    Returns (re)created project and a list of messages corresponding to the process of project loading.
    """
    path = os.path.normpath(path)

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if os.path.isfile(path):
        project = Temporary(path)
        project_root_item, flagged_items, messages = import_file(path)
        project.root_item.appendRow(project_root_item)

        for fitem in flagged_items:
            if fitem.get("view"):
                project.mark_item_to_view(fitem["itempar"])
            if fitem.get("expand"):
                project.mark_item_to_expand(fitem["itempar"])

        return project, messages
    # If this is a directory, then we expect a Mir Commander project
    elif os.path.isdir(path):
        config_path = os.path.join(path, ".mircmd", "config.yaml")
        # If config file does not exist in .mircmd
        if not os.path.isfile(config_path):
            msg = "Config file does not exist"
            logger.error(f"{msg}: {config_path}")
            raise exceptions.LoadProject(msg, f"{msg}: {config_path}")
        # or if we are trying to open user config dir
        elif config_path == consts.DIR.CONFIG / "config.yaml":
            msg = "Mir Commander user configuration directory cannot contain project file(s)"
            logger.error(msg)
            raise exceptions.LoadProject(msg)

        config = Config(config_path)
        project_type = config["type"]
        if project_type == "Molecule":
            return Molecule(path, config), []
        else:
            msg = "Invalid project type"
            logger.error(f"{msg}: {project_type}")
            raise exceptions.LoadProject(msg, f"{msg}: {project_type}")
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise exceptions.LoadProject(msg, f"{msg}: {path}")


__all__ = ["import_file", "load_project"]
