# Análisis de cumplimiento TDD — pdf-extractext

**Rol:** Ingeniero de desarrollo — Revisión de Pull Request
**Alcance:** Todo el repositorio (monolito `app/` + `tests/` + los 4 microservicios en `services/`)
**Fecha:** 2026-08-17
**Referencia:** Skill `tdd` (red → green, seams acordados, vertical slices, anti-patterns)

---

## 1. Resumen ejecutivo

| Área | Veredicto |
|---|---|
| Monolito (`app/` + `tests/`) | Cumplimiento **parcial**. Buena estructura y seams de test razonables, pero la suite **está roja en `main`** (6 tests fallan) y la historia git no muestra red → green real. |
| `validator_service` | Cumplimiento parcial. Trae 17 tests en el mismo commit que la implementación (sin rojo previo). Rutas HTTP sin testear. |
| `extractor_service` | Cumplimiento parcial. Trae 5 tests en el mismo commit que la implementación. Rutas HTTP sin testear. |
| `persistence_service` | **No cumple.** Cero tests (solo `tests/__init__.py` vacío). Sin `uv.lock` propio. |
| `orchestrator_service` | **No cumple.** Cero tests. Es la lógica más crítica (orquestación + mapeo de errores) y no tiene ninguna especificación ejecutable. |
| CI / verificabilidad | Sin CI. `pytest` desde la raíz (como documenta el README) **no recolecta**: errores de resolución de módulos. |

**Conclusión:** el proyecto no cumple TDD en su sentido estricto. Lo más cercano a TDD está en los tests del monolito (bien especificados y en seams públicos), pero la evidencia de la historia git y el estado de la suite indican un flujo de "implementación primero, tests después y en el mismo commit", con dos microservicios publicados sin ningún test.

---

## 2. Metodología

1. **Análisis estático** del código de producción (`app/`, `services/*/app/`) y de los tests.
2. **Análisis de historia git** para reconstruir el orden temporal de tests vs. implementación.
3. **Ejecución de la suite** para verificar el estado real de los tests:

| Comando | Resultado |
|---|---|
| `uv run pytest tests/` (monolito) | **6 failed, 48 passed** |
| `uv run pytest` (raíz, como indica el README) | **4 errores de colección** (conflicto de resolución de `app`/`main` entre raíz y `services/`) |
| `pytest` dentro de `services/validator_service` | 17 passed |
| `pytest` dentro de `services/extractor_service` | 5 passed |
| `pytest` dentro de `services/orchestrator_service` | **no tests ran** |
| `pytest` dentro de `services/persistence_service` | **no tests ran** |

---

## 3. Evidencia de la historia git (orden test ↔ implementación)

| Commit | Contenido | Lectura TDD |
|---|---|---|
| `359b763` "Base de los test, agrego funcionalidad de test_archivo_inexistente" | Crea `app/utils/pdf_extractor.py` **y** `tests/test_extraer_texto_pdf.py` en el mismo commit | Implementación y test juntos; sin rojo previo demostrable |
| `6f2cfbe` "Primeros 8 tests terminados" | Modifica implementación (`+88`) y test (`+58`) juntos | Ciclos red→green no separados |
| `84d06b3` | Implementación de `extraer.py`, `pdf_service.py`, `pdf_extractor.py` | Refuerza que la implementación precedió a la madurez de los tests |
| `4d7e74e`, `cfa46e3`, `6d2d340`, `8939311` | Tests de API y DB agregados | Tests escritos **después** de existir la implementación |
| `29118ae` "Implementación de tests de integración" | Tests de integración | Llegan tarde, tras la implementación |
| `86e3005` "pdf corrupto devuelve vacío" | Cambia implementación a devolver `""` **pero** edita el test para esperar una excepción (con indentación rota) | Test contradictorio con la implementación que lo acompañó |
| `854e92f`, `9496c57` (Validator/Extractor service) | Implementación + tests en un mismo commit | Sin red antes que green |
| `fb48b7e` (Persistence + Orchestrator) | Implementación completa, **cero tests** | Antipatrón de slicing horizontal |

No existe evidencia de ningún ciclo donde un test fallara antes de la implementación (red) ni de una herramienta que lo registrara (CI, commits separados).

---

## 4. Evaluación por criterio de la skill TDD

### 4.1 ¿Red antes que green? — NO demostrado

- Los tests y la implementación se comprometen juntos desde el primer commit (`359b763`).
- Los tests de API, DB e integración (`4d7e74e`–`29118ae`) se agregaron después de que la implementación ya funcionaba.
- Los microservicios de persistencia y orquestador se publicaron sin ninguna prueba.

### 4.2 ¿Tests en seams públicos? — PARCIAL

Lo positivo (buenos seams):

- `tests/db/test_database.py` prueba `DocumentoRepository` exclusivamente por su interfaz pública (CRUD) sobre SQLite en memoria con aislamiento por test.
- `tests/api/test_api.py` prueba por la interfaz HTTP (`TestClient`) e inyecta el repositorio vía `dependency_overrides`.
- `tests/unit/test_extraer_texto_pdf.py` prueba `extraer_texto()` por su contrato público.
- `extractor_service` muestra inyección de dependencias testeada (`test_inject_custom_extractor`).

Lo que falta:

- **No hay seams acordados documentados.** No existe `CONTEXT.md` ni ADRs; la skill TDD exige acordar los seams con el usuario antes de escribir tests.
- **Side-channel:** `test_integracion_api_db.py` accede a `client._test_repo` (atributo inyectado a mano al `TestClient`) en lugar de observar el comportamiento por la interfaz.
- Los endpoints HTTP de `validator_service` (`/validate`) y `extractor_service` (rutas) no están cubiertos.

