#!/usr/bin/env python3
"""
🧪 TESTES UNITÁRIOS - Estratégias NCNT Tier-0
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Adicionar caminho do projeto
project_root = Path(__file__).parent.parent
strategies_path = project_root / "01-Departamentos" / "Execution-Trading" / "strategies"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(strategies_path))

# Importar estratégias dinamicamente
import importlib.util

spec_alpha = importlib.util.spec_from_file_location("alpha_momentum", strategies_path / "alpha_momentum.py")
alpha_momentum = importlib.util.module_from_spec(spec_alpha)
spec_alpha.loader.exec_module(alpha_momentum)

spec_mean = importlib.util.spec_from_file_location("mean_reversion", strategies_path / "mean_reversion.py")
mean_reversion = importlib.util.module_from_spec(spec_mean)
spec_mean.loader.exec_module(mean_reversion)

spec_breakout = importlib.util.spec_from_file_location("breakout_detection", strategies_path / "breakout_detection.py")
breakout_detection = importlib.util.module_from_spec(spec_breakout)
spec_breakout.loader.exec_module(breakout_detection)

spec_base = importlib.util.spec_from_file_location("base_strategy", strategies_path / "base_strategy.py")
base_strategy = importlib.util.module_from_spec(spec_base)
spec_base.loader.exec_module(base_strategy)

AlphaMomentumStrategy = alpha_momentum.AlphaMomentumStrategy
MeanReversionStrategy = mean_reversion.MeanReversionStrategy
BreakoutDetectionStrategy = breakout_detection.BreakoutDetectionStrategy
BaseStrategy = base_strategy.BaseStrategy
TradeSignal = base_strategy.TradeSignal


class TestTradeSignal:
    """Testes para TradeSignal"""
    
    def test_trade_signal_creation(self):
        """Testar criação de TradeSignal"""
        signal = TradeSignal(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            action="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.0"),
            confidence=0.85,
            strategy_id="TEST_STRATEGY",
            checksum=""
        )
        signal.checksum = signal.calculate_checksum()
        
        assert signal.symbol == "BTCUSDT"
        assert signal.action == "BUY"
        assert len(signal.checksum) == 32
    
    def test_checksum_calculation(self):
        """Testar cálculo de checksum"""
        signal1 = TradeSignal(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            action="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.0"),
            confidence=0.85,
            strategy_id="TEST",
            checksum=""
        )
        checksum1 = signal1.calculate_checksum()
        
        signal2 = TradeSignal(
            timestamp=signal1.timestamp,
            symbol="BTCUSDT",
            action="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000.0"),
            confidence=0.85,
            strategy_id="TEST",
            checksum=""
        )
        checksum2 = signal2.calculate_checksum()
        
        assert checksum1 == checksum2


class TestAlphaMomentumStrategy:
    """Testes para AlphaMomentumStrategy"""
    
    def test_strategy_initialization(self):
        """Testar inicialização da estratégia"""
        strategy = AlphaMomentumStrategy()
        assert strategy.strategy_id == "ALPHA_MOMENTUM_v1"
        assert strategy.capital_allocation > Decimal("0")
    
    def test_validate_parameters(self):
        """Testar validação de parâmetros"""
        strategy = AlphaMomentumStrategy()
        assert strategy.validate_parameters() == True
    
    def test_analyze_with_valid_data(self):
        """Testar análise com dados válidos"""
        strategy = AlphaMomentumStrategy()
        
        test_data = {
            "close": [100, 102, 105, 108, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190],
            "high": [101, 103, 106, 109, 112, 118, 122, 128, 132, 138, 142, 148, 152, 158, 162, 168, 172, 178, 182, 188, 192],
            "low": [99, 101, 104, 107, 109, 114, 119, 124, 129, 134, 139, 144, 149, 154, 159, 164, 169, 174, 179, 184, 189],
            "volume": [1000, 1200, 1500, 1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000],
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(21)],
            "symbol": "BTCUSDT"
        }
        
        signals = strategy.analyze(test_data)
        assert isinstance(signals, list)
        # Pode retornar 0 ou mais sinais dependendo das condições
    
    def test_analyze_with_invalid_data(self):
        """Testar análise com dados inválidos"""
        strategy = AlphaMomentumStrategy()
        
        test_data = {
            "close": [100, 102],  # Dados insuficientes
            "symbol": "BTCUSDT"
        }
        
        signals = strategy.analyze(test_data)
        assert signals == []
    
    def test_risk_metrics(self):
        """Testar cálculo de métricas de risco"""
        strategy = AlphaMomentumStrategy()
        metrics = strategy.calculate_risk_metrics()
        
        assert "sharpe_ratio_target" in metrics
        assert metrics["sharpe_ratio_target"] > 1.5


class TestMeanReversionStrategy:
    """Testes para MeanReversionStrategy"""
    
    def test_strategy_initialization(self):
        """Testar inicialização da estratégia"""
        strategy = MeanReversionStrategy()
        assert strategy.strategy_id == "MEAN_REVERSION_v1"
    
    def test_validate_parameters(self):
        """Testar validação de parâmetros"""
        strategy = MeanReversionStrategy()
        assert strategy.validate_parameters() == True
    
    def test_analyze_with_valid_data(self):
        """Testar análise com dados válidos"""
        strategy = MeanReversionStrategy()
        
        test_data = {
            "close": [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60],
            "high": [101, 99, 97, 95, 93, 91, 89, 87, 85, 83, 81, 79, 77, 75, 73, 71, 69, 67, 65, 63, 61],
            "low": [99, 97, 95, 93, 91, 89, 87, 85, 83, 81, 79, 77, 75, 73, 71, 69, 67, 65, 63, 61, 59],
            "volume": [1000] * 21,
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(21)],
            "symbol": "BTCUSDT"
        }
        
        signals = strategy.analyze(test_data)
        assert isinstance(signals, list)


class TestBreakoutDetectionStrategy:
    """Testes para BreakoutDetectionStrategy"""
    
    def test_strategy_initialization(self):
        """Testar inicialização da estratégia"""
        strategy = BreakoutDetectionStrategy()
        assert strategy.strategy_id == "BREAKOUT_DETECTION_v1"
    
    def test_validate_parameters(self):
        """Testar validação de parâmetros"""
        strategy = BreakoutDetectionStrategy()
        assert strategy.validate_parameters() == True
    
    def test_analyze_with_valid_data(self):
        """Testar análise com dados válidos"""
        strategy = BreakoutDetectionStrategy()
        
        # Dados simulando breakout
        base_price = 100
        test_data = {
            "close": [base_price + i for i in range(21)],
            "high": [base_price + i + 1 for i in range(21)],
            "low": [base_price + i - 1 for i in range(21)],
            "volume": [2000] * 21,  # Volume alto para confirmar breakout
            "timestamp": [datetime.now() - timedelta(days=i) for i in range(21)],
            "symbol": "BTCUSDT"
        }
        
        signals = strategy.analyze(test_data)
        assert isinstance(signals, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

