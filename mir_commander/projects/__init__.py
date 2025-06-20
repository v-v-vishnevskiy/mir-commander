import logging
import pprint
import re
from collections import defaultdict
from enum import Enum
from pathlib import Path

import cclib
import numpy as np
from cclib.io import ccread
from periodictable import elements

from mir_commander import consts, exceptions
from mir_commander.data_structures import molecule as ds_molecule
from mir_commander.data_structures import unex
from mir_commander.projects.base import ItemParametrized, Project
from mir_commander.projects.molecule import Molecule
from mir_commander.projects.temporary import Temporary
from mir_commander.ui.utils import item
from mir_commander.utils.config import Config

logger = logging.getLogger(__name__)


class FileFormat(Enum):
    UNKNOWN = 0
    UNEX = 1
    XYZ = 2
    CFOUR = 3
    MDLMOL2000 = 4


class XyzParserState(Enum):
    INIT = 0
    COMMENT = 1
    CARDS = 2


class MDLMolV2000ParserState(Enum):
    INIT = 0
    CONTROL = 1
    ATOM = 2
    BOND = 3


def import_file_mdlmol2000(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from MDL Mol V2000 file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []

    messages.append("MDL Molfile V2000.")

    moldata = ds_molecule.Molecule()
    molitem = item.Molecule(path.parts[1], moldata)
    molitem.file_path = path

    title = ""

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    state = MDLMolV2000ParserState.INIT
    at_coord_item = None
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if state == MDLMolV2000ParserState.INIT:
                if len(title) == 0:
                    title = line.strip()
                if line_number == 2:
                    state = MDLMolV2000ParserState.CONTROL
            elif state == MDLMolV2000ParserState.CONTROL:
                line_items = line.strip().split()

                try:
                    num_atoms = int(line_items[0])
                except ValueError:
                    raise exceptions.LoadFile(f"Invalid control line {line_number + 1}, expected number of atoms.")

                try:
                    num_bonds = int(line_items[1])
                except ValueError:
                    raise exceptions.LoadFile(f"Invalid control line {line_number + 1}, expected number of bonds.")

                if num_atoms <= 0:
                    raise ValueError(f"Invalid number of atoms {num_atoms} defined in line {line_number+1}.")

                if num_bonds < 0:
                    raise ValueError(f"Invalid number of bonds {num_atoms} defined in line {line_number+1}.")

                num_read_at_cards = 0
                atom_atomic_num = []
                atom_coord_x = []
                atom_coord_y = []
                atom_coord_z = []
                state = MDLMolV2000ParserState.ATOM
            elif state == MDLMolV2000ParserState.ATOM:
                line_items = line.strip().split()

                try:
                    coord_x = float(line_items[0])
                    coord_y = float(line_items[1])
                    coord_z = float(line_items[2])
                except ValueError:
                    # Something is wrong with format
                    logger.info(f"Invalid atom coordinate value(s) at line {line_number + 1}.")
                    raise

                try:
                    # Convert here atomic symbol to atomic number
                    if line_items[3] == "X":
                        atomic_num = -1
                    elif line_items[3] == "Q":
                        atomic_num = -2
                    else:
                        atomic_num = elements.symbol(line_items[3]).number
                except ValueError:
                    logger.info(f"Invalid atom symbol at line {line_number + 1}.")
                    raise

                num_read_at_cards += 1
                atom_atomic_num.append(atomic_num)
                atom_coord_x.append(coord_x)
                atom_coord_y.append(coord_y)
                atom_coord_z.append(coord_z)

                if num_read_at_cards == num_atoms:
                    # Add the set of Cartesian coordinates directly to the molecule
                    at_coord_data = ds_molecule.AtomicCoordinates(
                        np.array(atom_atomic_num, dtype="int16"),
                        np.array(atom_coord_x, dtype="float64"),
                        np.array(atom_coord_y, dtype="float64"),
                        np.array(atom_coord_z, dtype="float64"),
                    )
                    if len(title) == 0:
                        title = path.name
                    at_coord_item = item.AtomicCoordinates(title, at_coord_data)
                    molitem.appendRow(at_coord_item)

                    state = MDLMolV2000ParserState.BOND
            elif state == MDLMolV2000ParserState.BOND:
                # TODO: read here explicit bonds, but the viewer must be reimplemented,
                # so that the bonds are not necessarily autogenerated.
                break

    # Autoview last set of coordinates
    if at_coord_item:
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})

    return molitem, flagged_items, messages


