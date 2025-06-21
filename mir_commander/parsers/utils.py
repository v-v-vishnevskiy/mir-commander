from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mir_commander.ui.utils.item import Item


@dataclass
class ItemParametrized:
    item: "Item"
    parameters: dict
