"""
Financial news handler for getting latest economic news
"""

import logging
import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime


class FinancialNewsHandler:
    """Handles financial news from various sources"""
    
    def __init__(self):
        """Initialize financial news handler"""
        self.logger = logging.getLogger(__name__)
        
        # RSS feeds for financial news
        self.rss_feeds = {
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
            'expansion': 'https://www.expansion.com/rss/portada.xml',
            'eleconomista': 'https://www.eleconomista.es/rss/rss-economia.xml',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'bbc_business': 'https://feeds.bbci.co.uk/news/business/rss.xml'
        }
    
    def get_latest_news(self, max_articles: int = 5) -> List[Dict]:
        """
        Get latest financial news from RSS feeds
        
        Args:
            max_articles: Maximum number of articles to return
        
        Returns:
            List of news articles with title, link, published date, and source
        """
        all_articles = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                self.logger.info(f"Fetching news from {source_name}")
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                # Extract articles
                for entry in feed.entries[:3]:  # Top 3 from each source
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
                        'source': source_name.replace('_', ' ').title()
                    }
                    all_articles.append(article)
                    
            except Exception as e:
                self.logger.error(f"Error fetching from {source_name}: {e}")
        
        # Sort by published date (most recent first) and limit results
        try:
            all_articles.sort(
                key=lambda x: datetime.strptime(x['published'][:25], '%a, %d %b %Y %H:%M:%S') if x['published'] else datetime.min,
                reverse=True
            )
        except:
            # If date parsing fails, keep original order
            pass
        
        return all_articles[:max_articles]
    
    def get_crypto_news(self, max_articles: int = 3) -> List[Dict]:
        """Get cryptocurrency-specific news"""
        crypto_feeds = {
            'cointelegraph': 'https://cointelegraph.com/rss',
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        }
        
        articles = []
        
        for source_name, feed_url in crypto_feeds.items():
            try:
                self.logger.info(f"Fetching crypto news from {source_name}")
                
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:2]:  # Top 2 from each crypto source
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:150] + '...' if entry.get('summary') else '',
                        'source': source_name.title()
                    }
                    articles.append(article)
                    
            except Exception as e:
                self.logger.error(f"Error fetching crypto news from {source_name}: {e}")
        
        return articles[:max_articles]
    
    def get_market_data(self) -> Dict:
        """Get basic market data using free APIs"""
        market_data = {}
        
        try:
            # Get major indices using Yahoo Finance (free)
            import yfinance as yf
            
            symbols = {
                '^IBEX': 'IBEX 35',
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^RUT': 'Russell 2000',
                'GOLD': 'Gold',
                'SILVER': 'Silver'
            }
            
            for symbol, name in symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change_percent = ((current - previous) / previous) * 100
                        
                        market_data[symbol] = {
                            'name': name,
                            'price': round(current, 2),
                            'change_percent': round(change_percent, 2)
                        }
                except Exception as e:
                    self.logger.warning(f"Could not fetch data for {symbol}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
        
        return market_data
    
    def create_news_summary(self, include_crypto: bool = True, include_markets: bool = True) -> str:
        """
        Create a formatted news summary for Telegram
        
        Args:
            include_crypto: Whether to include cryptocurrency news
            include_markets: Whether to include market data
        
        Returns:
            Formatted string ready for Telegram
        """
        summary_parts = []
        
        # Add header
        summary_parts.append("📈 RESUMEN FINANCIERO DIARIO")
        summary_parts.append(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        summary_parts.append("")
        
        # Add market data
        if include_markets:
            market_data = self.get_market_data()
            if market_data:
                summary_parts.append("📊 MERCADOS:")
                for symbol, data in market_data.items():
                    direction = "📈" if data['change_percent'] >= 0 else "📉"
                    summary_parts.append(f"{direction} {data['name']}: {data['change_percent']:+.2f}%")
                summary_parts.append("")
        
        # Add general financial news
        news_articles = self.get_latest_news(max_articles=3)
        if news_articles:
            summary_parts.append("📰 NOTICIAS DESTACADAS:")
            for i, article in enumerate(news_articles, 1):
                summary_parts.append(f"{i}. {article['title']}")
                summary_parts.append(f"   🔗 {article['link']}")
            summary_parts.append("")
        
        # Add crypto news
        if include_crypto:
            crypto_news = self.get_crypto_news(max_articles=2)
            if crypto_news:
                summary_parts.append("₿ NOTICIAS CRYPTO:")
                for i, article in enumerate(crypto_news, 1):
                    summary_parts.append(f"{i}. {article['title']}")
                    summary_parts.append(f"   🔗 {article['link']}")
                summary_parts.append("")
        
        summary_parts.append("🤖 Resumen automatizado")
        
        return "\n".join(summary_parts)


if __name__ == "__main__":
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the handler
    news_handler = FinancialNewsHandler()
    
    print("Testing financial news handler...")
    
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