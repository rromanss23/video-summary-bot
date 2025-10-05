"""Database module - supports both SQLite and PostgreSQL"""

from .factory import get_database, Database

__all__ = ['Database', 'get_database']
