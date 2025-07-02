from pydantic import BaseModel

from .molecular_structure.config import MolecularStructureViewerConfig


class ViewersConfig(BaseModel):
    molecular_structure: MolecularStructureViewerConfig = MolecularStructureViewerConfig()
