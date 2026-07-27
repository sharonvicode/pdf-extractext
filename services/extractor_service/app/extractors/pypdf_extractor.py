from pathlib import Path

from pypdf import PdfReader

from app.extractors.interface import ExtractorInterface


class PyPDFExtractor(ExtractorInterface):

    def extract(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
