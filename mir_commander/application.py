import os
from typing import Dict

from PySide6.QtCore import QDir, QLocale, QResource, QTranslator
from PySide6.QtWidgets import QApplication

from mir_commander import exceptions
from mir_commander.main_window import MainWindow
from mir_commander.projects import load_project
from mir_commander.recent_projects import RecentProjects
from mir_commander.settings import Settings
from mir_commander.utils.config import Config
from mir_commander.widgets.recent_projects import RecentProjects as RecentProjectsWidget

CONFIG_DIR = os.path.join(QDir.homePath(), ".mircmd")


class Application(QApplication):
    """Application class. In fact, only one instance is created thereof."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._quitting = False

        QResource.registerResource(os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "general.rcc"))

        self.config = Config(os.path.join(CONFIG_DIR, "config.yaml"))
        self.settings = Settings(self.config)
        self.recent_projects = RecentProjects(os.path.join(CONFIG_DIR, "recent.yaml"))

        self._projects: Dict[int, MainWindow] = {}
        self._recent_projects_widget = RecentProjectsWidget(self)

        self._translator = QTranslator(self)
        self._set_translation()

        self.settings.set_default("language", "system")
        self.settings.add_apply_callback("language", self._set_translation)

    def _set_translation(self):
        """The callback called by the Settings when a setting is applied or set."""

        language = self.settings["language"]
        if language == "system":
            language = QLocale.languageToCode(QLocale.system().language())

        self.removeTranslator(self._translator)
        i18n_path = os.path.join(os.path.dirname(__file__), "..", "resources", "i18n")
        if not self._translator.load(os.path.join(i18n_path, f"app_{language}")):
            self._translator.load(os.path.join(i18n_path, "app_en"))
        self.installTranslator(self._translator)

    def open_project(self, path: str, raise_exc: bool = False) -> bool:
        try:
            project = load_project(path, CONFIG_DIR)
        except exceptions.LoadProject:
            if raise_exc:
                raise
            # TODO: Show message from the exception
            return False

        if project:
            main_window = MainWindow(self, project)
            self._projects[id(main_window)] = main_window
            self.recent_projects.add_opened(project.name, project.path)
            self.recent_projects.add_recent(project.name, project.path)
            main_window.show()
            return True
        return False

    def close_project(self, main_window: MainWindow):
        del self._projects[id(main_window)]

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
            if not self.open_project(projpath):
                return 1
        else:
            if self.recent_projects.opened:
                for item in self.recent_projects.opened:
                    self.open_project(item.path)
            else:
                self._recent_projects_widget.show()
        return self.exec()
