import pprint
from pathlib import Path

import cclib
import numpy as np
from cclib.io import ccread

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.data_structures.molecule import Molecule
from mir_commander.api.file_importer import ImportFileError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1 as Node

from .utils import BaseImporter


class CCLibImporter(BaseImporter):
    def get_name(self) -> str:
        return "CCLib"

    def get_extensions(self) -> list[str]:
        return ["*"]

    def read(self, path: Path, logs: list[str]) -> Node:
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
        data = ccread(str(path), **kwargs)
        if data is None:
            raise ImportFileError(f"cclib cannot determine the format of file: {path}")

        if hasattr(data, "metadata"):
            logs.append(pprint.pformat(data.metadata, compact=True))

        molecule = Molecule(n_atoms=data.natom, atomic_num=data.atomnos)
        result = Node(name=path.name, type="molecule", data=molecule)

        if hasattr(data, "charge"):
            molecule.charge = data.charge
        if hasattr(data, "mult"):
            molecule.multiplicity = data.mult

        # If we have coordinates of atoms.
        # This is actually expected to be always true
        if hasattr(data, "atomcoords"):
            cshape = np.shape(data.atomcoords)  # Number of structure sets is in cshape[0]

            if hasattr(data, "optdone"):
                # optdone is here a list due to the experimental feature in cclib turned on by the future option above
                # Take here the first converged structure
                if len(data.optdone) > 0:
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
            at_coord_item = Node(
                name=xyz_title,
                type="atomic_coordinates",
                data=AtomicCoordinates(
                    atomic_num=molecule.atomic_num[:],
                    x=data.atomcoords[xyz_idx][:, 0],
                    y=data.atomcoords[xyz_idx][:, 1],
                    z=data.atomcoords[xyz_idx][:, 2],
                ),
                auto_open=True,
            )
            result.nodes.append(at_coord_item)

            # If we have multiple sets of coordinates
            if cshape[0] > 1:
                # If this was an optimization
                if hasattr(data, "optstatus"):
                    optcg_item = Node(name="Optimization", type="atomic_coordinates_group")
                    result.nodes.append(optcg_item)
                    # Adding sets of atomic coordinates to the group
                    for i in range(0, cshape[0]):
                        csname = f"Step {i + 1}"
                        if data.optstatus[i] & data.OPT_NEW:
                            csname += ", new"
                        if data.optstatus[i] & data.OPT_DONE:
                            csname += ", done"
                        if data.optstatus[i] & data.OPT_UNCONVERGED:
                            csname += ", unconverged"
                        optcg_item.nodes.append(
                            Node(
                                name=csname,
                                type="atomic_coordinates",
                                data=AtomicCoordinates(
                                    atomic_num=molecule.atomic_num[:],
                                    x=data.atomcoords[i][:, 0],
                                    y=data.atomcoords[i][:, 1],
                                    z=data.atomcoords[i][:, 2],
                                ),
                            )
                        )
                # Otherwise this is an undefined set of coordinates
                else:
                    molcg_item = Node(name="Coordinates", type="atomic_coordinates_group")
                    result.nodes.append(molcg_item)
                    # Adding sets of atomic coordinates to the group
                    for i in range(0, cshape[0]):
                        molcg_item.nodes.append(
                            Node(
                                name="Set {}".format(i + 1),
                                type="atomic_coordinates",
                                data=AtomicCoordinates(
                                    atomic_num=molecule.atomic_num[:],
                                    x=data.atomcoords[i][:, 0],
                                    y=data.atomcoords[i][:, 1],
                                    z=data.atomcoords[i][:, 2],
                                ),
                            )
                        )

        # If there was an energy scan along some geometrical parameter(s)
        if hasattr(data, "scancoords"):
            cshape = np.shape(data.scancoords)  # Number of structure sets is in cshape[0]
            if cshape[0] > 0:
                scancg_item = Node(name="Scan", type="atomic_coordinates_group")
                result.nodes.append(scancg_item)
                # Adding sets of atomic coordinates to the group
                for i in range(0, cshape[0]):
                    scancg_item.nodes.append(
                        Node(
                            name="Step {}".format(i + 1),
                            type="atomic_coordinates",
                            data=AtomicCoordinates(
                                atomic_num=molecule.atomic_num[:],
                                x=data.scancoords[i][:, 0],
                                y=data.scancoords[i][:, 1],
                                z=data.scancoords[i][:, 2],
                            ),
                        )
                    )

        return result
