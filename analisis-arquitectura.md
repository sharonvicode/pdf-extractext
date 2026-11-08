# Análisis de Arquitectura de Capas

**Rol:** Arquitecto de Software — Revisión de arquitectura
**Alcance:** Todo el repositorio (monolito `app/` + `tests/` + microservicios en `services/`)
**Fecha:** 2026-08-17
**Criterios evaluados:** N-capas, Hexagonal, Onion y Clean Architecture

---

## 1. Resumen ejecutivo

| Estilo | ¿Se usa? | Nivel de cumplimiento |
|---|---|---|
| **N-capas (Layered)** | **Sí, es la arquitectura real** | Alto en el monolito; desvíos en `persistence_service` |
| **Hexagonal (Ports & Adapters)** | Elementos presentes | Parcial — ports/adapters en validator/extractor/repositorios, pero puertos con fuga de framework y orquestador sin ports |
| **Onion** | Elementos presentes | Parcial — dependencias hacia interfaces en el monolito, pero la capa de aplicación toca infraestructura y no hay dominio |
| **Clean Architecture** | No | No cumple — sin entidades, regla de dependencia violada en varios puntos |

**Clasificación final:** el proyecto implementa una **arquitectura N-capas clásica** (`presentación → aplicación → datos`) con **intenciones de Hexagonal/Onion** en la base de código de los microservicios de validación y extracción. No es hexagonal ni clean en sentido estricto: le faltan puertos formales, un dominio modelado, un composition root y disciplina en la dirección de dependencias.

La documentación oficial (README y `docs/*.md`) declara explícitamente "arquitectura en capas", y la estructura de carpetas del monolito lo confirma.

---

## 2. Metodología

- Reconstrucción del **grafo de dependencias real** entre módulos (imports) y contraste con la documentación (`docs/app.md`, `docs/app-core.md`, `docs/app-services.md`, README).
- Verificación de dirección de dependencias (quién importa a quién) para detectar fugas entre capas.
- Evaluación contra los 4 estilos de referencia según sus reglas canónicas:
  - N-capas: separación Presentación / Lógica de negocio / Datos, con flujo estrictamente descendente.
  - Hexagonal: puertos (interfaces) + adaptadores, dominio aislado, todo lo externo entra por puertos.
  - Onion: dependencias apuntan **hacia adentro** (dominio en el centro).
  - Clean: regla de dependencia (las capas internas no conocen a las externas), entidades en el centro.

---

## 3. Arquitectura actual

### 3.1 Monolito (`app/`)

```
┌──────────────────────────────────────────────────────────┐
│ PRESENTACIÓN        routes/  (extraer, documentos_get,   │
│                     documentos_delete, health, test)     │
│                     schemas/ (respuestas DTO)            │
├──────────────────────────────────────────────────────────┤
│ APLICACIÓN          services/ (pdf_service, test_service)│
│                     utils/   (pdf_extractor, validators) │
├──────────────────────────────────────────────────────────┤
│ DATOS               repository/ (SQLite, MongoDB)        │
│                     core/db.py (conexión MongoDB)        │
├──────────────────────────────────────────────────────────┤
│ INFRA/COMÚN         core/ (config, logger, dependencies) │
│                     core/dependencies.py (DI: Depends)   │
└──────────────────────────────────────────────────────────┘
```

Flujo: `routes` → (validación) → `services` → `repository` → `db`. La inyección se hace con `Depends(get_documento_repository)` y se sobrescribe en tests con `dependency_overrides`.

### 3.2 Microservicios (`services/`)

| Servicio | Capas internas | Rol |
|---|---|---|
| `validator_service` | `api` → `service/PDFValidationService` → `validators/*` (interfaz + 3 impl) | Puerto `ValidatorInterface`, 3 adaptadores |
| `extractor_service` | `api` → `service/PDFExtractorService` → `extractors/*` (interfaz + impl) | Puerto `ExtractorInterface`, 1 adaptador |
| `persistence_service` | `api` → `services/DocumentService` (muerto) → `repository/DocumentRepository` → `core/db.py` | Repositorio MongoDB (nuevo contrato) |
| `orchestrator_service` | `api` → `services/OrchestratorService` → `clients/*` (httpx) | Fachada que orquesta los 3 servicios anteriores |

