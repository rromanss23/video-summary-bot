"""Listen bot - Processes YouTube URLs sent by users via Telegram"""

from video_summary_bot.handlers import YouTubeHandler, GeminiHandler, TelegramHandler
from video_summary_bot.config import youtube_api_key, gemini_api_key, bot_token
from video_summary_bot.database.factory import get_database
from video_summary_bot.utils import extract_video_id
import logging
import time
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Session state management for pending authentication
# Format: {chat_id: {'state': 'waiting_for_password', 'username': 'John'}}
pending_auth_sessions = {}


def process_video_url(video_id: str, user_chat_id: str, yt: YouTubeHandler,
                      gemini: GeminiHandler, telegram: TelegramHandler, db):
    """Process a video URL - either from cache or generate new summary"""

    # Check if video has been processed before
    if db.has_video_id_been_processed(video_id):
        logger.info(f"Video {video_id} already processed - retrieving from database")
        telegram.send_to_users(
            "📂 Found existing summary, retrieving...",
            None,
            [user_chat_id]
        )

        existing_summary = db.get_summary_by_video_id(video_id)
        if existing_summary:
            response_message = f"📺 {existing_summary['video_title']}\n\n{existing_summary['summary_text']}\n\n{existing_summary['video_url']}"
            telegram.send_to_users(response_message, None, [user_chat_id])
            logger.info("✅ Existing summary sent to Telegram!")
            return True

    # Video not processed before - generate new summary
    logger.info(f"Processing new video ID: {video_id}")
    telegram.send_to_users(
        "🔍 Processing your YouTube link...",
        None,
        [user_chat_id]
    )

    video_info = yt.get_video_info(video_id)

    if not video_info:
        telegram.send_to_users(
            "❌ Could not retrieve video information",
            None,
            [user_chat_id]
        )
        logger.error("❌ Could not retrieve video information")
        return False

    transcript = yt.get_transcript(video_id)
    if not transcript:
        telegram.send_to_users(
            "❌ No transcript available for this video",
            None,
            [user_chat_id]
        )
        logger.error("❌ No transcript available for this video")
        return False

    summary = gemini.summarize_video(
        transcript,
        video_info['title'],
        video_info['channel_title']
    )

    if not summary:
        telegram.send_to_users(
            "❌ Failed to generate summary",
            None,
            [user_chat_id]
        )
        logger.error("❌ Failed to generate summary")
        return False

    # Build video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Save to database
    today = datetime.now().strftime('%Y-%m-%d')
    db.add_summary(
        channel_handle=video_info.get('channel_title', 'manual'),
        video_id=video_id,
        video_title=video_info['title'],
        video_url=video_url,
        summary_text=summary,
        video_date=today,
        success=True
    )
    logger.info(f"Summary saved to database for video {video_id}")

    # Send summary to user
    response_message = f"📺 {video_info['title']}\n\n{summary}\n\n{video_url}"
    telegram.send_to_users(response_message, None, [user_chat_id])
    logger.info("✅ Summary sent to Telegram!")
    return True


