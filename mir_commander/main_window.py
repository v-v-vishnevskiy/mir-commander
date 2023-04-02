import os

from PySide6.QtCore import QDir, QLocale, QSettings, QTranslator, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow

from mir_commander.widgets import About, Preferences


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        QMainWindow.__init__(self, None)
        self.app = app

        self.setWindowTitle("Mir Commander")
        self.setWindowIcon(QIcon("resources/appicon.svg"))

        self.settings = QSettings(os.path.join(QDir.homePath(), ".mircmd", "config"), QSettings.Format.IniFormat)
        self._restore_settings()
        self._load_translation()

        # Menu Bar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu(self.tr("File"))
        self.help_menu = self.menubar.addMenu(self.tr("Help"))
        self.setup_menubar()

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage(self.tr("Ready"))

    def setup_menubar(self):
        self._setup_menubar_file()
        self._setup_menubar_help()

    def _setup_menubar_file(self):
        self.file_menu.addAction(self._preferences_action())
        self.file_menu.addAction(self._quit_action())

    def _setup_menubar_help(self):
        self.help_menu.addAction(self._about_action())

    def _preferences_action(self) -> QAction:
        action = QAction(self.tr("Preferences..."), self)
        action.setMenuRole(QAction.PreferencesRole)
        action.triggered.connect(Preferences(self, self.settings).show)
        return action

    def _quit_action(self) -> QAction:
        action = QAction(self.tr("Quit"), self)
        action.setMenuRole(QAction.QuitRole)
        action.setShortcut(QKeySequence.Quit)
        action.triggered.connect(self.quit_app)
        return action

    def _about_action(self) -> QAction:
        action = QAction(self.tr("About"), self)
        action.setMenuRole(QAction.AboutRole)
        action.triggered.connect(About(self).show)
        return action

    def _save_settings(self):
        self.settings.setValue("main_window/pos", [self.pos().x(), self.pos().y()])
        self.settings.setValue("main_window/size", [self.size().width(), self.size().height()])

    def _load_translation(self):
        language = self.settings.value("language", "system")
        if language == "system":
            language = QLocale.languageToCode(QLocale.system().language())

        translator = QTranslator(self.app)
        if translator.load(f"../resources/i18n/app_{language}", os.path.dirname(__file__)):
            self.app.installTranslator(translator)

    def _restore_settings(self):
        # Window dimensions
        geometry = self.screen().availableGeometry()
        pos = self.settings.value("main_window/pos", [geometry.width() * 0.125, geometry.height() * 0.125])
        size = self.settings.value("main_window/size", [geometry.width() * 0.75, geometry.height() * 0.75])
        self.setGeometry(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

    @Slot()
    def quit_app(self, *args, **kwargs):
        self._save_settings()
        QApplication.quit()

    def closeEvent(self, *args, **kwargs):
        self._save_settings()
