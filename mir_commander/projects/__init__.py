import logging
import os

import numpy as np
from cclib.io import ccread

from mir_commander import consts, exceptions
from mir_commander.data_structures import molecule as ds_molecule
from mir_commander.projects.base import Project
from mir_commander.projects.molecule import Molecule
from mir_commander.projects.temporary import Temporary
from mir_commander.utils import item
from mir_commander.utils.config import Config

logger = logging.getLogger(__name__)


def import_file(path: str) -> item.Item:
    # Use here cclib for parsing files
    data = ccread(path)
    if data is None:
        msg = "cclib cannot determine the format of file"
        logger.error(f"{msg}: {path}")
        raise exceptions.LoadFile(msg, f"{msg}: {path}")

    moldata = ds_molecule.Molecule(data.natom, data.atomnos)
    if hasattr(data, "charge"):
        moldata.charge = data.charge
    if hasattr(data, "mult"):
        moldata.multiplicity = data.mult
    molitem = item.Molecule(os.path.split(path)[1], moldata)
    molitem.file_path = path
    acg_item = item.AtomicCoordinatesGroup()
    molitem.appendRow(acg_item)

    # Adding sets of atomic coordinates to the molecule
    cshape = np.shape(data.atomcoords)  # Number of structure sets is in cshape[0]
    for i in range(0, cshape[0]):
        atcoods_data = ds_molecule.AtomicCoordinates(
            moldata.atomic_num, data.atomcoords[i][:, 0], data.atomcoords[i][:, 1], data.atomcoords[i][:, 2]
        )
        acg_item.appendRow(item.AtomicCoordinates("XYZ", atcoods_data))

    return molitem


def load_project(path: str) -> Project:
    path = os.path.normpath(path)

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if os.path.isfile(path):
        project = Temporary(os.path.split(path)[1])
        project_item = import_file(path)
        project.root_item.appendRow(project_item)
        project.mark_item_as_opened(project_item)
        return project
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
            return Molecule(path, config)
        else:
            msg = "Invalid project type"
            logger.error(f"{msg}: {project_type}")
            raise exceptions.LoadProject(msg, f"{msg}: {project_type}")
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise exceptions.LoadProject(msg, f"{msg}: {path}")


__all__ = ["import_file", "load_project"]
