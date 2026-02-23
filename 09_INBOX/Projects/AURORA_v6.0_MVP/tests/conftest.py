"""
Pytest configuration and fixtures for AURORA CORE TIER-0 tests
"""

import pytest
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_vault():
    """Mock Vault client"""
    from unittest.mock import AsyncMock
    
    vault = AsyncMock()
    vault.get_secret = AsyncMock(side_effect=lambda path, key=None: {
        "aurora/health": {"test": "value"},
        "aurora/jwt": {"secret": "test_jwt_secret"},
        "aurora/mt5": {"account": "12345", "password": "pass", "server": "demo"},
        "aurora/risk_limits": {
            "max_drawdown": 0.15,
            "daily_loss_limit": 0.05,
            "max_position_size": 0.10,
            "var_95_limit": 0.02
        },
        "aurora/api_keys/test_key": {"user": "test_user", "permissions": ["trade"]}
    }.get(path, {}).get(key) if key else {
        "aurora/health": {"test": "value"},
        "aurora/jwt": {"secret": "test_jwt_secret"},
        "aurora/mt5": {"account": "12345", "password": "pass", "server": "demo"},
        "aurora/risk_limits": {
            "max_drawdown": 0.15,
            "daily_loss_limit": 0.05,
            "max_position_size": 0.10,
            "var_95_limit": 0.02
        },
        "aurora/api_keys/test_key": {"user": "test_user", "permissions": ["trade"]}
    }.get(path, {}))
    vault.is_authenticated = lambda: True
    
    return vault


@pytest.fixture
def mock_redlock():
    """Mock Redlock manager"""
    from unittest.mock import AsyncMock
    
    redlock = AsyncMock()
    redlock.lock = AsyncMock(return_value="lock_id_123")
    redlock.unlock = AsyncMock(return_value=True)
    redlock.is_locked = AsyncMock(return_value=False)
    redlock.get_available_nodes = lambda: 3
    
    return redlock


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker"""
    from unittest.mock import AsyncMock
    from core.async_orchestrator import CircuitState
    
    cb = AsyncMock()
    cb.can_execute = AsyncMock(return_value=True)
    cb.get_state = AsyncMock(return_value={
        "state": CircuitState.CLOSED,
        "failure_count": 0,
        "last_failure": None,
        "last_success": None,
        "since": "2026-01-11T00:00:00"
    })
    cb.record_success = AsyncMock()
    cb.record_failure = AsyncMock()
    cb.reset = lambda: None
    
    return cb


