from pathlib import Path

from app.extractors.interface import ExtractorInterface


class PDFExtractorService:

    def __init__(self, extractor: ExtractorInterface) -> None:
        self._extractor = extractor

    def extract(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        return self._extractor.extract(file_path)
