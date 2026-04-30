# Tests del Proyecto

## 1. Propósito de la carpeta `tests/`

La carpeta `tests/` contiene todas las pruebas automatizadas del sistema.  
Su objetivo es verificar que cada parte de la aplicación funcione correctamente, tanto de forma aislada como integrada.

Se utilizan distintos tipos de tests:
- Unitarios → prueban funciones individuales
- Integración → prueban interacción entre módulos
- API → prueban endpoints HTTP

---

## 2. Estructura de la carpeta
- tests/
- ├── api/
- │ └── test_api.py
- ├── db/
- │ └── test_database.py
- ├── fixtures/
- │ └── create_test_pdf.py
- ├── integration/
- │ └── test_integracion_api_db.py
- ├── unit/
- │ └── test_extraer_texto_pdf.py

---

## 3. Explicación de cada archivo

---

### tests/api/test_api.py

#### Qué hace
Prueba los endpoints HTTP de la API sin ejecutar la lógica real.

#### Cómo lo hace
- Usa `TestClient` de FastAPI
- Usa `patch` para mockear el servicio `procesar_pdf`

#### Qué verifica

##### Endpoint `/health`
- Responde 200
- Devuelve `{ "status": "ok" }`

##### Endpoint `/extraer`
- PDF válido → 200 + datos correctos
- Archivo no PDF → 400
- Sin archivo → 422
- PDF vacío → 422
- PDF inválido → 400
- Error interno → 500

#### Responsabilidad
Validar que la API responda correctamente ante distintos escenarios.

---

### tests/db/test_database.py

#### Qué hace
Prueba la capa de persistencia (`DocumentoRepository`) usando SQLite en memoria.

#### Qué verifica

##### Guardado
- Retorna ID válido
- Persiste datos correctamente

##### Recuperación
- Obtener por ID
- Obtener por nombre
- Manejo de inexistentes

##### Operaciones múltiples
- Listado de documentos
- Conteo total

##### Eliminación
- Elimina correctamente
- Maneja IDs inexistentes

##### Integridad
- IDs únicos e incrementales

##### Casos límite
- Texto vacío
- Unicode
- Fechas extremas

#### Responsabilidad
Garantizar que el repositorio funcione correctamente de forma aislada.

---

### tests/integration/test_integracion_api_db.py

#### Qué hace
Prueba el flujo completo del sistema:
- request → extracción → guardado → respuesta

#### Cómo lo hace
- Usa FastAPI TestClient
- Inyecta SQLite en memoria (override del repositorio)
- Genera PDFs reales con `FPDF`

#### Qué verifica

##### Flujo completo
- Se puede subir un PDF y procesarlo correctamente

##### Persistencia
- El documento se guarda en la base de datos

##### Múltiples requests
- Se guardan múltiples documentos

##### Manejo de errores
- PDFs inválidos no se guardan

##### Recuperación
- Listado
- Obtener por ID

##### Integridad
- El texto guardado coincide con el extraído
- La fecha es válida

#### Responsabilidad
Validar que todos los componentes trabajen correctamente juntos.

---

### tests/unit/test_extraer_texto_pdf.py

#### Qué hace
Prueba la función:
- extraer_texto(ruta_pdf)

#### Qué verifica

##### Casos normales
- Extrae texto correctamente
- Maneja múltiples páginas
- Funciona con `Path` y strings

##### Casos vacíos
- PDF vacío → ""
- PDF sin texto → ""

##### Errores
- Archivo inexistente → FileNotFoundError
- No PDF → ValueError
- PDF corrupto → ValueError

##### Inputs inválidos
- Tipos incorrectos → TypeError / ValueError

##### Casos límite
- Muchas páginas
- Caracteres especiales
- Símbolos
- PDF con firma pero corrupto

#### Responsabilidad
Validar el comportamiento de la extracción de texto de forma aislada.

---

### tests/fixtures/create_test_pdf.py

#### Qué hace
Genera PDFs de prueba para usar en tests.

#### Funciones principales

- `crear_pdf_simple()` → crea PDF en memoria
- `guardar_pdf()` → guarda archivo en disco

#### Características
- Usa `reportlab`
- Maneja múltiples páginas
- Soporta texto largo

#### Responsabilidad
Proveer datos de prueba reutilizables.

---

## 4. Flujo general de testing

El sistema de tests cubre tres niveles:

### 1. Unitario
- utils → extraer_texto()

### 2. Integración parcial
- repository → base de datos (SQLite)

### 3. Integración completa
- API → Service → Repository → DB

---

## 5. Ejemplo de ejecución

Ejecutar todos los tests:
- pytest

## Ejecutar por tipo:
- pytest tests/unit/
- pytest tests/api/
- pytest tests/integration/
- pytest tests/db/

---

## 6. Relación con el sistema

- `test_api.py` → prueba `routes`
- `test_database.py` → prueba `repository`
- `test_integracion_api_db.py` → conecta `routes + services + repository`
- `test_extraer_texto_pdf.py` → prueba `utils`
- `create_test_pdf.py` → soporte para tests

---

## 7. Conclusión

La carpeta `tests/` garantiza:

- Correcto funcionamiento del sistema
- Validación de errores
- Integración entre componentes
- Calidad del código

Cubre desde funciones individuales hasta el flujo completo de la aplicación.