from pathlib import Path
from typing import cast

from PySide6.QtWidgets import QCheckBox, QDialogButtonBox, QFileDialog, QLineEdit

from mir_commander.core import FileManager
from mir_commander.plugin_system.file_exporter import FileExporter
from mir_commander.ui.utils.widget import ComboBox, Dialog, GridLayout, Label, PushButton
from mir_commander.ui.widgets.docks.project_dock.items import TreeItem
from mir_commander.utils.text import sanitize_filename


class ExportItemDialog(Dialog):
    def __init__(self, item: TreeItem, file_manager: FileManager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._item = item
        self._file_manager = file_manager

        self.setWindowTitle(self.tr("Export"))

        layout = GridLayout()

        layout.addWidget(Label(Label.tr("File format:")), 0, 0)
        self._exporters_combo_box = ComboBox()
        exporters = sorted(file_manager.get_file_exporters(), key=lambda x: x[1].get_name())
        for e_id, exporter in exporters:
            self._exporters_combo_box.addItem(exporter.get_name(), userData=(e_id, exporter))
        self._exporters_combo_box.setCurrentIndex(0)
        self._exporters_combo_box.currentIndexChanged.connect(self._exporters_combo_box_handler)
        layout.addWidget(self._exporters_combo_box, 0, 1, 1, 2)

        self._export_nested_label = Label(Label.tr("Export nested:"))
        self._export_nested_checkbox = QCheckBox()
        self._export_nested_checkbox.setChecked(False)

        layout.addWidget(self._export_nested_label, 1, 0)
        layout.addWidget(self._export_nested_checkbox, 1, 1, 1, 2)

        layout.addWidget(Label(Label.tr("Output file:")), 2, 0)
        self._file_name_editbox = QLineEdit()
        self._file_name_editbox.setText(str(Path.cwd() / sanitize_filename(item.text())) + ".log")
        layout.addWidget(self._file_name_editbox, 2, 1)
        choose_pb = PushButton(PushButton.tr("Choose..."))
        choose_pb.clicked.connect(self._choose_pb_handler)
        layout.addWidget(choose_pb, 2, 2)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(buttonBox, 3, 1, 1, 2)
        self.setLayout(layout)

        self._update()

    def get_params(self) -> tuple[Path, bool, str]:
        return (
            Path(self._file_name_editbox.text()),
            self._export_nested_checkbox.isChecked(),
            self._exporters_combo_box.currentData()[0],
        )

    def _update(self):
        ext = cast(FileExporter, self._exporters_combo_box.currentData()[1])
        text = self._file_name_editbox.text()
        if suffix := Path(text).suffix:
            self._file_name_editbox.setText(text.replace(suffix, "." + ext.get_extensions()[0]))

        if ext.can_export_nested():
            self._export_nested_label.setEnabled(True)
            self._export_nested_checkbox.setEnabled(True)
        else:
            self._export_nested_label.setEnabled(False)
            self._export_nested_checkbox.setEnabled(False)

    def _exporters_combo_box_handler(self, index: int):
        self._update()

    def _choose_pb_handler(self):
        file_dialog = QFileDialog(self, self.tr("Choose file"), self._file_name_editbox.text())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        if file_dialog.exec() == Dialog.DialogCode.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self._file_name_editbox.setText(file_name)
