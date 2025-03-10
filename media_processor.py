import os
import logging
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

# Configurar logging
logger = logging.getLogger(__name__)

# Función para añadir una miniatura (carátula) al archivo de audio MP3
async def add_thumbnail_to_audio(mp3_path, thumbnail_path):
    """
    Añade una miniatura como carátula a un archivo MP3.
    
    Args:
        mp3_path (str): Ruta al archivo MP3
        thumbnail_path (str): Ruta a la imagen de miniatura
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        # Verificar que ambos archivos existan
        if not os.path.exists(mp3_path):
            logger.error(f"El archivo MP3 no existe: {mp3_path}")
            return False
            
        if not os.path.exists(thumbnail_path):
            logger.warning(f"La miniatura no existe: {thumbnail_path}")
            return False
            
        # Añadir la carátula al archivo MP3
        audio = MP3(mp3_path, ID3=ID3)
        
        # Intentar añadir tags si no existen
        try:
            audio.add_tags()
        except:
            # Los tags ya existen, continuar
            pass
            
        # Leer y añadir la miniatura como carátula
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
            
        # Guardar los cambios
        audio.save()
        
        # Eliminar la miniatura después de usarla
        os.remove(thumbnail_path)
        
        return True
        
    except Exception as e:
        logger.error(f"Error al añadir la carátula: {e}")
        return False

# Función para limpiar archivos temporales
async def clean_files(file_paths):
    """
    Elimina los archivos especificados en la lista si existen.
    
    Args:
        file_paths (list): Lista de rutas de archivos a eliminar
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo eliminado: {file_path}")
        except Exception as e:
            logger.warning(f"Error al eliminar el archivo {file_path}: {e}")
