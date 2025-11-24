from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTableView, QVBoxLayout

from mir_commander.core.plugins_registry import PluginItem, plugins_registry

from .base import BasePage


class Plugins(BasePage):
    """The page with plugins information.

    Displays a table with all registered plugins and their metadata.
    """

    def setup_ui(self):
        layout = QVBoxLayout()

        self._table = QTableView()
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

        self._model = QStandardItemModel()
        self._table.setModel(self._model)

        layout.addWidget(self._table)

        return layout

    def setup_data(self):
        self._populate_table()

    def _populate_table(self):
        self._model.clear()

        headers = [
            self.tr("Name"),
            self.tr("Type"),
            self.tr("Version"),
            self.tr("Author"),
            self.tr("Contacts"),
            self.tr("Enabled"),
        ]
        self._model.setHorizontalHeaderLabels([h for h in headers])

        plugins: list[tuple[PluginItem, str]] = []

        for importer in plugins_registry.file_importer.get_all():
            plugins.append((importer, self.tr("File Importer")))

        for exporter in plugins_registry.file_exporter.get_all():
            plugins.append((exporter, self.tr("File Exporter")))

        for program in plugins_registry.program.get_all():
            plugins.append((program, self.tr("Program")))

        for project_node in plugins_registry.project_node.get_all():
            plugins.append((project_node, self.tr("Project Node")))

        for resources in plugins_registry.resources.get_all():
            plugins.append((resources, self.tr("Resources")))

        for item, plugin_type in plugins:
            plugin = item.plugin

            metadata = plugin.metadata

            name_item = QStandardItem(metadata.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            type_item = QStandardItem(plugin_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            version = ".".join(map(str, metadata.version))
            version_item = QStandardItem(version)
            version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            author_item = QStandardItem(metadata.author)
            author_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            contacts_item = QStandardItem(metadata.contacts)
            contacts_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            enabled_item = QStandardItem(self.tr("Yes") if item.enabled else self.tr("No"))
            enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self._model.appendRow([name_item, type_item, version_item, author_item, contacts_item, enabled_item])

        self._table.resizeColumnsToContents()
