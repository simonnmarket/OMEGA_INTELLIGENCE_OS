import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..backend.agents.riskguardian import RiskGuardian
from ..backend.core.database import Database

class TestRiskGuardian:
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = MagicMock(spec=Database)
        return mock

    @pytest.fixture
    def risk_guardian(self, mock_db):
        """Create a test instance of RiskGuardian."""
        return RiskGuardian(
            max_risk_per_trade=0.02,
            max_daily_risk=0.05,
            max_drawdown=0.1,
            db=mock_db
        )

    def test_assess_trade_risk(self, risk_guardian, mock_db):
        """Test trade risk assessment."""
        # Mock account balance
        mock_db.get_account_info.return_value = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 1000.0,
            'free_margin': 9000.0
        }

        assessment = risk_guardian.assess_trade_risk(
            symbol="EURUSD",
            volume=0.1,
            entry_price=1.0,
            stop_loss=0.9
        )

        assert isinstance(assessment, dict)
        assert 'approved' in assessment
        assert 'position_risk' in assessment
        assert 'risk_percentage' in assessment
        assert 'daily_risk' in assessment
        assert 'drawdown' in assessment

    @pytest.mark.stress
    def test_stress_trade_risk_assessment(self, risk_guardian, mock_db):
        """Stress test for trade risk assessment."""
        # Mock account balance
        mock_db.get_account_info.return_value = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 1000.0,
            'free_margin': 9000.0
        }

        # Test multiple concurrent assessments
        for i in range(100):
            symbol = f"EURUSD{i}"
            volume = np.random.uniform(0.01, 0.5)
            entry_price = 1.0 + (i * 0.0001)
            stop_loss = entry_price - np.random.uniform(0.001, 0.01)

            assessment = risk_guardian.assess_trade_risk(
                symbol=symbol,
                volume=volume,
                entry_price=entry_price,
                stop_loss=stop_loss
            )

            assert isinstance(assessment, dict)
            assert all(key in assessment for key in ['approved', 'position_risk', 'risk_percentage', 'daily_risk', 'drawdown'])

    def test_monitor_positions(self, risk_guardian, mock_db):
        """Test position monitoring."""
        # Mock positions
        mock_positions = [
            {
                'symbol': 'EURUSD',
                'type': 'buy',
                'volume': 0.1,
                'price': 1.0,
                'sl': 0.9,
                'tp': 1.1
            }
        ]
        mock_db.get_positions.return_value = mock_positions

        # Mock market data
        mock_market_data = pd.DataFrame({
            'close': np.random.uniform(0.95, 1.05, 100),
            'volume': np.random.randint(1000, 2000, 100)
        })
        mock_db.get_market_data.return_value = mock_market_data

        monitoring = risk_guardian.monitor_positions()
        assert isinstance(monitoring, dict)
        assert 'risk_level' in monitoring
        assert 'total_exposure' in monitoring
        assert 'exposure_percentage' in monitoring
        assert 'volatility' in monitoring
        assert 'correlation' in monitoring

    @pytest.mark.stress
    def test_stress_position_monitoring(self, risk_guardian, mock_db):
        """Stress test for position monitoring."""
        # Mock multiple positions
        mock_positions = []
        for i in range(100):
            mock_positions.append({
                'symbol': f'EURUSD{i}',
                'type': 'buy',
                'volume': np.random.uniform(0.01, 0.5),
                'price': 1.0 + (i * 0.0001),
                'sl': 0.9,
                'tp': 1.1
            })
        mock_db.get_positions.return_value = mock_positions

        # Mock market data
        mock_market_data = pd.DataFrame({
            'close': np.random.uniform(0.95, 1.05, 10000),
            'volume': np.random.randint(1000, 2000, 10000)
        })
        mock_db.get_market_data.return_value = mock_market_data

        # Test multiple concurrent monitoring
        for _ in range(100):
            monitoring = risk_guardian.monitor_positions()
            assert isinstance(monitoring, dict)
            assert all(key in monitoring for key in ['risk_level', 'total_exposure', 'exposure_percentage', 'volatility', 'correlation'])

    def test_calculate_position_size(self, risk_guardian, mock_db):
        """Test position size calculation."""
        # Mock account balance
        mock_db.get_account_info.return_value = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 1000.0,
            'free_margin': 9000.0
        }

        position_size = risk_guardian.calculate_position_size(
            symbol="EURUSD",
            entry_price=1.0,
            stop_loss=0.9,
            risk_amount=100.0
        )

        assert isinstance(position_size, float)
        assert position_size > 0

    @pytest.mark.stress
    def test_stress_position_size_calculation(self, risk_guardian, mock_db):
        """Stress test for position size calculation."""
        # Mock account balance
        mock_db.get_account_info.return_value = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 1000.0,
            'free_margin': 9000.0
        }

        # Test multiple concurrent calculations
        for i in range(100):
            symbol = f"EURUSD{i}"
            entry_price = 1.0 + (i * 0.0001)
            stop_loss = entry_price - np.random.uniform(0.001, 0.01)
            risk_amount = np.random.uniform(50.0, 200.0)

            position_size = risk_guardian.calculate_position_size(
                symbol=symbol,
                entry_price=entry_price,
                stop_loss=stop_loss,
                risk_amount=risk_amount
            )

            assert isinstance(position_size, float)
            assert position_size > 0

    def test_error_handling(self, risk_guardian, mock_db):
        """Test error handling."""
        # Test database error
        mock_db.get_account_info.return_value = None
        assert risk_guardian.assess_trade_risk("EURUSD", 0.1, 1.0, 0.9) is None

        # Test invalid position size calculation
        assert risk_guardian.calculate_position_size("EURUSD", 1.0, 1.0, 100.0) is None

        # Test monitoring error
        mock_db.get_positions.return_value = None
        assert risk_guardian.monitor_positions() is None 