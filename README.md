# PDF ExtractText
API REST desarrollada en Python que permite extraer texto desde archivos PDF, procesarlos y almacenarlos en una base de datos.
________________________________________
## Integrantes
- Sharon Vico
- Franco Portaz
- Axel Altamirano
- Pachi 

## Descripción
Este proyecto implementa un servicio backend que recibe archivos PDF, extrae su contenido textual y lo persiste para su posterior uso.
El sistema está diseñado para automatizar el procesamiento de documentos, facilitando la digitalización y consulta de información contenida en PDFs.
________________________________________
## Objetivo
- Automatizar la extracción de texto desde documentos PDF 
- Centralizar el almacenamiento de contenido procesado 
- Facilitar el acceso y análisis de información textual 
________________________________________
## Estado actual del proyecto

El proyecto se encuentra en un estado **funcional en entorno de desarrollo**.
________________________________________
### Funcionalidades implementadas
- Extracción de texto desde archivos PDF
- Validación de archivos (tipo, tamaño, formato)
- API REST con FastAPI
- Persistencia de datos:
  - MongoDB (producción)
  - SQLite (tests)
- Manejo de errores (PDF inválido, vacío, etc.)
- Tests completos:
  - Unitarios
  - API (con mocks)
  - Base de datos
  - Integración (end-to-end)
________________________________________
## Flujo del sistema
1.	El usuario envía un PDF mediante una petición HTTP (POST /extraer) 
2.	El sistema valida que el archivo sea un PDF válido 
3.	Se guarda temporalmente el archivo 
4.	Se extrae el texto usando pypdf 
5.	Se valida que el contenido tenga al menos 20 caracteres 
6.	Se guarda la información en la base de datos 
7.	Se devuelve la respuesta en formato JSON 
8.	Se elimina el archivo temporal 
________________________________________
## Tecnologías utilizadas
Backend
- Python 3.12+ 
- FastAPI 
- Uvicorn 
Procesamiento de PDF
- pypdf 
Base de datos
- MongoDB (producción) 
- SQLite en memoria (tests) 
Testing
- pytest 
Otras herramientas
- Docker Compose (para MongoDB) 
- UV (gestión de dependencias) 
- python-dotenv 
________________________________________
## Variables de entorno

El proyecto utiliza variables de entorno definidas en `app/core/config.py` y `db.py`.

| Variable        | Descripción                             | Valor por defecto           |
|-----------------|-----------------------------------------|-----------------------------|
| MONGO_URL       | URL de conexión a MongoDB               | mongodb://localhost:27017   |
| DATABASE_NAME   | Nombre de la base de datos              | pdf_extractext              |
| MAX_FILE_SIZE   | Tamaño máximo de archivo (bytes)        | 10485760 (10MB)             |
| HOST            | Host del servidor                       | 0.0.0.0                     |
| PORT            | Puerto del servidor                     | 8000                        |

### Ejemplo `.env`

 ``env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=pdf_extractext
MAX_FILE_SIZE=10485760
HOST=0.0.0.0
PORT=8000
________________________________________
## Arquitectura
El proyecto sigue una arquitectura en capas:
- Capa de Presentación
Endpoints API (FastAPI)
- Capa de Aplicación (Lógica de negocio)
Procesamiento de PDFs y validaciones
- Capa de Datos
Repositorios MongoDB y SQLite
________________________________________
## Estructura del proyecto

- pdf-extractext/
- ├── app/
- │   ├── core/          # Configuración de base de datos
- │   ├── routes/        # Endpoints (API)
- │   ├── services/      # Lógica de negocio
- │   ├── repository/    # Acceso a datos (MongoDB / SQLite)
- │   ├── utils/         # Funciones auxiliares (extracción PDF)
- │   └── schemas/       # Esquemas (actualmente vacío)
- ├── tests/             # Tests unitarios, integración y API
- ├── main.py            # Punto de entrada
- ├── docker-compose.yml # MongoDB
- ├── pyproject.toml     # Dependencias
________________________________________
## Instalación y ejecución
### 1. Clonar repositorio
git clone https://github.com/tu-usuario/pdf-extractext.git
cd pdf-extractext
________________________________________
### 2. Crear entorno:
- uv venv
#### Activar entorno:
#### Windows
- .venv\Scripts\activate

#### Linux / Mac
- source .venv/bin/activate
________________________________________
### 3. Instalar dependencias
- uv pip install -e .
________________________________________
### 4. Levantar MongoDB
- docker-compose up -d
________________________________________
### 5. Ejecutar servidor
- uvicorn main:app --reload
________________________________________
## Endpoints
#### Health Check:
- GET /health/
#### Respuesta:
- {
  "status": "ok"
}
________________________________________
### Test de base de datos
- GET /test
________________________________________
### Extraer texto de PDF
- POST /extraer
#### Request: 
- multipart/form-data 
- Campo: file (archivo PDF) 
#### Response:
- {
  "exito": true,
  "texto": "contenido extraído...",
  "nombre_archivo": "archivo.pdf"
}
________________________________________
## Tests
El proyecto incluye distintos niveles de testing:
- Unitarios 
- API (con mocks) 
- Base de datos 
- Integración (end-to-end) 
Ejecutar tests
- pytest
________________________________________
## Limitaciones
- No procesa PDFs escaneados (sin OCR) 
- No incluye procesamiento con Inteligencia Artificial 
- No permite consultar documentos almacenados 
- No tiene autenticación 
- MongoDB sin configuración de seguridad 
- Validación estricta de contenido mínimo (20 caracteres)