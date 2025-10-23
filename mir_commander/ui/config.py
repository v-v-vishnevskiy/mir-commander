from typing import Any, Callable, Literal

from pydantic import BaseModel, Field

from mir_commander.utils.config import BaseConfig

from .widgets.docks.config import DocksConfig
from .widgets.programs.config import ProgramsConfig
from .widgets.settings.config import SettingsConfig


class Toolbars(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class Widgets(BaseModel):
    toolbars: Toolbars = Toolbars()
    docks: DocksConfig = DocksConfig()
    programs: ProgramsConfig = ProgramsConfig()


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


class OpenGLConfig(BaseModel):
    antialiasing: bool = True


class AppConfig(BaseConfig):
    language: Literal["system", "en", "ru"] = "system"
    opengl: OpenGLConfig = OpenGLConfig()
    project_window: ProjectWindowConfig = ProjectWindowConfig()
    settings: SettingsConfig = SettingsConfig()


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
