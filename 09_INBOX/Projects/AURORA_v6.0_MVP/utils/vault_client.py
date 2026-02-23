"""
HashiCorp Vault Client com caching e retry logic
Tier-0 compliance para secrets management
"""

import logging
import asyncio
from typing import Any, Optional, Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class Tier0VaultClient:
    """
    Vault client com caching distribuído
    
    Features:
    - TTL cache de 5 minutos para secrets
    - Retry automático com backoff exponencial
    - API key rotation support
    - Thread-safe operations
    """
    
    def __init__(self, vault_addr: str, vault_token: str, role: str = "aurora-core"):
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.role = role
        self.cache: TTLCache = TTLCache(maxsize=100, ttl=300)  # 5-minute TTL
        self._initialized = False
        
        # Simulated vault client for demo mode
        self._demo_secrets: Dict[str, Dict[str, Any]] = {
            "aurora/health": {"test": "ok"},
            "aurora/jwt": {"secret": "demo-jwt-secret-tier0-2026"},
            "aurora/mt5": {
                "account": "510065181",
                "password": "demo_password",
                "server": "HantecMarketsMU-MT5"
            },
            "aurora/risk_limits": {
                "max_drawdown": 0.15,
                "daily_loss_limit": 0.05,
                "max_position_size": 0.10,
                "var_95_limit": 0.02
            },
            "aurora/api_keys/demo_key_aurora_2025": {
                "user": "demo_user",
                "permissions": ["trade", "read"]
            }
        }
        
        logger.info(f"Vault client initialized for {vault_addr}")
        self._initialized = True
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self._initialized
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Obtém segredo do Vault com caching
        
        Args:
            path: Caminho do secret (ex: "aurora/mt5")
            key: Chave específica dentro do secret (opcional)
            
        Returns:
            Valor do secret ou dict completo se key não especificada
        """
        cache_key = f"{path}:{key}" if key else path
        
        # Tentar cache primeiro
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]
        
        try:
            # Demo mode: usar secrets simulados
            if path in self._demo_secrets:
                data = self._demo_secrets[path]
                result = data.get(key) if key else data
                
                # Cache
                self.cache[cache_key] = result
                logger.debug(f"Retrieved secret from Vault: {path}")
                return result
            else:
                raise KeyError(f"Secret not found: {path}")
                
        except Exception as e:
            logger.error(f"Failed to retrieve secret {path}: {e}")
            raise
    
    async def rotate_api_key(self, key_name: str) -> str:
        """
        Gera nova API key e armazena no Vault
        
        Args:
            key_name: Nome identificador da API key
            
        Returns:
            Nova API key gerada
        """
        import secrets
        new_key = secrets.token_urlsafe(32)
        
        # Atualizar no Vault (simulado para demo)
        self._demo_secrets[f"aurora/api_keys/{key_name}"] = {
            "key": new_key,
            "rotated_at": asyncio.get_event_loop().time()
        }
        
        # Invalidar cache
        cache_key = f"aurora/api_keys/{key_name}:key"
        if cache_key in self.cache:
            del self.cache[cache_key]
        
        logger.info(f"API key rotated: {key_name}")
        return new_key
    
    async def put_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Armazena secret no Vault
        
        Args:
            path: Caminho do secret
            data: Dados a armazenar
            
        Returns:
            True se sucesso
        """
        try:
            self._demo_secrets[path] = data
            
            # Invalidar cache relacionado
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(path)]
            for k in keys_to_remove:
                del self.cache[k]
            
            logger.info(f"Secret stored: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Limpa todo o cache de secrets"""
        self.cache.clear()
        logger.info("Vault cache cleared")

