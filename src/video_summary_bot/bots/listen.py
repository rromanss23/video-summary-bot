"""Listen bot - Processes YouTube URLs sent by users via Telegram"""

from video_summary_bot.handlers import YouTubeHandler, GeminiHandler, TelegramHandler
from video_summary_bot.config import youtube_api_key, gemini_api_key, bot_token, chat_id
from video_summary_bot.utils import extract_video_id
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """Main bot loop"""
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
                # if message was received after bot started process it, otherwise ignore
                if last_update_id is not None and message['update_id'] <= last_update_id:
                    time.sleep(5)
                    continue

                # Inform user we received their message
                telegram.send_to_users(
                    "🔍 Message received. Processing...",
                    None,
                    [message['message']['chat']['id']]
                )

                # Update the last_update_id to avoid reprocessing
                last_update_id = message['update_id']

                message_text = message['message'].get('text', '')
                print(f"New message received: {message_text}")

                # check if message contains a youtube video url
                if "youtube.com" in message_text or "youtu.be" in message_text:
                    video_id = extract_video_id(message_text)

                    if not video_id:
                        telegram.send_to_users(
                            "❌ Could not extract video ID from URL",
                            None,
                            [message['message']['chat']['id']]
                        )
                        print("❌ Could not extract video ID from URL")
                        continue

                    print(f"Processing video ID: {video_id}")
                    telegram.send_to_users(
                        "🔍 Processing your YouTube link...",
                        None,
                        [message['message']['chat']['id']]
                    )

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
                                telegram.send_to_users(
                                    response_message,
                                    None,
                                    [message['message']['chat']['id']]
                                )
                                print("✅ Summary sent to Telegram!")
                            else:
                                print("❌ Failed to generate summary")
                        else:
                            telegram.send_to_users(
                                "❌ No transcript available for this video",
                                None,
                                [message['message']['chat']['id']]
                            )
                            print("❌ No transcript available for this video")
                    else:
                        telegram.send_to_users(
                            "❌ Could not retrieve video information",
                            None,
                            [message['message']['chat']['id']]
                        )
                        print("❌ Could not retrieve video information")

            time.sleep(10)  # Poll every 10 seconds

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Bot crashed: {e}")


if __name__ == "__main__":
    main()
