from app.core.logger import logger
from app.clients.extractor_client import ExtractorClient
from app.clients.validator_client import ValidatorClient
from app.clients.persistence_client import PersistenceClient


class OrchestrationError(Exception):
    pass


class PDFEmptyError(OrchestrationError):
    pass


class PDFExtractionError(OrchestrationError):
    pass


class OrchestratorService:
    def __init__(
        self,
        extractor: ExtractorClient,
        validator: ValidatorClient,
        persistence: PersistenceClient,
    ):
        self._extractor = extractor
        self._validator = validator
        self._persistence = persistence

    def execute(self, file_path: str, filename: str) -> str:
        logger.info("Iniciando orquestación para %s", filename)

        try:
            texto = self._extractor.extract(file_path, filename)
        except Exception as e:
            logger.error("Error al extraer texto de %s: %s", filename, str(e))
            raise PDFExtractionError(f"Error al extraer texto del PDF: {e}")

        logger.info("Texto extraído correctamente de %s", filename)

        valido = self._validator.validate(texto)
        if not valido:
            logger.warning("Texto de %s no pasó la validación", filename)
            raise PDFEmptyError("El PDF no contiene texto suficiente")

        self._persistence.save(
            filename=filename,
            content=texto,
            metadata={},
        )

        logger.info("Orquestación completada para %s", filename)
        return texto