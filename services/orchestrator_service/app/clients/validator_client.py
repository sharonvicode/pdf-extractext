import httpx

from app.core.config import VALIDATOR_URL
from app.core.logger import logger


class ValidatorClient:
    def __init__(self, base_url: str = VALIDATOR_URL):
        self.base_url = base_url

    def validate(self, text: str) -> bool:
        logger.info("Enviando texto a validator-service (%d caracteres)", len(text))

        response = httpx.post(
            f"{self.base_url}/validate",
            json={"text": text},
            timeout=30,
        )

        if response.status_code == 422:
            logger.warning("Validator-service rechazó el texto: %s", response.text)
            return False

        response.raise_for_status()
        result = response.json()
        valido = result.get("valid", False)
        logger.info("Resultado de validación: %s", valido)
        return valido