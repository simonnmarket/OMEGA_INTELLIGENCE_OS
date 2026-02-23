"""
PACKAGE PRINCIPAL DA API AURORA v5.0
"""

__version__ = "5.0.0"
__author__ = "Aurora Trading System"

from .database import (
    Base, engine, get_db, db_session, init_database,
    get_database_status, SessionFactory, ScopedSession, TimestampMixin
)

from .main import app
from .endpoints import strategies, health, monitoring

__all__ = [
    "app", "__version__",
    "Base", "engine", "get_db", "db_session", "init_database",
    "get_database_status", "SessionFactory", "ScopedSession", "TimestampMixin",
    "strategies", "health", "monitoring"
]