from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    success: bool
    text: str
    filename: str
