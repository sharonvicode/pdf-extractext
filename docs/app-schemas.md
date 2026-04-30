# Carpeta app/schemas

## 1. Propósito

La carpeta `app/schemas` define los modelos de datos utilizados para las respuestas de la API.

Su función principal es:
- Estructurar los datos que devuelve la API
- Validar automáticamente las respuestas
- Facilitar la documentación automática (Swagger/OpenAPI)

Utiliza Pydantic para definir estos modelos.

---

## 2. Archivos que contiene

- responses.py

---

## 3. Descripción de cada archivo

### responses.py

Contiene los esquemas de respuesta de la API.

#### Responsabilidades:
- Definir el formato de salida de cada endpoint
- Validar los datos antes de enviarlos al cliente
- Estandarizar las respuestas

---

#### Modelos definidos

##### HealthResponse

Representa la respuesta del endpoint `/health`.

Campos:
- `status: str` → indica el estado de la API

Ejemplo:
```json
{
  "status": "ok"
}