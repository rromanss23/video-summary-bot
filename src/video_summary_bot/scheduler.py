"""Scheduler for automated video processing"""

import schedule
import time
from datetime import datetime
import pytz
import logging

from video_summary_bot.handlers import YouTubeRSSHandler, GeminiHandler, TelegramHandler
from video_summary_bot.database import Database
from video_summary_bot.config import gemini_api_key, bot_token

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


def reset_daily_status():
    """No longer needed - database tracks daily status automatically"""
    logger.info("New day - database will track today's videos")


def check_and_send_video(channel_handle, youtube_channel_id, channel_language=['es']):
    """Search for channel video and send if exists"""
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if already processed today
    if db.has_video_been_processed(channel_handle, today):
        logger.info(f"{channel_handle} already processed today")
        return

    logger.info(f"Searching for video from {channel_handle} (RSS)...")

    try:
        # Get subscribers from database
        target_users = db.get_channel_subscribers(channel_handle)

        if not target_users:
            logger.warning(f"No users subscribed to {channel_handle}")
            return

        # Check for youtube_channel_id
        if not youtube_channel_id:
            logger.warning(f"No YouTube channel ID set for {channel_handle}. Please update database.")
            return

        # Search for video using RSS (no API quota!)
        video_data = yt_rss.get_video_info_with_transcript(youtube_channel_id, channel_language)

        if video_data and 'transcript' in video_data:
            logger.info(f"Video found: {video_data['title']}")

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

                logger.info(f"Summary sent and saved for {channel_handle}")
            else:
                logger.error(f"Error generating summary for {channel_handle}")
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
            logger.info(f"No video today from {channel_handle}")

    except Exception as e:
        logger.error(f"Error processing {channel_handle}: {e}")


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


# Schedule jobs
schedule.every(10).minutes.do(check_all_channels)
schedule.every().day.at("00:00").do(reset_daily_status)

logger.info("Scheduler started")
logger.info("Checking all channels with subscribers every 10 minutes")


def main():
    """Main scheduler loop"""
    check_all_channels()
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
