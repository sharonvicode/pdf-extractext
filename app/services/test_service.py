from app.core.db import db

def guardar(nombre: str):
    result = db["prueba"].insert_one({"nombre": nombre})
    return {"inserted_id": str(result.inserted_id), "nombre": nombre}
