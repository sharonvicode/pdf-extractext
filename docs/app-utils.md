# Carpeta app/utils

## 1. Propósito

La carpeta `app/utils` contiene funciones auxiliares del sistema.

Su función principal es:
- Proveer herramientas reutilizables
- Evitar duplicación de código
- Separar lógica técnica de la lógica de negocio

Estas funciones son utilizadas principalmente por la capa de servicios.

---

## 2. Archivos que contiene

- pdf_extractor.py
- validators.py

---

## 3. Descripción de cada archivo

### pdf_extractor.py

Encargado de la extracción de texto desde archivos PDF.

#### Responsabilidades:
- Validar que el archivo exista
- Verificar que sea un PDF válido
- Extraer texto del contenido del PDF

---

#### Función principal

##### extraer_texto(ruta_pdf)

Parámetros:
- ruta al archivo PDF (string o Path)

Funcionamiento:
1. Convierte la ruta a objeto Path
2. Verifica que el archivo exista
3. Valida que sea un PDF:
   - extensión .pdf
   - firma del archivo (%PDF-)
4. Llama a la función interna de extracción
5. Retorna el texto extraído

---

#### Funciones internas

##### _es_pdf_valido()
- Verifica si el archivo es realmente un PDF
- Controla:
  - extensión
  - tamaño
  - firma del archivo

##### _extraer_texto_de_pdf()
- Usa la librería pypdf
- Recorre todas las páginas del PDF
- Extrae el texto de cada una
- Une el contenido en un solo string

---

#### Comportamiento ante errores

- Si el archivo no existe → lanza error
- Si no es PDF válido → lanza error
- Si el PDF está corrupto o no tiene texto → devuelve string vacío

---

### validators.py

Contiene validaciones para archivos subidos por el usuario.

#### Responsabilidades:
- Validar tipo de archivo
- Validar extensión
- Validar tamaño

---

#### Clase FileValidator

Define métodos estáticos para validar archivos.

##### validate_pdf(file)

Valida que el archivo cumpla con:

- Extensión .pdf
- Tipo MIME: application/pdf
- Tamaño máximo permitido

---

#### Funcionamiento

1. Verifica la extensión del archivo
2. Verifica el tipo de contenido (content-type)
3. Calcula el tamaño del archivo sin cargarlo completamente en memoria
4. Compara con el tamaño máximo permitido (`MAX_FILE_SIZE`)

---

#### Manejo de errores

- Si alguna validación falla:
  - Lanza una excepción HTTP (HTTPException)
  - Devuelve código 400 (error del cliente)

---

## 4. Relación con otras capas

- `services` → usan `pdf_extractor` para procesar PDFs  
- `routes` → usan `validators` para validar archivos  
- `core/config` → provee configuración (ej: tamaño máximo)  

---

## 5. Flujo de uso

1. El usuario envía un archivo
2. La ruta valida el archivo usando `validators`
3. El servicio procesa el PDF usando `pdf_extractor`
4. Se obtiene el texto para continuar el flujo

---

## 6. Rol dentro del sistema

- Proveer funciones reutilizables
- Mantener el código limpio y modular
- Separar responsabilidades técnicas del negocio