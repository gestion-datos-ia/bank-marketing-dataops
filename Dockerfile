FROM python:3.12-slim

# 1. Instalar dependencias esenciales del sistema para PostgreSQL y compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Variables de control para fijar la versión de Poetry y optimizar Python
ENV POETRY_VERSION=2.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Instalar la versión exacta de Poetry del proyecto
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# 4. Copiar las configuraciones de dependencias
COPY pyproject.toml poetry.lock* /app/

# 5. SOLUCIÓN: Forzamos la regeneración del lock dentro del contenedor antes de instalar
RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-interaction --no-ansi

# 6. Crear la estructura física de carpetas requerida por config.py
RUN mkdir -p /app/data/raw /app/data/processed /app/data/logs

# 7. Copiar el código fuente y el dataset
COPY src/ /app/src/
COPY data/raw/02_bank.csv /app/data/raw/02_bank.csv

# 8. Ejecutar el orquestador usando el entorno controlado de Poetry
CMD ["poetry", "run", "python", "-m", "src.main"]