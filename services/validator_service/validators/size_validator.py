from fastapi import UploadFile

from validators.interface import ValidatorInterface


class SizeValidator(ValidatorInterface):

    def __init__(self, max_size: int) -> None:
        self._max_size = max_size

    def validate(self, file: UploadFile) -> str | None:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > self._max_size:
            return f"El archivo excede el tamaño máximo de {self._max_size} bytes"
        return None
