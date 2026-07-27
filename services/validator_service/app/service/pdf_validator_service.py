from dataclasses import dataclass, field

from fastapi import UploadFile

from app.validators.interface import ValidatorInterface


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


class PDFValidationService:

    def __init__(self, validators: list[ValidatorInterface]) -> None:
        self._validators = validators

    def validate(self, file: UploadFile) -> ValidationResult:
        errors: list[str] = []
        for validator in self._validators:
            error = validator.validate(file)
            if error:
                errors.append(error)
        return ValidationResult(valid=len(errors) == 0, errors=errors)
