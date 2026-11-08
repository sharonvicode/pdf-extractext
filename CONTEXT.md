# CONTEXT — pdf-extractext (monolito)

Este documento fija el lenguaje del dominio y los **seams de test acordados**:
los puntos de la aplicación donde se escriben las pruebas. Cualquier test nuevo
debe escribirse en uno de estos seams, observando comportamiento por la interfaz
pública, nunca detalles internos.

## Lenguaje del dominio

| Término | Significado |
|---|---|
| **Documento** | PDF procesado y guardado: `id`, `nombre`, `texto`, `fecha_procesamiento` (UTC). |
| **Extracción** | Obtener el texto plano de un PDF (puerto `ExtractorTexto`). |
| **Texto suficiente** | Texto con al menos `MIN_TEXT_LENGTH` caracteres. Si no llega, `PDFEmptyError` y HTTP 422. |
| **Archivo inválido** | No es `.pdf`, no es `application/pdf` o supera `MAX_FILE_SIZE`. `ArchivoInvalidoError` y HTTP 400. |
| **PDF ilegible** | No existe, no tiene firma `%PDF-` o pypdf no lo puede leer. `PDFExtractionError` y HTTP 400. |

## Seams de test acordados

| # | Seam | Interfaz pública | Qué se inyecta / reemplaza | Tests |
|---|---|---|---|---|
| 1 | **HTTP** | Endpoints FastAPI vía `TestClient` | `get_documento_repository` (y opcionalmente `get_extractor_texto`) con `app.dependency_overrides` | `tests/api/` |
| 2 | **Flujo completo** | `POST /extraer` + repositorio real SQLite en memoria | Repositorio SQLite compartido por fixture e inyectado con `dependency_overrides` | `tests/integration/` |
| 3 | **Servicio de extracción** | `procesar_pdf(ruta, nombre, extractor)` | Extractor fake (una función) que implementa el puerto `ExtractorTexto` | `tests/unit/test_pdf_service.py` |
| 4 | **Extractor concreto** | `extraer_texto(ruta)` | Nada: PDFs reales generados con `fpdf2` en `tmp_path` | `tests/unit/test_extraer_texto_pdf.py` |
| 5 | **Validación de archivo** | `FileValidator.validate_pdf(nombre, content_type, archivo)` | Nada: `io.BytesIO` | `tests/unit/test_validators.py` |
| 6 | **Repositorio** | Contrato `DocumentoRepositoryInterface` | Conexión SQLite en memoria, BD limpia por test | `tests/db/` |
| 7 | **Configuración** | `app.core.config` y `app.core.mongo` | Nada | `tests/unit/test_config.py` |

## Reglas

- **Nada de side-channels:** no leer atributos privados ni agregados a mano (por ejemplo `client._algo`). Si un test necesita el repositorio, lo recibe por fixture.
- **No mockear lo que no es nuestro:** pypdf se prueba de verdad (seam 4). Fuera de ese seam, la extracción se reemplaza por el puerto (seam 3).
- **`patch` solo como último recurso.** Antes, usar `dependency_overrides` o inyección por parámetro, porque sobreviven a los refactors.
- **Ciclo TDD:** test que falla → implementación mínima → test verde → refactor. El commit que agrega comportamiento lleva su test, y la suite debe estar verde (CI) para mergear.

## Cómo correr los tests

```bash
uv sync
uv run pytest tests/
```
