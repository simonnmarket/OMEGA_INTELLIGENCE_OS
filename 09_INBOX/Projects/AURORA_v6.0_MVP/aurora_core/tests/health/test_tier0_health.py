"""
Testes da health server Tier-0
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from health.tier0_health import HealthLevel, Tier0HealthMonitor, ComponentHealth


@pytest.mark.asyncio
async def test_health_monitor_initialization(mock_vault, mock_redlock):
    """Testar inicialização do monitor de saúde"""
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    
    assert monitor.dependency_matrix is not None
    assert "vault" in monitor.dependency_matrix
    assert "redis_cluster" in monitor.dependency_matrix
    assert len(monitor.matrix_history) == 0


@pytest.mark.asyncio
async def test_vault_health_check_success(mock_vault, mock_redlock):
    """Testar check de saúde do Vault com sucesso"""
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    result = await monitor.check_vault()
    
    assert result.name == "vault"
    assert result.level in [HealthLevel.OPTIMAL, HealthLevel.RESILIENT]
    assert "authenticated" in result.details
    assert result.details["authenticated"] is True


@pytest.mark.asyncio
async def test_vault_health_check_failure(mock_vault, mock_redlock):
    """Testar check de saúde do Vault com falha"""
    mock_vault.get_secret = AsyncMock(side_effect=Exception("Vault connection failed"))
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    result = await monitor.check_vault()
    
    assert result.name == "vault"
    assert result.level == HealthLevel.CRITICAL
    assert "error" in result.details


@pytest.mark.asyncio
async def test_redis_health_check_success(mock_vault, mock_redlock):
    """Testar check de saúde do Redis com sucesso"""
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    result = await monitor.check_redis_cluster()
    
    assert result.name == "redis_cluster"
    assert result.level in [HealthLevel.OPTIMAL, HealthLevel.RESILIENT]
    assert result.details["distributed_locking"] is True


@pytest.mark.asyncio
async def test_comprehensive_health_matrix(mock_vault, mock_redlock):
    """Testar matriz de saúde completa"""
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    matrix = await monitor.check_comprehensive()
    
    assert matrix.overall in HealthLevel
    assert "vault" in matrix.components
    assert "redis_cluster" in matrix.components
    assert isinstance(matrix.audit_trail, list)
    assert isinstance(matrix.recommendations, list)
    
    # Verificar que histórico está sendo mantido
    assert len(monitor.matrix_history) > 0


def test_health_level_hierarchy():
    """Testar hierarquia dos níveis de saúde"""
    assert HealthLevel.CRITICAL.value < HealthLevel.DEGRADED.value
    assert HealthLevel.DEGRADED.value < HealthLevel.STABLE.value
    assert HealthLevel.STABLE.value < HealthLevel.OPTIMAL.value
    assert HealthLevel.OPTIMAL.value < HealthLevel.RESILIENT.value


@pytest.mark.asyncio
async def test_health_history_management(mock_vault, mock_redlock):
    """Testar gerenciamento do histórico de health checks"""
    monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    
    # Executar múltiplos checks
    for _ in range(5):
        await monitor.check_comprehensive()
    
    # Verificar histórico
    history = monitor.get_history(limit=3)
    assert len(history) == 3
    
    # Limpar histórico
    monitor.clear_history()
    assert len(monitor.matrix_history) == 0

