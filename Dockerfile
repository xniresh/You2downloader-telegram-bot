# ---- Etapa de construcción ----
FROM python:3.9-slim AS builder

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar solo los archivos de requisitos
COPY requirements.txt .

# Instalar las dependencias en un virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Etapa final ----
FROM python:3.9-slim AS final

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el entorno virtual desde la etapa de construcción
COPY --from=builder /opt/venv /opt/venv

# Instalar solo los paquetes necesarios para la ejecución
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar el código de la aplicación
COPY app.py .
COPY config.py .
COPY telegram_interface.py .
COPY youtube_downloader.py .
COPY media_processor.py .
COPY cookies/ ./cookies/

# Crear un usuario no root para mayor seguridad
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Especificar el comando para ejecutar el bot
CMD ["python", "app.py"]
