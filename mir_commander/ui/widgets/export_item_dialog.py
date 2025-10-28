from pathlib import Path
from typing import Any, cast

from PySide6.QtWidgets import QDialogButtonBox, QFileDialog, QLineEdit

from mir_commander.core import FileManager
from mir_commander.plugin_system.item_exporter import ItemExporter
from mir_commander.ui.utils.widget import ComboBox, Dialog, GridLayout, Label, PushButton, VBoxLayout
from mir_commander.ui.widgets.docks.project_dock.items import TreeItem
from mir_commander.utils.text import sanitize_filename


class ExportItemDialog(Dialog):
    def __init__(self, item: TreeItem, file_manager: FileManager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._item = item
        self._file_manager = file_manager

        self.setWindowTitle(self.tr("Export: {}").format(item.text()))
        self.setFixedWidth(450)

        main_layout = VBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        layout = GridLayout()

        layout.addWidget(Label(Label.tr("Format:")), 0, 0)
        self._exporters_combo_box = ComboBox()
        exporters = sorted(file_manager.get_item_exporters(), key=lambda x: x.get_name())
        for exporter in exporters:
            self._exporters_combo_box.addItem(exporter.get_name(), userData=exporter)
        self._exporters_combo_box.setCurrentIndex(0)
        self._exporters_combo_box.currentIndexChanged.connect(self._exporters_combo_box_handler)
        layout.addWidget(self._exporters_combo_box, 0, 1, 1, 2)

        layout.addWidget(Label(Label.tr("Save to:")), 1, 0)
        self._file_name_editbox = QLineEdit()
        self._file_name_editbox.setText(str(Path.cwd() / sanitize_filename(item.text())) + ".log")
        layout.addWidget(self._file_name_editbox, 1, 1)
        choose_pb = PushButton(PushButton.tr("Browse..."))
        choose_pb.clicked.connect(self._choose_pb_handler)
        layout.addWidget(choose_pb, 1, 2)

        button_box = QDialogButtonBox()
        button_box.addButton(PushButton(PushButton.tr("Export")), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(PushButton(PushButton.tr("Cancel")), QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout.addLayout(layout)
        main_layout.addStretch(1)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self._update()

    def get_params(self) -> tuple[Path, str, dict[str, Any]]:
        return (
            Path(self._file_name_editbox.text()),
            self._exporters_combo_box.currentData().get_name(),
            {},  # TODO: add format settings
        )

    def _update(self):
        exporter = cast(ItemExporter, self._exporters_combo_box.currentData())
        text = self._file_name_editbox.text()
        if suffix := Path(text).suffix:
            self._file_name_editbox.setText(text.replace(suffix, "." + exporter.get_extensions()[0]))

        # TODO: add format settings

    def _exporters_combo_box_handler(self, index: int):
        self._update()

    def _choose_pb_handler(self):
        file_dialog = QFileDialog(parent=self, directory=self._file_name_editbox.text())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        if file_dialog.exec() == Dialog.DialogCode.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self._file_name_editbox.setText(file_name)
