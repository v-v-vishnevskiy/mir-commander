from pathlib import Path

from PySide6.QtCore import QLibraryInfo, QLocale, QResource, Qt, QTranslator
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from mir_commander import exceptions
from mir_commander.consts import DIR
from mir_commander.projects import load_project
from mir_commander.recent_projects import RecentProjects
from mir_commander.ui.main_window import MainWindow
from mir_commander.ui.recent_projects import RecentProjects as RecentProjectsWidget
from mir_commander.utils.config import Config
from mir_commander.utils.settings import Settings


class Application(QApplication):
    """Application class. In fact, only one instance is created thereof."""

    def __init__(self, *args, **kwargs):
        self.setAttribute(Qt.AA_ShareOpenGLContexts)
        super().__init__(*args, **kwargs)
        self._quitting = False

        self.register_resources()

        self.config = Config(DIR.CONFIG / "config.yaml")
        self.config.set_defaults(Config(DIR.DEFAULT_CONFIGS / "config.yaml", read_only=True))
        self.settings = Settings(self.config)
        self.recent_projects = RecentProjects(DIR.CONFIG / "recent.yaml")

        self._projects: dict[int, MainWindow] = {}
        self._recent_projects_widget = RecentProjectsWidget(self)

        self._translator_app = QTranslator(self)
        self._translator_qt = QTranslator(self)
        self._set_translation()

        self.settings.set_default("language", "system")
        self.settings.add_apply_callback("language", self._set_translation)

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

        language = self.settings["language"]
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
        try:
            project, messages = load_project(path)
        except exceptions.LoadProject:
            if raise_exc:
                raise
            # TODO: Show message from the exception
            return False

        if project:
            messages.insert(0, f"{path}")
            main_window = MainWindow(self, project, messages)
            self._projects[id(main_window)] = main_window
            if not main_window.project.is_temporary:
                self.recent_projects.add_opened(project.name, project.path)
                self.recent_projects.add_recent(project.name, project.path)
            main_window.show()
            return True
        return False

    def close_project(self, main_window: MainWindow):
        del self._projects[id(main_window)]

        main_window.project.config.dump()

        if not main_window.project.is_temporary:
            self.recent_projects.add_recent(main_window.project.name, main_window.project.path)
            if not self._quitting:
                self.recent_projects.remove_opened(main_window.project.path)

        if not self._projects:
            self.recent_projects.load()  # reload
            self._recent_projects_widget.show()

    def quit(self):
        self._quitting = True
        for value in list(self._projects.values()):
            value.close()
        super().quit()

    def run(self, projpath: str) -> int:
        if projpath:
            if not self.open_project(Path(projpath)):
                return 1
        else:
            if self.recent_projects.opened:
                for item in self.recent_projects.opened:
                    self.open_project(item.path)
            else:
                self._recent_projects_widget.show()
        return self.exec()
