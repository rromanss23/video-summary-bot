# Test both handlers together
from youtube_handler import YouTubeHandler
from gemini_handler import GeminiHandler
import os
from dotenv import load_dotenv

youtube_api_key = os.getenv('YOUTUBE_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

yt = YouTubeHandler(youtube_api_key)
gemini = GeminiHandler(gemini_api_key)

video_data = yt.get_video_with_transcript("@JoseLuisCavatv")
if video_data and 'transcript' in video_data:
    summary = gemini.summarize_video(
        video_data['transcript'],
        video_data['title'], 
        video_data['channel_title']
    )
    print(summary)