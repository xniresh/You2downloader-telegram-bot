# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requisitos y el código fuente
COPY . .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instalar ffmpeg para el procesamiento de audio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Especificar el comando para ejecutar el bot
CMD ["python", "app.py"]
