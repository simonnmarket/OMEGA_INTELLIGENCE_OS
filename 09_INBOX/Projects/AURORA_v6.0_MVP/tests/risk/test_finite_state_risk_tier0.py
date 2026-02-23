"""
Testes do Risk Engine Tier-0
"""

import pytest
from pydantic import ValidationError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from risk.finite_state_risk_tier0 import (
    Tier0RiskEngine,
    TradeData,
    RiskState,
    RiskMetrics
)


@pytest.fixture
async def risk_engine(mock_vault, mock_circuit_breaker):
    """Create risk engine instance"""
    engine = Tier0RiskEngine(mock_vault, mock_circuit_breaker)
    await engine.load_limits_from_vault()
    return engine


def test_trade_data_validation_valid():
    """Testar validação de dados de trade válidos"""
    valid_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05
    }
    trade = TradeData(**valid_data)
    
    assert trade.symbol == "EURUSD"
    assert trade.operation == "BUY"
    assert trade.volume == 0.01
    assert trade.price == 1.0850


def test_trade_data_validation_invalid_symbol():
    """Testar validação de símbolo inválido (lowercase)"""
    invalid_data = {
        "symbol": "eurusd",  # lowercase
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05
    }
    
    with pytest.raises(ValidationError):
        TradeData(**invalid_data)


def test_trade_data_validation_invalid_operation():
    """Testar validação de operação inválida"""
    invalid_data = {
        "symbol": "EURUSD",
        "operation": "HOLD",  # inválido
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05
    }
    
    with pytest.raises(ValidationError):
        TradeData(**invalid_data)


def test_trade_data_validation_invalid_volume():
    """Testar validação de volume inválido"""
    invalid_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": -0.01,  # negativo
        "price": 1.0850,
        "drawdown": 0.05
    }
    
    with pytest.raises(ValidationError):
        TradeData(**invalid_data)


def test_risk_metrics_validation():
    """Testar validação de métricas de risco"""
    valid_metrics = {
        "current_drawdown": 0.05,
        "daily_pnl": 100.0,
        "position_size": 0.05,
        "var_95": 0.01,
        "max_drawdown": 0.15
    }
    metrics = RiskMetrics(**valid_metrics)
    assert metrics.current_drawdown == 0.05


def test_risk_metrics_validation_invalid():
    """Testar validação de métricas inválidas"""
    invalid_metrics = {
        "current_drawdown": 1.5,  # > 100%
        "daily_pnl": 100.0,
        "position_size": 0.05,
        "var_95": 0.01,
        "max_drawdown": 0.15
    }
    
    with pytest.raises(ValidationError):
        RiskMetrics(**invalid_metrics)


@pytest.mark.asyncio
async def test_risk_engine_initialization(risk_engine):
    """Testar inicialização do risk engine"""
    assert risk_engine.state == RiskState.NORMAL
    assert risk_engine.limits["max_drawdown"] == 0.15
    assert risk_engine.limits["daily_loss_limit"] == 0.05
    assert len(risk_engine.audit_trail) == 0


@pytest.mark.asyncio
async def test_trade_evaluation_normal(risk_engine):
    """Testar avaliação de trade em estado NORMAL"""
    trade_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05  # 5% drawdown
    }
    
    result = await risk_engine.evaluate_trade(trade_data)
    
    assert result["approved"] is True
    assert result["reason"] == "trade_within_limits"
    assert result["state"] == RiskState.NORMAL.value


@pytest.mark.asyncio
async def test_trade_evaluation_high_drawdown(risk_engine):
    """Testar avaliação de trade com drawdown alto"""
    trade_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.12  # 12% drawdown (80% do limite)
    }
    
    result = await risk_engine.evaluate_trade(trade_data)
    
    assert result["approved"] is False
    assert "approaching_max_drawdown" in result["reason"]
    assert risk_engine.state == RiskState.CRITICAL


@pytest.mark.asyncio
async def test_trade_evaluation_halted(risk_engine):
    """Testar que trade não é aprovado quando engine está HALTED"""
    # Forçar estado HALTED
    risk_engine.state = RiskState.HALTED
    
    trade_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.01
    }
    
    result = await risk_engine.evaluate_trade(trade_data)
    
    assert result["approved"] is False
    assert result["reason"] == "risk_engine_halted"
    assert result["state"] == RiskState.HALTED.value


@pytest.mark.asyncio
async def test_audit_trail(risk_engine):
    """Testar que audit trail é mantido"""
    trade_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.05
    }
    
    await risk_engine.evaluate_trade(trade_data)
    
    assert len(risk_engine.audit_trail) > 0
    last_entry = risk_engine.audit_trail[-1]
    assert "timestamp" in last_entry
    assert "action" in last_entry
    assert last_entry["action"] == "trade_evaluated"


@pytest.mark.asyncio
async def test_state_transition_warning(risk_engine):
    """Testar transição para WARNING state"""
    # Drawdown de 9% (60% do limite de 15%)
    trade_data = {
        "symbol": "EURUSD",
        "operation": "BUY",
        "volume": 0.01,
        "price": 1.0850,
        "drawdown": 0.09
    }
    
    await risk_engine.evaluate_trade(trade_data)
    
    assert risk_engine.state == RiskState.WARNING


@pytest.mark.asyncio
async def test_risk_engine_reset(risk_engine):
    """Testar reset do risk engine"""
    # Colocar em estado não-normal
    risk_engine.state = RiskState.HALTED
    risk_engine.metrics.current_drawdown = 0.20
    
    # Reset
    risk_engine.reset_state()
    
    assert risk_engine.state == RiskState.NORMAL
    assert risk_engine.metrics.current_drawdown == 0.0


@pytest.mark.asyncio
async def test_metrics_update(risk_engine):
    """Testar atualização de métricas"""
    risk_engine.update_metrics(
        drawdown=0.10,
        daily_pnl=-500.0,
        open_positions=3
    )
    
    assert risk_engine.metrics.current_drawdown == 0.10
    assert risk_engine.metrics.daily_pnl == -500.0
    assert risk_engine.metrics.open_positions == 3


