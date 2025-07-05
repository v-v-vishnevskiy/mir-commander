from pydantic import BaseModel

from .base import BaseViewer
from .molecular_structure import MolecularStructureViewer, MolecularStructureViewerConfig


class ViewersConfig(BaseModel):
    molecular_structure: MolecularStructureViewerConfig = MolecularStructureViewerConfig()

    def get_viewer_config(self, viewer_cls: type[BaseViewer]) -> BaseModel:
        if viewer_cls is MolecularStructureViewer:
            return self.molecular_structure
        raise RuntimeError(f"Unknown viewer: {viewer_cls}")
