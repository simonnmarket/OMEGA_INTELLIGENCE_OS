from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from functools import wraps
import time

from ..config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Classe para gerenciamento de rate limiting.
    """
    def __init__(self):
        self.requests: Dict[str, Dict[datetime, int]] = defaultdict(dict)
        self.limits: Dict[str, Dict[str, Any]] = {
            "default": {
                "limit": settings.RATE_LIMIT,
                "period": 60  # segundos
            },
            "auth": {
                "limit": 5,
                "period": 60
            },
            "api": {
                "limit": 100,
                "period": 60
            }
        }

    async def get_key(self, request: Request) -> str:
        """
        Obtém a chave para rate limiting baseada no IP ou usuário.
        """
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.id}"
        return f"ip:{request.client.host}"

    async def is_rate_limited(self, request: Request, key: str = "default") -> bool:
        """
        Verifica se a requisição excedeu o limite.
        """
        client_key = await self.get_key(request)
        limit_config = self.limits.get(key, self.limits["default"])
        
        now = datetime.now()
        period = timedelta(seconds=limit_config["period"])
        
        # Remove requisições antigas
        self.requests[client_key] = {
            timestamp: count
            for timestamp, count in self.requests[client_key].items()
            if now - timestamp < period
        }
        
        # Verifica o número de requisições
        total_requests = sum(self.requests[client_key].values())
        if total_requests >= limit_config["limit"]:
            logger.warning(f"Rate limit excedido para {client_key}")
            return True
        
        # Registra a requisição
        self.requests[client_key][now] = self.requests[client_key].get(now, 0) + 1
        return False

    def get_remaining_requests(self, request: Request, key: str = "default") -> int:
        """
        Retorna o número de requisições restantes.
        """
        client_key = await self.get_key(request)
        limit_config = self.limits.get(key, self.limits["default"])
        
        now = datetime.now()
        period = timedelta(seconds=limit_config["period"])
        
        # Remove requisições antigas
        self.requests[client_key] = {
            timestamp: count
            for timestamp, count in self.requests[client_key].items()
            if now - timestamp < period
        }
        
        # Calcula requisições restantes
        total_requests = sum(self.requests[client_key].values())
        return max(0, limit_config["limit"] - total_requests)

    def get_reset_time(self, request: Request, key: str = "default") -> datetime:
        """
        Retorna o tempo até o reset do rate limit.
        """
        client_key = await self.get_key(request)
        limit_config = self.limits.get(key, self.limits["default"])
        
        if not self.requests[client_key]:
            return datetime.now()
        
        oldest_request = min(self.requests[client_key].keys())
        return oldest_request + timedelta(seconds=limit_config["period"])

# Instância global do rate limiter
rate_limiter = RateLimiter()

# Função para obter a chave de rate limiting
async def get_rate_limit_key(request: Request) -> str:
    return await rate_limiter.get_key(request)

# Decorator para rate limiting
def rate_limit(
    key: str,
    max_requests: int = 100,
    time_window: int = 60
):
    """
    Decorador para limitar a taxa de requisições em endpoints.
    
    Args:
        key: Identificador único para o limite de taxa
        max_requests: Número máximo de requisições permitidas
        time_window: Janela de tempo em segundos
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            limit = rate_limits[key]
            
            # Reseta o contador se a janela de tempo expirou
            if current_time > limit["reset_time"]:
                limit["count"] = 0
                limit["reset_time"] = current_time + time_window
            
            # Verifica se o limite foi excedido
            if limit["count"] >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de requisições excedido. Tente novamente em {int(limit['reset_time'] - current_time)} segundos."
                )
            
            # Incrementa o contador
            limit["count"] += 1
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 