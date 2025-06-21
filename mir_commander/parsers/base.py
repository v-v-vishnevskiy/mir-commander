import re
from enum import Enum
from pathlib import Path

from mir_commander import errors
from mir_commander.ui.utils.item import Item

from .cclib_parser import load_cclib
from .cfour_rapser import load_cfour
from .mdlmol2000_parser import load_mdlmol2000
from .unex_parser import load_unex
from .xyz_parser import load_xyz


class FileFormat(Enum):
    UNKNOWN = 0
    UNEX = 1
    XYZ = 2
    CFOUR = 3
    MDLMOL2000 = 4


def load_file(path: Path) -> tuple[Item, list[dict], list[str]]:
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
                        raise errors.LoadFileError(msg, f"line={line}")
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
                            raise errors.LoadFileError(msg, f"line={line}")
                elif file_format == FileFormat.MDLMOL2000:
                    if line_number == 3:
                        if " V2000" in line:
                            # Accept file format
                            break
                        else:
                            msg = "Invalid control string in MDLMOL2000 file"
                            raise errors.LoadFileError(msg, f"line={line}")
                else:
                    if "<<<     CCCCCC     CCCCCC   |||     CCCCCC     CCCCCC   >>>" in line:
                        file_format = FileFormat.CFOUR
                        break

            if line_number > line_number_limit:  # line_number starts at 0.
                break

    if file_format == FileFormat.UNEX:
        project_root_item, flagged_items, messages = load_unex(path)
    elif file_format == FileFormat.XYZ:
        project_root_item, flagged_items, messages = load_xyz(path)
    elif file_format == FileFormat.CFOUR:
        project_root_item, flagged_items, messages = load_cfour(path)
    elif file_format == FileFormat.MDLMOL2000:
        project_root_item, flagged_items, messages = load_mdlmol2000(path)
    else:
        project_root_item, flagged_items, messages = load_cclib(path)

    return project_root_item, flagged_items, messages
