# You2downloader - Bot de Telegram

## Descripción

You2downloader es un bot de Telegram modular que permite a los usuarios descargar videos o extraer audio de YouTube de manera sencilla y eficiente.

## Características

- Descarga de videos de YouTube con selección de calidad (desde 1080p+ hasta 360p)
- Extracción de audio en formato MP3 con metadatos, carátula y calidad configurable (96-320kbps)
- Interfaz conversacional intuitiva mediante botones
- Indicador de progreso optimizado durante la descarga
- Soporte para cookies para acceder a contenido con restricciones
- Implementación en contenedores Docker con multi-stage build para despliegue eficiente
- Arquitectura modular para mejor mantenimiento y extensibilidad

## Requisitos

- Python 3.9 o superior (solo si quieres correrlo en local)
- API de Telegram (ID de API, Hash de API y Token de Bot)
- Docker y Docker Compose (para despliegue en contenedores, recomendado)
- ffmpeg (para procesamiento de audio)

## Instalación

### Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
TELEGRAM_API_ID=tu_api_id
TELEGRAM_API_HASH=tu_api_hash
TELEGRAM_BOT_TOKEN=tu_token_de_bot
```

Puedes obtener estas credenciales en [my.telegram.org](https://my.telegram.org) y el token del bot a través de [@BotFather](https://t.me/BotFather) en Telegram.

### Instalación local (desarrollo)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/xniresh/You2downloader-telegram-bot.git
   cd You2downloader-telegram-bot
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Instala ffmpeg (necesario para el procesamiento de audio):
   - En Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - En Windows: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade a PATH

4. Ejecuta el bot:
   ```bash
   python app.py
   ```
**NOTA**: Es mejor probarlo mediante Docker para evitar instalaciones innecesarias en el sistema.

### Despliegue con Docker (recomendado)

1. Asegúrate de tener Docker y Docker Compose instalados

2. Ejecuta el bot con Docker Compose:
   ```bash
   docker-compose up -d
   ```

   Esto iniciará dos contenedores:
   - Un servidor local de la API de Telegram
   - El bot de YouTube Downloader (con imagen optimizada mediante multi-stage build)

## Uso

1. Inicia una conversación con tu bot en Telegram
2. Envía el comando `/start` para recibir instrucciones
3. Envía la URL de un video de YouTube
4. Selecciona si deseas descargar el video o extraer el audio
5. Elige la calidad que prefieres para el formato seleccionado
6. Espera a que el bot procese y envíe el archivo (verás actualizaciones de progreso)

## Estructura del proyecto

```
You2downloader-telegram-bot/
├── app.py                # Punto de entrada principal de la aplicación
├── config.py              # Configuraciones centralizadas
├── telegram_interface.py   # Módulo para interacción con Telegram
├── youtube_downloader.py  # Módulo para descargas de YouTube
├── media_processor.py     # Módulo para procesamiento de archivos multimedia
├── requirements.txt       # Dependencias del proyecto
├── Dockerfile             # Configuración optimizada con multi-stage build
├── docker-compose.yml     # Configuración para desplegar con Docker Compose
├── .env                   # Variables de entorno (no incluido en el repositorio)
├── cookies/               # Directorio para almacenar cookies
│   └── cookies.txt        # Archivo de cookies para YouTube
└── .gitignore            # Archivos y directorios ignorados por git
```

## Mejoras recientes

### 1. Arquitectura Modular
Se ha refactorizado el código para seguir una estructura modular con separación clara de responsabilidades:
- `telegram_interface.py`: Maneja la interacción con Telegram
- `youtube_downloader.py`: Lógica de descarga de YouTube
- `media_processor.py`: Procesamiento de archivos multimedia
- `config.py`: Centraliza la configuración

### 2. Optimización de Docker con Multi-stage Build
El Dockerfile ha sido optimizado usando multi-stage build para:
- Reducir significativamente el tamaño de la imagen final
- Mejorar la seguridad ejecutando como usuario no privilegiado
- Optimizar la estructura de capas para builds más rápidos

### 3. Rate Limiting para Actualizaciones de Progreso
Se ha implementado un sistema de limitación de frecuencia para las actualizaciones de progreso, evitando timeouts en la API de Telegram y mejorando la estabilidad del bot.

### 4. Selección de Calidad de Descarga
Se ha añadido la posibilidad de seleccionar la calidad deseada tanto para videos como para audios:
- **Videos**: Opciones desde máxima calidad (1080p+) hasta calidad baja (360p)
- **Audios**: Opciones desde alta fidelidad (320kbps) hasta calidad ligera (96kbps)

## Solución de problemas

### El bot no responde
- Verifica que las credenciales en el archivo `.env` sean correctas
- Asegúrate de que el bot esté en ejecución
- Comprueba los logs para identificar posibles errores

### Error al descargar videos
- Verifica que la URL del video sea válida y accesible
- Comprueba que el video no tenga restricciones geográficas o de edad
- Si hay restricciones de edad, configura correctamente el archivo de cookies

### Error al enviar archivos grandes
- Telegram tiene un límite de 50MB para bots, pero con el servidor API de Telegram configurado en el docker-compose se pueden enviar archivos de hasta 2GB
- Para videos muy grandes, considera usar la opción de audio

### Timeouts en la API de Telegram
- Se ha implementado un sistema de rate limiting para evitar este problema
- Si persiste, verifica la conexión de red y los logs para más detalles
