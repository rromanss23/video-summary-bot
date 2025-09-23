"""
Telegram handler for sending messages
"""

import logging
import requests
from typing import Optional


class TelegramHandler:
    """Handles Telegram bot operations"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram handler"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, text: str, parse_mode: str) -> bool:
        """
        Send a text message to Telegram
        
        Args:
            text: Message text to send
            parse_mode: Format for the message ('Markdown' or 'HTML')
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Split long messages if needed
            max_length = 4000
            if len(text) <= max_length:
                return self._send_single_message(text, parse_mode)
            else:
                return self._send_long_message(text, parse_mode, max_length)
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def _send_single_message(self, text: str, parse_mode: str) -> bool:
        """Send a single message"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'disable_web_page_preview': True
            }
                    # Only add parse_mode if it's not None or empty
            if parse_mode:
                payload['parse_mode'] = parse_mode
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("Message sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in _send_single_message: {e}")
            return False
    
    def _send_long_message(self, text: str, parse_mode: str, max_length: int) -> bool:
        """Split and send long messages"""
        try:
            parts = []
            while text:
                if len(text) <= max_length:
                    parts.append(text)
                    break
                
                # Find good split point
                split_point = text.rfind('\n', 0, max_length)
                if split_point == -1:
                    split_point = max_length
                
                parts.append(text[:split_point])
                text = text[split_point:].lstrip()
            
            # Send each part
            success = True
            for i, part in enumerate(parts):
                if len(parts) > 1:
                    part = f"**Parte {i+1}/{len(parts)}**\n\n{part}"
                
                if not self._send_single_message(part, parse_mode):
                    success = False
                
                # Small delay between parts
                if i < len(parts) - 1:
                    import time
                    time.sleep(2)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending long message: {e}")
            return False
    
    def send_photo(self, photo_url: str, caption: str = "") -> bool:
        """
        Send a photo with optional caption
        
        Args:
            photo_url: URL of the photo to send
            caption: Optional caption for the photo
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/sendPhoto"
            
            payload = {
                'chat_id': self.chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("Photo sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send photo: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending photo: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test if the bot token and chat ID work
        
        Returns:
            True if connection works, False otherwise
        """
        try:
            test_message = "🤖 Bot connection test successful!"
            return self.send_message(test_message)
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_bot_info(self) -> Optional[dict]:
        """
        Get information about the bot
        
        Returns:
            Bot info dict or None if failed
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get bot info: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting bot info: {e}")
            return None
        
    def send_to_users(self, text: str, parse_mode: str, user_list: list) -> dict:
        """Send message to multiple users"""
        results = {}
        for chat_id in user_list:
            self.chat_id = chat_id  # Update current chat_id
            results[chat_id] = self.send_message(text, parse_mode)
        return results


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("Set TELEGRAM_BOT_TOKEN in .env file")
        exit(1)
        
    if not chat_id:
        print("Set TELEGRAM_CHAT_ID in .env file")
        exit(1)
    
    # Test the handler
    telegram = TelegramHandler(bot_token, chat_id)
    
    # Test connection
    if telegram.test_connection():
        print("✅ Telegram connection successful!")
        
        # Get bot info
        bot_info = telegram.get_bot_info()
        if bot_info:
            print(f"Bot name: {bot_info['result']['first_name']}")
            print(f"Bot username: @{bot_info['result']['username']}")
    else:
        print("❌ Telegram connection failed")