def import_file_xyz(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from XYZ file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []

    messages.append("XYZ format.")

    moldata = ds_molecule.Molecule()
    molitem = item.Molecule(path.parts[-1], moldata)
    molitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    state = XyzParserState.INIT
    at_coord_item = None
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if state == XyzParserState.INIT:
                if len(line.strip()) == 0:
                    # Silently exit the cycle early if empty line is found where number of atoms can be expected.
                    # This may happen, for example, in case of empty line after the last set of Cartesian coordinates.
                    break
                try:
                    num_atoms = int(line.strip())
                except ValueError:
                    logger.info(f"Invalid line {line_number+1}, expected number of atoms.")
                    raise
                if num_atoms <= 0:
                    raise ValueError(f"Invalid number of atoms {num_atoms} at line {line_number+1}.")
                state = XyzParserState.COMMENT
            elif state == XyzParserState.COMMENT:
                title = line.strip()
                if len(title) == 0:
                    title = f"Set@line={line_number}"
                state = XyzParserState.CARDS
                num_read_cards = 0
                atom_atomic_num = []
                atom_coord_x = []
                atom_coord_y = []
                atom_coord_z = []
            elif state == XyzParserState.CARDS:
                line_items = line.strip().split()
                try:
                    atomic_num = int(line_items[0])
                except ValueError:
                    try:
                        # Convert here atomic symbol to atomic number
                        if line_items[0] == "X":
                            atomic_num = -1
                        elif line_items[0] == "Q":
                            atomic_num = -2
                        else:
                            atomic_num = elements.symbol(line_items[0]).number
                    except ValueError:
                        logger.info(f"Invalid atom at line {line_number + 1}.")
                        raise
                try:
                    coord_x = float(line_items[1])
                    coord_y = float(line_items[2])
                    coord_z = float(line_items[3])
                except ValueError:
                    # Something is wrong with format
                    logger.info(f"Invalid coordinate value(s) at line {line_number + 1}.")
                    raise

                num_read_cards += 1
                atom_atomic_num.append(atomic_num)
                atom_coord_x.append(coord_x)
                atom_coord_y.append(coord_y)
                atom_coord_z.append(coord_z)

                if num_read_cards == num_atoms:
                    # Add the set of Cartesian coordinates directly to the molecule
                    at_coord_data = ds_molecule.AtomicCoordinates(
                        np.array(atom_atomic_num, dtype="int16"),
                        np.array(atom_coord_x, dtype="float64"),
                        np.array(atom_coord_y, dtype="float64"),
                        np.array(atom_coord_z, dtype="float64"),
                    )
                    at_coord_item = item.AtomicCoordinates(title, at_coord_data)
                    molitem.appendRow(at_coord_item)

                    state = XyzParserState.INIT

    # Autoview last set of coordinates
    if at_coord_item:
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})

    return molitem, flagged_items, messages


def import_file_unex(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from UNEX file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []
    mol_items: dict[str, item.Molecule] = {}  # name: item
    mol_cart_item_last: dict[str, item.AtomicCoordinates] = {}  # name of molecule: last item of Cartesian coordinates
    mol_cart_set_number: dict[str, int] = defaultdict(int)  # name: number of sets of Cartesian coordinates

    project_data = unex.Project()
    rootitem = item.UnexProject(path.parts[1], project_data)
    rootitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(rootitem, {}), "expand": True})

    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                messages.append(line.strip())  # First string is the UNEX version.
            if "> Cartesian coordinates of all atoms (Angstroms) in" in line:
                molname = line.split(">")[0]
                if molname in mol_items:
                    current_mol_item = mol_items[molname]
                else:
                    current_mol_ds = unex.Molecule()
                    current_mol_item = item.Molecule(molname, current_mol_ds)
                    mol_items[molname] = current_mol_item
                    rootitem.appendRow(current_mol_item)

                mol_cart_set_number[molname] += 1

                # Skip header of the table (3 lines)
                for block_line_number, block_line in enumerate(input_file):
                    if block_line_number > 1:
                        break

                # Read the table
                atomic_num = []
                at_coord_x = []
                at_coord_y = []
                at_coord_z = []
                for block_line in input_file:
                    if "--" in block_line:
                        break
                    line_items = block_line.split()
                    atomic_num.append(int(line_items[2]))
                    at_coord_x.append(float(line_items[4]))
                    at_coord_y.append(float(line_items[5]))
                    at_coord_z.append(float(line_items[6]))

                # Add the set of Cartesian coordinates directly to the molecule
                at_coord_data = ds_molecule.AtomicCoordinates(
                    np.array(atomic_num, dtype="int16"),
                    np.array(at_coord_x, dtype="float64"),
                    np.array(at_coord_y, dtype="float64"),
                    np.array(at_coord_z, dtype="float64"),
                )
                at_coord_item = item.AtomicCoordinates(f"Set#{mol_cart_set_number[molname]}", at_coord_data)
                current_mol_item.appendRow(at_coord_item)
                mol_cart_item_last[molname] = at_coord_item

    # Set flags to items
    prm = {}
    if len(mol_cart_item_last) == 1:
        prm = {"maximize": True}

    # Autoview last sets of coordinates of each molecule
    for at_coord_item in mol_cart_item_last.values():
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, prm), "view": True})

    return rootitem, flagged_items, messages


