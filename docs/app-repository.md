# Carpeta app/repository

## 1. Propósito

La carpeta `app/repository` contiene la capa de acceso a datos del sistema.

Su función principal es:
- Persistir información en la base de datos
- Recuperar datos almacenados
- Aislar la lógica de base de datos del resto de la aplicación

Permite desacoplar la lógica de negocio de la tecnología de almacenamiento.

---

## 2. Archivos que contiene

- documento_repository.py
- mongodb_repository.py

---

## 3. Descripción de cada archivo

### documento_repository.py

Implementa un repositorio utilizando SQLite.

#### Responsabilidades:
- Guardar documentos en la base de datos
- Consultar documentos
- Actualizar registros
- Eliminar datos
- Contar registros

---

#### Funcionamiento

Utiliza una conexión SQLite (`sqlite3.Connection`) para ejecutar consultas SQL.

#### Métodos principales:

- `guardar(...)`
  - Inserta un documento en la base de datos
  - Retorna el ID generado

- `obtener_por_id(id)`
  - Busca un documento por ID
  - Retorna un diccionario o `None`

- `obtener_por_nombre(nombre)`
  - Busca un documento por nombre

- `listar_todos()`
  - Devuelve todos los documentos

- `actualizar(...)`
  - Modifica un documento existente
  - Retorna `True` o `False`

- `eliminar(id)`
  - Elimina un documento
  - Retorna `True` o `False`

- `contar()`
  - Retorna la cantidad total de documentos

---

#### Características

- Usa SQL directamente
- Convierte fechas a formato ISO
- Devuelve datos como diccionarios

---

### mongodb_repository.py

Implementa un repositorio utilizando MongoDB.

#### Responsabilidades:
- Persistir documentos en MongoDB
- Consultar documentos
- Eliminar registros
- Contar documentos

---

#### Funcionamiento

Utiliza una colección de MongoDB obtenida desde `core/db.py`.

#### Métodos principales:

- `guardar(...)`
  - Inserta un documento en MongoDB
  - Retorna el ID generado como string

- `obtener_por_id(id)`
  - Busca un documento usando `ObjectId`
  - Retorna un diccionario o `None`

- `obtener_por_nombre(nombre)`
  - Busca un documento por nombre

- `listar_todos()`
  - Devuelve todos los documentos ordenados

- `eliminar(id)`
  - Elimina un documento
  - Retorna `True` o `False`

- `contar()`
  - Cuenta documentos almacenados

---

#### Características

- Usa `ObjectId` para identificar documentos
- Maneja errores en conversiones de ID
- Devuelve datos en formato diccionario

---

## 4. Relación entre ambos repositorios

Ambos repositorios:

- Implementan la misma lógica de operaciones
- Permiten intercambiar la base de datos sin cambiar el resto del sistema

Uso típico:
- SQLite → tests
- MongoDB → producción

---

## 5. Relación con otras capas

- `services` → usan repository para guardar y obtener datos  
- `core/db` → provee conexión a MongoDB  
- `routes` → no acceden directamente  

---

## 6. Flujo de uso

1. El servicio recibe datos procesados
2. Llama al repositorio correspondiente
3. El repositorio guarda o consulta la base de datos
4. Devuelve el resultado al servicio

---

## 7. Rol dentro del sistema

- Encapsula el acceso a datos
- Evita que otras capas conozcan detalles de la base de datos
- Permite cambiar de tecnología sin afectar la lógica de negocio