import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..backend.agents.traderbot import TraderBot
from ..backend.api.mt5_connector import MT5Connector
from ..backend.core.database import Database

class TestTraderBot:
    @pytest.fixture
    def mock_mt5(self):
        """Create a mock MT5 connector."""
        mock = MagicMock(spec=MT5Connector)
        mock.connected = True
        return mock

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = MagicMock(spec=Database)
        return mock

    @pytest.fixture
    def trader_bot(self, mock_mt5, mock_db):
        """Create a test instance of TraderBot."""
        return TraderBot(mock_mt5, mock_db)

    def test_fetch_market_data(self, trader_bot, mock_mt5, mock_db):
        """Test market data fetching."""
        # Mock market data
        mock_data = pd.DataFrame({
            'time': [datetime.now()],
            'open': [1.0],
            'high': [1.1],
            'low': [0.9],
            'close': [1.05],
            'tick_volume': [1000]
        })
        mock_mt5.get_market_data.return_value = mock_data
        mock_db.add_market_data.return_value = True

        result = trader_bot.fetch_market_data("EURUSD", 1, 1)
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        mock_db.add_market_data.assert_called_once()

    @pytest.mark.stress
    def test_stress_market_data_fetching(self, trader_bot, mock_mt5, mock_db):
        """Stress test for market data fetching."""
        # Mock market data
        mock_data = pd.DataFrame({
            'time': [datetime.now()] * 1000,
            'open': np.random.uniform(1.0, 1.1, 1000),
            'high': np.random.uniform(1.1, 1.2, 1000),
            'low': np.random.uniform(0.9, 1.0, 1000),
            'close': np.random.uniform(1.0, 1.1, 1000),
            'tick_volume': np.random.randint(1000, 2000, 1000)
        })
        mock_mt5.get_market_data.return_value = mock_data
        mock_db.add_market_data.return_value = True

        # Test multiple concurrent requests
        for _ in range(100):
            result = trader_bot.fetch_market_data("EURUSD", 1, 1000)
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1000

    def test_analyze_market(self, trader_bot):
        """Test market analysis."""
        # Create test data
        data = pd.DataFrame({
            'close': np.random.uniform(1.0, 1.1, 100),
            'volume': np.random.randint(1000, 2000, 100)
        })

        analysis = trader_bot.analyze_market(data)
        assert isinstance(analysis, dict)
        assert 'trend' in analysis
        assert 'momentum' in analysis
        assert 'volatility' in analysis

    @pytest.mark.stress
    def test_stress_market_analysis(self, trader_bot):
        """Stress test for market analysis."""
        # Create large test dataset
        data = pd.DataFrame({
            'close': np.random.uniform(1.0, 1.1, 10000),
            'volume': np.random.randint(1000, 2000, 10000)
        })

        # Test multiple concurrent analyses
        for _ in range(100):
            analysis = trader_bot.analyze_market(data)
            assert isinstance(analysis, dict)
            assert all(key in analysis for key in ['trend', 'momentum', 'volatility'])

    def test_execute_trade(self, trader_bot, mock_mt5, mock_db):
        """Test trade execution."""
        # Mock order result
        mock_result = {
            'ticket': 12345,
            'price': 1.0,
            'volume': 0.1,
            'comment': 'Test order'
        }
        mock_mt5.send_order.return_value = mock_result
        mock_db.add_transaction.return_value = True

        result = trader_bot.execute_trade(
            symbol="EURUSD",
            action="buy",
            volume=0.1,
            entry_price=1.0,
            stop_loss=0.9,
            take_profit=1.1
        )

        assert result is not None
        assert result['ticket'] == 12345
        assert "EURUSD" in trader_bot.positions

    @pytest.mark.stress
    def test_stress_trade_execution(self, trader_bot, mock_mt5, mock_db):
        """Stress test for trade execution."""
        # Mock order results
        mock_result = {
            'ticket': 12345,
            'price': 1.0,
            'volume': 0.1,
            'comment': 'Test order'
        }
        mock_mt5.send_order.return_value = mock_result
        mock_db.add_transaction.return_value = True

        # Test multiple concurrent trades
        for i in range(100):
            symbol = f"EURUSD{i}"
            result = trader_bot.execute_trade(
                symbol=symbol,
                action="buy",
                volume=0.1,
                entry_price=1.0 + (i * 0.0001),
                stop_loss=0.9,
                take_profit=1.1
            )
            assert result is not None
            assert symbol in trader_bot.positions

    def test_close_position(self, trader_bot, mock_mt5, mock_db):
        """Test position closing."""
        # Setup initial position
        trader_bot.positions["EURUSD"] = {
            'ticket': 12345,
            'type': 'buy',
            'price': 1.0,
            'volume': 0.1
        }

        # Mock close order result
        mock_result = {
            'ticket': 12346,
            'price': 1.05,
            'volume': 0.1,
            'comment': 'Close order'
        }
        mock_mt5.send_order.return_value = mock_result
        mock_db.update_transaction.return_value = True

        result = trader_bot.close_position("EURUSD")
        assert result is True
        assert "EURUSD" not in trader_bot.positions

    @pytest.mark.stress
    def test_stress_position_closing(self, trader_bot, mock_mt5, mock_db):
        """Stress test for position closing."""
        # Setup multiple positions
        for i in range(100):
            symbol = f"EURUSD{i}"
            trader_bot.positions[symbol] = {
                'ticket': 12345 + i,
                'type': 'buy',
                'price': 1.0,
                'volume': 0.1
            }

        # Mock close order results
        mock_result = {
            'ticket': 12346,
            'price': 1.05,
            'volume': 0.1,
            'comment': 'Close order'
        }
        mock_mt5.send_order.return_value = mock_result
        mock_db.update_transaction.return_value = True

        # Test closing all positions
        for i in range(100):
            symbol = f"EURUSD{i}"
            result = trader_bot.close_position(symbol)
            assert result is True
            assert symbol not in trader_bot.positions

    def test_error_handling(self, trader_bot, mock_mt5, mock_db):
        """Test error handling."""
        # Test connection error
        mock_mt5.connected = False
        assert trader_bot.fetch_market_data("EURUSD", 1, 1) is None

        # Test market data error
        mock_mt5.connected = True
        mock_mt5.get_market_data.return_value = None
        assert trader_bot.fetch_market_data("EURUSD", 1, 1) is None

        # Test trade execution error
        mock_mt5.send_order.return_value = None
        assert trader_bot.execute_trade("EURUSD", "buy", 0.1, 1.0) is None

        # Test position closing error
        trader_bot.positions["EURUSD"] = {'ticket': 12345}
        mock_mt5.send_order.return_value = None
        assert trader_bot.close_position("EURUSD") is False 