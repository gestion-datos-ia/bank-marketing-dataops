FROM python:3.12-slim

# 1. Instalar dependencias esenciales del sistema para PostgreSQL y compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Variables de control para optimizar Python dentro del contenedor
ENV POETRY_VERSION=2.0.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Instalar la versión exacta de Poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# 4. Copiar archivos de dependencias e instalarlas en el sistema global del contenedor
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 5. Copiar el código fuente y el dataset requerido
COPY src/ /app/src/
COPY data/ /app/data/

# 6. Ejecutar el pipeline de forma modular para evitar fallos de rutas
CMD ["poetry", "run", "python", "-m", "src.main"]