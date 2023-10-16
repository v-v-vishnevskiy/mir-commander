import logging

logger = logging.getLogger(__name__)


class Item:
    def clear(self):
        pass

    def paint(self):
        raise NotImplementedError()
