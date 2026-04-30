# Carpeta app/services

## 1. Propósito

La carpeta `app/services` contiene la lógica de negocio del sistema.

Su función principal es:
- Procesar los datos recibidos desde las rutas
- Aplicar reglas de negocio
- Coordinar el uso de utilidades y repositorios
- Mantener separada la lógica del acceso a datos

---

## 2. Archivos que contiene

- pdf_service.py
- test_service.py

---

## 3. Descripción de cada archivo

### pdf_service.py

Es el archivo principal de la lógica de negocio relacionada con PDFs.

#### Responsabilidades:
- Extraer texto de archivos PDF
- Validar el contenido extraído
- Manejar errores del proceso
- Guardar los datos en la base de datos mediante un repositorio

---

#### Componentes principales

##### DocumentoRepositoryInterface

- Define un contrato (interfaz) para los repositorios
- Establece el método:
  - `guardar(nombre, texto, fecha_procesamiento)`

Permite que el servicio no dependa de una base de datos específica.

---

##### Excepciones personalizadas

- `PDFServiceError`: clase base de errores
- `PDFEmptyError`: se lanza si el texto es muy corto
- `PDFExtractionError`: se lanza si falla la extracción

Permiten manejar errores de forma controlada.

---

##### Función procesar_pdf()

Es la función principal del servicio.

#### Parámetros:
- `ruta_pdf`: ubicación del archivo
- `nombre_archivo`: nombre original del PDF
- `repositorio`: implementación para guardar datos

#### Funcionamiento:

1. Extrae el texto usando `extraer_texto` (utils)
2. Maneja errores posibles:
   - archivo no encontrado
   - PDF inválido
   - errores generales
3. Valida que el texto tenga al menos 20 caracteres
4. Crea un objeto con:
   - nombre
   - texto
   - fecha de procesamiento
5. Guarda el documento usando el repositorio
6. Retorna el texto extraído

---

#### Relación con otras capas

- Usa `utils/pdf_extractor.py` → para extraer texto  
- Usa `repository` → para guardar datos  
- Es llamado por `routes/extraer.py`  

---

### test_service.py

Servicio simple utilizado para pruebas.

#### Responsabilidad:
- Insertar un registro en la base de datos

#### Funcionamiento:
- Inserta un documento en la colección `prueba`
- Retorna:
  - ID generado
  - nombre guardado

---

#### Relación con otras capas

- Usa `core/db.py` → conexión a MongoDB  
- Es llamado por `routes/test.py`  

---

## 4. Flujo de funcionamiento

Para el procesamiento de PDF:

1. La ruta recibe un archivo
2. Llama a `procesar_pdf`
3. Se extrae el texto
4. Se valida el contenido
5. Se guarda en la base de datos
6. Se retorna el resultado

---

## 5. Rol dentro del sistema

- Implementa la lógica de negocio
- No maneja HTTP directamente
- No accede directamente a la base de datos (usa repositorios)
- Actúa como intermediario entre rutas y datos