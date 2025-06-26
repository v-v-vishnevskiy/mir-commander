from typing import Literal

from pydantic import BaseModel, Field

from .base_config import BaseConfig
from .widgets.docks.config import DocksConfig
from .widgets.settings.config import SettingsConfig
from .widgets.viewers.molecular_structure.config import MolecularStructureViewerConfig


class Toolbars(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class Viewers(BaseModel):
    molecular_structure: MolecularStructureViewerConfig = MolecularStructureViewerConfig()


class Widgets(BaseModel):
    toolbars: Toolbars = Toolbars()
    docks: DocksConfig = DocksConfig()
    viewers: Viewers = Viewers()


class MainWindowConfig(BaseModel):
    state: None | str = None
    pos: None | list[int] = Field(default=None, min_length=2, max_length=2, description="x, y coordinates")
    size: None | list[int] = Field(default=None, min_length=2, max_length=2, description="width, height")
    widgets: Widgets = Widgets()


class AppConfig(BaseConfig):
    language: Literal["system", "en", "ru"] = "system"
    main_window: MainWindowConfig = MainWindowConfig()
    settings: SettingsConfig = SettingsConfig()
