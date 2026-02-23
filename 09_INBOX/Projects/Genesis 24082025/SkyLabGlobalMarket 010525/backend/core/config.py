from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class for all modules."""
    
    # Database Configuration
    DATABASE = {
        'url': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/samsung_global_market'),
        'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10)),
        'echo': os.getenv('DB_ECHO', 'False').lower() == 'true'
    }
    
    # MT5 Configuration
    MT5 = {
        'login': int(os.getenv('MT5_LOGIN', 12345)),
        'password': os.getenv('MT5_PASSWORD', 'password'),
        'server': os.getenv('MT5_SERVER', 'server'),
        'timeout': int(os.getenv('MT5_TIMEOUT', 10000))
    }
    
    # Redis Configuration
    REDIS = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': int(os.getenv('REDIS_DB', 0)),
        'password': os.getenv('REDIS_PASSWORD', None)
    }
    
    # TraderBot Configuration
    TRADER_BOT = {
        'max_positions': int(os.getenv('MAX_POSITIONS', 10)),
        'default_timeframe': os.getenv('DEFAULT_TIMEFRAME', 'H1'),
        'default_symbols': os.getenv('DEFAULT_SYMBOLS', 'EURUSD,GBPUSD,USDJPY').split(',')
    }
    
    # AnalystAgent Configuration
    ANALYST_AGENT = {
        'analysis_periods': {
            'short': int(os.getenv('SHORT_PERIOD', 14)),
            'medium': int(os.getenv('MEDIUM_PERIOD', 50)),
            'long': int(os.getenv('LONG_PERIOD', 200))
        },
        'indicators': {
            'rsi_period': int(os.getenv('RSI_PERIOD', 14)),
            'macd_fast': int(os.getenv('MACD_FAST', 12)),
            'macd_slow': int(os.getenv('MACD_SLOW', 26)),
            'macd_signal': int(os.getenv('MACD_SIGNAL', 9))
        }
    }
    
    # RiskGuardian Configuration
    RISK_GUARDIAN = {
        'max_risk_per_trade': float(os.getenv('MAX_RISK_PER_TRADE', 0.02)),
        'max_daily_risk': float(os.getenv('MAX_DAILY_RISK', 0.05)),
        'max_drawdown': float(os.getenv('MAX_DRAWDOWN', 0.1)),
        'max_correlation': float(os.getenv('MAX_CORRELATION', 0.7))
    }
    
    # Logging Configuration
    LOGGING = {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': os.getenv('LOG_FILE', 'app.log')
    }
    
    # API Configuration
    API = {
        'host': os.getenv('API_HOST', '0.0.0.0'),
        'port': int(os.getenv('API_PORT', 8000)),
        'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
        'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
    }
    
    @classmethod
    def get_module_config(cls, module_name: str) -> Dict[str, Any]:
        """Get configuration for a specific module."""
        return getattr(cls, module_name.upper(), {})
    
    @classmethod
    def update_config(cls, module_name: str, config: Dict[str, Any]) -> None:
        """Update configuration for a specific module."""
        if hasattr(cls, module_name.upper()):
            setattr(cls, module_name.upper(), config)
        else:
            raise ValueError(f"Module {module_name} not found in configuration") 