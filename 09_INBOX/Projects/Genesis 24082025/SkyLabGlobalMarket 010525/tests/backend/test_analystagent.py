import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..backend.agents.analystagent import AnalystAgent
from ..backend.core.database import Database

class TestAnalystAgent:
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = MagicMock(spec=Database)
        return mock

    @pytest.fixture
    def analyst_agent(self, mock_db):
        """Create a test instance of AnalystAgent."""
        return AnalystAgent(mock_db)

    def test_analyze_performance(self, analyst_agent, mock_db):
        """Test performance analysis."""
        # Mock transaction data
        mock_transactions = [
            {
                'symbol': 'EURUSD',
                'timestamp': datetime.now(),
                'action': 'buy',
                'entry_price': 1.0,
                'exit_price': 1.1,
                'volume': 0.1,
                'profit': 0.01,
                'status': 'closed'
            }
        ]
        mock_db.get_transactions.return_value = mock_transactions

        analysis = analyst_agent.analyze_performance(days=1)
        assert isinstance(analysis, dict)
        assert 'total_trades' in analysis
        assert 'win_rate' in analysis
        assert 'profit_factor' in analysis
        assert 'sharpe_ratio' in analysis

    @pytest.mark.stress
    def test_stress_performance_analysis(self, analyst_agent, mock_db):
        """Stress test for performance analysis."""
        # Create large mock transaction dataset
        mock_transactions = []
        for i in range(1000):
            profit = np.random.uniform(-0.01, 0.01)
            mock_transactions.append({
                'symbol': f'EURUSD{i}',
                'timestamp': datetime.now() - timedelta(days=i),
                'action': 'buy' if profit > 0 else 'sell',
                'entry_price': 1.0,
                'exit_price': 1.0 + profit,
                'volume': 0.1,
                'profit': profit,
                'status': 'closed'
            })
        mock_db.get_transactions.return_value = mock_transactions

        # Test multiple concurrent analyses
        for _ in range(100):
            analysis = analyst_agent.analyze_performance(days=1000)
            assert isinstance(analysis, dict)
            assert all(key in analysis for key in ['total_trades', 'win_rate', 'profit_factor', 'sharpe_ratio'])

    def test_analyze_market_conditions(self, analyst_agent):
        """Test market conditions analysis."""
        # Create test data
        data = pd.DataFrame({
            'close': np.random.uniform(1.0, 1.1, 100),
            'volume': np.random.randint(1000, 2000, 100)
        })

        analysis = analyst_agent.analyze_market_conditions(data)
        assert isinstance(analysis, dict)
        assert 'trend' in analysis
        assert 'momentum' in analysis
        assert 'volatility' in analysis
        assert 'volume' in analysis
        assert 'support_resistance' in analysis

    @pytest.mark.stress
    def test_stress_market_conditions_analysis(self, analyst_agent):
        """Stress test for market conditions analysis."""
        # Create large test dataset
        data = pd.DataFrame({
            'close': np.random.uniform(1.0, 1.1, 10000),
            'volume': np.random.randint(1000, 2000, 10000)
        })

        # Test multiple concurrent analyses
        for _ in range(100):
            analysis = analyst_agent.analyze_market_conditions(data)
            assert isinstance(analysis, dict)
            assert all(key in analysis for key in ['trend', 'momentum', 'volatility', 'volume', 'support_resistance'])

    def test_generate_signals(self, analyst_agent):
        """Test signal generation."""
        # Create test market conditions
        market_conditions = {
            'trend': {'direction': 'up', 'strength': 0.8},
            'momentum': {'rsi': 60, 'macd': 0.001},
            'volatility': {'atr': 0.001, 'bollinger_bands': {'upper': 1.1, 'lower': 0.9}},
            'volume': {'trend': 'increasing', 'strength': 0.7},
            'support_resistance': {'support': 1.0, 'resistance': 1.1}
        }

        signals = analyst_agent.generate_signals(market_conditions)
        assert isinstance(signals, dict)
        assert 'entry' in signals
        assert 'exit' in signals
        assert 'strength' in signals

    @pytest.mark.stress
    def test_stress_signal_generation(self, analyst_agent):
        """Stress test for signal generation."""
        # Create multiple test market conditions
        for _ in range(100):
            market_conditions = {
                'trend': {
                    'direction': np.random.choice(['up', 'down', 'sideways']),
                    'strength': np.random.uniform(0, 1)
                },
                'momentum': {
                    'rsi': np.random.uniform(30, 70),
                    'macd': np.random.uniform(-0.01, 0.01)
                },
                'volatility': {
                    'atr': np.random.uniform(0.001, 0.01),
                    'bollinger_bands': {
                        'upper': 1.0 + np.random.uniform(0.01, 0.1),
                        'lower': 1.0 - np.random.uniform(0.01, 0.1)
                    }
                },
                'volume': {
                    'trend': np.random.choice(['increasing', 'decreasing', 'stable']),
                    'strength': np.random.uniform(0, 1)
                },
                'support_resistance': {
                    'support': 1.0 - np.random.uniform(0.01, 0.1),
                    'resistance': 1.0 + np.random.uniform(0.01, 0.1)
                }
            }

            signals = analyst_agent.generate_signals(market_conditions)
            assert isinstance(signals, dict)
            assert all(key in signals for key in ['entry', 'exit', 'strength'])

    def test_error_handling(self, analyst_agent, mock_db):
        """Test error handling."""
        # Test database error
        mock_db.get_transactions.return_value = None
        assert analyst_agent.analyze_performance(days=1) is None

        # Test invalid data error
        assert analyst_agent.analyze_market_conditions(pd.DataFrame()) is None

        # Test invalid market conditions error
        assert analyst_agent.generate_signals({}) is None 