import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "data/video_summary.db"):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    wants_news INTEGER DEFAULT 1,
                    active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Channels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_handle TEXT UNIQUE NOT NULL,
                    channel_name TEXT,
                    youtube_channel_id TEXT,
                    language TEXT DEFAULT 'es',
                    check_start_hour INTEGER DEFAULT 10,
                    check_start_minute INTEGER DEFAULT 0,
                    check_end_hour INTEGER DEFAULT 14,
                    check_interval_minutes INTEGER DEFAULT 5,
                    active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # User-Channel subscriptions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_channels (
                    user_id TEXT,
                    channel_id INTEGER,
                    subscribed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, channel_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
                )
            ''')

            # Summaries log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summaries (
                    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_handle TEXT NOT NULL,
                    video_id TEXT,
                    video_title TEXT,
                    video_url TEXT,
                    summary_text TEXT,
                    video_date TEXT,
                    processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_date ON summaries(video_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_channel ON summaries(channel_handle)')

            logger.info("Database initialized successfully")

    # User operations
    def add_user(self, user_id: str, username: str = None, wants_news: bool = True):
        """Add or update a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, username, wants_news)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, username, int(wants_news)))
            logger.info(f"User {user_id} added/updated")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user_preferences(self, user_id: str, wants_news: bool = None):
        """Update user preferences"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if wants_news is not None:
                cursor.execute('UPDATE users SET wants_news = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                             (int(wants_news), user_id))
            logger.info(f"User {user_id} preferences updated")

    # Channel operations
    def add_channel(self, channel_handle: str, channel_name: str = None,
                   youtube_channel_id: str = None, language: str = 'es',
                   check_start_hour: int = 10, check_start_minute: int = 0,
                   check_end_hour: int = 14, check_interval_minutes: int = 5):
        """Add a new channel"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO channels
                (channel_handle, channel_name, youtube_channel_id, language, check_start_hour,
                 check_start_minute, check_end_hour, check_interval_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (channel_handle, channel_name, youtube_channel_id, language, check_start_hour,
                  check_start_minute, check_end_hour, check_interval_minutes))
            logger.info(f"Channel {channel_handle} added")

    def get_channel(self, channel_handle: str) -> Optional[Dict[str, Any]]:
        """Get channel by handle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM channels WHERE channel_handle = ?', (channel_handle,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_channels(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all channels"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM channels'
            if active_only:
                query += ' WHERE active = 1'
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    # Subscription operations
    def subscribe_user_to_channel(self, user_id: str, channel_handle: str):
        """Subscribe a user to a channel"""
        channel = self.get_channel(channel_handle)
        if not channel:
            raise ValueError(f"Channel {channel_handle} not found")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO user_channels (user_id, channel_id)
                VALUES (?, ?)
            ''', (user_id, channel['channel_id']))
            logger.info(f"User {user_id} subscribed to {channel_handle}")

    def unsubscribe_user_from_channel(self, user_id: str, channel_handle: str):
        """Unsubscribe a user from a channel"""
        channel = self.get_channel(channel_handle)
        if not channel:
            raise ValueError(f"Channel {channel_handle} not found")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_channels
                WHERE user_id = ? AND channel_id = ?
            ''', (user_id, channel['channel_id']))
            logger.info(f"User {user_id} unsubscribed from {channel_handle}")

    def get_user_channels(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all channels a user is subscribed to"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.* FROM channels c
                INNER JOIN user_channels uc ON c.channel_id = uc.channel_id
                WHERE uc.user_id = ? AND c.active = 1
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_channel_subscribers(self, channel_handle: str) -> List[str]:
        """Get all users subscribed to a channel"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.user_id FROM users u
                INNER JOIN user_channels uc ON u.user_id = uc.user_id
                INNER JOIN channels c ON uc.channel_id = c.channel_id
                WHERE c.channel_handle = ? AND u.active = 1
            ''', (channel_handle,))
            return [row['user_id'] for row in cursor.fetchall()]

    # Summary operations
    def add_summary(self, channel_handle: str, video_id: str, video_title: str,
                   video_url: str, summary_text: str, video_date: str = None,
                   success: bool = True):
        """Log a video summary"""
        if video_date is None:
            video_date = datetime.now().strftime('%Y-%m-%d')

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO summaries
                (channel_handle, video_id, video_title, video_url, summary_text, video_date, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (channel_handle, video_id, video_title, video_url, summary_text, video_date, int(success)))
            logger.info(f"Summary logged for {channel_handle}: {video_title}")

    def has_video_been_processed(self, channel_handle: str, date: str = None) -> bool:
        """Check if a video from a channel has been processed today"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM summaries
                WHERE channel_handle = ? AND video_date = ? AND success = 1
            ''', (channel_handle, date))
            result = cursor.fetchone()
            return result['count'] > 0

    def get_summaries(self, channel_handle: str = None, date: str = None,
                     limit: int = 10) -> List[Dict[str, Any]]:
        """Get summaries with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM summaries WHERE 1=1'
            params = []

            if channel_handle:
                query += ' AND channel_handle = ?'
                params.append(channel_handle)

            if date:
                query += ' AND video_date = ?'
                params.append(date)

            query += ' ORDER BY processed_at DESC LIMIT ?'
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_summary_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a specific video ID if it exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM summaries
                WHERE video_id = ? AND success = 1
                ORDER BY processed_at DESC
                LIMIT 1
            ''', (video_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def has_video_id_been_processed(self, video_id: str) -> bool:
        """Check if a specific video ID has been processed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM summaries
                WHERE video_id = ? AND success = 1
            ''', (video_id,))
            result = cursor.fetchone()
            return result['count'] > 0