from gemini_handler import GeminiHandler
from config import gemini_api_key, bot_token, chat_id
from telegram_handler import TelegramHandler
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
    
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)

news_summary = gemini.get_todays_news()

if news_summary:
    logger.info("Sending news summary to Telegram...")
    message = f"📰 *Today's Financial News Summary*\n\n{news_summary}"
    if telegram.send_message(message, None):
        print("✅ News summary sent to Telegram!")
    else:
        print("❌ Failed to send news summary to Telegram")