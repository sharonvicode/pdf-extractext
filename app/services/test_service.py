from app.core.db import db

def guardar():
    db["prueba"].insert_one({"nombre": "Juan"})