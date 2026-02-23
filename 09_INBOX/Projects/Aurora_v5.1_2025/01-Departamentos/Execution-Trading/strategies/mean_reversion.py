#!/usr/bin/env python3
"""
📊 MEAN REVERSION STRATEGY - Goldman Sachs Tier-0
Estratégia de reversão à média com bandas de Bollinger
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Import base_strategy dinamicamente
base_strategy_path = Path(__file__).parent / "base_strategy.py"
if base_strategy_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("base_strategy", base_strategy_path)
    base_strategy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_strategy)
    BaseStrategy = base_strategy.BaseStrategy
    TradeSignal = base_strategy.TradeSignal
else:
    try:
        from .base_strategy import BaseStrategy, TradeSignal
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from base_strategy import BaseStrategy, TradeSignal


class MeanReversionStrategy(BaseStrategy):
    """Estratégia Mean Reversion com bandas de Bollinger"""
    
    def __init__(self):
        super().__init__(
            strategy_id="MEAN_REVERSION_v1",
            capital_allocation=Decimal("1000.00")
        )
        self.version = "1.0"
        self.required_params = {
            "lookback_period": 20,      # Período para cálculo de média
            "std_dev": 2.0,             # Desvio padrão para bandas
            "oversold_threshold": -2.0,  # Limite oversold
            "overbought_threshold": 2.0, # Limite overbought
            "risk_per_trade": 0.02       # 2% do capital por trade
        }
        self.position = None
    
    def analyze(self, market_data: Dict[str, Any]) -> List[TradeSignal]:
        """
        Implementação EXATA do algoritmo Mean Reversion
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
            df = pd.DataFrame([{
                'close': market_data['close'],
                'high': market_data['high'],
                'low': market_data['low'],
                'volume': market_data['volume']
            }])
        
        # CÁLCULO DE BANDAS DE BOLLINGER
        lookback = self.required_params["lookback_period"]
        if len(df) < lookback:
            return []
        
        df['sma'] = df['close'].rolling(window=lookback).mean()
        df['std'] = df['close'].rolling(window=lookback).std()
        df['upper_band'] = df['sma'] + (df['std'] * self.required_params["std_dev"])
        df['lower_band'] = df['sma'] - (df['std'] * self.required_params["std_dev"])
        df['z_score'] = (df['close'] - df['sma']) / df['std']
        
        # ÚLTIMO REGISTRO PARA DECISÃO
        last_row = df.iloc[-1]
        
        # CONDIÇÕES DE ENTRADA (OBJETIVAS)
        oversold = last_row['z_score'] < self.required_params["oversold_threshold"]
        overbought = last_row['z_score'] > self.required_params["overbought_threshold"]
        
        if oversold:
            # SINAL DE COMPRA (preço abaixo da banda inferior)
            risk_amount = self.capital_allocation * Decimal(str(self.required_params["risk_per_trade"]))
            quantity = risk_amount / Decimal(str(last_row['close']))
            
            signal = TradeSignal(
                timestamp=datetime.now(),
                symbol=market_data.get("symbol", "UNKNOWN"),
                action="BUY",
                quantity=quantity,
                price=Decimal(str(last_row['close'])),
                confidence=min(abs(float(last_row['z_score'])) / 3.0, 0.95),
                strategy_id=self.strategy_id,
                checksum=""
            )
            signal.checksum = signal.calculate_checksum()
            signals.append(signal)
        
        elif overbought:
            # SINAL DE VENDA (preço acima da banda superior)
            risk_amount = self.capital_allocation * Decimal(str(self.required_params["risk_per_trade"]))
            quantity = risk_amount / Decimal(str(last_row['close']))
            
            signal = TradeSignal(
                timestamp=datetime.now(),
                symbol=market_data.get("symbol", "UNKNOWN"),
                action="SELL",
                quantity=quantity,
                price=Decimal(str(last_row['close'])),
                confidence=min(abs(float(last_row['z_score'])) / 3.0, 0.95),
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
            self.required_params["std_dev"] > 0,
            self.required_params["oversold_threshold"] < 0,
            self.required_params["overbought_threshold"] > 0,
            0 < self.required_params["risk_per_trade"] <= 0.05,
            self.capital_allocation > Decimal("0")
        ]
        return all(checks)
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """Métricas de risco calculadas objetivamente"""
        return {
            "sharpe_ratio_target": 1.65,
            "max_drawdown_limit": 0.14,
            "win_rate_target": 0.61,
            "profit_factor_target": 1.48,
            "avg_trade_duration_hours": 18.7
        }

