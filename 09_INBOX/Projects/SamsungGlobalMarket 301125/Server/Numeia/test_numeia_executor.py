import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numeia_executor_v2 import Task, Metrics, Config, CapitalManagement, SignalGenerator

class TestNumeiaExecutor(unittest.TestCase):

    def test_task_creation(self):
        task_data = {"id": 1, "symbol": "EURUSD", "action": "buy", "volume": 0.01}
        task = Task(**task_data)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.symbol, "EURUSD")

    def test_metrics_recording(self):
        metrics = Metrics()
        metrics.record_result(True, filled=True)
        metrics.record_result(False)
        self.assertEqual(metrics.failure_rate(), 0.5)
        self.assertEqual(metrics.total_orders, 2)
        self.assertEqual(metrics.filled_orders, 1)

    @patch('numeia_executor_v2.mt5')
    def test_capital_management(self, mock_mt5):
        mock_mt5.account_info.return_value = Mock(balance=10000)
        mock_mt5.symbol_info.return_value = Mock(volume_min=0.01, volume_max=10.0, volume_step=0.01, trade_tick_value=1.0, trade_tick_size=0.00001)
        
        config = Config(**{
            "EMERGENCY_MODE_ENABLED": True, "MAX_PARALLEL_WORKERS": 10, "EXECUTION_CYCLE_SECONDS": 15,
            "MAX_LATENCY_MS_P95": 300, "MAX_FAILURE_RATE": 0.03, "ROLLBACK_WINDOW_SECONDS": 600,
            "NOTIFICATION_WEBHOOK_URL": None, "TRADING_SYMBOLS": ["EURUSD"],
            "RISK_PARAMETERS": {"max_daily_drawdown": 0.02, "max_position_size_pct": 0.1, "kelly_fraction": 0.25, "correlation_threshold": 0.7, "max_sector_exposure": 0.3},
            "MONITORING": {"prometheus_port": 8000, "health_check_interval": 60, "order_timeout_seconds": 10}
        })
        cm = CapitalManagement(config)
        size = cm.calculate_position_size("EURUSD", 1.1, 1.09)
        self.assertGreater(size, 0)

if __name__ == '__main__':
    unittest.main()

