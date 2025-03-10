"""You2downloader - Bot de Telegram para descargar videos de YouTube
Archivo principal que coordina los módulos del bot"""

import os
import logging
from telegram.ext import Application

# Importar módulos propios
import config
from telegram_interface import setup_bot

# Configurar logging para la aplicación principal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """
    Función principal que inicia el bot de Telegram.
    """
    # Verificar que el token está disponible en las variables de entorno
    if not config.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno")
    
    logger.info("Iniciando el bot de You2downloader...")
    
    # Configurar la aplicación del bot usando el módulo telegram_interface
    application = setup_bot(
        token=config.TELEGRAM_BOT_TOKEN,
        base_url=config.TELEGRAM_API_BASE_URL
    )
    
    # Inicia el bot
    logger.info("Bot iniciado correctamente. Esperando comandos...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()