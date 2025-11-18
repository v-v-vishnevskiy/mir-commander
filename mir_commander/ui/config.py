from typing import Any, Callable, Literal

from pydantic import BaseModel, Field

from mir_commander.core.config import BaseConfig

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


class AppConfig(BaseConfig):
    language: Literal["system", "en", "ru"] = "system"
    project_window: ProjectWindowConfig = ProjectWindowConfig()
    settings: SettingsConfig = SettingsConfig()
    import_file_rules: ImportFileRulesConfig = ImportFileRulesConfig()


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
