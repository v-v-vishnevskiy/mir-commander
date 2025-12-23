import asyncio
import logging
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMenu, QPushButton, QVBoxLayout

from mir_commander import __version__
from mir_commander.core.consts import BASE_URL
from mir_commander.core.errors import NetworkError
from mir_commander.core.network.utils import get_latest_version

from .config import AppConfig
from .sdk.async_worker import AsyncWorker
from .sdk.widget import Link, Notification

logger = logging.getLogger("UI.Updates")


class NewVersionNotification(Notification):
    def __init__(self, app_config: AppConfig, *args, **kwargs):
        self._text = QLabel("")
        self._download_link = Link(self.tr("Download"), f"{BASE_URL}/downloads")
        self._release_notes_link = Link(self.tr("Release Notes"), f"{BASE_URL}/changelog")
        options_menu = QMenu()
        options_menu.addAction(self.tr("Skip this version"), self._skip_version)
        options_menu.addAction(self.tr("Remind me later"), self._remind_later)

        super().__init__(
            *args,
            **kwargs
            | dict(
                text=self._text,
                actions=[self._release_notes_link, self._download_link],
                options=options_menu,
            ),
        )

        self._app_config = app_config
        self._version = ""

    def _skip_version(self):
        self._app_config.updates.skip_version = self._version
        self._app_config.dump()
        self.hide()

    def _remind_later(self):
        self.hide()

    def show_message(self, version: str):
        self._version = version
        self._text.setText(self.tr("A new version is available – v{}").format(version))
        self._text.adjustSize()
        self._release_notes_link.update_url(f"{BASE_URL}/changelog/{version}")
        self.show()


class CheckForUpdates(AsyncWorker):
    latest_version_signal = Signal(str)

    def __init__(self, app_config: AppConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_config = app_config

    async def task(self):
        try:
            self.latest_version_signal.emit(await get_latest_version())
            self._app_config.updates.last_check = datetime.now()
            self._app_config.dump()
        except NetworkError as e:
            logger.error("Failed to check for updates: %s", e)
            self.failed_signal.emit()


class ApplicationUpdateDialog(QDialog):
    def __init__(self, app_config: AppConfig, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(modal=True))

        self._app_config = app_config
        self._check_for_updates = CheckForUpdates(app_config)
        self._check_for_updates.latest_version_signal.connect(self._check_for_updates_finished)
        self._check_for_updates.failed_signal.connect(self._check_for_updates_error)

        self._version = ""
        self._status_label = QLabel("")
        self._status_label.setObjectName("mircmd-updates-status")
        self._info_label = QLabel("")
        self._info_label.setWordWrap(True)
        self._ok_button = QPushButton(self.tr("Ok"))
        self._ok_button.clicked.connect(self.hide)
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.clicked.connect(self._cancel)
        self._skip_button = QPushButton(self.tr("Skip this version"))
        self._skip_button.clicked.connect(self._skip_version)
        self._remind_later_button = QPushButton(self.tr("Remind me later"))
        self._remind_later_button.clicked.connect(self._remind_later)
        self._release_notes_link = Link(self.tr("Release Notes"), f"{BASE_URL}/changelog")
        self._download_link = Link(self.tr("Download"), f"{BASE_URL}/downloads")

        self._layout = QVBoxLayout()

        self._layout.addWidget(self._status_label)
        self._layout.addSpacing(15)
        self._layout.addWidget(self._info_label)

        self._links_layout = QHBoxLayout()
        self._links_layout.addWidget(self._release_notes_link)
        self._links_layout.addSpacing(5)
        self._links_layout.addWidget(self._download_link)
        self._links_layout.addStretch(1)
        self._layout.addLayout(self._links_layout)

        self._layout.addStretch(1)

        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.addStretch(1)
        self._layout.addLayout(self._buttons_layout)

        self.setLayout(self._layout)

        self.setWindowTitle(self.tr("Mir Commander Update"))

    def _skip_version(self):
        self._app_config.updates.skip_version = self._version
        self._app_config.dump()
        self.hide()

    def _remind_later(self):
        self.hide()

    def _cancel(self):
        self.hide()
        self._check_for_updates.stop()

    def _check_for_updates_finished(self, version: str):
        self._version = version

        self._buttons_layout.removeWidget(self._cancel_button)

        if version > __version__:
            logger.info("A new version is available: %s", version)
            self._status_label.setText(self.tr("A new version is available!"))
            self._info_label.setText(self.tr("Version {} is now available (You: v{})").format(version, __version__))
            self._release_notes_link.update_url(f"{BASE_URL}/changelog/{version}")
            self._release_notes_link.show()
            self._download_link.show()
            self._buttons_layout.addWidget(self._skip_button)
            self._buttons_layout.addWidget(self._remind_later_button)
        else:
            self._status_label.setText(self.tr("You are using the latest version."))
            self._info_label.setText(self.tr("Current version: {}").format(__version__))
            self._buttons_layout.addWidget(self._ok_button)

    def _check_for_updates_error(self):
        self._status_label.setText(self.tr("Update check failed."))
        self._info_label.setText(self.tr("Failed to check for updates. Check your logs for more information."))
        self._buttons_layout.removeWidget(self._cancel_button)
        self._buttons_layout.addWidget(self._ok_button)

    def show(self):
        self._version = ""
        self._status_label.setText(self.tr("Checking for updates..."))
        self._info_label.setText("")
        self._release_notes_link.hide()
        self._download_link.hide()

        self._buttons_layout.removeWidget(self._ok_button)
        self._buttons_layout.removeWidget(self._skip_button)
        self._buttons_layout.removeWidget(self._remind_later_button)
        self._buttons_layout.addWidget(self._cancel_button)

        self._check_for_updates.start()

        super().show()

    def closeEvent(self, event: QCloseEvent):
        self._check_for_updates.stop()
        event.accept()


class CheckForUpdatesBackgroundWorker(AsyncWorker):
    new_version_signal = Signal(str)

    def __init__(self, app_config: AppConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_config = app_config

    async def task(self):
        interval = self._app_config.updates.interval * 3600
        while True:
            last_check_seconds = (datetime.now() - self._app_config.updates.last_check).total_seconds()
            if interval > last_check_seconds:
                await asyncio.sleep(600)
                continue

            if self._app_config.updates.check_in_background is False:
                continue

            try:
                version = await get_latest_version()
            except NetworkError as e:
                logger.error("Failed to check for updates: %s", e)
                continue

            self._app_config.updates.last_check = datetime.now()
            self._app_config.dump()

            if self._app_config.updates.skip_version == version:
                continue

            if version > __version__:
                logger.info("A new version is available: %s", version)
                self.new_version_signal.emit(version)
