# Test both handlers together
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

youtube_api_key = os.getenv('YOUTUBE_API_KEY')
if not youtube_api_key:
    logger.error("❌ Please set YOUTUBE_API_KEY in .env file")
    exit(1)
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    logger.error("❌ Please set GEMINI_API_KEY in .env file")
    exit(1)
    
yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)

video_data = yt.get_video_info_with_transcript("@JoseLuisCavatv")
if video_data and 'transcript' in video_data:
    summary = gemini.summarize_video(
        video_data['transcript'],
        video_data['title'], 
        video_data['channel_title']
    )
    print(summary)