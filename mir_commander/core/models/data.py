from mir_commander.base_config import BaseConfig

from .item import Item


class Data(BaseConfig):
    items: list[Item] = []
