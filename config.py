import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, "cookies", "cookies.txt")

# Configuración del bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
TELEGRAM_API_BASE_URL = 'http://telegram-api:8081/bot'  # URL base con /bot al final

# Configuración de descargas
DEFAULT_AUDIO_QUALITY = '192'  # Calidad de audio predeterminada
DEFAULT_VIDEO_FORMAT = 'best'  # Formato de video predeterminado
