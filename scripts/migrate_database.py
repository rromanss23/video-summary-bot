"""
Migration script to populate database with existing config data
Run this once to migrate from config.py to SQLite
"""
from database import Database
from config import user_preferences
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    db = Database()

    # Add channels with their specific schedule
    channels_config = [
        {
            'handle': '@JoseLuisCavatv',
            'channel_id': 'UCvCCLJkQpRg0NdT3zNcI08A',
            'name': 'José Luis Cava TV',
            'start_hour': 8,
            'start_minute': 30,
            'end_hour': 14,
            'interval': 3,
            'language': 'es'
        },
        {
            'handle': '@nacho_ic',
            'channel_id': 'UCZLtNl1TyvNJ9K8OYKT43Cw',
            'name': 'Nacho IC',
            'start_hour': 12,
            'start_minute': 15,
            'end_hour': 16,
            'interval': 3,
            'language': 'es'
        },
        {
            'handle': '@juanrallo',
            'name': 'Juan Rallo',
            'channel_id': 'UCBLCvUUCiSqBCEc-TqZ9rGw',
            'start_hour': 8,
            'start_minute': 0,
            'end_hour': 22,
            'interval': 5,
            'language': 'es'
        },
        {
            'handle': '@bravosresearchcrypto',
            'channel_id': 'UC9jTdAaVgvRjhU0gl5LWoZg',
            'name': 'Bravos Crypto Research',
            'start_hour': 8,
            'start_minute': 0,
            'end_hour': 22,
            'interval': 5,
            'language': 'en'
        },
        {
            'handle': '@bravosresearch',
            'channel_id': 'UCOHxDwCcOzBaLkeTazanwcw',
            'name': 'Bravos Research',
            'start_hour': 8,
            'start_minute': 0,
            'end_hour': 22,
            'interval': 5,
            'language': 'en'
        }
    ]

    logger.info("Adding channels...")
    for channel in channels_config:
        db.add_channel(
            channel_handle=channel['handle'],
            channel_name=channel['name'],
            youtube_channel_id=channel['channel_id'],
            language=channel['language'],
            check_start_hour=channel['start_hour'],
            check_start_minute=channel['start_minute'],
            check_end_hour=channel['end_hour'],
            check_interval_minutes=channel['interval']
        )

    # Add users and their subscriptions
    logger.info("Adding users and subscriptions...")
    for user_id, prefs in user_preferences.items():
        db.add_user(
            user_id=user_id,
            username=prefs.get('user_name', 'Unknown'),
            wants_news=prefs.get('wants_news', True)
        )

        # Subscribe to channels
        for channel in prefs['channels']:
            try:
                db.subscribe_user_to_channel(user_id, channel)
            except ValueError as e:
                logger.warning(f"Could not subscribe {user_id} to {channel}: {e}")

    logger.info("Migration completed successfully!")

    # Display summary
    logger.info("\n=== Migration Summary ===")
    logger.info(f"Channels: {len(db.get_all_channels())}")
    for channel in db.get_all_channels():
        subscribers = db.get_channel_subscribers(channel['channel_handle'])
        logger.info(f"  {channel['channel_handle']}: {len(subscribers)} subscribers")

if __name__ == "__main__":
    migrate()