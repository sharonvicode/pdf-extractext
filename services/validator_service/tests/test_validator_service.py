from io import BytesIO

from fastapi import UploadFile

from validators.content_validator import ContentValidator
from validators.extension_validator import ExtensionValidator
from validators.interface import ValidatorInterface
from validators.size_validator import SizeValidator
from service.pdf_validator_service import PDFValidationService


class TestExtensionValidator:
    def test_valid_extension(self) -> None:
        file = UploadFile(filename="documento.pdf", file=BytesIO(b""))
        validator = ExtensionValidator()
        assert validator.validate(file) is None

    def test_invalid_extension(self) -> None:
        file = UploadFile(filename="documento.txt", file=BytesIO(b""))
        validator = ExtensionValidator()
        assert validator.validate(file) is not None

    def test_no_extension(self) -> None:
        file = UploadFile(filename="documento", file=BytesIO(b""))
        validator = ExtensionValidator()
        assert validator.validate(file) is not None

    def test_extension_case_insensitive(self) -> None:
        file = UploadFile(filename="documento.PDF", file=BytesIO(b""))
        validator = ExtensionValidator()
        assert validator.validate(file) is None

    def test_none_filename(self) -> None:
        file = UploadFile(filename=None, file=BytesIO(b""))
        validator = ExtensionValidator()
        assert validator.validate(file) is not None


class TestSizeValidator:
    def test_valid_size(self) -> None:
        content = b" " * 100
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = SizeValidator(max_size=1000)
        assert validator.validate(file) is None

    def test_exceeds_size(self) -> None:
        content = b" " * 2000
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = SizeValidator(max_size=1000)
        assert validator.validate(file) is not None

    def test_empty_file(self) -> None:
        content = b""
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = SizeValidator(max_size=1000)
        assert validator.validate(file) is None

    def test_exact_max_size(self) -> None:
        content = b" " * 1000
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = SizeValidator(max_size=1000)
        assert validator.validate(file) is None


class TestContentValidator:
    def test_valid_pdf_header(self) -> None:
        content = b"%PDF-1.4\n..."
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = ContentValidator()
        assert validator.validate(file) is None

    def test_invalid_header(self) -> None:
        content = b"Not a PDF file"
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = ContentValidator()
        assert validator.validate(file) is not None

    def test_empty_content(self) -> None:
        content = b""
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = ContentValidator()
        assert validator.validate(file) is not None

    def test_partial_header(self) -> None:
        content = b"%PDF"
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validator = ContentValidator()
        assert validator.validate(file) is not None


class TestPDFValidationService:
    def test_all_validators_pass(self) -> None:
        content = b"%PDF-1.4\n..."
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validators: list[ValidatorInterface] = [
            ExtensionValidator(),
            SizeValidator(max_size=1000),
            ContentValidator(),
        ]
        service = PDFValidationService(validators)
        result = service.validate(file)
        assert result.valid
        assert result.errors == []

    def test_extension_fails(self) -> None:
        content = b"%PDF-1.4\n..."
        file = UploadFile(filename="test.txt", file=BytesIO(content))
        validators: list[ValidatorInterface] = [
            ExtensionValidator(),
            ContentValidator(),
        ]
        service = PDFValidationService(validators)
        result = service.validate(file)
        assert not result.valid
        assert len(result.errors) == 1

    def test_multiple_failures(self) -> None:
        content = b"Not a PDF"
        file = UploadFile(filename="test.txt", file=BytesIO(content))
        validators: list[ValidatorInterface] = [
            ExtensionValidator(),
            ContentValidator(),
        ]
        service = PDFValidationService(validators)
        result = service.validate(file)
        assert not result.valid
        assert len(result.errors) == 2

    def test_size_fails(self) -> None:
        content = b" " * 5000
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        validators: list[ValidatorInterface] = [
            ExtensionValidator(),
            SizeValidator(max_size=100),
        ]
        service = PDFValidationService(validators)
        result = service.validate(file)
        assert not result.valid
        assert len(result.errors) == 1
