FROM python:3.12-slim

# Instalar dependencias del sistema para Tesseract y PyMuPDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root por seguridad
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar archivos de dependencias primero (cache de Docker)
COPY pyproject.toml uv.lock ./

# Instalar dependencias
RUN uv sync --frozen --no-dev

# Copiar código
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]