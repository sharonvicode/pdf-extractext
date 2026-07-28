import httpx

from app.core.config import VALIDATOR_URL
from app.core.logger import logger


class ValidatorClient:
    def __init__(self, base_url: str = VALIDATOR_URL):
        self.base_url = base_url

    def validate(self, file_path: str) -> bool:
        """
        Envía el PDF al validator-service para validar:
        - extensión
        - firma del archivo
        - tamaño
        """

        logger.info(
            "Enviando PDF a validator-service: %s",
            file_path,
        )

        try:
            with open(file_path, "rb") as file:
                files = {
                    "file": (
                        "document.pdf",
                        file,
                        "application/pdf",
                    )
                }

                response = httpx.post(
                    f"{self.base_url}/validate",
                    files=files,
                    timeout=30,
                )

        except Exception as exc:
            logger.error(
                "Error comunicándose con validator-service: %s",
                exc,
            )
            raise

        if response.status_code == 422:
            logger.warning(
                "Validator-service rechazó el archivo: %s",
                response.text,
            )
            return False

        response.raise_for_status()

        result = response.json()

        valido = result.get("valid", False)

        logger.info(
            "Resultado de validación del PDF: %s",
            valido,
        )

        return valido