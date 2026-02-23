from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
import time

def setup_logger(name: str) -> logging.Logger:
    """Configura um logger com formatação padrão"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def format_currency(value: float) -> str:
    """Formata um valor como moeda"""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Formata um valor como porcentagem"""
    return f"{value:.2%}"

def calculate_time_delta(start_time: datetime) -> str:
    """Calcula o tempo decorrido desde start_time"""
    delta = datetime.utcnow() - start_time
    if delta.days > 0:
        return f"{delta.days}d {delta.seconds//3600}h"
    elif delta.seconds > 3600:
        return f"{delta.seconds//3600}h {(delta.seconds%3600)//60}m"
    else:
        return f"{delta.seconds//60}m {delta.seconds%60}s"

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator para tentar novamente uma função em caso de falha"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

def validate_json(data: str) -> bool:
    """Valida se uma string é um JSON válido"""
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def parse_date(date_str: str) -> Optional[datetime]:
    """Converte uma string de data para datetime"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def generate_unique_id() -> str:
    """Gera um ID único baseado no timestamp"""
    return str(int(time.time() * 1000))

def format_error_message(error: Exception) -> Dict[str, str]:
    """Formata uma mensagem de erro para resposta da API"""
    return {
        "error": str(error),
        "type": error.__class__.__name__
    }

def calculate_weighted_average(values: List[float], weights: List[float]) -> float:
    """Calcula a média ponderada"""
    if not values or not weights or len(values) != len(weights):
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)

def format_timestamp(timestamp: datetime) -> str:
    """Formata um timestamp para string ISO"""
    return timestamp.isoformat()

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Converte uma string ISO para datetime"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        return None

def calculate_compound_return(returns: List[float]) -> float:
    """Calcula o retorno composto"""
    return (1 + sum(returns)) ** (1 / len(returns)) - 1 if returns else 0.0

def format_large_number(number: float) -> str:
    """Formata números grandes com sufixos (K, M, B)"""
    if number >= 1e9:
        return f"{number/1e9:.2f}B"
    elif number >= 1e6:
        return f"{number/1e6:.2f}M"
    elif number >= 1e3:
        return f"{number/1e3:.2f}K"
    else:
        return f"{number:.2f}" 