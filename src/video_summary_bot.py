from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
from telegram_handler import TelegramHandler
from config import youtube_api_key, gemini_api_key, bot_token, chat_id, youtube_channels, user_preferences
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
    
yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)
telegram = TelegramHandler(bot_token, chat_id)

# For YouTube summaries - send to users who want that channel
# TODO: schedule the script to run daily on weekdays
# If time is 10.30AM on a weekday, Madrid time, run for channel @JoseLuisCavatv
# if time is 12.30PM on a weekday, Madrid time, run for channel @nacho_ic
for channel in youtube_channels:
    # Get users who want this channel
    target_users = [chat_id for chat_id, prefs in user_preferences.items() 
                   if channel in prefs['channels']]
    
    if target_users:
        video_data = yt.get_video_info_with_transcript(channel)
        if video_data and 'transcript' in video_data:
            summary = gemini.summarize_video(
                video_data['transcript'],
                video_data['title'], 
                video_data['channel_title']
            )
            if summary:
                message = f"📺 {video_data['title']}\n\n{summary}"
                telegram.send_to_users(message, None, target_users)
                print("✅ Summary sent to Telegram!")
            else:
                print("❌ Failed to send summary to Telegram")
        else:
            print("❌ Failed to generate summary")
    else:
        print("❌ Failed to retrieve video data or transcript")