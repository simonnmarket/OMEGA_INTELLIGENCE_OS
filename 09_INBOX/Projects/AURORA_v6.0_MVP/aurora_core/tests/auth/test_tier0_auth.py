"""
Testes do authentication middleware Tier-0
"""

import pytest
import jwt
import time
from unittest.mock import AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from auth.tier0_auth import Tier0AuthMiddleware


@pytest.fixture
def auth_middleware(mock_vault, mock_redlock):
    """Create auth middleware instance"""
    return Tier0AuthMiddleware(mock_vault, mock_redlock)


@pytest.mark.asyncio
async def test_jwt_validation_success(auth_middleware):
    """Testar validação de JWT válido"""
    # Criar token válido
    secret = "test_jwt_secret"
    auth_middleware.jwt_secret_cache['jwt_secret'] = secret
    
    payload = {"user": "test_user", "exp": time.time() + 3600}
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    valid, result = await auth_middleware.validate_jwt(token)
    
    assert valid is True
    assert "user" in result
    assert result["user"] == "test_user"


@pytest.mark.asyncio
async def test_jwt_validation_expired(auth_middleware):
    """Testar validação de JWT expirado"""
    secret = "test_jwt_secret"
    auth_middleware.jwt_secret_cache['jwt_secret'] = secret
    
    payload = {"user": "test_user", "exp": time.time() - 3600}  # Expirado
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    valid, result = await auth_middleware.validate_jwt(token)
    
    assert valid is False
    assert "error" in result
    assert "expired" in result["error"]


@pytest.mark.asyncio
async def test_jwt_validation_invalid(auth_middleware):
    """Testar validação de JWT inválido"""
    valid, result = await auth_middleware.validate_jwt("invalid_token")
    
    assert valid is False
    assert "error" in result


@pytest.mark.asyncio
async def test_rate_limiting_by_ip(auth_middleware):
    """Testar rate limiting por IP"""
    test_ip = "192.168.1.1"
    
    # Primeiras requests devem passar
    for i in range(100):
        allowed = await auth_middleware.rate_limit_by_ip(test_ip)
        assert allowed is True
    
    # A 101ª deve falhar
    allowed = await auth_middleware.rate_limit_by_ip(test_ip)
    assert allowed is False


@pytest.mark.asyncio
async def test_rate_limiting_reset(auth_middleware):
    """Testar reset do rate limiting após TTL"""
    test_ip = "192.168.1.2"
    
    # Esgotar limite
    for i in range(100):
        await auth_middleware.rate_limit_by_ip(test_ip)
    
    # Esperar que cache expire (simulado manipulando cache)
    auth_middleware.rate_limit_cache.clear()
    
    # Agora deve passar
    allowed = await auth_middleware.rate_limit_by_ip(test_ip)
    assert allowed is True


@pytest.mark.asyncio
async def test_api_key_validation(auth_middleware, mock_vault):
    """Testar validação de API key"""
    # Configure mock to return user data
    mock_vault.get_secret = AsyncMock(return_value={"user": "api_user", "permissions": ["trade"]})
    auth_middleware.vault = mock_vault
    
    valid, result = await auth_middleware.validate_api_key("test_api_key")
    
    assert valid is True
    assert "user" in result


def test_jwt_generation(auth_middleware):
    """Testar geração de JWT"""
    secret = "test_jwt_secret"
    auth_middleware.jwt_secret_cache['jwt_secret'] = secret
    
    token = auth_middleware.generate_jwt("test_user", expiry_hours=1)
    
    # Decodificar e verificar
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    assert payload["user"] == "test_user"
    assert payload["exp"] > time.time()

