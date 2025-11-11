from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QVBoxLayout

from mir_commander.api.plugin import Plugin
from mir_commander.core import plugins_manager
from mir_commander.ui.sdk.widget import StandardItem, TableView

from .base import BasePage


class Plugins(BasePage):
    """The page with plugins information.

    Displays a table with all registered plugins and their metadata.
    """

    def setup_ui(self):
        layout = QVBoxLayout()

        self._table = TableView()
        self._table.setEditTriggers(TableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)

        self._model = QStandardItemModel()
        self._table.setModel(self._model)

        layout.addWidget(self._table)

        return layout

    def setup_data(self):
        self._populate_table()

    def _populate_table(self):
        self._model.clear()

        headers = [
            StandardItem.tr("Name"),
            StandardItem.tr("Type"),
            StandardItem.tr("Version"),
            StandardItem.tr("Author"),
            StandardItem.tr("Contacts"),
        ]
        self._model.setHorizontalHeaderLabels([h for h in headers])

        plugins: list[tuple[Plugin, str]] = []

        for importer in plugins_manager.file._importers:
            plugins.append((importer, StandardItem.tr("File Importer")))

        for exporter in plugins_manager.file._exporters:
            plugins.append((exporter, StandardItem.tr("File Exporter")))

        for program in plugins_manager.program.programs:
            plugins.append((program, StandardItem.tr("Program")))

        for project_node in plugins_manager.project_node.get_project_nodes().values():
            plugins.append((project_node, StandardItem.tr("Project Node")))

        for plugin, plugin_type in plugins:
            metadata = plugin.get_metadata()

            name_item = StandardItem(metadata.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            type_item = StandardItem(plugin_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            version = ".".join(map(str, metadata.version))
            version_item = StandardItem(version)
            version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            author_item = StandardItem(metadata.author)
            author_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            contacts_item = StandardItem(metadata.contacts)
            contacts_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self._model.appendRow([name_item, type_item, version_item, author_item, contacts_item])

        self._table.resizeColumnsToContents()
