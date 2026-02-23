import pytest
import MetaTrader5 as mt5
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..backend.api.mt5_connector import MT5Connector

class TestMT5Connector:
    @pytest.fixture
    def mt5_connector(self):
        """Create a test instance of MT5Connector."""
        return MT5Connector(login=12345, password="test", server="test")

    @pytest.fixture
    def mock_mt5(self):
        """Mock MetaTrader5 module."""
        with patch('MetaTrader5.mt5') as mock:
            yield mock

    def test_connection(self, mt5_connector, mock_mt5):
        """Test MT5 connection."""
        # Mock successful connection
        mock_mt5.initialize.return_value = True
        mock_mt5.login.return_value = True
        
        assert mt5_connector.connect() is True
        assert mt5_connector.connected is True

    def test_connection_failure(self, mt5_connector, mock_mt5):
        """Test MT5 connection failure."""
        # Mock connection failure
        mock_mt5.initialize.return_value = False
        
        assert mt5_connector.connect() is False
        assert mt5_connector.connected is False

    def test_get_market_data(self, mt5_connector, mock_mt5):
        """Test market data retrieval."""
        # Mock market data
        mock_data = pd.DataFrame({
            'time': [datetime.now()],
            'open': [1.0],
            'high': [1.1],
            'low': [0.9],
            'close': [1.05],
            'tick_volume': [1000]
        })
        mock_mt5.copy_rates_from_pos.return_value = mock_data
        
        data = mt5_connector.get_market_data("EURUSD", 1, 1)
        assert isinstance(data, pd.DataFrame)
        assert not data.empty

    @pytest.mark.stress
    def test_stress_market_data(self, mt5_connector, mock_mt5):
        """Stress test for market data retrieval."""
        # Mock market data
        mock_data = pd.DataFrame({
            'time': [datetime.now()] * 1000,
            'open': np.random.uniform(1.0, 1.1, 1000),
            'high': np.random.uniform(1.1, 1.2, 1000),
            'low': np.random.uniform(0.9, 1.0, 1000),
            'close': np.random.uniform(1.0, 1.1, 1000),
            'tick_volume': np.random.randint(1000, 2000, 1000)
        })
        mock_mt5.copy_rates_from_pos.return_value = mock_data
        
        # Test multiple concurrent requests
        for _ in range(100):
            data = mt5_connector.get_market_data("EURUSD", 1, 1000)
            assert isinstance(data, pd.DataFrame)
            assert len(data) == 1000

    def test_get_account_info(self, mt5_connector, mock_mt5):
        """Test account info retrieval."""
        # Mock account info
        mock_account = MagicMock()
        mock_account.balance = 10000.0
        mock_account.equity = 10500.0
        mock_account.margin = 1000.0
        mock_account.margin_free = 9000.0
        mock_account.margin_level = 1000.0
        mock_mt5.account_info.return_value = mock_account
        
        info = mt5_connector.get_account_info()
        assert info is not None
        assert 'balance' in info
        assert info['balance'] == 10000.0

    @pytest.mark.stress
    def test_stress_account_info(self, mt5_connector, mock_mt5):
        """Stress test for account info retrieval."""
        # Mock account info
        mock_account = MagicMock()
        mock_account.balance = 10000.0
        mock_mt5.account_info.return_value = mock_account
        
        # Test multiple concurrent requests
        for _ in range(1000):
            info = mt5_connector.get_account_info()
            assert info is not None
            assert info['balance'] == 10000.0

    def test_send_order(self, mt5_connector, mock_mt5):
        """Test order sending."""
        # Mock order result
        mock_result = MagicMock()
        mock_result.retcode = mt5.TRADE_RETCODE_DONE
        mock_result.order = 12345
        mock_mt5.order_send.return_value = mock_result
        
        result = mt5_connector.send_order(
            symbol="EURUSD",
            order_type="buy",
            volume=0.1,
            price=1.0,
            sl=0.9,
            tp=1.1
        )
        assert result is not None
        assert 'ticket' in result
        assert result['ticket'] == 12345

    @pytest.mark.stress
    def test_stress_orders(self, mt5_connector, mock_mt5):
        """Stress test for order sending."""
        # Mock order result
        mock_result = MagicMock()
        mock_result.retcode = mt5.TRADE_RETCODE_DONE
        mock_result.order = 12345
        mock_mt5.order_send.return_value = mock_result
        
        # Test multiple concurrent orders
        for i in range(100):
            result = mt5_connector.send_order(
                symbol="EURUSD",
                order_type="buy",
                volume=0.1,
                price=1.0 + (i * 0.0001),
                sl=0.9,
                tp=1.1
            )
            assert result is not None
            assert result['ticket'] == 12345

    def test_error_handling(self, mt5_connector, mock_mt5):
        """Test error handling."""
        # Mock various error scenarios
        mock_mt5.initialize.side_effect = Exception("Connection error")
        assert mt5_connector.connect() is False
        
        mock_mt5.copy_rates_from_pos.side_effect = Exception("Data error")
        assert mt5_connector.get_market_data("EURUSD", 1, 1) is None
        
        mock_mt5.order_send.side_effect = Exception("Order error")
        assert mt5_connector.send_order("EURUSD", "buy", 0.1, 1.0) is None 