import logging
from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mir_commander.api.file_exporter import (
    BoolParam,
    FileExporterPlugin,
    FormatParamsConfig,
    ListParam,
    NumberParam,
    TextParam,
)
from mir_commander.core.file_manager import FileManager
from mir_commander.core.plugins_registry import PluginItem
from mir_commander.core.project_node import ProjectNode
from mir_commander.core.utils import sanitize_filename

logger = logging.getLogger("UI.ExportFileDialog")


class ExportFileDialog(QDialog):
    def __init__(self, node: ProjectNode, file_manager: FileManager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._node = node
        self._format_params_widgets: dict[str, QWidget] = {}
        self._file_manager = file_manager

        self.setWindowTitle(self.tr("Export: {}").format(node.name))
        self.setFixedWidth(500)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        format_path_layout = QGridLayout()

        format_path_layout.addWidget(QLabel(self.tr("Format:")), 0, 0)
        self._format_combo_box = QComboBox()
        exporters = sorted(self._file_manager.get_exporters(node.type), key=lambda x: x.plugin.metadata.name)
        for exporter in exporters:
            self._format_combo_box.addItem(exporter.plugin.metadata.name, userData=exporter)
        self._set_proper_format()
        self._format_combo_box.currentIndexChanged.connect(self._exporters_combo_box_handler)
        format_path_layout.addWidget(self._format_combo_box, 0, 1, 1, 2)

        format_path_layout.addWidget(QLabel(self.tr("Save to:")), 1, 0)
        self._file_name_editbox = QLineEdit()
        self._file_name_editbox.setText(str(Path.cwd() / sanitize_filename(node.name)) + ".log")
        format_path_layout.addWidget(self._file_name_editbox, 1, 1)
        choose_pb = QPushButton(self.tr("Browse..."))
        choose_pb.clicked.connect(self._choose_pb_handler)
        format_path_layout.addWidget(choose_pb, 1, 2)

        format_params_layout = QHBoxLayout()
        format_params_layout.addSpacing(50)
        self._format_params_group_box = QGroupBox(self.tr("Format parameters"))
        self._format_params_group_box.setVisible(False)
        format_params_layout.addWidget(self._format_params_group_box)
        format_params_layout.addSpacing(50)

        button_box = QDialogButtonBox()
        button_box.addButton(QPushButton(self.tr("Export")), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(QPushButton(self.tr("Cancel")), QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout.addLayout(format_path_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(format_params_layout)
        main_layout.addSpacing(10)
        main_layout.addStretch(1)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self._update()

    def _set_proper_format(self):
        if self._node.type != "builtin.atomic_coordinates":
            self._format_combo_box.setCurrentIndex(0)
            return

        self._format_combo_box.setCurrentText("XYZ")

    def _get_format_params(self) -> dict[str, Any]:
        exporter = cast(PluginItem[FileExporterPlugin], self._format_combo_box.currentData())
        if exporter.id not in self._format_params_widgets:
            return {}

        widget_container = self._format_params_widgets[exporter.id]
        layout = cast(QGridLayout, widget_container.layout())
        params: dict[str, Any] = {}

        for i, config in enumerate(exporter.plugin.details.format_params_config):
            layout_item = layout.itemAtPosition(i, 1)
            if layout_item is None:
                continue

            if isinstance(config, TextParam):
                params[config.id] = cast(QLineEdit, layout_item.widget()).text()
            elif isinstance(config, NumberParam):
                params[config.id] = cast(QSpinBox, layout_item.widget()).value()
            elif isinstance(config, ListParam):
                combo_widget = cast(QComboBox, layout_item.widget())
                params[config.id] = combo_widget.currentText() if combo_widget.count() > 0 else ""
            elif isinstance(config, BoolParam):
                params[config.id] = cast(QCheckBox, layout_item.widget()).isChecked()

        return params

    def _get_default_value(self, config: FormatParamsConfig) -> Any:
        if config.default.type == "property":
            property_path = config.default.value
            if property_path == "node.name":
                return self._node.name
            elif property_path == "node.full_name":
                return "/".join(self._node.full_name)
            return None
        elif config.default.type == "literal":
            return config.default.value

        return None

    def _create_text_widget(self, default_value: Any) -> QLineEdit:
        widget = QLineEdit()
        if default_value is not None:
            widget.setText(str(default_value))
        return widget

    def _create_number_widget(self, default_value: Any, config: NumberParam) -> QSpinBox:
        widget = QSpinBox()
        widget.setMinimum(config.min)
        widget.setMaximum(config.max)
        widget.setSingleStep(config.step)
        if default_value is not None:
            widget.setValue(int(default_value))
        return widget

    def _create_list_widget(self, default_value: Any, config: ListParam) -> QComboBox:
        widget = QComboBox()
        for item in config.items:
            widget.addItem(item)
        if default_value is not None:
            index = widget.findText(str(default_value))
            if index >= 0:
                widget.setCurrentIndex(index)
        return widget

    def _create_bool_widget(self, default_value: Any) -> QCheckBox:
        widget = QCheckBox("")
        if default_value is not None:
            widget.setChecked(bool(default_value))
        return widget

    def _create_format_params_widget(self, exporter: PluginItem[FileExporterPlugin]) -> QWidget:
        container = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        for i, config in enumerate[FormatParamsConfig](exporter.plugin.details.format_params_config):
            default_value = self._get_default_value(config)
            if isinstance(config, TextParam):
                widget = self._create_text_widget(default_value)
            elif isinstance(config, NumberParam):
                widget = self._create_number_widget(default_value, config)  # type: ignore[assignment]
            elif isinstance(config, ListParam):
                widget = self._create_list_widget(default_value, config)  # type: ignore[assignment]
            elif isinstance(config, BoolParam):
                widget = self._create_bool_widget(default_value)  # type: ignore[assignment]
            else:
                logger.error("Unknown format parameter type: %s", config.type)
                continue

            layout.addWidget(QLabel(QCoreApplication.translate(exporter.id, config.label) + ":"), i, 0)
            layout.addWidget(widget, i, 1)

        layout.setColumnStretch(1, 1)

        container.setLayout(layout)
        return container

    def _update(self):
        exporter = cast(PluginItem[FileExporterPlugin], self._format_combo_box.currentData())
        text = self._file_name_editbox.text()
        if suffix := Path(text).suffix:
            self._file_name_editbox.setText(text.replace(suffix, "." + exporter.plugin.details.extensions[0]))

        if exporter.plugin.details.format_params_config:
            if exporter.id not in self._format_params_widgets:
                self._format_params_widgets[exporter.id] = self._create_format_params_widget(exporter)

            # Remove old layout
            old_layout = self._format_params_group_box.layout()
            if old_layout is not None:
                # Remove all widgets from old layout
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                QWidget().setLayout(old_layout)

            # Create new layout and add widget
            new_layout = QGridLayout()
            new_layout.addWidget(self._format_params_widgets[exporter.id])
            self._format_params_group_box.setLayout(new_layout)
            self._format_params_group_box.setVisible(True)
        else:
            self._format_params_group_box.setVisible(False)

    def get_params(self) -> tuple[Path, str, dict[str, Any]]:
        return (
            Path(self._file_name_editbox.text()),
            cast(PluginItem[FileExporterPlugin], self._format_combo_box.currentData()).id,
            self._get_format_params(),
        )

    def _exporters_combo_box_handler(self, index: int):
        self._update()

    def _choose_pb_handler(self):
        file_dialog = QFileDialog(parent=self, directory=self._file_name_editbox.text())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        if file_dialog.exec() == QDialog.DialogCode.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self._file_name_editbox.setText(file_name)
