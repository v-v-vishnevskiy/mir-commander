from pydantic import BaseModel

from .molecular_structure_viewer.config import MolecularStructureViewerConfig


class ProgramsConfig(BaseModel):
    molecular_structure_viewer: MolecularStructureViewerConfig = MolecularStructureViewerConfig()