Topología física: 4 servicios en puertos 8001–8004 + MongoDB, conectados por red Docker (`docker-compose.*.yml`). El orquestador es la **fachada** del sistema; el monolito sigue existiendo con la misma funcionalidad.

---

## 4. Evaluación vs N-capas

### 4.1 Lo que cumple

- **Separación de capas correcta en el monolito:** las rutas no tocan la BD directamente; `pdf_service` coordina extracción → validación → persistencia (`app/services/pdf_service.py`).
- **Inyección del repositorio por la capa de presentación** (`Depends`) mantiene la capa de datos desacoplada del ciclo de vida HTTP.
- **DTOs de respuesta** en `schemas/` separan el contrato de API del modelo interno.

### 4.2 Desvíos

| Desvío | Evidencia |
|---|---|
| **Salto de capa en `persistence_service`:** las rutas usan `repository.*` directo y **nunca instancian `DocumentService`** (verificado: sin importaciones). La capa de aplicación existe pero está muerta. | `persistence_service/app/api/routes.py:14` vs `persistence_service/app/services/document_service.py:5` |
| **Utilidad que levanta errores HTTP:** `FileValidator` (capa utils) lanza `HTTPException` de FastAPI. Una utilidad de negocio no debería conocer el framework web. | `app/utils/validators.py:7`, `orchestrator_service/app/utils/validators.py:1` |
| **Servicio de prueba que accede a `db` directo** (global de MongoDB) desde la capa de aplicación. | `app/services/test_service.py:1` |

Conclusión N-capas: el monolito es una implementación razonable de N-capas; los microservicios la siguen de forma inconsistente (capa de servicio ignorada en persistence).

---

## 5. Evaluación vs Hexagonal (Ports & Adapters)

### 5.1 Ports y adapters presentes (bien)

| Puerto (interfaz) | Adaptadores | Ubicación |
|---|---|---|
| `DocumentoRepositoryInterface` (Protocol) | `DocumentoRepository` (SQLite), `MongoDBDocumentoRepository` | `app/services/pdf_service.py:20` |
| `ValidatorInterface` | `ExtensionValidator`, `SizeValidator`, `ContentValidator` | `validator_service/.../validators/interface.py` |
| `ExtractorInterface` | `PyPDFExtractor` | `extractor_service/.../extractors/interface.py` |

El `PDFExtractorService` acepta cualquier `ExtractorInterface` (testeado con un `MockExtractor`), y `PDFValidationService` es composable por lista de validadores. Esto es patrón de estrategia puro y correcto.

### 5.2 Fallas

1. **Fuga de framework en los puertos:** `ValidatorInterface.validate(self, file: UploadFile)` y `PDFValidationService` importan `fastapi.UploadFile` (`validator_service/.../interface.py:3`, `.../service/pdf_validator_service.py:3`). El puerto —el contrato de dominio— depende del framework web. Un adapter HTTP (la ruta) debería traducir el request a un tipo de dominio antes de cruzar el puerto.
2. **Orquestador sin puertos:** `OrchestratorService` recibe **clases concretas** (`ExtractorClient`, `ValidatorClient`, `PersistenceClient`) en el constructor (`orchestrator_service/app/services/orchestrator_service.py:20-28`). No hay interfaces para esos adapters externos; el dominio orquestador está acoplado a adaptadores HTTP concretos.
3. **Sin composition root:** en `orchestrator_service/app/api/routes.py:27-31` se construye `_orchestrator = OrchestratorService(ExtractorClient(), ...)` como singleton a nivel de módulo. Hexagonal exige componer en el borde (composition root) para poder inyectar fakes en tests; aquí no hay seam.
4. **Adapters instanciados contra globals:** los repositorios MongoDB se crean contra `db` global importado (`app/repository/mongodb_repository.py:12`), acoplando el adapter a estado de módulo.

Conclusión Hexagonal: la mitad "datos/externos" tiene ports y adapters (validator, extractor, repos); la **mitad "entrada/driving"** (rutas, orquestador) no respeta el patrón.

---

## 6. Evaluación vs Onion Architecture

