from typing import Any, Callable, Literal

from pydantic import BaseModel, Field

from mir_commander.utils.config import BaseConfig

from .docks.config import DocksConfig
from .settings.config import SettingsConfig


class Toolbars(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class Widgets(BaseModel):
    toolbars: Toolbars = Toolbars()
    docks: DocksConfig = DocksConfig()


class MenuFileHotkeys(BaseModel):
    import_file: str = "Ctrl+I"


class HotkeysConfig(BaseModel):
    menu_file: MenuFileHotkeys = MenuFileHotkeys()


class ProjectWindowConfig(BaseModel):
    state: None | str = None
    pos: None | list[int] = Field(default=None, min_length=2, max_length=2, description="x, y coordinates")
    size: None | list[int] = Field(default=None, min_length=2, max_length=2, description="width, height")
    hotkeys: HotkeysConfig = HotkeysConfig()
    widgets: Widgets = Widgets()


class ImportFilesConfig(BaseModel):
    open_nodes_in_temporary_project: bool = True
    open_nodes_in_current_project: bool = False
    programs: list[str] = Field(
        default_factory=list,
        description="List of programs to open the node with."
        "If empty, the node will be opened with the default program.",
    )


class AppConfig(BaseConfig):
    language: Literal["system", "en", "ru"] = "system"
    project_window: ProjectWindowConfig = ProjectWindowConfig()
    settings: SettingsConfig = SettingsConfig()
    import_files: ImportFilesConfig = ImportFilesConfig()


class ApplyCallbacks(BaseModel):
    functions: list[Callable[[], Any]] = Field(
        default_factory=list, description="List of functions to call when applying config changes"
    )

    def add(self, fn: Callable[[], Any]):
        """Add a function to the list of apply callbacks."""
        self.functions.append(fn)

    def run(self):
        """Run all registered apply callbacks."""
        for fn in self.functions:
            fn()
