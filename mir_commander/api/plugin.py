from abc import ABC, abstractmethod

from .metadata import Metadata


class Plugin(ABC):
    @abstractmethod
    def get_metadata(self) -> Metadata: ...
