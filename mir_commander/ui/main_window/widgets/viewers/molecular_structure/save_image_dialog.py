import os
import re

from PySide6.QtCore import Slot
from PySide6.QtGui import QImageWriter
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from mir_commander.ui.utils.widget import CheckBox, Dialog, GroupBox, Label, PushButton, SpinBox


class SaveImageDialog(Dialog):
    file_name_sanitize_re = re.compile(r"[^\w _\-]|(\s)(?=\1+)")

    def __init__(self, img_width: int, img_height: int, filename: str, parent: QWidget):
        super().__init__(parent)

        self.img_width = 0
        self.img_height = 0
        self.img_file_path = ""
        self.img_file_name_init = self.sanitize_file_name(filename)
        self.img_width_init = img_width
        self.img_height_init = img_height
        self.img_sratio_init = float(img_width) / float(img_height)
        self._main_window = self.parent().parent().mdiArea().parent()

        self.setWindowTitle(self.tr("Save image"))

        options_group_box = GroupBox(GroupBox.tr("Options"), self)
        options_group_box_layout = QVBoxLayout(options_group_box)
        self.proportional_checkbox = CheckBox(CheckBox.tr("Proportional size"), options_group_box)
        self.proportional_checkbox.setChecked(True)
        options_group_box_layout.addWidget(self.proportional_checkbox)

        options_size_layout = QHBoxLayout()
        options_size_layout.addWidget(Label(Label.tr("Width:"), self))
        self.width_spinbox = SpinBox(options_group_box)
        self.width_spinbox.setSuffix(SpinBox.tr(" pixels"))
        self.width_spinbox.setRange(1, 100000)
        self.width_spinbox.setValue(self.img_width_init)
        self.width_spinbox.valueChanged.connect(self.width_spinbox_handler)
        options_size_layout.addWidget(self.width_spinbox)

        options_size_layout.addWidget(Label(Label.tr("Height:"), self))
        self.height_spinbox = SpinBox(options_group_box)
        self.height_spinbox.setSuffix(SpinBox.tr(" pixels"))
        self.height_spinbox.setRange(1, 100000)
        self.height_spinbox.setValue(self.img_height_init)
        self.height_spinbox.valueChanged.connect(self.height_spinbox_handler)
        options_size_layout.addWidget(self.height_spinbox)
        options_size_layout.addStretch()

        options_group_box_layout.addLayout(options_size_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(options_group_box)
        message = Label(Label.tr("Output file:"))
        self.main_layout.addWidget(message)

        file_path_layout = QHBoxLayout()
        self.file_path_editbox = QLineEdit()
        # Molecule -> QMdiSubWindow -> QMdiArea -> MainWindow -> project.path
        self.initial_file_path = self._main_window.project.path
        self.initial_file_path = os.path.join(self.initial_file_path, self.img_file_name_init + ".png")
        self.file_path_editbox.setText(self.initial_file_path)
        file_path_layout.addWidget(self.file_path_editbox)
        self.file_path_button = PushButton(PushButton.tr("Choose..."))
        self.file_path_button.clicked.connect(self.file_path_button_handler)
        file_path_layout.addWidget(self.file_path_button)
        self.main_layout.addLayout(file_path_layout)

        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept_handler)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)

    def sanitize_file_name(self, filename: str) -> str:
        filename = re.sub(self.file_name_sanitize_re, "", filename)
        filename = filename.strip().replace(" ", "_")
        return filename

    @Slot()
    def width_spinbox_handler(self):
        self.img_width = self.width_spinbox.value()
        if self.proportional_checkbox.isChecked():
            self.height_spinbox.blockSignals(True)
            self.height_spinbox.setValue(int(self.img_width / self.img_sratio_init))
            self.height_spinbox.blockSignals(False)

    @Slot()
    def height_spinbox_handler(self):
        self.img_height = self.height_spinbox.value()
        if self.proportional_checkbox.isChecked():
            self.width_spinbox.blockSignals(True)
            self.width_spinbox.setValue(int(self.img_height * self.img_sratio_init))
            self.width_spinbox.blockSignals(False)

    @Slot()
    def file_path_button_handler(self):
        fileDialog = QFileDialog(self, self.tr("Choose file"), self.initial_file_path)
        fileDialog.setAcceptMode(QFileDialog.AcceptSave)
        fileDialog.setFileMode(QFileDialog.AnyFile)
        fileDialog.setDirectory(self.initial_file_path)
        mime_types = []

        for bf in QImageWriter.supportedMimeTypes():
            mime_types.append(bf.data().decode("utf8"))
        fileDialog.setMimeTypeFilters(mime_types)
        fileDialog.selectMimeTypeFilter("image/png")
        fileDialog.setDefaultSuffix("png")

        if fileDialog.exec() == QDialog.Accepted:
            file_name = fileDialog.selectedFiles()[0]
            self.file_path_editbox.setText(file_name)

    @Slot()
    def accept_handler(self):
        self.img_width = self.width_spinbox.value()
        self.img_height = self.height_spinbox.value()
        self.img_file_path = self.file_path_editbox.text()
        self.accept()
