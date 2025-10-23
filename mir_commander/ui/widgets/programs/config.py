from pydantic import BaseModel

from .molecular_visualizer.config import MolecularVisualizerConfig


class ProgramsConfig(BaseModel):
    molecular_visualizer: MolecularVisualizerConfig = MolecularVisualizerConfig()
