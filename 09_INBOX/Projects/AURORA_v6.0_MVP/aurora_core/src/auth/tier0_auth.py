"""
Authentication middleware Tier-0
JWT + API Key + Rate limiting + Audit trail
"""

import time
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Tuple, Any
import jwt
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)


class Tier0AuthMiddleware:
    """
    Middleware de autenticação Tier-0
    
    Features:
    - JWT validation com cache
    - API key validation
    - Rate limiting por IP e por key
    - Audit logging
    """
    
    def __init__(self, vault_client: Any, redlock: Any):
        """
        Initialize auth middleware
        
        Args:
            vault_client: Instância do Tier0VaultClient
            redlock: Instância do RedlockManager
        """
        self.vault = vault_client
        self.redlock = redlock
        
        # Caches
        self.jwt_secret_cache: TTLCache = TTLCache(maxsize=1, ttl=300)
        self.api_key_cache: TTLCache = TTLCache(maxsize=100, ttl=60)
        self.rate_limit_cache: TTLCache = TTLCache(maxsize=1000, ttl=60)
        
        # Rate limiting
        self.rate_limit_per_key = int(os.getenv("RATE_LIMIT_PER_KEY", "1000"))
        self.rate_limit_per_ip = int(os.getenv("RATE_LIMIT_PER_IP", "100"))
    
    async def get_jwt_secret(self) -> str:
        """Obtém JWT secret do Vault com cache"""
        if 'jwt_secret' in self.jwt_secret_cache:
            return self.jwt_secret_cache['jwt_secret']
        
        try:
            secret = await self.vault.get_secret("aurora/jwt", "secret")
            self.jwt_secret_cache['jwt_secret'] = secret
            return secret
        except Exception as e:
            logger.error(f"Failed to get JWT secret: {e}")
            # Fallback para demo
            return "demo-jwt-secret-tier0-2026"
    
    async def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict]]:
        """
        Valida API key com rate limiting e audit
        
        Args:
            api_key: API key a validar
            
        Returns:
            Tuple (válido, dados do usuário ou erro)
        """
        cache_key = f"api_key:{api_key}"
        
        # Verificar rate limiting
        request_count = self.rate_limit_cache.get(cache_key, 0)
        if request_count >= self.rate_limit_per_key:
            logger.warning(f"API key rate limit exceeded: {api_key[:8]}...")
            return False, {"error": "rate_limit_exceeded"}
        
        # Incrementar contador
        self.rate_limit_cache[cache_key] = request_count + 1
        
        # Verificar cache
        if cache_key in self.api_key_cache:
            return True, self.api_key_cache[cache_key]
        
        try:
            # Validar no Vault
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            lock_id = await self.redlock.lock(f"validate_api_key:{key_hash}")
            
            try:
                key_data = await self.vault.get_secret(f"aurora/api_keys/{api_key}")
                
                # Armazenar em cache
                self.api_key_cache[cache_key] = key_data
                
                # Audit log
                logger.info(f"API key validated: {api_key[:8]}..., user={key_data.get('user', 'unknown')}")
                
                return True, key_data
                
            finally:
                if lock_id:
                    await self.redlock.unlock(f"validate_api_key:{key_hash}", lock_id)
            
        except Exception as e:
            logger.error(f"API key validation failed: {api_key[:8]}..., error={e}")
            return False, {"error": "invalid_api_key"}
    
    async def validate_jwt(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Valida JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Tuple (válido, payload ou erro)
        """
        try:
            secret = await self.get_jwt_secret()
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            
            # Verificar expiração
            if payload.get('exp', 0) < time.time():
                return False, {"error": "token_expired"}
            
            logger.debug(f"JWT validated for user: {payload.get('user', 'unknown')}")
            return True, payload
            
        except jwt.ExpiredSignatureError:
            return False, {"error": "token_expired"}
        except jwt.InvalidTokenError as e:
            return False, {"error": f"invalid_token: {str(e)}"}
    
    async def rate_limit_by_ip(self, ip_address: str) -> bool:
        """
        Rate limiting por IP
        
        Args:
            ip_address: Endereço IP
            
        Returns:
            True se permitido, False se bloqueado
        """
        cache_key = f"ip_limit:{ip_address}"
        request_count = self.rate_limit_cache.get(cache_key, 0)
        
        if request_count >= self.rate_limit_per_ip:
            logger.warning(f"IP rate limit exceeded: {ip_address}")
            return False
        
        self.rate_limit_cache[cache_key] = request_count + 1
        return True
    
    def generate_jwt(self, user: str, expiry_hours: int = 24) -> str:
        """
        Gera JWT token para usuário
        
        Args:
            user: Identificador do usuário
            expiry_hours: Horas até expiração
            
        Returns:
            JWT token
        """
        import asyncio
        
        # Obter secret (síncrono para este método)
        secret = "demo-jwt-secret-tier0-2026"
        if 'jwt_secret' in self.jwt_secret_cache:
            secret = self.jwt_secret_cache['jwt_secret']
        
        payload = {
            "user": user,
            "iat": time.time(),
            "exp": time.time() + (expiry_hours * 3600)
        }
        
        return jwt.encode(payload, secret, algorithm="HS256")


async def get_auth_middleware() -> Tier0AuthMiddleware:
    """Dependency injection para auth middleware"""
    from src.utils.vault_client import Tier0VaultClient
    from src.utils.redlock_manager import RedlockManager
    
    vault_client = Tier0VaultClient(
        vault_addr=os.getenv("VAULT_ADDR", "http://localhost:8200"),
        vault_token=os.getenv("VAULT_TOKEN", "demo-token")
    )
    redlock = RedlockManager(
        redis_urls=os.getenv("REDIS_NODES", "localhost:6379").split(",")
    )
    return Tier0AuthMiddleware(vault_client, redlock)


async def authenticate_request(
    authorization: Optional[str] = None,
    api_key: Optional[str] = None,
    client_ip: str = "127.0.0.1",
    auth_middleware: Optional[Tier0AuthMiddleware] = None
) -> Dict[str, Any]:
    """
    Authenticate request with multiple methods
    
    Args:
        authorization: Bearer token (opcional)
        api_key: X-API-Key header (opcional)
        client_ip: IP do cliente
        auth_middleware: Instância do middleware
        
    Returns:
        Dict com método de auth e dados do usuário
    """
    if auth_middleware is None:
        auth_middleware = await get_auth_middleware()
    
    # Rate limiting por IP
    if not await auth_middleware.rate_limit_by_ip(client_ip):
        raise Exception("Too many requests")
    
    # Tentar JWT primeiro
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        valid, payload = await auth_middleware.validate_jwt(token)
        if valid:
            return {"auth_method": "jwt", "user": payload}
    
    # Tentar API key
    if api_key:
        valid, key_data = await auth_middleware.validate_api_key(api_key)
        if valid:
            return {"auth_method": "api_key", "user": key_data}
    
    # Se demo mode, permitir sem autenticação
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        return {"auth_method": "demo", "user": {"name": "demo_user", "permissions": ["trade", "read"]}}
    
    raise Exception("Authentication required")

