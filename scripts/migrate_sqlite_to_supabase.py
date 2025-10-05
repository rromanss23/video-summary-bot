"""Migrate data from SQLite to Supabase (PostgreSQL)"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from video_summary_bot.database.operations import Database as SQLiteDB
from video_summary_bot.database.postgres_operations import PostgresDatabase
import sqlite3


def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""

    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nPlease add your Supabase connection string to .env:")
        print("DATABASE_URL=postgresql://postgres:[PASSWORD]@...supabase.co:5432/postgres")
        sys.exit(1)

    print("=" * 70)
    print("🔄 Migrating from SQLite to Supabase (PostgreSQL)")
    print("=" * 70)

    # Initialize databases
    print("\n1. Connecting to databases...")
    sqlite_db = SQLiteDB("data/video_summary.db")
    postgres_db = PostgresDatabase(database_url)
    print("   ✅ Connected to both databases")

    # Migrate users
    print("\n2. Migrating users...")
    users = sqlite_db.get_all_users(active_only=False)
    for user in users:
        postgres_db.add_user(
            user_id=user['user_id'],
            username=user['username'],
            active=bool(user['active'])
        )
        print(f"   ✅ Migrated user: {user['username']} ({user['user_id']})")
    print(f"   Total users migrated: {len(users)}")

    # Migrate channels
    print("\n3. Migrating channels...")
    channels = sqlite_db.get_all_channels(active_only=False)
    for channel in channels:
        postgres_db.add_channel(
            channel_handle=channel['channel_handle'],
            channel_name=channel.get('channel_name'),
            youtube_channel_id=channel.get('youtube_channel_id'),
            language=channel.get('language', 'es'),
            check_start_hour=channel.get('check_start_hour', 10),
            check_start_minute=channel.get('check_start_minute', 0),
            check_end_hour=channel.get('check_end_hour', 14),
            check_interval_minutes=channel.get('check_interval_minutes', 5)
        )
        print(f"   ✅ Migrated channel: {channel['channel_handle']}")
    print(f"   Total channels migrated: {len(channels)}")

    # Migrate user-channel subscriptions
    print("\n4. Migrating user subscriptions...")
    with sqlite_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_channels')
        subscriptions = cursor.fetchall()

    subscription_count = 0
    for sub in subscriptions:
        try:
            postgres_db.subscribe_user_to_channel(
                user_id=sub['user_id'],
                channel_id=sub['channel_id']
            )
            subscription_count += 1
        except Exception as e:
            print(f"   ⚠️  Warning: {e}")

    print(f"   Total subscriptions migrated: {subscription_count}")

    # Migrate summaries
    print("\n5. Migrating video summaries...")
    with sqlite_db.get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM summaries ORDER BY processed_at')
        summaries = cursor.fetchall()

    summary_count = 0
    for summary in summaries:
        # Convert Row to dict for easier access
        summary_dict = dict(summary)
        postgres_db.add_summary(
            channel_handle=summary_dict['channel_handle'],
            video_id=summary_dict.get('video_id', ''),
            video_title=summary_dict.get('video_title', ''),
            video_url=summary_dict.get('video_url', ''),
            summary_text=summary_dict.get('summary_text', ''),
            video_date=summary_dict.get('video_date'),
            success=bool(summary_dict.get('success', 1))
        )
        summary_count += 1
        if summary_count % 10 == 0:
            print(f"   Migrated {summary_count} summaries...")

    print(f"   ✅ Total summaries migrated: {summary_count}")

    # Verification
    print("\n" + "=" * 70)
    print("✅ Migration Complete! Verification:")
    print("=" * 70)

    # Verify counts
    pg_users = postgres_db.get_all_users(active_only=False)
    pg_channels = postgres_db.get_all_channels(active_only=False)

    print(f"\n📊 Summary:")
    print(f"   Users:         {len(users)} (SQLite) → {len(pg_users)} (PostgreSQL)")
    print(f"   Channels:      {len(channels)} (SQLite) → {len(pg_channels)} (PostgreSQL)")
    print(f"   Subscriptions: {len(subscriptions)} (SQLite) → {subscription_count} (PostgreSQL)")
    print(f"   Summaries:     {len(summaries)} (SQLite) → {summary_count} (PostgreSQL)")

    print("\n✅ All data migrated successfully!")
    print("\n" + "=" * 70)
    print("📝 Next steps:")
    print("   1. Add to .env: USE_SUPABASE=true")
    print("   2. Test connection: uv run python scripts/test_supabase_connection.py")
    print("   3. Run bot: ./run.sh combined")
    print("=" * 70)

    # Close connections
    postgres_db.close()


if __name__ == "__main__":
    try:
        migrate_data()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
