"""Test Supabase connection and verify data"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_summary_bot.database import get_database
import logging

logging.basicConfig(level=logging.INFO)


def test_connection():
    """Test Supabase database connection"""

    print("=" * 60)
    print("🔍 Testing Supabase Connection")
    print("=" * 60)

    # Get database instance (should be PostgreSQL)
    print("\n1. Connecting to database...")
    try:
        db = get_database()
        print(f"   ✅ Connected to: {type(db).__name__}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    # Test queries
    print("\n2. Testing database queries...")

    try:
        # Get all users
        users = db.get_all_users(active_only=False)
        print(f"   ✅ Found {len(users)} users")

        if users:
            print("\n   Users in database:")
            for user in users:
                status = "✅" if user.get('active') else "❌"
                print(f"   {status} {user.get('username')} ({user.get('user_id')})")

        # Get all channels
        channels = db.get_all_channels(active_only=False)
        print(f"\n   ✅ Found {len(channels)} channels")

        if channels:
            print("\n   Channels in database:")
            for channel in channels:
                status = "✅" if channel.get('active') else "❌"
                print(f"   {status} {channel.get('channel_handle')}")

        # Test authorization
        if users:
            test_user_id = users[0]['user_id']
            is_auth = db.is_user_authorized(test_user_id)
            print(f"\n   ✅ Authorization check works: {is_auth}")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\n📝 Supabase is ready to use!")
        print("   Run: ./run.sh combined")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