Regla de Onion: el dominio está en el centro y **todas las dependencias apuntan hacia adentro**; la capa externa es infraestructura (DB, framework, HTTP).

### 6.1 Lo que cumple

- El monolito invierte la dependencia de persistencia: `pdf_service` depende del `Protocol` (`DocumentoRepositoryInterface`), no de `DocumentoRepository` ni de MongoDB. La infraestructura queda afuera.
- Los microservicios validator/extractor siguen el patrón onion de forma natural: servicio de aplicación → interfaz → implementación concreta.

### 6.2 Violaciones de la dirección de dependencia

1. **Aplicación → infraestructura:** `pdf_service.py` importa `app/utils/pdf_extractor.py`, que envuelve **pypdf** (`app/utils/pdf_extractor.py:11`). La extracción es infraestructura (librería externa) y está siendo invocada desde la capa de aplicación sin mediar un puerto. El monolito mezcla el port de extracción con la utilidad concreta.
2. **Sin dominio en el centro:** `app/models/` solo contiene diagramas `.puml`; no hay entidades ni objetos de dominio. Los datos viajan como `dict` planos (repositorios) y Pydantic DTOs (schemas). El "núcleo" onion está vacío.
3. **Config/conexión como infraestructura global:** `app/core/db.py` crea el `MongoClient` y expone `db` a nivel de módulo; la capa de datos importa ese global en vez de recibir la conexión inyectada.

Conclusión Onion: la forma general (servicio → interfaz ← impl) se respeta, pero falta el centro (dominio) y hay dos fugas hacia afuera (pypdf desde aplicación, framework desde puertos).

---

## 7. Evaluación vs Clean Architecture

Mapa Clean del proyecto (según las 4 capas de Uncle Bob):

| Capa Clean | En el proyecto | Estado |
|---|---|---|
| **Entities** | — | **Ausente.** No existen entidades de dominio; solo `dict` y DTOs |
| **Use Cases** | `pdf_service`, `PDFValidationService`, `PDFExtractorService`, `OrchestratorService`, `DocumentService` | Presente (aunque `DocumentService` está muerto) |
| **Interface Adapters** | `routes/`, `schemas/`, `repository/`, `clients/`, `extractors/`, `validators/` | Presente |
| **Frameworks & Drivers** | FastAPI, pypdf, pymongo, httpx, SQLite | Presente |

### 7.1 Violaciones de la regla de dependencia (interior no conoce exterior)

1. `app/utils/validators.py:7` y `orchestrator_service/app/utils/validators.py:1` — la capa de adaptadores/utilidades importa **FastAPI** (`HTTPException`, `UploadFile`).
2. `validator_service/.../validators/interface.py:3` y `.../service/pdf_validator_service.py:3` — el **use case** (`PDFValidationService`) y el **puerto** dependen de `fastapi.UploadFile`.
3. `orchestrator_service/app/services/orchestrator_service.py` — el **use case** `OrchestratorService` depende de clases de `clients/*` (adaptadores HTTP concretos), no de interfaces.
4. `pdf_service.py:14` — el use case depende de `utils/pdf_extractor` (framework pypdf).
5. `app/services/test_service.py:1` — use case dependiente del global `db` de infraestructura.

Conclusión Clean: estructura de carpetas razonable, pero **sin entities** y con la regla de dependencia violada en 5 puntos concretos, todos del mismo tipo: los use cases/puertos conocen a FastAPI o a la infraestructura de extracción.

---

## 8. Topología de despliegue

```
                    ┌─────────────┐
   Cliente ───────► │ orchestrator│ :8004 (fachada)
                    └──────┬──────┘
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
     ┌──────────────┐ ┌────────────┐ ┌──────────────┐
     │ validator    │ │ extractor  │ │ persistence  │
     │ service :8001│ │ service:8002│ │ service:8003 │
     └──────────────┘ └────────────┘ └──────┬───────┘
                                            ▼
                                      ┌───────────┐
                                      │  MongoDB  │
                                      └───────────┘
```

- Despliegue por contenedores (`Docker/*.yml`, `Dockerfile` por servicio).
- El monolito (`app/`, puerto 8000) coexiste con la nueva arquitectura y expone la misma API.

### 8.1 Deudas de la topología

