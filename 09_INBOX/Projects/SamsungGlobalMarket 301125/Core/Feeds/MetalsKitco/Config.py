# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T19:58:30+01:00
# AUTHOR: Cursor_Omega

"""
Configurações centrais para o feed de metais Kitco.
"""

from pathlib import Path

KITCO_URL = "https://www.kitco.com/"
METALS = ["gold", "silver", "platinum", "palladium"]
LOG_LEVEL = "INFO"
REQUEST_TIMEOUT_SECONDS = 10

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "metal_prices.db"
DB_STRING = f"sqlite:///{DB_PATH.as_posix()}"

