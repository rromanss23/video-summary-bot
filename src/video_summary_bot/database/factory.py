"""Database factory - automatically chooses between SQLite and PostgreSQL"""

import os
import logging

logger = logging.getLogger(__name__)


def get_database():
    """
    Factory function to get the appropriate database instance

    Automatically chooses between PostgreSQL (Supabase) and SQLite based on environment

    Returns:
        Database instance (either PostgresDatabase or Database/SQLite)
    """
    database_url = os.getenv('DATABASE_URL')
    use_supabase = os.getenv('USE_SUPABASE', 'false').lower() == 'true'

    # If DATABASE_URL is set and starts with postgresql://, use PostgreSQL
    if database_url and database_url.startswith('postgresql://'):
        logger.info("🐘 Using PostgreSQL (Supabase) database")
        from .postgres_operations import PostgresDatabase
        return PostgresDatabase(database_url)

    # If USE_SUPABASE is explicitly set to true but no URL, error
    elif use_supabase and not database_url:
        raise ValueError(
            "USE_SUPABASE=true but DATABASE_URL not set. "
            "Please add your Supabase connection string to .env"
        )

    # Default to SQLite
    else:
        logger.info("📁 Using SQLite database (local)")
        from .operations import Database
        db_path = os.getenv('SQLITE_DB_PATH', 'data/video_summary.db')
        return Database(db_path)


# Convenience alias
Database = get_database
