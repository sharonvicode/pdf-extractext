# Análisis de Clean Code — DRY, KISS, YAGNI, SOLID

**Rol:** Ingeniero de desarrollo — Revisión de Pull Request
**Alcance:** Todo el repositorio (monolito `app/` + `tests/` + microservicios en `services/`)
**Fecha:** 2026-08-17
**Referencia:** Skill `clean-code` (nombres, funciones, comentarios, objetos, errores, SOLID, smells)

---

## 1. Resumen ejecutivo

| Principio | Veredicto |
|---|---|
| **DRY** (Don't Repeat Yourself) | **No cumple.** Se detectaron 8+ duplicaciones reales (logger, validador de archivos, repositorio MongoDB, config de BD, manejo de archivos temporales, constantes). |
| **KISS** (Keep It Simple, Stupid) | **Cumple parcialmente.** El código base es simple y legible, pero hay ruido de comentarios (`# AGREGAR`), cheques redundantes y un módulo de BD con nombres confusos. |
| **YAGNI** (You Aren't Gonna Need It) | **No cumple.** Endpoint de debug en producción, esquemas y métodos muertos, dependencias sin uso y una dependencia instalada en runtime. |
| **SOLID** | **Cumple parcialmente.** Excelente OCP/ISP en los microservicios de validación y extracción; DIP sólido en el monolito (DI), pero roto en el orquestador; asimetría de interfaz entre repositorios (LSP débil). |
| **Bug colateral** | La configuración de base de datos es **inconsistente**: el monolito escribe en `mi_base` y el `persistence_service` en `pdf_extractext`. |

**Conclusión:** el proyecto tiene buen instinto de diseño (inyección de dependencias, interfaces pequeñas, funciones cortas), pero la migración a microservicios duplicó componentes en vez de reutilizarlos, y quedó código muerto sin limpiar. La deuda más importante es la **duplicación de configuración y componentes**, no la complejidad algorítmica.

---

## 2. Metodología

- **Análisis estático** de producción y tests, contrastando cada principio.
- **Verificación de duplicaciones** mediante comparación directa de módulos y búsqueda de usos (dead code).
- Se cita evidencia como `archivo:línea` para cada hallazgo.

---

## 3. DRY — No cumple

### 3.1 Configuración de logging duplicada (3 copias)

- `app/core/logger.py`
- `services/orchestrator_service/app/core/logger.py`
- `services/persistence_service/app/core/logger.py`

Los tres archivos son **idénticos** (mismo `LOG_FORMAT`, `DATE_FORMAT`, `_configurar_logger()`), diferenciándose solo en el nombre del logger (`"app"` vs `"orchestrator_service"` vs `"persistence_service"`). Verificado con `diff`: la única diferencia funcional es la línea `logging.getLogger(...)`.

### 3.2 Validador de archivos duplicado

- `app/utils/validators.py:15` — `class FileValidator`
- `services/orchestrator_service/app/utils/validators.py:10` — `class FileValidator`

Misma lógica (extensión `.pdf`, content-type `application/pdf`, tamaño máximo) copiada entre el monolito y el orquestador.

### 3.3 Repositorio MongoDB duplicado

- `app/repository/mongodb_repository.py` — `MongoDBDocumentoRepository`
- `services/persistence_service/app/repository/mongodb_repository.py` — `DocumentRepository`

CRUD MongoDB casi idéntico (mismos métodos, mismo patrón `try/except` + log + `raise`). Además, la estructura de documentos diverge (`nombre/texto` vs `filename/content`), lo que demuestra que la duplicación ya está derivando en comportamiento inconsistente.

### 3.4 Boilerplate `try/except` + log + re-raise repetido ~14 veces

En todos los métodos de `app/repository/documento_repository.py`, `app/repository/mongodb_repository.py` y `services/persistence_service/app/repository/mongodb_repository.py` se repite el mismo patrón:

```python
try:
    ...
except Exception as exc:
    logger.error("...", str(exc))
    raise
```

Candidato natural a un decorador o helper (`@log_errors`), eliminando ~14 bloques idénticos.

### 3.5 Configuración de BD duplicada e inconsistente (bug)

- `app/core/config.py:16-18` define `MONGO_URL` y `DATABASE_NAME = "pdf_extractext"`.
- `app/core/db.py:9-15` vuelve a cargar `load_dotenv()` y define su propia variable `MONGO_DATABASE` con default **`"mi_base"`**, y además **hardcodea** `db = client["mi_base"]` sin usar `MONGO_DATABASE`.

Consecuencia: el `MongoDBDocumentoRepository` del monolito (`app/repository/mongodb_repository.py:12`, que usa `from app.core.db import db`) persiste en la BD **`mi_base`**, mientras el `persistence_service` (`services/persistence_service/app/core/db.py:7`, que usa `DATABASE_NAME`) persiste en **`pdf_extractext`**. El mismo dominio se escribe en dos bases distintas según qué servicio lo haga.

### 3.6 Manejo de archivos temporales duplicado (3 copias)

El patrón `NamedTemporaryFile + shutil.copyfileobj + finally os.remove` aparece en:

- `app/routes/extraer.py:35` (`_guardar_archivo_temporal` como contextmanager)
- `services/orchestrator_service/app/api/routes.py:34` (`_guardar_archivo_temporal`, casi idéntico)
- `services/extractor_service/app/api/routes.py:26` (inline en el endpoint)

### 3.7 Constantes de PDF repetidas

- Firma `b"%PDF-"`: `app/utils/pdf_extractor.py:15` y `services/validator_service/app/validators/content_validator.py:8`.
- Extensión `.pdf`: `app/utils/pdf_extractor.py:14`, `app/utils/validators.py:11`, `services/orchestrator_service/app/utils/validators.py:6`, `services/validator_service/app/validators/extension_validator.py:9`.
- Tamaño máximo `10485760`: `app/core/config.py:20`, `services/orchestrator_service/app/core/config.py:6`, `services/validator_service/app/core/config.py:9`.

### 3.8 `MIN_TEXT_LENGTH` duplicada y con configuración muerta

- `app/core/config.py:22` la define desde env (`MIN_TEXT_LENGTH`).
- `app/services/pdf_service.py:17` la **vuelve a hardcodear** como `MIN_TEXT_LENGTH = 20`, ignorando el valor del config.

La configuración existe pero nunca se usa; la constante vive en dos lugares.

### 3.9 Duplicación de boilerplate entre microservicios (menor)

Los 4 `pyproject.toml` y los 4 `Dockerfile` son idénticos salvo puerto/nombre. Es parcialmente inherente a microservicios independientes, pero es copia literal y debería al menos heredar de una plantilla.

---

## 4. KISS — Cumple parcialmente

### 4.1 Fortalezas

- `app/services/pdf_service.py` es un buen ejemplo: funciones cortas y de una sola responsabilidad (`ejecutar_extraccion`, `validar_texto_extraido`, `guardar_documento`, `procesar_pdf`).
- `services/validator_service` y `services/extractor_service` son minimalistas: una interfaz, una implementación, un servicio.
- Las rutas de los microservicios son delgadas y delegan bien.

### 4.2 Ruido y complejidad innecesaria

- **Comentarios mumbling:** `app/services/test_service.py:6-12` contiene marcadores `# AGREGAR`, `# AGREGAR TRY`, `# AGREGAR EXCEPT` — restos de instrucciones de trabajo, no documentación. Violación directa de "don't comment bad code—rewrite it".
- **Chequeo redundante de archivo vacío:** `app/utils/pdf_extractor.py:80-82` trata el archivo vacío como PDF válido dentro de `_es_pdf_valido`, y luego `_extraer_texto_de_pdf` (líneas 105-107) vuelve a chequear `ruta.stat().st_size == 0`. El caso especial se maneja en dos sitios.
- **Módulo `db.py` confuso:** `app/core/db.py` define un módulo llamado `db` que exporta una variable también llamada `db` (`from app.core.db import db`). Ambiguo y difícil de leer.
- **Banners de posición** (`# ============`) en `documento_repository.py` y `test_database.py`: marcadores de ruido según Clean Code.
- **Docstring duplicado de comportamiento:** en `_es_pdf_valido` el docstring describe la regla del archivo vacío de forma innecesariamente detallada cuando el código podría autodocumentarse.

---

## 5. YAGNI — No cumple

### 5.1 Endpoint de debug en producción

- `app/routes/test.py` — `GET /test`
- `app/services/test_service.py` — `guardar()`
- `app/schemas/responses.py:12-15` — `TestResponse`
- Incluido en `main.py:34` (`app.include_router(test.router)`).

Es infraestructura de prueba ("probar pymongo") que quedó expuesta en la API pública. No responde a ningún requerimiento del usuario final.

### 5.2 Esquemas muertos

- `app/schemas/pdf_schema.py` completo (`PDFBase`, `PDFCreate`, `PDFInDB`, `PDFResponse`, `PDFError`) — **ninguno es importado** por ningún otro archivo (verificado por búsqueda).
- `services/persistence_service/app/schemas/document_schema.py:16-24` — `DocumentOut` y `ErrorResponse` definidos y **sin uso**.

### 5.3 Métodos y código muerto

- `app/repository/documento_repository.py:115` — `actualizar()` no tiene ningún consumidor en rutas ni servicios.
- `app/services/test_service.py` — solo lo usa el endpoint de debug.

### 5.4 Dependencias sin uso o redundantes

- **`pdfplumber`** (`pyproject.toml:15`): ninguna referencia en el código (verificado por búsqueda). Dependencia muerta.
- **`fpdf` (1.7.2) y `fpdf2` (2.8.7) simultáneos** (`pyproject.toml:22-23`): comparten namespace `fpdf`; pytest emite warning de conflicto y ambos se instalan. Solo se necesita `fpdf2`.
- **`reportlab` instalado en runtime:** `tests/fixtures/create_test_pdf.py:51-56` ejecuta `pip install reportlab` como fallback. Un fixture no debe instalar dependencias en ejecución; además ni siquiera está declarado en `pyproject.toml`.

### 5.5 Configuración muerta

- `MIN_TEXT_LENGTH` en `app/core/config.py:22` no se consume en ningún lugar (ver 3.8).

---

## 6. SOLID — Cumple parcialmente

### 6.1 S — Single Responsibility: bien, con dos excepciones

Buenos ejemplos:
- `services/validator_service` separa cada regla en su propia clase (`ExtensionValidator`, `SizeValidator`, `ContentValidator`).
- Las rutas son delgadas y la lógica vive en servicios.

Violaciones:
- **`app/core/db.py`**: mezcla carga de configuración (env vars) con la conexión y el "global" `db`. Responsabilidades combinadas en un módulo.
- **`FileValidator` duplicado** (3.2): la misma responsabilidad implementada en dos clases de dos servicios distintos, con dos mensajes de error ligeramente divergentes.

### 6.2 O — Open/Closed: excelente

- `services/validator_service`: agregar una validación nueva es agregar una clase que implemente `ValidatorInterface` e inyectarla (`app/service/pdf_validator_service.py:19-25`). Abierto a extensión, cerrado a modificación.
- `services/extractor_service`: `PDFExtractorService` depende de `ExtractorInterface`; puede cambiarse el motor (`PyPDFExtractor`) sin tocar el servicio (testeado con `MockExtractor`).
- Patrón de estrategia bien aplicado.

### 6.3 L — Liskov: asimetría de interfaz entre repositorios

- `app/repository/documento_repository.py` (SQLite) expone `actualizar()`.
- `app/repository/mongodb_repository.py` (MongoDB) **no** lo expone.

Ambos se presentan como intercambiables ("Implementa la misma interfaz que `DocumentoRepository`", `mongodb_repository.py:4`), pero no lo son: el contrato difiere. Además no existe una interfaz formal compartida; la sustituibilidad es solo por convención de duck typing (el `Protocol` de `pdf_service.py:20` solo declara `guardar`).

### 6.4 I — Interface Segregation: excelente

- `ValidatorInterface` (1 método: `validate`), `ExtractorInterface` (1 método: `extract`). Sin métodos sobrantes que obliguen a implementaciones vacías.

### 6.5 D — Dependency Inversion: bien en el monolito, roto en el orquestador

Bien:
- Monolito: rutas reciben el repositorio vía `Depends(get_documento_repository)` (`app/routes/extraer.py:119`), con `dependency_overrides` para tests. `pdf_service.py` depende del `Protocol`.
- `extractor_service` y `validator_service`: inyección vía `Depends(_build_service)`.

Roto:
- `services/orchestrator_service/app/api/routes.py:27-31` construye un **singleton a nivel de módulo** con los clientes concretos (`ExtractorClient()`, `ValidatorClient()`, `PersistenceClient()`) y URLs fijas desde config. No hay composition root ni seam para inyectar clientes fake → el orquestador (el servicio con más lógica y riesgo) no es testeable por DI.
- Los repositorios se instancian a nivel de módulo contra un `db` global (`app/repository/mongodb_repository.py:12`), acoplando la clase al estado global de conexión.

---

## 7. Smells transversales

| Smell | Dónde |
|---|---|
| **Rigidez** (cambiar un mensaje de error requiere tocar N copias) | `FileValidator` duplicado, constantes PDF repetidas |
| **Fragmentación** (un cambio en validación rompe en varios lugares) | 3 copias de manejo temporal, 3 loggers |
| **Fragilidad** (tests rotos tras refactor de alias) | ya documentado en `analisis.md` (TDD) |
| **Comentarios que repiten el código** | `# AGREGAR...`, banners `# ====`, docstrings de obviedades |
| **Complejidad accidental** | `db` módulo/global, doble chequeo de archivo vacío |

---

## 8. Recomendaciones priorizadas

1. **[Bug, alta] Unificar la configuración de BD.** `app/core/db.py` debe leer `DATABASE_NAME` de `app/core/config.py` y eliminar `mi_base`/`MONGO_DATABASE`. El monolito y el `persistence_service` deben apuntar a la misma base.
2. **[DRY, alta] Extraer componentes compartidos** en un paquete común (p. ej. `shared/` o un microservicio base): logger, `FileValidator`, manejo de archivos temporales, constantes PDF y `try/except`+log (decorador). Elimina las 3-4 copias de cada uno.
3. **[YAGNI, alta] Purgar código muerto:** quitar `GET /test`, `test_service.py`, `pdf_schema.py`, `DocumentOut`/`ErrorResponse`, `actualizar()`, `pdfplumber`, y dejar solo `fpdf2`.
4. **[YAGNI/seguridad, media] Eliminar el `pip install reportlab`** de `create_test_pdf.py` y reemplazar el fixture por uno basado en `fpdf2` (ya en deps).
5. **[SOLID/DIP, media] Componer el orquestador en un composition root:** inyectar `OrchestratorService` vía `Depends` con clientes inyectables, para habilitar tests.
6. **[KISS, media] Limpiar ruido:** borrar comentarios `# AGREGAR`/banners, resolver la ambigüedad `db`, y consolidar el chequeo de archivo vacío en un solo lugar.
7. **[LSP, baja] Definir una interfaz formal** de repositorio (el `Protocol` ya existe en `pdf_service.py`) e igualar el contrato entre SQLite y MongoDB, o eliminar métodos que no son del contrato.

---

## 9. Veredicto final

**No cumple** con DRY ni YAGNI en sentido estricto; **cumple parcialmente** con KISS y SOLID.

El estilo general de código es limpio y legible — funciones cortas, nombres claros, DI en el monolito, y un diseño de estrategia impecable en validator/extractor. Sin embargo, la migración a microservicios se implementó **copiando** en lugar de **reutilizando** (logger, validadores, repositorios, config, manejo temporal), dejando además código muerto en producción y una **inconsistencia de base de datos** que rompe la equivalencia entre el monolito y el `persistence_service`. Son problemas de higiene y diseño, no de lógica; corregibles con una pasada de refactor priorizada.
