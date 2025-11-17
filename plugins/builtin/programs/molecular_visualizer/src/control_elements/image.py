import re
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QImageWriter
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from mir_commander.core.graphics.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.sdk.widget import ColorButton

from ....program import ControlBlock
from .utils import add_slider

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class Image(ControlBlock):
    _file_name_sanitize_re = re.compile(r"[^\w _\-]|(\s)(?=\1+)")

    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        self._width = 500
        self._height = 500

        params_layout = QGridLayout()

        self._scale_slider, self._scale_double_spinbox = add_slider(
            layout=params_layout,
            row=0,
            text=self.tr("Scale factor:"),
            min_value=0.1,
            max_value=20.0,
            single_step=1,
            decimals=1,
            factor=10,
            default_value=1.0,
        )
        self._scale_slider.valueChanged.connect(self._scale_slider_value_changed_handler)
        self._scale_double_spinbox.valueChanged.connect(self._scale_double_spinbox_value_changed_handler)

        self._bg_color_inited = False
        self._bg_color_button = ColorButton(QColor(255, 255, 255, a=0))

        self._crop_to_content_checkbox = QCheckBox()
        self._crop_to_content_checkbox.setChecked(True)

        self._i_param = QSpinBox()
        self._i_param.setRange(1, 100000)
        self._i_param.setValue(1)

        self._file_path = QLineEdit()
        self._file_path.setText(str(Path.cwd() / "%n_%i.png"))
        choose_file_path_button = QPushButton(self.tr("Browse..."))
        choose_file_path_button.clicked.connect(self._choose_file_path_button_clicked_handler)

        save_image_button = QPushButton(self.tr("Save"))
        save_image_button.clicked.connect(self._save_image_button_clicked_handler)

        params_layout.addWidget(QLabel(self.tr("Background color:"), self), 1, 0)
        params_layout.addWidget(self._bg_color_button, 1, 1)
        params_layout.addWidget(QLabel(self.tr("Crop to content:"), self), 2, 0)
        params_layout.addWidget(self._crop_to_content_checkbox, 2, 1)
        params_layout.addWidget(QLabel(self.tr("%i starts from:"), self), 3, 0)
        params_layout.addWidget(self._i_param, 3, 1)
        params_layout.addWidget(self._file_path, 4, 0, 1, 2)
        params_layout.addWidget(choose_file_path_button, 4, 2)

        layout = QVBoxLayout(self)
        layout.addLayout(params_layout)
        layout.addWidget(save_image_button)
        self.setLayout(layout)

    def _scale_slider_value_changed_handler(self, i: int):
        self._scale_double_spinbox.setValue(i / 10)

    def _scale_double_spinbox_value_changed_handler(self, value: float):
        self._scale_slider.setValue(int(value * 10))

    def _choose_file_path_button_clicked_handler(self):
        mime_types = []
        for bf in QImageWriter.supportedMimeTypes():
            data: bytes = bf.data()
            mime_types.append(data.decode("utf8"))

        fileDialog = QFileDialog(self, self.tr("Choose file"), self._file_path.text())
        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        fileDialog.setFileMode(QFileDialog.FileMode.AnyFile)
        fileDialog.setMimeTypeFilters(mime_types)
        fileDialog.selectMimeTypeFilter("image/png")
        fileDialog.setDefaultSuffix("png")

        if fileDialog.exec() == QDialog.DialogCode.Accepted:
            file_name = fileDialog.selectedFiles()[0]
            self._file_path.setText(file_name)

    def _sanitize_filename(self, value: str) -> str:
        value = value.strip().replace(".", "_").replace(" ", "_").replace("/", "_")
        value = re.sub(self._file_name_sanitize_re, "", value)
        return value

    def _save_image_button_clicked_handler(self):
        i_value = self._i_param.value()
        bg_color = qcolor_to_color4f(self._bg_color_button.color)
        crop_to_content = self._crop_to_content_checkbox.isChecked()
        file_path = self._file_path.text()
        scale_factor = self._scale_double_spinbox.value()

        self._control_panel.program_action_signal.emit(
            "image.save",
            {
                "t_filename": file_path,
                "width": int(self._width * scale_factor),
                "height": int(self._height * scale_factor),
                "bg_color": bg_color,
                "crop_to_content": crop_to_content,
                "i_param": i_value,
            },
        )

    def update_values(self, program: "Program"):
        self._width = int(program.visualizer.size().width() * program.visualizer.devicePixelRatio())
        self._height = int(program.visualizer.size().height() * program.visualizer.devicePixelRatio())
        if self._bg_color_inited is False:
            self._bg_color_inited = True
            color = *program.visualizer.background_color[:3], 0.0
            self._bg_color_button.set_color(color4f_to_qcolor(color))
