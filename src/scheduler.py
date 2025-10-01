import schedule
import time
from datetime import datetime
import pytz
from youtube_rss_handler import YouTubeRSSHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from database import Database
from financial_news_handler import FinancialNewsHandler
from config import gemini_api_key, bot_token, user_preferences
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Timezone Madrid
madrid_tz = pytz.timezone('Europe/Madrid')

# Handlers
yt_rss = YouTubeRSSHandler()  # No API key needed - uses RSS feeds!
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, None)
db = Database()
news_handler = FinancialNewsHandler()

def reset_daily_status():
    """No longer needed - database tracks daily status automatically"""
    logger.info("New day - database will track today's videos")

def check_and_send_video(channel_handle, youtube_channel_id, channel_language=['es']):
    """Busca video del canal y lo envía si existe"""
    today = datetime.now().strftime('%Y-%m-%d')

    # # Check if already processed today
    if db.has_video_been_processed(channel_handle, today):
        logger.info(f"{channel_handle} ya procesado hoy")
        return

    logger.info(f"Buscando video de {channel_handle} (RSS)...")

    try:
        # Get subscribers from database
        target_users = db.get_channel_subscribers(channel_handle)

        if not target_users:
            logger.warning(f"No hay usuarios suscritos a {channel_handle}")
            return

        # Check for youtube_channel_id
        if not youtube_channel_id:
            logger.warning(f"No YouTube channel ID set for {channel_handle}. Please update database.")
            return

        # Search for video using RSS (no API quota!)
        video_data = yt_rss.get_video_info_with_transcript(youtube_channel_id, channel_language)

        if video_data and 'transcript' in video_data:
            logger.info(f"Video encontrado: {video_data['title']}")

            # Generate summary
            summary = gemini.summarize_video(
                video_data['transcript'],
                video_data['title'],
                video_data['channel_title'],
            )

            if summary:
                message = f"📺 {video_data['channel_title']}\n\n{video_data['title']}\n\n{summary}\n\n{video_data['url']}"
                telegram.send_to_users(message, None, target_users)

                # Log summary to database
                db.add_summary(
                    channel_handle=channel_handle,
                    video_id=video_data.get('video_id', ''),
                    video_title=video_data['title'],
                    video_url=video_data.get('url', ''),
                    summary_text=summary,
                    video_date=today,
                    success=True
                )

                logger.info(f"Resumen enviado y guardado para {channel_handle}")
            else:
                logger.error(f"Error generando resumen para {channel_handle}")
                # Log failed attempt
                db.add_summary(
                    channel_handle=channel_handle,
                    video_id=video_data.get('video_id', ''),
                    video_title=video_data['title'],
                    video_url=video_data.get('url', ''),
                    summary_text='',
                    video_date=today,
                    success=False
                )
        else:
            logger.info(f"No hay video hoy de {channel_handle}")

    except Exception as e:
        logger.error(f"Error procesando {channel_handle}: {e}")

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
        check_and_send_video(
            channel['channel_handle'], 
            channel.get('youtube_channel_id'), 
            [channel.get('language')]
            )

def send_financial_news():
    """Send financial news summary to subscribers at 8:00 AM"""
    logger.info("Sending financial news summary...")

    try:
        # Get users who want news
        news_users = [chat_id for chat_id, prefs in user_preferences.items()
                      if prefs.get('wants_news', False)]

        if not news_users:
            logger.info("No users subscribed to financial news")
            return

        # Generate news summary
        summary = news_handler.create_news_summary()

        if summary:
            message = f"📰 *Today's Financial News Summary*\n\n{summary}"
            telegram.send_to_users(message, None, news_users)
            logger.info(f"Financial news sent to {len(news_users)} users")
        else:
            logger.warning("Failed to generate financial news summary")

    except Exception as e:
        logger.error(f"Error sending financial news: {e}")

# Schedule the unified job (reduced from 3 to 15 minutes since RSS is quota-free)
schedule.every(10).minutes.do(check_all_channels)
schedule.every().day.at("00:00").do(reset_daily_status)
schedule.every().day.at("09:00").do(send_financial_news)

logger.info("Scheduler iniciado")
logger.info("Checking all channels with subscribers every 10 minutes")
logger.info("Financial news scheduled for 09:00 daily")

# Loop principal
if __name__ == "__main__":
    check_all_channels()
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto