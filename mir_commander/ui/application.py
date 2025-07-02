import logging
from pathlib import Path

from PySide6.QtCore import QLibraryInfo, QLocale, QResource, Qt, QTranslator
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from mir_commander.consts import DIR
from mir_commander.core import load_project
from mir_commander.core.errors import LoadFileError, LoadProjectError

from .recent_projects.config import RecentProjectsConfig
from .recent_projects.recent_projects_dialog import RecentProjectsDialog
from .config import AppConfig, ApplyCallbacks
from .main_window import MainWindow

logger = logging.getLogger("Application")


class Application(QApplication):
    """Application class. In fact, only one instance is created thereof."""

    def __init__(self, *args, **kwargs):
        self.setAttribute(Qt.AA_ShareOpenGLContexts)
        super().__init__(*args, **kwargs)
        self._quitting = False

        self.register_resources()

        self.apply_callbacks = ApplyCallbacks()
        self.config: AppConfig = AppConfig.load(DIR.HOME_CONFIG / "app_config.yaml")
        self.recent_projects_config = RecentProjectsConfig.load(DIR.HOME_CONFIG / "recent_projects.yaml")

        self._open_projects: dict[int, MainWindow] = {}
        self._recent_projects_dialog = RecentProjectsDialog(self)

        self._translator_app = QTranslator(self)
        self._translator_qt = QTranslator(self)
        self._set_translation()

        self.apply_callbacks.add(self._set_translation)

    def fix_palette(self):
        """
        PySide6 may work bad if GTK3 theme engine is active with builtin themes Adwaita, Adwaita-dark and High-Contrast.
        In this case text labels (window text) of many different (QLabel, etc) Qt widgets is shown as if it were
        disabled. This behavior has been seen in Debian 11, 12 with XFCE at least as of 19.06.2023.
        The problem is detected by checking current colors for active and disabled QPalette.WindowText.
        You may want to add more checking if the current way is too generic.
        It is also possible, that the bug will be fixed at some point in Adwaita, so we will not need this hack anymore.
        """
        palette = self.palette()
        color_windowtext = palette.color(QPalette.WindowText)
        color_disabledwindowtext = palette.color(QPalette.Disabled, QPalette.WindowText)

        # This combination is specific to Adwaita and High-Contrast:
        if (
            color_windowtext.red() == 146
            and color_windowtext.green() == 149
            and color_windowtext.blue() == 149
            and color_disabledwindowtext.red() == 73
            and color_disabledwindowtext.green() == 74
            and color_disabledwindowtext.blue() == 74
        ):
            palette.setColor(QPalette.WindowText, QColor(46, 52, 54))
            self.setPalette(palette)
        # specific to Adwaita-dark:
        elif (
            color_windowtext.red() == 145
            and color_windowtext.green() == 145
            and color_windowtext.blue() == 144
            and color_disabledwindowtext.red() == 72
            and color_disabledwindowtext.green() == 72
            and color_disabledwindowtext.blue() == 72
        ):
            palette.setColor(QPalette.WindowText, QColor(238, 238, 236))
            self.setPalette(palette)

    def register_resources(self):
        for file in DIR.ICONS.glob("*.rcc"):
            QResource.registerResource(str(file))

    def _set_translation(self):
        """The callback called by the Settings when a setting is applied or set."""

        language = self.config.language
        if language == "system":
            language = QLocale.languageToCode(QLocale.system().language())

        translator = QTranslator(self)
        if translator.load(str(DIR.TRANSLATIONS / f"app_{language}")):
            self.removeTranslator(self._translator_app)
            self.installTranslator(translator)
            self._translator_app = translator

        translator = QTranslator(self)
        path = Path(QLibraryInfo.location(QLibraryInfo.TranslationsPath)) / f"qtbase_{language}"
        if translator.load(str(path)):
            self.removeTranslator(self._translator_qt)
            self.installTranslator(translator)
            self._translator_qt = translator

    def open_project(self, path: Path, raise_exc: bool = False) -> bool:
        t = "file" if path.is_file() else "project"
        logger.debug(f"Loading {t}: {path}")
        try:
            project, messages = load_project(path)
        except (LoadFileError, LoadProjectError) as e:
            logger.error(f"Invalid load {t}: {str(e)}")
            if raise_exc:
                raise
            return False

        logger.debug(f"Loading {t} completed")

        messages.insert(0, f"{path}")
        main_window = MainWindow(
            app=self, 
            app_config=self.config, 
            app_apply_callbacks=self.apply_callbacks, 
            project=project, 
            init_msg=messages,
        )
        self._open_projects[id(main_window)] = main_window
        if not main_window.project.is_temporary:
            self.recent_projects_config.add_opened(project.name, project.path)
            self.recent_projects_config.add_recent(project.name, project.path)
        main_window.show()
        return True

    def close_project(self, main_window: MainWindow):
        del self._open_projects[id(main_window)]

        main_window.project.config.dump()

        if not main_window.project.is_temporary:
            self.recent_projects_config.add_recent(main_window.project.name, main_window.project.path)
            if not self._quitting:
                self.recent_projects_config.remove_opened(main_window.project.path)

        if not self._open_projects:
            self._recent_projects_dialog.show()

    def quit(self):
        self._quitting = True
        for value in list(self._open_projects.values()):
            value.close()
        super().quit()

    def run(self, project_path: Path) -> int:
        if project_path:
            if not self.open_project(project_path):
                return 1
        else:
            if self.recent_projects_config.opened:
                for item in self.recent_projects_config.opened:
                    self.open_project(item.path)
            else:
                self._recent_projects_dialog.show()
        return self.exec()
