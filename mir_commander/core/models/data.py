from mir_commander.utils.config import BaseConfig

from .item import Item


class Data(BaseConfig):
    items: list[Item] = []
