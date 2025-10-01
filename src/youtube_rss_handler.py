import feedparser
import logging
from typing import Optional, Dict
from datetime import datetime, timezone
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeRSSHandler:
    """Handles YouTube RSS operations without using API quota"""

    def __init__(self):
        """Initialize RSS handler"""
        self.logger = logging.getLogger(__name__)

    def get_todays_video_from_rss(self, channel_id: str) -> Optional[Dict]:
        """
        Get today's video from RSS feed (0 API quota usage)

        Args:
            channel_id: YouTube channel ID (e.g., 'UCxxxxxx')
                        NOT @handle - use get_channel_id_once() first

        Returns:
            Dict with video info or None if no video today
        """
        try:
            self.logger.info(f"Checking RSS feed for channel: {channel_id}")

            # RSS feed URL
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

            # Parse RSS feed
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                self.logger.warning(f"No entries in RSS feed for: {channel_id}")
                return None

            # Get the latest video
            latest = feed.entries[0]

            # Parse published date
            published = datetime.fromisoformat(latest.published.replace('Z', '+00:00'))
            today = datetime.now(timezone.utc).date()

            # Check if published today
            if published.date() != today:
                self.logger.info(f"Latest video not from today. Published: {published.date()}, Today: {today}")
                return None

            # Extract video info
            video_id = latest.yt_videoid
            video_info = {
                'id': video_id,
                'title': latest.title,
                'description': latest.summary if hasattr(latest, 'summary') else '',
                'published_at': latest.published,
                'channel_title': latest.author,
                'url': latest.link,
                'thumbnail_url': latest.media_thumbnail[0]['url'] if hasattr(latest, 'media_thumbnail') else ''
            }

            self.logger.info(f"Found today's video: {video_info['title']}")
            return video_info

        except Exception as e:
            self.logger.error(f"Error parsing RSS feed: {e}")
            return None

    def get_transcript(self, video_id: str, languages: list = ['es']) -> Optional[str]:
        """
        Get transcript for a video (uses youtube-transcript-api, not quota)

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (default: ['es'])

        Returns:
            Full transcript text or None if not available
        """
        try:
            self.logger.info(f"Getting transcript for video: {video_id}")
            transcript_api = YouTubeTranscriptApi()

            # Use list_transcripts method (correct API usage)
            try:
                transcript = transcript_api.fetch(video_id=video_id, languages=languages)
                full_text = ' '.join([snippet.text for snippet in transcript])
                self.logger.info(f"Transcript retrieved: {len(full_text)} characters")
                return full_text
            except Exception as e:
                self.logger.warning(f"Transcript fetch failed: {e}")
                return None

        except Exception as e:
            self.logger.error(f"Error getting transcript: {e}")
            return None

    def get_video_info_with_transcript(self, channel_id: str, languages: list = ['es']) -> Optional[Dict]:
        """
        Get today's video from channel with transcript using RSS (minimal quota usage)

        Args:
            channel_id: YouTube channel ID (not @handle)

        Returns:
            Dict with video info and transcript or None if failed
        """
        try:
            # Get today's video from RSS
            video_info = self.get_todays_video_from_rss(channel_id)
            if not video_info:
                return None

            # Get transcript
            transcript = self.get_transcript(video_info['id'], languages)
            if not transcript:
                self.logger.warning(f"No transcript available for: {video_info['title']}")
                return None  # Return None if no transcript (adjust if you want video anyway)

            # Add transcript to video info
            video_info['transcript'] = transcript
            video_info['video_id'] = video_info['id']  # Add video_id field for compatibility

            return video_info

        except Exception as e:
            self.logger.error(f"Error getting video with transcript: {e}")
            return None


if __name__ == "__main__":
    # Test the RSS handler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize handler (no API key needed!)
    rss_handler = YouTubeRSSHandler()

    # Test with a channel ID (you need to get this once using YouTube API)
    # Example: Lex Fridman's channel
    test_channel_id = "UCOHxDwCcOzBaLkeTazanwcw"

    logger.info(f"Testing RSS feed for channel: {test_channel_id}")

    # Test getting today's video
    video = rss_handler.get_todays_video_from_rss(test_channel_id)
    if video:
        logger.info(f"✅ Found video: {video['title']}")
        logger.info(f"📅 Published: {video['published_at']}")
        logger.info(f"🔗 URL: {video['url']}")

        # Test getting transcript
        transcript = rss_handler.get_transcript(video['id'], ['en'])
        if transcript:
            logger.info(f"✅ Transcript length: {len(transcript)} characters")
            logger.info(f"📝 First 200 chars: {transcript[:200]}...")
        else:
            logger.warning("❌ No transcript available")
    else:
        logger.info("ℹ️ No video published today")
