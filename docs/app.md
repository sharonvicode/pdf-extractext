# Carpeta app

## 1. Propósito

La carpeta `app` contiene la implementación principal del sistema.  
Aquí se encuentra toda la lógica de la aplicación, incluyendo:

- Definición de endpoints (API)
- Lógica de negocio
- Acceso a la base de datos
- Configuración
- Utilidades

Es el núcleo del backend y donde se ejecuta la funcionalidad principal: la extracción de texto desde PDFs.

---

## 2. Estructura general

La carpeta está organizada en subcarpetas con responsabilidades específicas:

- core/
- controllers/
- models/
- repository/
- routes/
- schemas/
- services/
- utils/

---

## 3. Descripción de subcarpetas y archivos

### core/

Contiene la configuración y conexión a la base de datos.

#### config.py
- Define la configuración de la aplicación
- Maneja variables de entorno (ej: conexión a MongoDB)
- Centraliza los parámetros del sistema

#### db.py
- Gestiona la conexión a MongoDB
- Inicializa el cliente de base de datos
- Es utilizado por los repositorios

---

### controllers/

- Actualmente está vacía
- Su propósito sería manejar la lógica intermedia entre rutas y servicios
- Actuaría como capa de control en una arquitectura tipo MVC

---

### models/

- Actualmente está vacía
- Estaría destinada a definir modelos de datos del sistema

---

### repository/

Contiene la capa de acceso a datos.

#### documento_repository.py
- Define una interfaz (contrato) para repositorios
- Establece métodos como guardar o buscar documentos
- Permite desacoplar la lógica de negocio de la base de datos

#### mongodb_repository.py
- Implementa el repositorio usando MongoDB
- Realiza operaciones de guardado y consulta
- Usa la conexión definida en `core/db.py`

---

### routes/

Define los endpoints de la API.

#### extraer.py
- Endpoint principal (POST /extraer)
- Recibe archivos PDF
- Llama al servicio para procesarlos
- Devuelve la respuesta al cliente

#### health.py
- Endpoint de verificación (GET /health)
- Indica si la API está funcionando

#### test.py
- Endpoint de prueba
- Se utiliza para verificar funcionamiento básico

---

### schemas/

Define estructuras de datos para respuestas.

#### responses.py
- Define el formato de salida de la API
- Permite validar y estructurar respuestas

---

### services/

Contiene la lógica de negocio.

#### pdf_service.py
- Coordina el proceso de extracción de texto
- Usa `pdf_extractor` para obtener el texto
- Usa el repositorio para guardar datos
- Aplica reglas de negocio

#### test_service.py
- Servicio de prueba
- Utilizado por endpoints de testing

---

### utils/

Funciones auxiliares del sistema.

#### pdf_extractor.py
- Extrae texto de archivos PDF
- Utiliza librerías externas (como pypdf)

#### validators.py
- Valida datos de entrada
- Verifica archivos y condiciones antes de procesar

---

## 4. Flujo interno

El flujo principal del sistema es:

1. El cliente envía un PDF a la API
2. La ruta (`routes/extraer.py`) recibe la solicitud
3. Se valida el archivo
4. El servicio (`pdf_service.py`) procesa el PDF
5. Se extrae el texto (`utils/pdf_extractor.py`)
6. Se guarda en la base de datos (`repository/`)
7. Se devuelve la respuesta al cliente

---

## 5. Relaciones entre componentes

- `routes` → llaman a `services`
- `services` → usan `repository` y `utils`
- `repository` → usa `core/db`
- `core` → maneja configuración y conexión
- `schemas` → definen estructura de respuestas

---

## 6. Ejemplo de uso

Ejemplo de request:

```bash
curl -X POST "http://localhost:8000/extraer" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@documento.pdf"