| Deuda | Detalle |
|---|---|
| **Dos implementaciones del mismo dominio** | Monolito (`/extraer`, `/documentos`) y orquestador (`/extraer`) son funcionalmente equivalentes; no hay una estrategia de deprecación del monolito. |
| **Dos bases de datos divergentes** | El monolito escribe en `mi_base` (`app/core/db.py:15`) y `persistence_service` en `pdf_extractext` (`services/persistence_service/app/core/db.py:7`) — incluso con `DATABASE_NAME: pdf_extractext` declarado en `docker-compose.app.yml:13`. |
| **Comunicación síncrona simple (HTTP)** | El orquestador encadena validación → extracción → persistencia de forma síncrona; sin colas ni manejo de idempotencia. Aceptable para el alcance, pero limita escala. |
| **Config por servicio duplicada** | Cada servicio replica `config.py`/`logger.py` (ver `analisis_clean_code.md`). |

---

## 9. Veredicto por estilo

| Estilo | Veredicto |
|---|---|
| **N-capas** | ✅ **Es lo que es.** Implementación real y razonable en el monolito; un salto de capa en `persistence_service` (rutas → repositorio directo). |
| **Hexagonal** | 🟡 **Intención parcial.** Ports/adapters sólidos en validator/extractor/repos; puertos contaminados con `UploadFile`, orquestador sin ports ni composition root. |
| **Onion** | 🟡 **Intención parcial.** Dependencias invertidas para persistencia; aplicación tocando infraestructura (pypdf) y dominio vacío. |
| **Clean** | ❌ **No.** Sin entities; regla de dependencia violada en 5 puntos. |

---

## 10. Recomendaciones priorizadas

**Alto impacto / bajo esfuerzo**
1. **Eliminar la fuga de FastAPI de los puertos.** `ValidatorInterface.validate` debe recibir un tipo de dominio (bytes/path) o el adapter HTTP (la ruta) convierte `UploadFile → bytes` antes de llamar al servicio. Afecta: `validator_service` interface + service.
2. **Componer el orquestador en un composition root.** Crear `OrchestratorService` vía `Depends` con clientes inyectables (fáciles de fakear en tests) en lugar del singleton de módulo.
3. **Definir puertos para los clientes del orquestador** (`ExtractorClient`, `ValidatorClient`, `PersistenceClient`) detrás de interfaces, para que el use case no dependa de adaptadores HTTP concretos.

**Medio impacto / esfuerzo medio**
4. **Mover la extracción detrás de un puerto en el monolito** (`ExtractorInterface` ya existe en `extractor_service`); que `pdf_service` dependa de la interfaz y no de `utils/pdf_extractor`.
5. **Eliminar la capa muerta** (`DocumentService` sin uso) o conectar las rutas de `persistence_service` a través de ella para respetar N-capas.
6. **Unificar la configuración de BD** (`mi_base` vs `pdf_extractext`) para que monolito y `persistence_service` hablen con la misma base.

**Bajo impacto / esfuerzo alto**
7. **Modelar el dominio:** introducir entidades (`Documento`, `PDF`), aunque sea simple, para dar contenido al centro de la arquitectura y que los DTOs de API no sean el único contrato.
8. **Definir la estrategia de convergencia:** deprecar el monolito o convertirlo en un quinto servicio; no mantener dos implementaciones equivalentes en paralelo sin plan.

---

## 11. Verdicto final

La arquitectura del proyecto es **N-capas**, ejecutada con buenas prácticas de inyección de dependencias y con varios elementos de Hexagonal/Onion que demuestran la intención de evolucionar hacia un diseño por puertos y adaptadores. Sin embargo, **no alcanza a ser Hexagonal, Onion ni Clean Architecture**:

- faltan las entidades de dominio (el centro está vacío),
- los puertos y use cases dependen de tipos del framework web,
- el orquestador —el componente de mayor riesgo— está acoplado a adaptadores concretos sin composition root,
- y existen dos implementaciones del mismo dominio (monolito vs microservicios) sobre dos bases de datos distintas.

La base de código está en el **punto ideal para madurar**: el salto a un diseño hexagonal/onion completo es una tarea de refactor acotada (ports, composition root y aislamiento de FastAPI), no una reescritura.
