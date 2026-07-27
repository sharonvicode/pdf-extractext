from app.core.db import db
from app.core.logger import logger

def guardar(nombre: str):
    """Guarda un documento de prueba en la colección 'prueba'."""
    logger.info("Intentando guardar documento de prueba: %s", nombre)  # AGREGAR
    try:  # AGREGAR TRY
        result = db["prueba"].insert_one({"nombre": nombre})
        logger.info("Documento de prueba guardado con id %s", str(result.inserted_id))  # AGREGAR
        return {"inserted_id": str(result.inserted_id), "nombre": nombre}
    except Exception as exc:  # AGREGAR EXCEPT
        logger.error("Error al guardar documento de prueba %s: %s", nombre, str(exc))  # AGREGAR
        raise