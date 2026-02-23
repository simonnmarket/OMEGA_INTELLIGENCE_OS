"""
Testes de integração completa do sistema Tier-0
"""

import pytest
import asyncio
import jwt
import time
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture
async def initialized_system(mock_vault, mock_redlock):
    """Fixture para sistema inicializado"""
    from health.tier0_health import Tier0HealthMonitor
    from auth.tier0_auth import Tier0AuthMiddleware
    from core.async_orchestrator import AsyncOrchestrator
    
    # Inicializar componentes
    health_monitor = Tier0HealthMonitor(mock_vault, mock_redlock)
    auth_middleware = Tier0AuthMiddleware(mock_vault, mock_redlock)
    orchestrator = AsyncOrchestrator(mock_vault, mock_redlock)
    
    return {
        "health_monitor": health_monitor,
        "auth_middleware": auth_middleware,
        "orchestrator": orchestrator,
        "vault": mock_vault,
        "redlock": mock_redlock
    }


@pytest.mark.asyncio
async def test_full_health_check_flow(initialized_system):
    """Testar fluxo completo de health check"""
    system = await initialized_system
    matrix = await system["health_monitor"].check_comprehensive()
    
    assert matrix.overall.value >= 2  # STABLE or better
    assert "vault" in matrix.components
    assert "redis_cluster" in matrix.components
    
    # Verificar que histórico foi atualizado
    assert len(system["health_monitor"].matrix_history) > 0


@pytest.mark.asyncio
async def test_authentication_flow(initialized_system):
    """Testar fluxo completo de autenticação"""
    system = await initialized_system
    
    # Criar token JWT válido
    secret = "test_jwt_secret"
    system["auth_middleware"].jwt_secret_cache['jwt_secret'] = secret
    
    payload = {"user": "test_user", "exp": time.time() + 3600}
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    # Validar token
    valid, result = await system["auth_middleware"].validate_jwt(token)
    assert valid is True
    assert result["user"] == "test_user"
    
    # Testar rate limiting
    ip = "192.168.1.100"
    for i in range(50):
        allowed = await system["auth_middleware"].rate_limit_by_ip(ip)
        assert allowed is True


@pytest.mark.asyncio
async def test_circuit_breaker_flow(initialized_system):
    """Testar fluxo de circuit breaker"""
    system = await initialized_system
    orchestrator = system["orchestrator"]
    
    # Verificar circuit breakers iniciais
    for name, cb in orchestrator.circuit_breakers.items():
        can_execute = await cb.can_execute()
        assert can_execute is True
        
        state = await cb.get_state()
        assert state["state"].value == "CLOSED"


@pytest.mark.asyncio
async def test_circuit_breaker_failure_handling(initialized_system):
    """Testar handling de falhas do circuit breaker"""
    system = await initialized_system
    orchestrator = system["orchestrator"]
    
    cb = orchestrator.circuit_breakers["mt5"]
    
    # Simular falhas
    for i in range(5):  # threshold padrão
        await cb.record_failure(f"error_{i}")
    
    # Verificar que circuito abriu
    state = await cb.get_state()
    assert state["state"].value == "OPEN"
    
    # Verificar que não pode executar
    can_execute = await cb.can_execute()
    assert can_execute is False


@pytest.mark.asyncio
async def test_risk_engine_trade_flow(mock_vault, mock_circuit_breaker):
    """Testar fluxo de avaliação de trade"""
    from risk.finite_state_risk_tier0 import Tier0RiskEngine, RiskState
    
    engine = Tier0RiskEngine(mock_vault, mock_circuit_breaker)
    await engine.load_limits_from_vault()
    
    # Trade válido
    result = await engine.evaluate_trade({
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05
    })
    
    assert result["approved"] is True
    assert engine.state == RiskState.NORMAL


@pytest.mark.asyncio
async def test_execution_engine_demo_trade(mock_vault, mock_redlock, mock_circuit_breaker):
    """Testar execução de trade em modo demo"""
    from connectors.mt5_connector_tier0 import Tier0MT5Connector
    from risk.finite_state_risk_tier0 import Tier0RiskEngine
    from execution.safe_execution_tier0 import Tier0ExecutionEngine
    
    # Setup
    mt5 = Tier0MT5Connector(
        account="demo",
        password="demo",
        server="demo",
        circuit_breaker=mock_circuit_breaker
    )
    
    risk = Tier0RiskEngine(mock_vault, mock_circuit_breaker)
    await risk.load_limits_from_vault()
    
    execution = Tier0ExecutionEngine(
        mt5_connector=mt5,
        risk_engine=risk,
        circuit_breaker=mock_circuit_breaker,
        redlock=mock_redlock
    )
    
    # Executar trade
    result = await execution.execute_trade({
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.02,
        "idempotency_key": "test_trade_001"
    })
    
    assert result["status"] == "executed"
    assert result["demo"] is True
    assert "trade_id" in result


@pytest.mark.asyncio
async def test_idempotency(mock_vault, mock_redlock, mock_circuit_breaker):
    """Testar idempotência de execução"""
    from connectors.mt5_connector_tier0 import Tier0MT5Connector
    from risk.finite_state_risk_tier0 import Tier0RiskEngine
    from execution.safe_execution_tier0 import Tier0ExecutionEngine
    
    # Setup
    mt5 = Tier0MT5Connector(
        account="demo",
        password="demo",
        server="demo",
        circuit_breaker=mock_circuit_breaker
    )
    
    risk = Tier0RiskEngine(mock_vault, mock_circuit_breaker)
    
    execution = Tier0ExecutionEngine(
        mt5_connector=mt5,
        risk_engine=risk,
        circuit_breaker=mock_circuit_breaker,
        redlock=mock_redlock
    )
    
    trade_request = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.02,
        "idempotency_key": "idempotency_test_001"
    }
    
    # Primeira execução
    result1 = await execution.execute_trade(trade_request)
    assert result1["status"] == "executed"
    
    # Segunda execução com mesma chave
    result2 = await execution.execute_trade(trade_request)
    assert result2["cached"] is True
    assert result2["trade_id"] == result1["trade_id"]


@pytest.mark.asyncio
async def test_mt5_connector_rate_limiting(mock_circuit_breaker):
    """Testar rate limiting do MT5 connector"""
    from connectors.mt5_connector_tier0 import Tier0MT5Connector
    
    mt5 = Tier0MT5Connector(
        account="demo",
        password="demo",
        server="demo",
        circuit_breaker=mock_circuit_breaker,
        requests_per_minute=10  # Limite baixo para teste
    )
    
    # Conectar
    await mt5.connect()
    assert mt5.is_connected() is True
    
    # Fazer requests até o limite
    for i in range(10):
        tick = await mt5.get_tick("EURUSD")
        assert tick is not None
    
    # A próxima deve falhar por rate limiting
    tick = await mt5.get_tick("EURUSD")
    assert tick is None  # Rate limited