def import_file_cfour(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from Cfour log file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []

    messages.append("Cfour format.")

    moldata = ds_molecule.Molecule()
    molitem = item.Molecule(path.parts[1], moldata)
    molitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    cart_set_number = 0

    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if "Z-matrix   Atomic            Coordinates (in bohr)" in line:
                cart_set_number += 1
                # Skip header of the table (2 lines)
                for block_line_number, block_line in enumerate(input_file):
                    if block_line_number > 0:
                        break

                # Read the table
                atomic_num = []
                at_coord_x = []
                at_coord_y = []
                at_coord_z = []
                for block_line in input_file:
                    if "--" in block_line:
                        break
                    line_items = block_line.split()
                    if line_items[1] == "0":
                        atomic_num.append(-1)
                    else:
                        atomic_num.append(int(line_items[1]))
                    at_coord_x.append(float(line_items[2]) * consts.BOHR2ANGSTROM)
                    at_coord_y.append(float(line_items[3]) * consts.BOHR2ANGSTROM)
                    at_coord_z.append(float(line_items[4]) * consts.BOHR2ANGSTROM)

                # Add the set of Cartesian coordinates directly to the molecule
                at_coord_data = ds_molecule.AtomicCoordinates(
                    np.array(atomic_num, dtype="int16"),
                    np.array(at_coord_x, dtype="float64"),
                    np.array(at_coord_y, dtype="float64"),
                    np.array(at_coord_z, dtype="float64"),
                )
                at_coord_item = item.AtomicCoordinates(f"Set#{cart_set_number}", at_coord_data)
                molitem.appendRow(at_coord_item)

    # Autoview last set of coordinates
    if at_coord_item:
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})

    return molitem, flagged_items, messages


def import_file_cclib(path: Path) -> tuple[item.Item, list[dict], list[str]]:
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
        at_coord_data = ds_molecule.AtomicCoordinates(
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


def import_file(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from file,
    return tree of items, list of flagged items and list of messages
    """
    unexver_validator = re.compile(r"^([0-9]+).([0-9]+)-([0-9]+)-([a-z0-9]+)$")  # For example 1.7-33-g5a83887
    int_validator = re.compile(r"^[1-9][0-9]*$")  # For example 15
    xyzcard_validator = re.compile(
        r"^([A-Z][a-z]?|[0-9]+)([\s]+[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?){3}$"
    )  # For example Ca 1.0 -2.0 +0.1e-01
    xyzcard_validated = 0

    # Guess format on the basis of the input file extension
    if path.suffix == ".xyz":
        file_format = FileFormat.XYZ
    elif path.suffix == ".mol" or path.suffix == ".sdf" or path.suffix == ".mdl" or path.suffix == ".sd":
        file_format = FileFormat.MDLMOL2000
    else:
        file_format = FileFormat.UNKNOWN

    line_number_limit = 10
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                if file_format == FileFormat.XYZ:
                    if numat_match := int_validator.match(line.strip()):
                        numat = int(numat_match.group(0))
                    else:
                        msg = "Invalid first string in XYZ file"
                        raise exceptions.LoadFile(msg, f"line={line}")
                else:
                    if "UNEX" in line and unexver_validator.match(line.split()[1]):
                        file_format = FileFormat.UNEX
                        break
            else:
                if file_format == FileFormat.XYZ:
                    if line_number == 1:
                        # in XYZ format second line is comment, it may be anything, even empty
                        pass
                    else:
                        if xyzcard_validator.match(line.strip()):
                            xyzcard_validated += 1
                            if xyzcard_validated == numat:
                                # All cards validated, accept here XYZ format
                                break
                            else:
                                # Call continue explicitly,
                                # otherwise we can hit the limit on the number of checked lines
                                continue
                        else:
                            msg = "Invalid atom string in XYZ file"
                            raise exceptions.LoadFile(msg, f"line={line}")
                elif file_format == FileFormat.MDLMOL2000:
                    if line_number == 3:
                        if " V2000" in line:
                            # Accept file format
                            break
                        else:
                            msg = "Invalid control string in MDLMOL2000 file"
                            raise exceptions.LoadFile(msg, f"line={line}")
                else:
                    if "<<<     CCCCCC     CCCCCC   |||     CCCCCC     CCCCCC   >>>" in line:
                        file_format = FileFormat.CFOUR
                        break

            if line_number > line_number_limit:  # line_number starts at 0.
                break

    if file_format == FileFormat.UNEX:
        project_root_item, flagged_items, messages = import_file_unex(path)
    elif file_format == FileFormat.XYZ:
        project_root_item, flagged_items, messages = import_file_xyz(path)
    elif file_format == FileFormat.CFOUR:
        project_root_item, flagged_items, messages = import_file_cfour(path)
    elif file_format == FileFormat.MDLMOL2000:
        project_root_item, flagged_items, messages = import_file_mdlmol2000(path)
    else:
        project_root_item, flagged_items, messages = import_file_cclib(path)

    return project_root_item, flagged_items, messages


def load_project(path: Path) -> tuple[Project, list[str]]:
    """
    Returns (re)created project and a list of messages corresponding to the process of project loading.
    """

    path = path.resolve()

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if path.is_file():
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
    elif path.is_dir():
        config_path = path / ".mircmd" / "config.yaml"
        # If config file does not exist in .mircmd
        if not config_path.is_file():
            msg = "Config file does not exist"
            logger.error(f"{msg}: {config_path}")
            raise exceptions.LoadProject(msg, f"{msg}: {config_path}")
        # or if we are trying to open user config dir
        elif config_path == consts.DIR.HOME_CONFIG / "config.yaml":
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
