"""
Database configuration for AURORA v6.0 MVP - TIER-0 Integrated
"""

import os

DATABASE_CONFIG = {
    "experience_buffer": os.path.join("data", "experience_buffer", "trades.db"),
    "models_path": os.path.join("data", "models"),
    "backups_path": os.path.join("data", "backups"),
    "logs_path": "logs",
    "cache_path": os.path.join("data", "cache")
}
