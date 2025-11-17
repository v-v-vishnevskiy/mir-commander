from dataclasses import dataclass
from pathlib import Path

from mir_commander.api.plugin import Resource


@dataclass
class PluginResource:
    namespace: str
    base_path: Path
    resources: list[Resource]
