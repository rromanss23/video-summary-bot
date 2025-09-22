from gemini_handler import GeminiHandler
from config import gemini_api_key, bot_token, chat_id
from src.financial_news_handler import FinancialNewsHandler
from telegram_handler import TelegramHandler
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
    
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)
news_handler = FinancialNewsHandler()

# Test news fetching
news = news_handler.get_latest_news(max_articles=3)
print(f"\nFound {len(news)} news articles:")
for article in news:
    print(f"- {article['title']} ({article['source']})")

# Test market data
market_data = news_handler.get_market_data()
print(f"\nMarket data for {len(market_data)} indices:")
for symbol, data in market_data.items():
    print(f"- {data['name']}: {data['change_percent']:+.2f}%")

# Test full summary
print("\n" + "="*50)
print("FULL SUMMARY:")
print("="*50)
summary = news_handler.create_news_summary()
print(summary)

if summary:
    logger.info("Sending news summary to Telegram...")
    message = f"📰 *Today's Financial News Summary*\n\n{summary}"
    if telegram.send_message(message, None):
        print("✅ News summary sent to Telegram!")
    else:
        print("❌ Failed to send news summary to Telegram")