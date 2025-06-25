from mir_commander.ui.base_config import BaseConfig


class Config(BaseConfig):
    name: str = "Untitled"
    items: dict[str, list[dict[str, str]]] = {}
