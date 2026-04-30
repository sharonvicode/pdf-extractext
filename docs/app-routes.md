# Carpeta app/routes

## 1. Propósito

La carpeta `app/routes` define los endpoints de la API REST.

Su función principal es:
- Recibir solicitudes HTTP del cliente
- Validar datos de entrada
- Delegar la lógica de negocio a los servicios
- Devolver respuestas en formato JSON

Es la capa de entrada del sistema.

---

## 2. Archivos que contiene

- extraer.py
- health.py
- test.py

---

## 3. Descripción de cada archivo

### extraer.py

- Define el endpoint principal: `POST /extraer`
- Permite subir archivos PDF

#### Responsabilidades:
- Recibir el archivo PDF
- Validar el archivo (tipo, contenido, etc.)
- Guardar el archivo temporalmente
- Llamar al servicio `pdf_service` para procesarlo
- Manejar errores y devolver respuesta adecuada

#### Detalles:
- Usa `UploadFile` de FastAPI
- Usa archivos temporales (`tempfile`)
- Maneja errores como:
  - PDF vacío
  - Error en extracción

---

### health.py

- Define el endpoint: `GET /health`

#### Responsabilidad:
- Verificar si la API está funcionando

#### Respuesta:
```json
{
  "status": "ok"
}