# Test both handlers together
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from config import youtube_api_key, gemini_api_key, bot_token, chat_id, youtube_channels
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
    
yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)

for channel in youtube_channels:
    logger.info(f"Checking channel: {channel}")
    
    # Get latest video with transcript
    video_data = yt.get_video_info_with_transcript(channel)
    if video_data and 'transcript' in video_data:
        summary = gemini.summarize_video(
            video_data['transcript'],
            video_data['title'], 
            video_data['channel_title']
        )
        print(summary)
        if summary:
            message = f"📺 *{video_data['title']}*\n\n{summary}\n\n🔗 https://www.youtube.com/watch?v={video_data['id']}"
            logger.info("Sending summary to Telegram...: ", message)
            if telegram.send_message(message):
                print("✅ Summary sent to Telegram!")
            else:
                print("❌ Failed to send summary to Telegram")
        else:
            print("❌ Failed to generate summary")
    else:
        print("❌ Failed to retrieve video data or transcript")