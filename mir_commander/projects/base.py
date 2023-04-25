from mir_commander.utils.item import Item


class Project:
    """The most basic class of projects."""

    def __init__(self):
        self.root_item = Item("root")
