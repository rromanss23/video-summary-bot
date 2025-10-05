"""Financial news bot - Aggregates and sends financial news summaries"""

from video_summary_bot.handlers import GeminiHandler, TelegramHandler
from video_summary_bot.core.financial_news_handler import FinancialNewsHandler
from video_summary_bot.config import gemini_api_key, bot_token, chat_id, user_preferences
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """Main bot execution"""
    gemini = GeminiHandler(gemini_api_key)
    telegram = TelegramHandler(bot_token, chat_id)
    news_handler = FinancialNewsHandler()

    # Get users who want news
    news_users = [
        chat_id for chat_id, prefs in user_preferences.items()
        if prefs['wants_news']
    ]

    if news_users:
        summary = news_handler.create_news_summary()
        if summary:
            telegram.send_to_users(summary, None, news_users)
            logger.info("✅ News summary sent to Telegram!")
        else:
            logger.error("❌ Failed to generate news summary")
    else:
        logger.info("No users subscribed to news")


if __name__ == "__main__":
    main()
