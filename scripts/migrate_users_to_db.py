"""Migrate users from config file to database"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_summary_bot.database import Database
from video_summary_bot.config.users import user_preferences

def migrate_users():
    """Migrate users from config/users.py to database"""
    db = Database()

    print("🔄 Migrating users from config to database...")
    print(f"Found {len(user_preferences)} users in config\n")

    for user_id, prefs in user_preferences.items():
        username = prefs.get('user_name', 'Unknown')
        channels = prefs.get('channels', [])

        print(f"  Adding user: {username} ({user_id})")
        db.add_user(user_id=user_id, username=username, active=True)

        # Add channel subscriptions
        for channel_handle in channels:
            # Get or create channel
            channel = db.get_channel(channel_handle)
            if not channel:
                print(f"    ⚠️  Channel {channel_handle} not in database, adding...")
                db.add_channel(
                    channel_handle=channel_handle,
                    channel_name=channel_handle.replace('@', ''),
                    youtube_channel_id=None  # Will need to be updated manually
                )
                channel = db.get_channel(channel_handle)

            # Subscribe user to channel
            try:
                db.subscribe_user_to_channel(user_id, channel['channel_id'])
                print(f"    ✅ Subscribed to {channel_handle}")
            except Exception as e:
                print(f"    ⚠️  Already subscribed to {channel_handle}")

        print()

    # Verify migration
    print("=" * 60)
    print("✅ Migration complete!\n")
    print("Verification:")
    all_users = db.get_all_users()
    print(f"  Total active users in database: {len(all_users)}")
    for user in all_users:
        print(f"    - {user['username']} ({user['user_id']})")

    print("\n" + "=" * 60)
    print("📝 Next steps:")
    print("  1. Update YouTube channel IDs in the channels table")
    print("  2. Remove config/users.py from code (will be deprecated)")
    print("  3. Restart the bot to use database for user management")
    print("=" * 60)

if __name__ == "__main__":
    migrate_users()
