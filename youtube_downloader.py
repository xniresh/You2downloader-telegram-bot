import os
import logging
import asyncio
import time
from yt_dlp import YoutubeDL
from media_processor import add_thumbnail_to_audio, clean_files
import config

# Configurar logging
logger = logging.getLogger(__name__)

# Diccionario para controlar la frecuencia de actualizaciones
_last_progress_updates = {}
# Intervalo mínimo entre actualizaciones (en segundos)
_UPDATE_INTERVAL = 3

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
                
                # Limitar actualizaciones usando un intervalo de tiempo
                chat_id = update.message.chat_id
                current_time = time.time()
                
                # Solo actualizar si ha pasado suficiente tiempo desde la última actualización
                if chat_id not in _last_progress_updates or current_time - _last_progress_updates[chat_id] >= _UPDATE_INTERVAL:
                    _last_progress_updates[chat_id] = current_time
                    
                    if speed:
                        speed_mb = speed / 1024 / 1024  # Convertir a MB/s
                        progress_text = f'Descargando: {progress:.1f}% | Velocidad: {speed_mb:.1f} MB/s'
                    else:
                        progress_text = f'Descargando: {progress:.1f}%'
                    
                    # Actualizar el mensaje existente con manejo de errores
                    try:
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
        except Exception as e:
            logger.warning(f"Error en progress_hook: {e}")
    elif d['status'] == 'finished':
        # Limpiar entrada de control de frecuencia
        chat_id = update.message.chat_id
        if chat_id in _last_progress_updates:
            del _last_progress_updates[chat_id]
            
        # Actualizar mensaje cuando la descarga termine
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                message = update.message._bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    message_id=context.user_data['progress_message'].message_id,
                    text="¡Descarga completada! Procesando archivo..."
                )
                asyncio.create_task(message)
        except Exception as e:
            logger.warning(f"Error al actualizar mensaje de finalización: {e}")

# Función para descargar video
async def download_video(url, update, context):
    # Configuración para video
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': config.COOKIES_PATH,
        'progress_hooks': [lambda d: progress_hook(d, update, context)],
    }
    
    file_path = None
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Enviar el archivo de video
            with open(file_path, 'rb') as media_file:
                await update.message.reply_video(
                    video=media_file,
                    read_timeout=60,
                    write_timeout=60,
                    connect_timeout=60,
                    pool_timeout=60
                )
                
            await update.message.reply_text('¡Video descargado y enviado con éxito!')
    finally:
        # Limpiar archivos
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# Función para descargar audio
async def download_audio(url, update, context):
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
        'cookiefile': config.COOKIES_PATH,
        'progress_hooks': [lambda d: progress_hook(d, update, context)],
        'keepvideo': True,
    }
    
    file_path = None
    mp3_path = None
    thumbnail_path = None
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Cambiar la extensión del archivo para el mp3
            mp3_path = file_path.replace(".webm", ".mp3").replace(".mp4", ".mp3")
            thumbnail_path = mp3_path.replace(".mp3", ".webp")
            
            if os.path.exists(mp3_path):
                # Intentar añadir la miniatura al archivo de audio
                success = await add_thumbnail_to_audio(mp3_path, thumbnail_path)
                
                # Enviar el archivo de audio
                with open(mp3_path, 'rb') as media_file:
                    await update.message.reply_audio(
                        audio=media_file,
                        read_timeout=60,
                        write_timeout=60,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                
                if success:
                    await update.message.reply_text('¡Audio descargado y enviado con éxito!')
                else:
                    await update.message.reply_text('¡Audio enviado! (sin carátula)')
            else:
                raise FileNotFoundError(f"El archivo de audio {mp3_path} no se generó correctamente")
    except Exception as e:
        error_message = str(e)
        if "Timed out" in error_message:
            # Intentar una última vez con timeouts más largos
            try:
                if mp3_path and os.path.exists(mp3_path):
                    with open(mp3_path, 'rb') as media_file:
                        await update.message.reply_audio(
                            audio=media_file,
                            read_timeout=90,
                            write_timeout=90,
                            connect_timeout=90,
                            pool_timeout=90
                        )
                    await update.message.reply_text('¡Audio enviado en el segundo intento!')
            except Exception as retry_error:
                logger.error(f"Error en el reintento: {retry_error}")
                raise
        else:
            raise
    finally:
        # Limpiar archivos utilizando la función del módulo media_processor
        await clean_files([file_path, mp3_path, thumbnail_path])
