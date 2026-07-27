from pathlib import Path

from app.extractors.interface import ExtractorInterface
from app.extractors.pypdf_extractor import PyPDFExtractor
from app.service.pdf_extractor_service import PDFExtractorService


class TestPyPDFExtractor:
    def test_extract_returns_string(self, pdf_valido: Path) -> None:
        extractor = PyPDFExtractor()
        text = extractor.extract(pdf_valido)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_extract_empty_pdf(self, pdf_vacio: Path) -> None:
        extractor = PyPDFExtractor()
        text = extractor.extract(pdf_vacio)
        assert text == ""


class TestPDFExtractorService:
    def test_extract_success(self, pdf_valido: Path) -> None:
        service = PDFExtractorService(PyPDFExtractor())
        text = service.extract(pdf_valido)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_extract_file_not_found(self) -> None:
        service = PDFExtractorService(PyPDFExtractor())
        try:
            service.extract(Path("no_existe.pdf"))
            assert False, "Debe lanzar FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_inject_custom_extractor(self, pdf_valido: Path) -> None:
        class MockExtractor(ExtractorInterface):
            def extract(self, file_path: Path) -> str:
                return "texto simulado"

        service = PDFExtractorService(MockExtractor())
        text = service.extract(pdf_valido)
        assert text == "texto simulado"
