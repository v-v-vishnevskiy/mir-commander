from mir_commander.api.file_importer import FileImporterDetails, FileImporterPlugin
from mir_commander.api.plugin import Metadata, Plugin

from .src import (
    cclib_importer,
    cfour_importer,
    gaussian_cube_importer,
    mdlmol2000_importer,
    unex_importer,
    xyz_importer,
)


def register_plugins() -> list[Plugin]:
    return [
        FileImporterPlugin(
            id="xyz",
            metadata=Metadata(
                name="XYZ",
                version=(1, 0, 0),
                description="XYZ file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["xyz"], read_function=xyz_importer.read),
        ),
        FileImporterPlugin(
            id="cclib",
            metadata=Metadata(
                name="CCLib",
                version=(1, 0, 1),
                description="CCLib file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["*"], read_function=cclib_importer.read),
        ),
        FileImporterPlugin(
            id="cfour",
            metadata=Metadata(
                name="CFOUR",
                version=(1, 0, 0),
                description="CFOUR file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["log"], read_function=cfour_importer.read),
        ),
        FileImporterPlugin(
            id="gaussian_cube",
            metadata=Metadata(
                name="Gaussian Cube",
                version=(1, 0, 0),
                description="Gaussian Cube file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["cube", "cub"], read_function=gaussian_cube_importer.read),
        ),
        FileImporterPlugin(
            id="mdlmol2000",
            metadata=Metadata(
                name="MDL Mol V2000",
                version=(1, 0, 0),
                description="MDL Mol V2000 file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["mol"], read_function=mdlmol2000_importer.read),
        ),
        FileImporterPlugin(
            id="unex",
            metadata=Metadata(
                name="UNEX",
                version=(1, 0, 0),
                description="UNEX file importer",
                publisher="mircmd",
            ),
            details=FileImporterDetails(extensions=["log"], read_function=unex_importer.read),
        ),
    ]
