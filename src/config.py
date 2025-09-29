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
# TODO: add bravoscryptoresearch and midulive --- IGNORE ---
youtube_channels = [
    "@JoseLuisCavatv", 
    "@nacho_ic", 
    "@juanrallo", 
    "@bravosresearchcrypto", 
    "@bravosresearch"
    ]

user_preferences = {
    '37150610': {  # Victor Roman
        'channels': ["@JoseLuisCavatv", '@nacho_ic', '@juanrallo', '@bravosresearchcrypto', '@bravosresearch'],
        'user_name': 'Victor Roman',
        'wants_news': True
    },
    '1021945174': { # Alberto Salcedo
        'channels': ['@JoseLuisCavatv', '@nacho_ic'],
        'user_name': 'Alberto Salcedo',
        'wants_news': True
    }
}