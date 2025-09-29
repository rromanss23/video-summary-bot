import schedule
import time
from datetime import datetime
import pytz
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from database import Database
from config import youtube_api_key, gemini_api_key, bot_token
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
db = Database()

def reset_daily_status():
    """No longer needed - database tracks daily status automatically"""
    logger.info("New day - database will track today's videos")

def check_and_send_video(channel):
    """Busca video del canal y lo envía si existe"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if already processed today
    if db.has_video_been_processed(channel, today):
        logger.info(f"{channel} ya procesado hoy")
        return

    logger.info(f"Buscando video de {channel}...")

    try:
        # Get subscribers from database
        target_users = db.get_channel_subscribers(channel)

        if not target_users:
            logger.warning(f"No hay usuarios suscritos a {channel}")
            return

        # Search for video
        video_data = yt.get_video_info_with_transcript(channel)

        if video_data and 'transcript' in video_data:
            logger.info(f"Video encontrado: {video_data['title']}")

            # Generate summary
            summary = gemini.summarize_video(
                video_data['transcript'],
                video_data['title'],
                video_data['channel_title']
            )

            if summary:
                message = f"📺 {video_data['title']}\n\n{summary}"
                telegram.send_to_users(message, None, target_users)

                # Log summary to database
                db.add_summary(
                    channel_handle=channel,
                    video_id=video_data.get('video_id', ''),
                    video_title=video_data['title'],
                    video_url=video_data.get('url', ''),
                    summary_text=summary,
                    video_date=today,
                    success=True
                )

                logger.info(f"Resumen enviado y guardado para {channel}")
            else:
                logger.error(f"Error generando resumen para {channel}")
                # Log failed attempt
                db.add_summary(
                    channel_handle=channel,
                    video_id=video_data.get('video_id', ''),
                    video_title=video_data['title'],
                    video_url=video_data.get('url', ''),
                    summary_text='',
                    video_date=today,
                    success=False
                )
        else:
            logger.info(f"No hay video hoy de {channel}")

    except Exception as e:
        logger.error(f"Error procesando {channel}: {e}")

def check_all_channels():
    """Check all channels with subscribers at their defined times"""
    now = datetime.now(madrid_tz)

    # Get all active channels
    channels = db.get_all_channels(active_only=True)

    for channel in channels:
        # Check if there are subscribers
        subscribers = db.get_channel_subscribers(channel['channel_handle'])
        if not subscribers:
            continue

        # Check if within the time window
        start_hour = channel['check_start_hour']
        start_minute = channel['check_start_minute']
        end_hour = channel['check_end_hour']

        # Check if current time is within the window
        start_time_minutes = start_hour * 60 + start_minute
        current_time_minutes = now.hour * 60 + now.minute
        end_time_minutes = end_hour * 60

        if current_time_minutes < start_time_minutes or current_time_minutes >= end_time_minutes:
            continue

        # Process the channel
        check_and_send_video(channel['channel_handle'])

# Schedule the unified job
schedule.every(3).minutes.do(check_all_channels)
schedule.every().day.at("00:00").do(reset_daily_status)

logger.info("Scheduler iniciado")
logger.info("Checking all channels with subscribers every 3 minutes")

# Loop principal
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto