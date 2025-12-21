import asyncio
import logging
import traceback

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger("UI.AsyncWorker")


class AsyncWorker(QThread):
    failed_signal = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = None
        self._loop = None

    async def task(self):
        raise NotImplementedError

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._task = self._loop.create_task(self.task())

        try:
            self._loop.run_until_complete(self._task)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Error running async worker: %s", e)
            self._task = None
            self._loop = None
            self.failed_signal.emit()
            traceback.print_exc()

    def stop(self):
        if (
            self.isRunning()
            and self._loop is not None
            and self._loop.is_running()
            and self._task is not None
            and not self._task.done()
        ):
            self._loop.call_soon_threadsafe(self._task.cancel)
            self._task = None
            self._loop = None
