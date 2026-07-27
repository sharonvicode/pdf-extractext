from abc import ABC, abstractmethod

from fastapi import UploadFile


class ValidatorInterface(ABC):

    @abstractmethod
    def validate(self, file: UploadFile) -> str | None:
        ...
