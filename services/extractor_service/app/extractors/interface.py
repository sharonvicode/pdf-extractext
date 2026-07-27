from abc import ABC, abstractmethod
from pathlib import Path


class ExtractorInterface(ABC):

    @abstractmethod
    def extract(self, file_path: Path) -> str:
        ...
