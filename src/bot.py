# Test both handlers together
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load API keys
youtube_api_key = os.getenv('YOUTUBE_API_KEY')
if not youtube_api_key:
    logger.error("❌ Please set YOUTUBE_API_KEY in .env file")
    exit(1)
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    logger.error("❌ Please set GEMINI_API_KEY in .env file")
    exit(1)
    
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not bot_token:
    print("Set TELEGRAM_BOT_TOKEN in .env file")
    exit(1)
    
if not chat_id:
    print("Set TELEGRAM_CHAT_ID in .env file")
    exit(1)
    
yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)

video_data = yt.get_video_info_with_transcript("@JoseLuisCavatv")
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