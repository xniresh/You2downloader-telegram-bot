# YTDown-Telegram Bot

## Descripción

YTDown-Telegram es un bot de Telegram que permite a los usuarios descargar videos o extraer audio de YT de manera sencilla.

## Características

- Descarga de videos de YouTube en la mejor calidad disponible
- Extracción de audio en formato MP3 con metadatos y carátula
- Interfaz conversacional intuitiva mediante botones
- Indicador de progreso durante la descarga (falta mejorar - sigue en fase de prueba)
- Soporte para cookies (falta mejorar - sigue en fase de prueba)
- Implementación en contenedores Docker para fácil despliegue

## Requisitos

- Python 3.9 o superior (solo si quieres correrlo en local)
- API de Telegram (ID de API, Hash de API y Token de Bot)
- Docker y Docker Compose (para despliegue en contenedores)
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
   git clone https://github.com/tu-usuario/YTDown-Telegram.git
   cd YTDown-Telegram
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
 NOTA: Es mejor probarlo en local mediante docker para evitar instalaciones innecesarias en el sistema.

### Despliegue con Docker (producción)

1. Asegúrate de tener Docker y Docker Compose instalados

2. Ejecuta el bot con Docker Compose:
   ```bash
   docker-compose up -d
   ```

   Esto iniciará dos contenedores:
   - Un servidor local de la API de Telegram
   - El bot de YouTube Downloader

## Uso

1. Inicia una conversación con tu bot en Telegram
2. Envía el comando `/start` para recibir instrucciones
3. Envía la URL de un video de YouTube
4. Selecciona si deseas descargar el video o extraer el audio
5. Espera a que el bot procese y envíe el archivo

## Estructura del proyecto

```
YTDown-Telegram/
├── app.py              # Código principal del bot
├── requirements.txt    # Dependencias del proyecto
├── Dockerfile          # Configuración para construir la imagen Docker
├── docker-compose.yml  # Configuración para desplegar con Docker Compose
├── .env                # Variables de entorno (no incluido en el repositorio)
├── cookies/            # Directorio para almacenar cookies
│   └── cookies.txt     # Archivo de cookies para YouTube
└── .gitignore         # Archivos y directorios ignorados por git
```

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
- Telegram tiene un límite de 50MB para bots pero con el telegram api server configurado en el docker compose no deberia haber problemas con enviar hasta 2GB.
- Para videos más grandes, considera usar la opción de audio
