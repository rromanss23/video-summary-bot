from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from config import youtube_api_key, gemini_api_key, bot_token, chat_id, youtube_channels, user_preferences
import logging
import time
import re
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&other=params
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    """
    # Pattern for youtu.be short URLs
    youtu_be_pattern = r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})'
    # Pattern for youtube.com URLs (watch, shorts, embed)
    youtube_pattern = r'(?:https?://)?(?:www\.|m\.)?youtube\.com/(?:watch\?v=|shorts/|embed/)([a-zA-Z0-9_-]{11})'

    # Try youtu.be pattern
    match = re.search(youtu_be_pattern, url)
    if match:
        return match.group(1)

    # Try youtube.com pattern
    match = re.search(youtube_pattern, url)
    if match:
        return match.group(1)

    # Fallback: try parsing as query parameter
    try:
        parsed = urlparse(url)
        if parsed.query:
            params = parse_qs(parsed.query)
            if 'v' in params:
                return params['v'][0]
    except:
        pass

    return None

yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)

# Track the last processed update_id to avoid duplicates
last_update_id = None

print("🤖 Bot started. Listening for YouTube URLs...")

try:
    while True:
        # Get new messages only (after last_update_id)
        offset = last_update_id + 1 if last_update_id is not None else None
        message = telegram.get_last_message(offset=offset)

        if message:
            # if message was recieved after bot started process it, otherwise ignore
            if last_update_id is not None and message['update_id'] <= last_update_id:
                time.sleep(5)
                continue
            # Inform user we received their message
            telegram.send_to_users("🔍 Message received. Processing...", None, [message['message']['chat']['id']])

            # Update the last_update_id to avoid reprocessing
            last_update_id = message['update_id']

            message_text = message['message'].get('text', '')
            print(f"New message received: {message_text}")

            # check if message contains a youtube video url
            if "youtube.com" in message_text or "youtu.be" in message_text:
                video_id = extract_video_id(message_text)

                if not video_id:
                    telegram.send_to_users("❌ Could not extract video ID from URL", None, [message['message']['chat']['id']])
                    print("❌ Could not extract video ID from URL")
                    continue

                print(f"Processing video ID: {video_id}")
                telegram.send_to_users("🔍 Processing your YouTube link...", None, [message['message']['chat']['id']])

                video_info = yt.get_video_info(video_id)

                if video_info:
                    transcript = yt.get_transcript(video_id)
                    if transcript:
                        summary = gemini.summarize_video(
                            transcript,
                            video_info['title'],
                            video_info['channel_title']
                        )
                        if summary:
                            response_message = f"📺 {video_info['title']}\n\n{summary}"
                            telegram.send_to_users(response_message, None, [message['message']['chat']['id']])
                            print("✅ Summary sent to Telegram!")
                        else:
                            print("❌ Failed to generate summary")
                    else:
                        telegram.send_to_users("❌ No transcript available for this video", None, [message['message']['chat']['id']])
                        print("❌ No transcript available for this video")
                else:
                    telegram.send_to_users("❌ Could not retrieve video information", None, [message['message']['chat']['id']])
                    print("❌ Could not retrieve video information")

        time.sleep(10)  # Poll every 10 seconds

except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user")
except Exception as e:
    logger.error(f"Fatal error: {e}")
    print(f"❌ Bot crashed: {e}")



# for channel in youtube_channels:
#     # Get users who want this channel
#     target_users = [chat_id for chat_id, prefs in user_preferences.items() 
#                    if channel in prefs['channels']]
    
#     if target_users:
#         video_data = yt.get_video_info_with_transcript(channel)
#         if video_data and 'transcript' in video_data:
#             summary = gemini.summarize_video(
#                 video_data['transcript'],
#                 video_data['title'], 
#                 video_data['channel_title']
#             )
#             if summary:
#                 message = f"📺 {video_data['title']}\n\n{summary}"
#                 telegram.send_to_users(message, None, target_users)
#                 print("✅ Summary sent to Telegram!")
#             else:
#                 print("❌ Failed to send summary to Telegram")
#         else:
#             print("❌ Failed to generate summary")
#     else:
#         print("❌ Failed to retrieve video data or transcript")