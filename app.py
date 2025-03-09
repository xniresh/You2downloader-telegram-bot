import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

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

# Ruta al archivo de cookies
COOKIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies", "cookies.txt")

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
            # Configuración para video
            ydl_opts = {
                'format': 'best',
                'outtmpl': '%(title)s.%(ext)s',
                'cookiefile': COOKIES_PATH,
                'progress_hooks': [lambda d: progress_hook(d, update, context)],
            }
        elif user_choice == "🎵 Audio":  # Cambiar a elif para ser más específico
            # Configuración para audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'writethumbnail': True,
                'cookiefile': COOKIES_PATH,
                'progress_hooks': [lambda d: progress_hook(d, update, context)],
                'keepvideo': True,
            }
        else:
            await update.message.reply_text('Opción no válida. Por favor, elige entre video o audio.')
            return CHOOSE_FORMAT

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # Si se descargó solo audio, cambia la extensión del archivo
            if user_choice == "🎵 Audio":
                mp3_path = file_path.replace(".webm", ".mp3").replace(".mp4", ".mp3")
                thumbnail_path = mp3_path.replace(".mp3", ".webp")

                if os.path.exists(mp3_path):
                    try:
                        # Agrega la carátula al archivo de audio si existe la miniatura
                        if os.path.exists(thumbnail_path):
                            audio = MP3(mp3_path, ID3=ID3)
                            try:
                                audio.add_tags()
                            except:
                                pass

                            with open(thumbnail_path, 'rb') as thumb_file:
                                audio.tags.add(
                                    APIC(
                                        encoding=3,
                                        mime='image/webp',
                                        type=3,
                                        desc=u'Cover',
                                        data=thumb_file.read()
                                    )
                                )
                            audio.save()

                            # Elimina la miniatura después de usarla
                            os.remove(thumbnail_path)

                        # Enviar el archivo de audio con timeouts más largos
                        with open(mp3_path, 'rb') as media_file:
                            await update.message.reply_audio(
                                audio=media_file,
                                read_timeout=60,
                                write_timeout=60,
                                connect_timeout=60,
                                pool_timeout=60
                            )

                        # Eliminar los archivos después de enviarlos
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        os.remove(mp3_path)
                        
                        # Mensaje de éxito
                        await update.message.reply_text('¡Audio descargado y enviado con éxito!')
                        
                    except Exception as e:
                        logger.error(f"Error al procesar el audio: {e}")
                        # Intentar enviar el archivo aunque haya fallado el procesamiento de la carátula
                        try:
                            with open(mp3_path, 'rb') as media_file:
                                await update.message.reply_audio(
                                    audio=media_file,
                                    read_timeout=60,
                                    write_timeout=60,
                                    connect_timeout=60,
                                    pool_timeout=60
                                )
                            await update.message.reply_text('¡Audio enviado! (sin carátula)')
                        except Exception as send_error:
                            logger.error(f"Error al enviar el audio: {send_error}")
                            raise
                else:
                    raise FileNotFoundError(f"El archivo de audio {mp3_path} no se generó correctamente")
            else:
                # Enviar el archivo de video
                with open(file_path, 'rb') as media_file:
                    await update.message.reply_video(video=media_file)
                os.remove(file_path)

    except Exception as e:
        error_message = str(e)
        if "Timed out" in error_message:
            await update.message.reply_text('El archivo se descargó pero hubo un error al enviarlo. Intentando de nuevo...')
            try:
                # Intentar enviar el archivo una última vez
                if os.path.exists(mp3_path):
                    with open(mp3_path, 'rb') as media_file:
                        await update.message.reply_audio(
                            audio=media_file,
                            read_timeout=90,
                            write_timeout=90,
                            connect_timeout=90,
                            pool_timeout=90
                        )
            except Exception as retry_error:
                logger.error(f"Error en el reintento: {retry_error}")
                await update.message.reply_text('Lo siento, no se pudo enviar el archivo. Por favor, intenta de nuevo.')
        else:
            logger.error(f"Error al descargar el {user_choice.lower()}: {e}")
            await update.message.reply_text(f'Hubo un error al descargar el {user_choice.lower()}. Por favor, asegúrate de que el enlace es válido.')

    # Limpiar archivos que puedan haber quedado
    for file in [file_path, mp3_path, thumbnail_path]:
        try:
            if file and os.path.exists(file):
                os.remove(file)
        except:
            pass

    # Reiniciar la conversación para una nueva URL
    await update.message.reply_text('Envíame otra URL si deseas descargar otro video o audio.')
    return GET_URL

# Función para mostrar el progreso de la descarga
def progress_hook(d, update, context):
    if d['status'] == 'downloading':
        try:
            # Calcular el progreso
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = (downloaded_bytes / total_bytes) * 100
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024  # Convertir a MB/s
                    progress_text = f'Descargando: {progress:.1f}% | Velocidad: {speed_mb:.1f} MB/s'
                else:
                    progress_text = f'Descargando: {progress:.1f}%'
                
                # Actualizar el mensaje existente con manejo de errores
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        message = update.message._bot.edit_message_text(
                            chat_id=update.message.chat_id,
                            message_id=context.user_data['progress_message'].message_id,
                            text=progress_text,
                            read_timeout=30,
                            write_timeout=30,
                            connect_timeout=30,
                            pool_timeout=30
                        )
                        asyncio.create_task(message)
                except Exception as e:
                    logger.warning(f"Error al actualizar progreso: {e}")
                    pass  # Ignorar errores de actualización de progreso
        except Exception as e:
            logger.warning(f"Error en progress_hook: {e}")
            pass
    elif d['status'] == 'finished':
        # Actualizar mensaje cuando la descarga termine
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            message = update.message._bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=context.user_data['progress_message'].message_id,
                text="¡Descarga completada! Procesando archivo..."
            )
            asyncio.create_task(message)

# Función para cancelar la conversación
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operación cancelada. Envíame /start para comenzar de nuevo.')
    return ConversationHandler.END

# Función principal
def main() -> None:
    # Obtener el token desde las variables de entorno
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno")
    
    # Configurar la aplicación para usar el servidor API local
    application = (
        Application.builder()
        .token(token)
        .base_url(f'http://telegram-api:8081/bot')  # URL base con /bot al final
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

    # Inicia el bot
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()