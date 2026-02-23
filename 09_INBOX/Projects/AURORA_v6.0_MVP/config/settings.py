"""
Configuration settings for AURORA v6.0 MVP - TIER-0 Integrated
Centralized configuration management
"""

import os

SETTINGS = {
    "system": {
        "name": "AURORA v6.0 MVP - TIER-0 Integrated",
        "version": "6.0.0-TIER0",
        "mode": os.getenv("MODE", "MVP"),
        "compliance": ["NIST SP 800-53", "ISO 27001", "SEC 15c3-5", "MiFID II"]
    },
    
    "mt5": {
        "account": os.getenv("MT5_DEMO_ACCOUNT", "510065181"),
        "server": os.getenv("MT5_DEMO_SERVER", "HantecMarketsMU-MT5"),
        "timeout": 60000
    },
    
    "risk": {
        "max_risk_per_trade": float(os.getenv("MAX_RISK_PER_TRADE", "0.01")),
        "max_daily_loss": float(os.getenv("DAILY_LOSS_LIMIT", "0.05")),
        "max_positions": int(os.getenv("MAX_POSITIONS", "3")),
        "max_drawdown": float(os.getenv("MAX_DRAWDOWN", "0.15")),
        "default_sl_pips": 50,
        "default_tp_pips": 100
    },
    
    "learning": {
        "retrain_frequency_hours": 6,
        "min_experiences": 1000,
        "validation_days": 30,
        "sharpe_threshold": 0.5,
        "check_interval_seconds": 3600
    },
    
    "strategies": {
        "active": ["alpha_momentum"],
        "symbols": ["XAUUSD", "EURUSD"],
        "timeframe": "M5",
        "confidence_threshold": 0.6
    },
    
    "execution": {
        "slippage_tolerance": 20,
        "max_retries": 3,
        "paper_trading": os.getenv("PAPER_TRADING", "true").lower() == "true"
    },
    
    "vault": {
        "addr": os.getenv("VAULT_ADDR", "http://localhost:8200"),
        "token": os.getenv("VAULT_TOKEN", "demo-token"),
        "role": "aurora-core"
    },
    
    "redis": {
        "nodes": os.getenv("REDIS_NODES", "localhost:6379").split(","),
        "retry_count": 3,
        "retry_delay": 200
    },
    
    "api": {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("HEALTH_CHECK_PORT", "8081")),
        "jwt_secret": os.getenv("JWT_SECRET"),
        "api_key_rotation_hours": 24,
        "rate_limit_per_key": int(os.getenv("RATE_LIMIT_PER_KEY", "1000")),
        "rate_limit_per_ip": int(os.getenv("RATE_LIMIT_PER_IP", "100"))
    },
    
    "monitoring": {
        "metrics_port": int(os.getenv("METRICS_PORT", "9091")),
        "health_check_interval": 30
    }
}
