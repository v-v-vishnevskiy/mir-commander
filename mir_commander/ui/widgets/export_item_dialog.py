from pathlib import Path
from typing import Any, cast

from PySide6.QtWidgets import QCheckBox, QDialogButtonBox, QFileDialog, QLineEdit, QWidget

from mir_commander.core.file_manager import file_manager
from mir_commander.core.project_node import ProjectNode
from mir_commander.api.file_exporter import FileExporterPlugin
from mir_commander.ui.utils.widget import (
    CheckBox,
    ComboBox,
    Dialog,
    GridLayout,
    GroupBox,
    HBoxLayout,
    Label,
    PushButton,
    SpinBox,
    VBoxLayout,
)
from mir_commander.utils.text import sanitize_filename


class ExportFileDialog(Dialog):
    def __init__(self, node: ProjectNode, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._node = node
        self._format_settings_widgets: dict[str, QWidget] = {}

        self.setWindowTitle(self.tr("Export: {}").format(node.name))
        self.setFixedWidth(500)

        main_layout = VBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        format_path_layout = GridLayout()

        format_path_layout.addWidget(Label(Label.tr("Format:")), 0, 0)
        self._format_combo_box = ComboBox()
        exporters = sorted(file_manager.get_exporters(node.type), key=lambda x: x.get_name())
        for exporter in exporters:
            self._format_combo_box.addItem(exporter.get_name(), userData=exporter)
        self._set_proper_format()
        self._format_combo_box.currentIndexChanged.connect(self._exporters_combo_box_handler)
        format_path_layout.addWidget(self._format_combo_box, 0, 1, 1, 2)

        format_path_layout.addWidget(Label(Label.tr("Save to:")), 1, 0)
        self._file_name_editbox = QLineEdit()
        self._file_name_editbox.setText(str(Path.cwd() / sanitize_filename(node.name)) + ".log")
        format_path_layout.addWidget(self._file_name_editbox, 1, 1)
        choose_pb = PushButton(PushButton.tr("Browse..."))
        choose_pb.clicked.connect(self._choose_pb_handler)
        format_path_layout.addWidget(choose_pb, 1, 2)

        format_settings_layout = HBoxLayout()
        format_settings_layout.addSpacing(50)
        self._format_settings_group_box = GroupBox(GroupBox.tr("Format settings"))
        self._format_settings_group_box.setVisible(False)
        format_settings_layout.addWidget(self._format_settings_group_box)
        format_settings_layout.addSpacing(50)

        button_box = QDialogButtonBox()
        button_box.addButton(PushButton(PushButton.tr("Export")), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(PushButton(PushButton.tr("Cancel")), QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout.addLayout(format_path_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(format_settings_layout)
        main_layout.addSpacing(10)
        main_layout.addStretch(1)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self._create_functions_by_type = {
            "text": self._create_text_widget,
            "number": self._create_number_widget,
            "list": self._create_list_widget,
            "bool": self._create_bool_widget,
        }

        self._update()

    def _set_proper_format(self):
        if self._node.type != "atomic_coordinates":
            self._format_combo_box.setCurrentIndex(0)
            return

        self._format_combo_box.setCurrentText("XYZ")

    def _get_format_settings(self) -> dict[str, Any]:
        exporter_name = self._format_combo_box.currentData().get_name()
        if exporter_name not in self._format_settings_widgets:
            return {}

        widget_container = self._format_settings_widgets[exporter_name]
        layout = cast(GridLayout, widget_container.layout())
        exporter = cast(FileExporterPlugin, self._format_combo_box.currentData())
        settings: dict[str, Any] = {}

        for i, config in enumerate(exporter.get_settings_config()):
            layout_item = layout.itemAtPosition(i, 1)
            if layout_item is None:
                continue
            widget = layout_item.widget()
            setting_id = config["id"]

            if config["type"] == "text":
                settings[setting_id] = cast(QLineEdit, widget).text()
            elif config["type"] == "number":
                settings[setting_id] = cast(SpinBox, widget).value()
            elif config["type"] == "list":
                combo_widget = cast(ComboBox, widget)
                settings[setting_id] = combo_widget.currentText() if combo_widget.count() > 0 else ""
            elif config["type"] == "bool":
                settings[setting_id] = cast(QCheckBox, widget).isChecked()

        return settings

    def _get_default_value(self, config: dict[str, Any]) -> Any:
        if "default" not in config:
            return None

        default = config["default"]

        if default["type"] == "property":
            property_path = default["value"]
            if property_path == "node.name":
                return self._node.name
            elif property_path == "node.full_name":
                return "/".join(self._node.full_name)
            return None
        elif default["type"] == "literal":
            return default["value"]

        return None

    def _create_text_widget(self, default_value: Any, config: dict[str, Any]) -> QLineEdit:
        widget = QLineEdit()
        if default_value is not None:
            widget.setText(str(default_value))
        return widget

    def _create_number_widget(self, default_value: Any, config: dict[str, Any]) -> SpinBox:
        widget = SpinBox()
        widget.setMinimum(config.get("min", -2147483648))
        widget.setMaximum(config.get("max", 2147483647))
        widget.setSingleStep(config.get("step", 1))
        if default_value is not None:
            widget.setValue(int(default_value))
        return widget

    def _create_list_widget(self, default_value: Any, config: dict[str, Any]) -> ComboBox:
        widget = ComboBox()
        items = config.get("items", [])
        for item in items:
            widget.addItem(str(item))
        if default_value is not None:
            index = widget.findText(str(default_value))
            if index >= 0:
                widget.setCurrentIndex(index)
        return widget

    def _create_bool_widget(self, default_value: Any, config: dict[str, Any]) -> CheckBox:
        widget = CheckBox("")
        if default_value is not None:
            widget.setChecked(bool(default_value))
        return widget

    def _create_format_settings_widget(self, exporter: FileExporterPlugin) -> QWidget:
        container = QWidget()
        layout = GridLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        for i, config in enumerate(exporter.get_settings_config()):
            default_value = self._get_default_value(config)
            widget = self._create_functions_by_type[config["type"]](default_value, config)

            layout.addWidget(Label(config["label"] + ":"), i, 0)
            layout.addWidget(widget, i, 1)

        layout.setColumnStretch(1, 1)

        container.setLayout(layout)
        return container

    def _update(self):
        item_exporter = cast(FileExporterPlugin, self._format_combo_box.currentData())
        text = self._file_name_editbox.text()
        if suffix := Path(text).suffix:
            self._file_name_editbox.setText(text.replace(suffix, "." + item_exporter.get_extensions()[0]))

        if item_exporter.get_settings_config():
            exporter_name = item_exporter.get_name()
            if exporter_name not in self._format_settings_widgets:
                self._format_settings_widgets[exporter_name] = self._create_format_settings_widget(item_exporter)

            # Remove old layout
            old_layout = self._format_settings_group_box.layout()
            if old_layout is not None:
                # Remove all widgets from old layout
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                QWidget().setLayout(old_layout)

            # Create new layout and add widget
            new_layout = GridLayout()
            new_layout.addWidget(self._format_settings_widgets[exporter_name])
            self._format_settings_group_box.setLayout(new_layout)
            self._format_settings_group_box.setVisible(True)
        else:
            self._format_settings_group_box.setVisible(False)

    def get_params(self) -> tuple[Path, str, dict[str, Any]]:
        return (
            Path(self._file_name_editbox.text()),
            self._format_combo_box.currentData().get_name(),
            self._get_format_settings(),
        )

    def _exporters_combo_box_handler(self, index: int):
        self._update()

    def _choose_pb_handler(self):
        file_dialog = QFileDialog(parent=self, directory=self._file_name_editbox.text())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        if file_dialog.exec() == Dialog.DialogCode.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self._file_name_editbox.setText(file_name)
