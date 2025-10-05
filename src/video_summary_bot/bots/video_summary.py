"""Video summary bot - Processes today's videos from configured channels"""

from video_summary_bot.handlers import YouTubeHandler, GeminiHandler, TelegramHandler
from video_summary_bot.config import youtube_api_key, gemini_api_key, bot_token
from video_summary_bot.database import Database
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """Main bot execution - processes channels from database"""
    yt = YouTubeHandler(youtube_api_key)
    gemini = GeminiHandler(gemini_api_key)
    telegram = TelegramHandler(bot_token, None)
    db = Database()

    # Get all active channels from database
    channels = db.get_all_channels(active_only=True)

    if not channels:
        print("⚠️  No active channels found in database")
        return

    for channel in channels:
        channel_handle = channel['channel_handle']

        # Get users subscribed to this channel
        target_users = db.get_channel_subscribers(channel_handle)

        if not target_users:
            logger.info(f"No subscribers for {channel_handle}, skipping")
            continue

        # Get today's video
        video_data = yt.get_video_info_with_transcript(channel_handle)

        if video_data and 'transcript' in video_data:
            summary = gemini.summarize_video(
                video_data['transcript'],
                video_data['title'],
                video_data['channel_title']
            )
            if summary:
                message = f"📺 {video_data['title']}\n\n{summary}"
                telegram.send_to_users(message, None, target_users)
                print(f"✅ Summary sent for {channel_handle}!")
            else:
                print(f"❌ Failed to generate summary for {channel_handle}")
        else:
            print(f"ℹ️  No video or transcript found for {channel_handle}")


if __name__ == "__main__":
    main()
