import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Load API keys
youtube_api_key = os.getenv('YOUTUBE_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# Channels to monitor
youtube_channels = ["@nacho_ic"]