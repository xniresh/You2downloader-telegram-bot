import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Importar los demás módulos
from youtube_downloader import download_video, download_audio
import config

# Configura el logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de la conversación
GET_URL, CHOOSE_FORMAT = range(2)

# Opciones para el menú
CHOOSE_FORMAT_KEYBOARD = [["🎥 Video", "🎵 Audio"]]

# Función para manejar el comando /start
async def start(update: Update, context: CallbackContext) -> int:
    # Mensaje de bienvenida e instrucciones
    instructions = (
        "¡Hola! Soy un bot que te permite descargar videos o audio de YouTube. "
        "Sigue estos pasos para usarme:\n\n"
        "1. Envíame la URL de un video de YouTube.\n"
        "2. Elige si deseas descargar el video o solo el audio.\n"
        "3. ¡Listo! Te enviaré el archivo que elegiste.\n\n"
        "Puedes enviarme tantas URLs como quieras. ¡Comencemos!"
    )
    await update.message.reply_text(instructions)
    return GET_URL

# Función para manejar la URL enviada
async def get_url(update: Update, context: CallbackContext) -> int:
    url = update.message.text
    # Limpiar la URL para mantener solo el ID del video
    if '&' in url:
        url = url.split('&')[0]
    context.user_data['url'] = url  # Guarda la URL limpia en el contexto

    # Pregunta si quiere video o audio
    await update.message.reply_text(
        '¿Qué deseas descargar? Elige una opción:',
        reply_markup=ReplyKeyboardMarkup(CHOOSE_FORMAT_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_FORMAT

# Función para manejar la elección del formato
async def choose_format(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    url = context.user_data.get('url')  # Obtener la URL guardada anteriormente

    if not url:
        await update.message.reply_text('No se encontró una URL válida. Por favor, envía primero el enlace del video.')
        return GET_URL

    try:
        # Enviar mensaje inicial de progreso
        progress_message = await update.message.reply_text('Iniciando descarga...')
        context.user_data['progress_message'] = progress_message

        if user_choice == "🎥 Video":
            await download_video(url, update, context)
        elif user_choice == "🎵 Audio":
            await download_audio(url, update, context)
        else:
            await update.message.reply_text('Opción no válida. Por favor, elige entre video o audio.')
            return CHOOSE_FORMAT

    except Exception as e:
        error_message = str(e)
        if "Timed out" in error_message:
            await update.message.reply_text('El archivo se descargó pero hubo un error al enviarlo. Por favor, intenta de nuevo.')
        else:
            logger.error(f"Error al descargar: {e}")
            await update.message.reply_text(f'Hubo un error al descargar el {user_choice.lower()}. Por favor, asegúrate de que el enlace es válido.')

    # Reiniciar la conversación para una nueva URL
    await update.message.reply_text('Envíame otra URL si deseas descargar otro video o audio.')
    return GET_URL

# Función para cancelar la conversación
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operación cancelada. Envíame /start para comenzar de nuevo.')
    return ConversationHandler.END

# Función para inicializar la aplicación del bot
def setup_bot(token, base_url):
    # Configurar la aplicación para usar el servidor API local
    application = (
        Application.builder()
        .token(token)
        .base_url(base_url)
        .build()
    )

    # Configura el manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_url)],
            CHOOSE_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_format)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Registra el manejador de conversación
    application.add_handler(conv_handler)
    
    return application
