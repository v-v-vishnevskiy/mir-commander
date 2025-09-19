from typing import Any, Callable


class MessageChannel:
    def __init__(self):
        self._handlers = []

    def connect(self, handler: Callable):
        self._handlers.append(handler)

    def send(self, *args: Any, **kwargs: Any):
        for handler in self._handlers:
            handler(*args, **kwargs)
