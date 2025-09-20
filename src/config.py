import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()

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

# Channels to monitor
youtube_channels = ["@JoseLuisCavatv", "@nacho_ic"]