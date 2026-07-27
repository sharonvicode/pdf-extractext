from pydantic import BaseModel


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]
