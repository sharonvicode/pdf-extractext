# Imagen base oficial de Python 3.12 slim
FROM python:3.12-slim

# Variables de entorno recomendadas para Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear un usuario y grupo no root por seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero los archivos de configuración de dependencias para aprovechar la caché de capas
COPY pyproject.toml uv.lock .python-version ./

# Instalar uv y las dependencias del proyecto en el entorno global del contenedor
RUN pip install --no-cache-dir uv && \
    uv sync

# Copiar el código fuente de la aplicación
COPY app/ ./app/
COPY main.py ./

# Asignar permisos del directorio de trabajo al usuario no root
RUN chown -R appuser:appuser /app

# Cambiar al usuario no root
USER appuser

# Exponer el puerto en el que se ejecutará la aplicación FastAPI
EXPOSE 8000

# Comando por defecto para levantar el servidor Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
