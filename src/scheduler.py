import schedule
import time
from datetime import datetime
import pytz
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from config import youtube_api_key, gemini_api_key, bot_token, user_preferences
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Timezone Madrid
madrid_tz = pytz.timezone('Europe/Madrid')

# Handlers
yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, None)

# Estado de videos encontrados
videos_found = {
    "@JoseLuisCavatv": False,
    "@nacho_ic": False
}

def reset_daily_status():
    """Resetea el estado diariamente a las 00:00"""
    global videos_found
    videos_found = {channel: False for channel in videos_found}
    logger.info("Estado diario reseteado")

def check_and_send_video(channel):
    """Busca video del canal y lo envía si existe"""
    global videos_found
    
    if videos_found[channel]:
        logger.info(f"{channel} ya procesado hoy")
        return
    
    logger.info(f"Buscando video de {channel}...")
    
    try:
        # Obtener usuarios interesados en este canal
        target_users = [chat_id for chat_id, prefs in user_preferences.items() 
                       if channel in prefs['channels']]
        
        if not target_users:
            logger.warning(f"No hay usuarios suscritos a {channel}")
            return
        
        # Buscar video
        video_data = yt.get_video_info_with_transcript(channel)
        
        if video_data and 'transcript' in video_data:
            logger.info(f"Video encontrado: {video_data['title']}")
            
            # Generar resumen
            summary = gemini.summarize_video(
                video_data['transcript'],
                video_data['title'], 
                video_data['channel_title']
            )
            
            if summary:
                message = f"📺 {video_data['title']}\n\n{summary}"
                telegram.send_to_users(message, None, target_users)
                
                videos_found[channel] = True
                logger.info(f"Resumen enviado para {channel}")
            else:
                logger.error(f"Error generando resumen para {channel}")
        else:
            logger.info(f"No hay video hoy de {channel}")
            
    except Exception as e:
        logger.error(f"Error procesando {channel}: {e}")

def job_cava():
    """Job para JoseLuisCavatv"""
    now = datetime.now(madrid_tz)
    
    # Solo ejecutar entre 10:30 y 14:00
    if now.hour < 10 or (now.hour == 10 and now.minute < 30) or now.hour >= 14:
        return
    
    check_and_send_video("@JoseLuisCavatv")

def job_nacho():
    """Job para nacho_ic"""
    now = datetime.now(madrid_tz)
    
    # Solo ejecutar entre 12:15 y 16:00
    if now.hour < 12 or (now.hour == 12 and now.minute < 15) or now.hour >= 16:
        return
    
    check_and_send_video("@nacho_ic")

# Programar tareas
schedule.every(3).minutes.do(job_cava)
schedule.every(3).minutes.do(job_nacho)
schedule.every().day.at("00:00").do(reset_daily_status)

logger.info("Scheduler iniciado")
logger.info("Cava: cada 5 min desde 10:30")
logger.info("Nacho: cada 5 min desde 12:15")

# Loop principal
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto