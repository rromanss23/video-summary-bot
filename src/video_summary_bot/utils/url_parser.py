"""URL parsing utilities for YouTube videos"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&other=params
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID

    Args:
        url: YouTube URL string

    Returns:
        Video ID or None if not found
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
