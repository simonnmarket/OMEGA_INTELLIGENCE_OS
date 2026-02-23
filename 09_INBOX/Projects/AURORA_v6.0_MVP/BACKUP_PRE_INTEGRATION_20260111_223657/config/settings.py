"""
Settings - AURORA v6.0 MVP
Configurações centralizadas do sistema
"""

SETTINGS = {
    "mt5": {
        "account": 510065181,
        "server": "HantecMarketsMU-MT5",
        "password": None,  # Definir via variável de ambiente MT5_PASSWORD
        "timeout": 60000
    },
    "risk": {
        "max_risk_per_trade": 0.01,   # 1% do capital por trade
        "max_daily_loss": 0.05,        # 5% perda máxima diária
        "max_positions": 3,            # Máximo de posições simultâneas
        "max_drawdown": 0.15,          # 15% drawdown máximo (kill switch)
        "default_sl_pips": 50,         # Stop loss padrão em pips
        "default_tp_pips": 100         # Take profit padrão em pips
    },
    "learning": {
        "retrain_frequency_hours": 6,   # Frequência de retreino
        "min_experiences": 1000,        # Mínimo de experiências para treinar
        "validation_days": 30,          # Dias de backtest para validação
        "sharpe_threshold": 0.5,        # Sharpe mínimo para deploy
        "check_interval_seconds": 3600  # Intervalo de check (1 hora)
    },
    "strategies": {
        "active": ["alpha_momentum"],   # Estratégias ativas
        "symbols": ["XAUUSD"],          # Símbolos para operar
        "timeframe": "M5",              # Timeframe principal
        "confidence_threshold": 0.6     # Confiança mínima para executar
    },
    "execution": {
        "slippage_tolerance": 20,       # Tolerância de slippage em pontos
        "max_retries": 3,               # Tentativas de execução
        "retry_delay_ms": 500,          # Delay entre tentativas
        "paper_trading": True           # Modo paper trading (sem execução real)
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        "file": "logs/aurora_v6.log",
        "console": True
    },
    "system": {
        "name": "AURORA v6.0 MVP",
        "version": "6.0.0",
        "mode": "MVP",  # MVP, PRODUCTION, DEBUG
        "heartbeat_interval": 60  # Segundos entre heartbeats
    }
}


def get_setting(path: str, default=None):
    """
    Obtém configuração por caminho pontilhado
    
    Exemplo:
        get_setting("mt5.account") -> 510065181
        get_setting("risk.max_positions") -> 3
    """
    keys = path.split(".")
    value = SETTINGS
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def update_setting(path: str, value):
    """
    Atualiza configuração em runtime
    
    Exemplo:
        update_setting("strategies.symbols", ["XAUUSD", "EURUSD"])
    """
    keys = path.split(".")
    target = SETTINGS
    
    for key in keys[:-1]:
        target = target[key]
    
    target[keys[-1]] = value

