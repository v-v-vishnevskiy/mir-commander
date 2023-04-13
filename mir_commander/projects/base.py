from mir_commander.utils.items_model import ItemsModel


class Project:
    """The most basic class of projects."""

    def __init__(self, title: str):
        self.items = ItemsModel(title)
