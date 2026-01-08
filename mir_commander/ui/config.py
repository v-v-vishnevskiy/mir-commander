from datetime import datetime, timedelta
from typing import Any, Callable, Literal

from pydantic import Field, field_validator

from mir_commander.core.config import BaseConfig, BaseModel

from .docks.config import DocksConfig
from .settings.config import SettingsConfig


class FontConfig(BaseModel):
    family: Literal["system", "inter"] = Field(default="inter", description="Font family")
    size: int = Field(default=13, ge=8, le=72, description="Font size in pixels to use for internal font")


class Toolbars(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class Widgets(BaseModel):
    toolbars: Toolbars = Toolbars()
    docks: DocksConfig = DocksConfig()


class MenuFileHotkeys(BaseModel):
    import_file: str = "Ctrl+I"


class HotkeysConfig(BaseModel):
    menu_file: MenuFileHotkeys = MenuFileHotkeys()


class ControlPanelState(BaseModel):
    visible: bool = True


class ProjectWindowConfig(BaseModel):
    state: None | str = None
    window_state: int = 0
    pos: None | list[int] = Field(default=None, min_length=2, max_length=2, description="x, y coordinates")
    size: None | list[int] = Field(default=None, min_length=2, max_length=2, description="width, height")
    hotkeys: HotkeysConfig = HotkeysConfig()
    widgets: Widgets = Widgets()
    control_panels: dict[str, ControlPanelState] = Field(default_factory=dict, description="Control panel states")

    @field_validator("pos", "size", mode="before")
    @classmethod
    def pos_size(cls, value: list[int]) -> list[int]:
        for i, item in enumerate(value):
            value[i] = max(0, item)
        return value


class NodeTypeImportConfig(BaseModel):
    """Configuration for importing a specific node type."""

    open_nodes_on_startup: bool = True
    open_nodes_on_import: bool = False
    programs_ids: list[str] = Field(
        default_factory=list,
        description="List of program ids to open the node with. If empty list, will open with the default program.",
    )


class ImportFileRulesConfig(NodeTypeImportConfig):
    node_types: dict[str, NodeTypeImportConfig] = Field(
        default_factory=dict,
        description="Per-node-type import configuration. "
        "Keys are node type identifiers (e.g., 'atomic_coordinates', 'molecule'). ",
    )

    def get_open_on_startup(self, node_type: str) -> bool:
        """Get open_nodes_in_temporary_project setting for a specific node type."""
        if node_type in self.node_types:
            return self.node_types[node_type].open_nodes_on_startup
        return self.open_nodes_on_startup

    def get_open_on_import(self, node_type: str) -> bool:
        """Get open_nodes_in_current_project setting for a specific node type."""
        if node_type in self.node_types:
            return self.node_types[node_type].open_nodes_on_import
        return self.open_nodes_on_import

    def get_programs(self, node_type: str) -> list[str]:
        """Get programs list for a specific node type."""
        if node_type in self.node_types:
            return self.node_types[node_type].programs_ids
        return self.programs_ids


class UpdatesConfig(BaseModel):
    check_in_background: bool = Field(default=True, description="Check for updates in the background")
    skip_version: str = Field(default="", description="Version to skip")
    interval: int = Field(
        default=4, ge=1, le=24, description="Interval in hours to check for updates in the background"
    )
    last_check: datetime = Field(default=datetime.now() - timedelta(hours=4), description="Last check for updates")

    @field_validator("last_check", mode="before")
    @classmethod
    def last_check_parser(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


class AppConfig(BaseConfig):
    font: FontConfig = FontConfig()
    language: Literal["system", "en", "ru"] = "system"
    project_window: ProjectWindowConfig = ProjectWindowConfig()
    settings: SettingsConfig = SettingsConfig()
    import_file_rules: ImportFileRulesConfig = ImportFileRulesConfig()
    updates: UpdatesConfig = UpdatesConfig()


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
