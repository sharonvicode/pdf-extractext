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
- db.py

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
- `db.py` → para conexión a base de datos
- configuración general del servidor

---

### db.py

Define la conexión a la base de datos MongoDB.

#### Responsabilidades:
- Crear cliente de MongoDB
- Establecer conexión a la base de datos
- Exponer la instancia de la base (`db`)

---

#### Funcionamiento

1. Carga variables de entorno con dotenv
2. Obtiene `MONGO_URL`
3. Crea un cliente MongoDB (`MongoClient`)
4. Selecciona una base de datos (`mi_base`)
5. Expone la variable `db` para ser usada en otros módulos

---

#### Detalles importantes

- La base usada es `"mi_base"` (hardcodeada)
- Imprime la URL de conexión (para debug)

---

## 4. Relación con otras capas

- `repository` → usa `db` para acceder a MongoDB  
- `utils/validators` → usa `MAX_FILE_SIZE`  
- `services` → indirectamente dependen de la configuración  

---

## 5. Flujo de uso

1. Se carga la configuración al iniciar la app
2. Se establece la conexión a MongoDB
3. Otros módulos importan `db` o variables de configuración
4. Se utilizan en ejecución normal

---

## 6. Rol dentro del sistema

- Centraliza configuración
- Inicializa recursos globales
- Evita duplicación de valores en el código