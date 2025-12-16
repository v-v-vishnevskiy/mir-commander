import logging
from pathlib import Path

from PySide6.QtCore import QFile, QLocale, QResource, Qt, QTranslator
from PySide6.QtGui import QColor, QFont, QFontDatabase, QOpenGLContext, QPalette, QSurfaceFormat
from PySide6.QtWidgets import QApplication, QMessageBox

from mir_commander.api.plugin import Translation
from mir_commander.core.consts import DIR
from mir_commander.core.errors import LoadProjectError
from mir_commander.core.models import PluginResource
from mir_commander.core.project import Project

from .config import AppConfig, ApplyCallbacks
from .project_window import ProjectWindow
from .recent_projects.recent_projects_dialog import RecentProjectsDialog

logger = logging.getLogger("UI.Application")


class Application(QApplication):
    """Application class. In fact, only one instance is created thereof."""

    def __init__(self, *args, **kwargs):
        self.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, on=False)
        super().__init__(*args, **kwargs)
        self.setApplicationName("mir_commander")
        self.setApplicationDisplayName("Mir Commander")
        self.setAttribute(Qt.ApplicationAttribute.AA_DontShowShortcutsInContextMenus, on=False)
        self._quitting = False

        self._apply_callbacks = ApplyCallbacks()
        self._config: AppConfig = AppConfig.load(DIR.HOME_MIRCMD / "config.yaml")

        if self._config.language != "system":
            QLocale.setDefault(QLocale(self._config.language))

        self._register_resources()

        self._open_projects: dict[int, ProjectWindow] = {}
        self._recent_projects_dialog = RecentProjectsDialog()
        self._recent_projects_dialog.open_project_signal.connect(self.open_project)

        self._set_translation()

        self._error = QMessageBox()
        self._error.setIcon(QMessageBox.Icon.Critical)

        self._setup_opengl()
        self._fix_palette()
        self._load_fonts()
        self._set_stylesheet()
        self._load_license()

    def _setup_opengl(self):
        context = QOpenGLContext()
        fmt = QSurfaceFormat()
        fmt.setVersion(4, 6)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        context.setFormat(fmt)
        context.create()
        version = context.format().version()

        sf = QSurfaceFormat()
        sf.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        sf.setVersion(*version)
        sf.setColorSpace(QSurfaceFormat.ColorSpace.sRGBColorSpace)
        QSurfaceFormat.setDefaultFormat(sf)

    def _fix_palette(self):
        """
        PySide6 may work bad if GTK3 theme engine is active with builtin themes Adwaita, Adwaita-dark and High-Contrast.
        In this case text labels (window text) of many different (QLabel, etc) Qt widgets is shown as if it were
        disabled. This behavior has been seen in Debian 11, 12 with XFCE at least as of 19.06.2023.
        The problem is detected by checking current colors for active and disabled QPalette.WindowText.
        You may want to add more checking if the current way is too generic.
        It is also possible, that the bug will be fixed at some point in Adwaita, so we will not need this hack anymore.
        """
        palette = self.palette()
        color_windowtext = palette.color(QPalette.ColorRole.WindowText)
        color_disabledwindowtext = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)

        # This combination is specific to Adwaita and High-Contrast:
        if (
            color_windowtext.red() == 146
            and color_windowtext.green() == 149
            and color_windowtext.blue() == 149
            and color_disabledwindowtext.red() == 73
            and color_disabledwindowtext.green() == 74
            and color_disabledwindowtext.blue() == 74
        ):
            palette.setColor(QPalette.ColorRole.WindowText, QColor(46, 52, 54))
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
            palette.setColor(QPalette.ColorRole.WindowText, QColor(238, 238, 236))
            self.setPalette(palette)

    def _register_resources(self):
        for file in DIR.RESOURCES.glob("*.rcc"):
            if QResource.registerResource(str(file)) is False:
                logger.error("Failed to register resource %s", file)

    def _set_translation(self):
        locale = QLocale()
        translator = QTranslator(self)
        if translator.load(locale, "", "", ":/core/i18n"):
            if not self.installTranslator(translator):
                logger.error("Failed to install translator for language %s", locale.name())
        else:
            logger.error("Failed to load translator for language %s", locale.name())

    def _load_fonts(self):
        font_id = QFontDatabase.addApplicationFont(":/core/fonts/Inter-Regular.ttf")
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font_family = font_families[0]
                font = QFont(font_family)
                font.setPixelSize(13)
                font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
                font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
                self.setFont(font)
        else:
            logger.error("Failed to open font file: %s", ":/core/fonts/Inter-Regular.ttf")

    def _set_stylesheet(self):
        styles = QFile(":/core/styles/stylesheets.qss")
        if styles.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            self.setStyleSheet(styles.readAll().data().decode("utf-8"))  # type: ignore[union-attr]
            styles.close()
        else:
            logger.error("Failed to open stylesheet file: %s", styles.errorString())

    def _load_license(self):
        license = QFile(":/core/policy/LICENSE.txt")
        if license.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            self._license_text = license.readAll().data().decode("utf-8")  # type: ignore[union-attr]
        else:
            logger.error("Failed to open license file: %s", license.errorString())

    def _setup_project_window(self, project_window: ProjectWindow):
        project_window.close_project_signal.connect(self.close_project)
        project_window.quit_application_signal.connect(self.close_app)
        self._open_projects[id(project_window)] = project_window
        if not project_window.project.is_temporary:
            self._recent_projects_dialog.add_opened(project_window.project)
            self._recent_projects_dialog.add_recent(project_window.project)

    def register_plugin_resources(self, plugin_resources: list[PluginResource]):
        for pr in plugin_resources:
            for resource in pr.resources:
                path = pr.base_path / resource.path
                if QResource.registerResource(str(path), pr.namespace) is False:
                    logger.error("Failed to register resource %s", path)
                    continue
                self._install_plugins_translations(resource.translations, pr.namespace)

    def _install_plugins_translations(self, translations: list[Translation], namespace: str):
        locale = QLocale()
        for translation in translations:
            translator = QTranslator(self)
            directory = f":{namespace}/{translation.path.lstrip('/')}"
            if translator.load(locale, translation.filename, translation.prefix, directory):
                if not self.installTranslator(translator):
                    logger.error("Failed to install plugin translator: %s", directory)
            else:
                logger.error("Failed to load plugin translator: %s", directory)

    def open_project(self, path: Path) -> int:
        try:
            project = Project(path=path, temporary=False)
        except LoadProjectError as e:
            logger.error(str(e))
            self._error.setText(e.__class__.__name__)
            self._error.setInformativeText(str(e))
            self._error.show()
            return self.exec()

        project_window = ProjectWindow(
            app_config=self._config,
            app_apply_callbacks=self._apply_callbacks,
            project=project,
            license_text=self._license_text,
        )
        self._setup_project_window(project_window)
        project_window.show()
        return self.exec()

    def open_empty_project(self) -> int:
        logger.info("Creating temporary empty project ...")

        project = Project(path=Path(), temporary=True)

        project_window = ProjectWindow(
            app_config=self._config,
            app_apply_callbacks=self._apply_callbacks,
            project=project,
            license_text=self._license_text,
            init_msg=[],
        )
        self._setup_project_window(project_window)

        project_window.show()

        return self.exec()

    def open_temporary_project(self, files: list[Path]) -> int:
        logger.info("Creating temporary project from files ...")

        project = Project(path=Path(), temporary=True)
        messages: list[str] = []
        project.import_files(files, messages)

        project_window = ProjectWindow(
            app_config=self._config,
            app_apply_callbacks=self._apply_callbacks,
            project=project,
            license_text=self._license_text,
            init_msg=messages,
        )
        self._setup_project_window(project_window)

        project_window.show()

        return self.exec()

    def open_recent_projects_dialog(self) -> int:
        self._recent_projects_dialog.show()
        return self.exec()

    def close_project(self, project_window: ProjectWindow):
        del self._open_projects[id(project_window)]

        project_window.project.save()

        if not project_window.project.is_temporary:
            self._recent_projects_dialog.add_recent(project_window.project)
            if not self._quitting:
                self._recent_projects_dialog.remove_opened(project_window.project)

        # TODO: uncomment this when we have a way to open the recent projects dialog
        # if not self._open_projects:
        #     self._recent_projects_dialog.show()
        self.close_app()

    def close_app(self):
        self._quitting = True
        for value in list(self._open_projects.values()):
            value.close()
        self._config.dump()
        self.quit()