### 4.3 Anti-patterns detectados

1. **Tests acoplados a implementación (stale).** `test_api.py` parchea `app.routes.extraer.procesar_pdf`, atributo que ya no existe (fue importado con alias `procesar_pdf_service`). El refactor no cambió comportamiento y aun así rompió 5 tests → síntoma clásico de test acoplado al detalle interno.

2. **Test falso positivo.** `test_pdf_solo_firma_sin_contenido_valido_lanza_error` (líneas 200-206):
   - El bloque `with pytest.raises(Exception):` quedó **a nivel de clase** (indentación de 4 espacios, igual que `def`). Se ejecuta al importar el módulo, atrapa un `NameError` (`ruta_pdf` no definido en ese scope) y pasa silenciosamente: es código muerto.
   - El método de test en sí tiene **0 aserciones**: pasa sin verificar nada.
   - Comprobado vía AST: bloque `with` en cuerpo de clase en línea 205; método con 0 asserts.

3. **Test que contradice la implementación.** El commit `86e3005` declara "pdf corrupto devuelve vacío", pero el test editado en ese mismo commit dice "debe lanzar una excepción y no devolver vacío". La especificación y la implementación quedaron en direcciones opuestas.

4. **APIs deprecadas que rompen tests.** `test_fecha_es_datetime_valido` usa `datetime.utcnow()` (naive) y compara contra `fecha_procesamiento` aware (`datetime.now(UTC)` en `pdf_service.py`) → `TypeError: can't compare offset-naive and offset-aware datetimes`.

5. **Slicing horizontal en los microservicios.** El commit `fb48b7e` agregó dos servicios completos (repositorio, servicios, rutas, clientes HTTP, orquestación, mapeo de errores) sin ningún tracer bullet ni ciclo test→implementación.

### 4.4 Lo que sí está bien (para conservar)

- Los valores esperados en las aserciones son literales (fuente independiente de verdad), no recomputados por la implementación → no hay tests tautológicos.
- Los nombres de tests son descriptivos y leen como especificación ("PDF corrupto debe lanzar una excepción...").
- `test_database.py` es un buen ejemplo de suite de repositorio por contrato público con fixtures de BD limpia.
- El uso de `dependency_overrides` para inyectar el repositorio en API/integración es el seam correcto y sobrevive a refactors.
- `extractor_service` testea la inyección de un extractor alternativo, validando el seam por interfaz.

---

## 5. Hallazgos críticos de verificación

1. **La suite está roja en `main`** (monolito: 6 failed, 48 passed). Un PR que llegara así no debería mergearse.
2. **El comando documentado falla.** `pytest` desde la raíz no recolecta (4 errores) por conflicto de resolución entre el paquete `app/` de raíz y los `app/` de cada microservicio (`services/*/app/`). El README indica simplemente `pytest`.
3. **`persistence_service` y `orchestrator_service` no tienen tests**, a pesar de contener la lógica de mayor riesgo (persistencia MongoDB, orquestación de 3 servicios, mapeo de excepciones).
4. **`persistence_service` ni siquiera tiene `uv.lock`** propio, inconsistente con el resto de los servicios.

---

## 6. Recomendaciones

1. **Red antes que green para la deuda existente:**
   - Escribir tests para `orchestrator_service` (inyectando `ValidatorClient`, `ExtractorClient`, `PersistenceClient` como fakes/`httpx.MockTransport`), cubriendo: PDF inválido → `PDFExtractionError`; texto vacío → `PDFEmptyError`; flujo exitoso → persistencia llamada con el texto extraído.
   - Escribir tests para `persistence_service` (repositorio sobre MongoDB real/`mongomock`, y rutas con repositorio inyectado).
   - Cubrir los endpoints HTTP de `validator_service` (`/validate`) y `extractor_service`.

2. **Arreglar la suite antes de seguir:** corregir los targets de `patch` en `test_api.py`, la comparación de fechas en `test_integracion_api_db.py`, y el test falso positivo de `test_extraer_texto_pdf.py` (mover `with pytest.raises` dentro del método y decidir si el comportamiento esperado del PDF corrupto es `""` o excepción — implementación y test deben coincidir).

3. **Documentar los seams:** crear `CONTEXT.md` y/o ADRs que fijen dónde se prueba (HTTP, servicio, repositorio) para que los tests futuros se escriban en seams acordados.

4. **Separar los ciclos:** cada cambio debe ir en la forma "test que falla" → "implementación mínima" → "test verde", idealmente en commits separados o al menos en un PR donde la suite esté verde.

5. **Verificabilidad y CI:** habilitar CI que ejecute la suite por raíz y por cada microservicio en su propio directorio, para que `pytest` (documentado) sea reproducible y el estado verde sea obligatorio para mergear.

---

## 7. Veredicto final

**No cumple TDD** en su definición estricta (red → green, un slice por vez, seams acordados). Se reconoce un esfuerzo genuino de testing con buenos seams en el monolito y tests de calidad en `validator_service` y `extractor_service`, pero:

- la implementación siempre precedió o acompañó a los tests (nunca los precedió en rojo),
- dos servicios se publicaron sin ninguna prueba,
- la suite no está verde ni es ejecutable con el comando documentado.

El proyecto está en una posición intermedia entre "code that works without tests" y TDD real: tiene **tests útiles**, pero el proceso y el estado actual no satisfacen el ciclo TDD ni su gate de verificación.
