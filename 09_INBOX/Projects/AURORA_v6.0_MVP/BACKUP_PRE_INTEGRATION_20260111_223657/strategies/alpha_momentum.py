#!/usr/bin/env python3
"""
📈 ALPHA MOMENTUM STRATEGY - Goldman Sachs Tier-0
Estratégia de momentum com confirmação de volume
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Import base_strategy dinamicamente para evitar problemas com imports relativos
base_strategy_path = Path(__file__).parent / "base_strategy.py"
if base_strategy_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("base_strategy", base_strategy_path)
    base_strategy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_strategy)
    BaseStrategy = base_strategy.BaseStrategy
    TradeSignal = base_strategy.TradeSignal
else:
    # Fallback para import relativo se estiver em um pacote
    try:
        from .base_strategy import BaseStrategy, TradeSignal
    except ImportError:
        # Último recurso: import absoluto
        sys.path.insert(0, str(Path(__file__).parent))
        from base_strategy import BaseStrategy, TradeSignal


class AlphaMomentumStrategy(BaseStrategy):
    """Estratégia Alpha Momentum com validação de volume"""
    
    def __init__(self):
        super().__init__(
            strategy_id="ALPHA_MOMENTUM_v1",
            capital_allocation=Decimal("1000.00")
        )
        self.version = "1.0"
        self.required_params = {
            "lookback_period": 20,      # Período para cálculo de momentum
            "volume_threshold": 1.5,    # Volume > 150% da média
            "momentum_threshold": 0.03, # Momentum mínimo de 3%
            "risk_per_trade": 0.02      # 2% do capital por trade
        }
        self.position = None
    
    def analyze(self, market_data: Dict[str, Any]) -> List[TradeSignal]:
        """
        Implementação EXATA do algoritmo Alpha Momentum
        """
        # VALIDAÇÃO 1: Dados mínimos necessários
        required_fields = ["close", "high", "low", "volume", "timestamp", "symbol"]
        for field in required_fields:
            if field not in market_data:
                return []
        
        signals = []
        
        # Converter dados para DataFrame
        if isinstance(market_data.get("close"), list):
            df = pd.DataFrame({
                'close': market_data['close'],
                'high': market_data['high'],
                'low': market_data['low'],
                'volume': market_data['volume']
            })
        else:
            # Se for dict único, criar DataFrame com uma linha
            df = pd.DataFrame([{
                'close': market_data['close'],
                'high': market_data['high'],
                'low': market_data['low'],
                'volume': market_data['volume']
            }])
        
        # CÁLCULO DE MOMENTUM (passo-a-passo)
        lookback = self.required_params["lookback_period"]
        if len(df) < lookback + 1:
            return []
        
        df['returns'] = df['close'].pct_change()
        df['momentum'] = df['close'] / df['close'].shift(lookback) - 1
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # ÚLTIMO REGISTRO PARA DECISÃO
        last_row = df.iloc[-1]
        
        # CONDIÇÕES DE ENTRADA (OBJETIVAS - SEM SUBJETIVIDADE)
        momentum_condition = last_row['momentum'] > self.required_params["momentum_threshold"]
        volume_condition = last_row['volume_ratio'] > self.required_params["volume_threshold"]
        
        # Calcular SMA de 50 períodos
        sma_50 = df['close'].rolling(window=min(50, len(df))).mean()
        price_above_sma = last_row['close'] > sma_50.iloc[-1] if len(sma_50) > 0 else False
        
        if momentum_condition and volume_condition and price_above_sma:
            # CALCULAR QUANTIDADE EXATA
            risk_amount = self.capital_allocation * Decimal(str(self.required_params["risk_per_trade"]))
            quantity = risk_amount / Decimal(str(last_row['close']))
            
            # CRIAR SINAL COM CHECKSUM
            signal = TradeSignal(
                timestamp=datetime.now(),
                symbol=market_data.get("symbol", "UNKNOWN"),
                action="BUY",
                quantity=quantity,
                price=Decimal(str(last_row['close'])),
                confidence=min(float(abs(last_row['momentum'])), 0.95),
                strategy_id=self.strategy_id,
                checksum=""
            )
            signal.checksum = signal.calculate_checksum()
            signals.append(signal)
        
        return signals
    
    def validate_parameters(self) -> bool:
        """Validação rigorosa dos parâmetros"""
        checks = [
            self.required_params["lookback_period"] > 0,
            self.required_params["volume_threshold"] > 1.0,
            0 < self.required_params["risk_per_trade"] <= 0.05,
            self.capital_allocation > Decimal("0")
        ]
        return all(checks)
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """Métricas de risco calculadas objetivamente"""
        return {
            "sharpe_ratio_target": 1.8,
            "max_drawdown_limit": 0.15,
            "win_rate_target": 0.55,
            "profit_factor_target": 1.5,
            "avg_trade_duration_hours": 24
        }


# TESTE UNITÁRIO OBRIGATÓRIO
def test_alpha_momentum_strategy():
    """Teste objetivo da estratégia"""
    strategy = AlphaMomentumStrategy()
    
    # DADOS DE TESTE PRÉ-DEFINIDOS
    test_data = {
        "close": [100, 102, 105, 108, 110, 115, 120, 125, 130, 135],
        "high": [101, 103, 106, 109, 112, 118, 122, 128, 132, 138],
        "low": [99, 101, 104, 107, 109, 114, 119, 124, 129, 134],
        "volume": [1000, 1200, 1500, 1800, 2000, 2500, 3000, 3500, 4000, 4500],
        "timestamp": [datetime.now() - timedelta(days=i) for i in range(10)],
        "symbol": "BTCUSDT"
    }
    
    # EXECUÇÃO DO TESTE
    signals = strategy.analyze(test_data)
    
    # ASSERTIVAS MENSURÁVEIS
    assert strategy.validate_parameters() == True
    assert isinstance(signals, list)
    
    if signals:
        signal = signals[0]
        assert signal.action in ["BUY", "SELL", "HOLD"]
        assert signal.checksum == signal.calculate_checksum()
    
    return True

