# Carpeta app/core

## 1. Propósito

La carpeta `app/core` contiene la configuración central y la conexión a la base de datos.

Su función principal es:
- Gestionar variables de entorno
- Definir configuraciones globales
- Inicializar conexiones externas (como MongoDB)

Es utilizada por otras capas del sistema (services, repository, routes).

---

## 2. Archivos que contiene

- config.py
- mongo.py

---

## 3. Descripción de cada archivo

### config.py

Define la configuración global de la aplicación.

#### Responsabilidades:
- Cargar variables de entorno
- Establecer valores por defecto
- Centralizar la configuración del sistema

---

#### Funcionamiento

1. Usa `dotenv` para cargar variables desde un archivo `.env`
2. Lee variables del sistema con `os.getenv`
3. Define valores por defecto si no existen

---

#### Variables definidas

- `MONGO_URL`
  - URL de conexión a MongoDB
  - Valor por defecto: `mongodb://localhost:27017`

- `DATABASE_NAME`
  - Nombre de la base de datos

- `MAX_FILE_SIZE`
  - Tamaño máximo permitido para archivos (en bytes)
  - Default: 10MB

- `HOST`
  - Dirección donde corre el servidor

- `PORT`
  - Puerto del servidor

---

#### Uso

Estas variables son utilizadas por:
- `validators` → para validar tamaño de archivos
- `mongo.py` → para conexión a base de datos
- configuración general del servidor

---

### mongo.py

Define la conexión a la base de datos MongoDB.

#### Responsabilidades:
- Crear el cliente de MongoDB (`client`)
- Exponer la base de la aplicación (`database`)

#### Funcionamiento

1. Toma `MONGO_URL` y `DATABASE_NAME` de `config.py` (única fuente de configuración)
2. Crea el `MongoClient`
3. Selecciona la base `DATABASE_NAME` (por defecto `pdf_extractext`)
4. Solo la usa `core/dependencies.py` (composition root), que le pasa la colección al repositorio

---

## 4. Relación con otras capas

- `core/dependencies` → toma `database` y le inyecta la colección al repositorio MongoDB  
- `utils/validators` → usa `MAX_FILE_SIZE`  
- `services` → indirectamente dependen de la configuración  

---

## 5. Flujo de uso

1. Se carga la configuración al iniciar la app
2. Se establece la conexión a MongoDB
3. `dependencies.py` arma el repositorio con la colección; el resto importa solo configuración
4. Se utilizan en ejecución normal

---

## 6. Rol dentro del sistema

- Centraliza configuración
- Inicializa recursos globales
- Evita duplicación de valores en el código