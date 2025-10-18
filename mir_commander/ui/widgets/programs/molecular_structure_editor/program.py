from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import Translator


class MolecularStructureEditor(ProgramWindow):
    name = Translator.tr("Molecular Structure Editor")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumSize(150, 150)
        self.resize(150, 150)

        self.update_window_title()

    def update_window_title(self):
        title = self.item.text()
        parent_item = self.item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.setWindowTitle(title)
        self.setWindowIcon(self.item.icon())