def main():
    """Main bot loop - listens for messages from all authorized users in database"""
    yt = YouTubeHandler(youtube_api_key)
    gemini = GeminiHandler(gemini_api_key)
    telegram = TelegramHandler(bot_token, None)  # Don't set default chat_id
    db = get_database()

    # Get all active users from database
    active_users = db.get_all_users(active_only=True)
    allowed_user_ids = {user['user_id'] for user in active_users}

    # Track the last processed update_id to avoid duplicates
    last_update_id = None

    print(f"🤖 Bot started. Listening for YouTube URLs from {len(allowed_user_ids)} authorized users...")
    print(f"📋 Authorized users: {', '.join([user['username'] for user in active_users])}")

    try:
        while True:
            # Get new messages only (after last_update_id)
            offset = last_update_id + 1 if last_update_id is not None else None
            message = telegram.get_last_message(offset=offset)

            if message:
                # If message was received after bot started process it, otherwise ignore
                if last_update_id is not None and message['update_id'] <= last_update_id:
                    time.sleep(5)
                    continue

                # Update the last_update_id to avoid reprocessing
                last_update_id = message['update_id']

                # Get message details
                message_text = message['message'].get('text', '')
                user_chat_id = str(message['message']['chat']['id'])
                user_name = message['message']['chat'].get('first_name', 'Unknown')
                username = message['message']['chat'].get('username', user_name)

                # Check if user is in pending authentication flow
                if user_chat_id in pending_auth_sessions:
                    bot_password = os.getenv('BOT_PASSWORD')

                    if not bot_password:
                        logger.error("BOT_PASSWORD not set in environment variables")
                        telegram.send_to_users(
                            "❌ Authentication system not configured. Please contact admin.",
                            None,
                            [user_chat_id]
                        )
                        del pending_auth_sessions[user_chat_id]
                        continue

                    # User is expected to send password
                    if message_text.strip() == bot_password:
                        # Password correct - register user
                        logger.info(f"Correct password from {username} ({user_chat_id})")

                        try:
                            db.add_user(user_id=user_chat_id, username=username, active=True)
                            logger.info(f"✅ Registered new user: {username} ({user_chat_id})")

                            telegram.send_to_users(
                                f"✅ Welcome {username}! You are now registered.\n\n"
                                "Send me a YouTube URL to get a summary.",
                                None,
                                [user_chat_id]
                            )

                            # Remove from pending sessions
                            del pending_auth_sessions[user_chat_id]
                            continue

                        except Exception as e:
                            logger.error(f"Failed to register user {username}: {e}")
                            telegram.send_to_users(
                                "❌ Registration failed. Please try again later or contact admin.",
                                None,
                                [user_chat_id]
                            )
                            del pending_auth_sessions[user_chat_id]
                            continue
                    else:
                        # Password incorrect
                        logger.warning(f"Incorrect password from {username} ({user_chat_id})")
                        telegram.send_to_users(
                            "❌ Incorrect password. Please try again or contact admin.",
                            None,
                            [user_chat_id]
                        )
                        del pending_auth_sessions[user_chat_id]
                        continue

                # Check if user is authorized (check database)
                if not db.is_user_authorized(user_chat_id):
                    logger.warning(f"Unauthorized user {username} ({user_chat_id}) tried to use bot")

                    # Add user to pending authentication sessions
                    pending_auth_sessions[user_chat_id] = {
                        'state': 'waiting_for_password',
                        'username': username
                    }

                    telegram.send_to_users(
                        f"👋 Hi {username}!\n\n"
                        "You are not yet registered to use this bot.\n\n"
                        "🔐 Please send the password to register and start using the bot.",
                        None,
                        [user_chat_id]
                    )
                    continue

                # Get user info from database
                user = db.get_user(user_chat_id)
                logger.info(f"New message from {user['username']}: {message_text}")

                # Inform user we received their message
                telegram.send_to_users(
                    "🔍 Message received. Processing...",
                    None,
                    [user_chat_id]
                )

                # Check if message contains a YouTube video URL
                if "youtube.com" in message_text or "youtu.be" in message_text:
                    video_id = extract_video_id(message_text)

                    if not video_id:
                        telegram.send_to_users(
                            "❌ Could not extract video ID from URL",
                            None,
                            [user_chat_id]
                        )
                        logger.error("❌ Could not extract video ID from URL")
                        continue

                    # Process the video URL
                    process_video_url(video_id, user_chat_id, yt, gemini, telegram, db)
                else:
                    telegram.send_to_users(
                        "ℹ️ Please send me a YouTube video URL to get a summary.",
                        None,
                        [user_chat_id]
                    )

            time.sleep(10)  # Poll every 10 seconds

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Bot crashed: {e}")


if __name__ == "__main__":
    main()
