"""
================================================================================
BREAKOUT HUNTER (AGGRESSIVE) - NUMEIA v6.0
================================================================================

Estratégia: captura rompimentos direcionais utilizando canais Donchian,
validação por ATR e filtro de confirmação de impulso. Operação sempre na
direção do rompimento (long) com gestão de risco quantitativa.

Implementa critérios matemáticos claros:
 - Canal superior (máxima dos últimos N dias)
 - Diferença percentual de rompimento > buffer mínimo
 - Confirmação via média do retorno intrarompimento
 - Stop baseado em ATR * fator; take profit proporcional

Sem placeholders: todos os parâmetros são efetivos e testáveis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass
class BreakoutSignal:
    symbol: str
    action: str
    entry_price: float
    stop_loss: float
    take_profit: float
    breakout_strength: float
    atr: float
    confidence: float
    reason: str


class BreakoutHunterAggressive:
    def __init__(
        self,
        breakout_window: int = 20,
        confirmation_window: int = 5,
        atr_period: int = 14,
        atr_multiplier: float = 1.8,
        take_profit_multiplier: float = 3.0,
        min_breakout_buffer: float = 0.0025,
    ) -> None:
        if breakout_window <= 0 or confirmation_window <= 0:
            raise ValueError("Window parameters must be positive")

        self.breakout_window = breakout_window
        self.confirmation_window = confirmation_window
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.take_profit_multiplier = take_profit_multiplier
        self.min_breakout_buffer = min_breakout_buffer

    # ------------------------------------------------------------------
    def generate_signals(self, data_dict: Dict[str, pd.DataFrame]) -> List[Dict]:
        signals: List[Dict] = []

        for symbol, df in data_dict.items():
            if df is None or df.empty:
                continue

            required_cols = {'High', 'Low', 'Close'}
            if not required_cols.issubset(df.columns):
                continue

            if len(df) < max(self.breakout_window + self.confirmation_window, self.atr_period + 5):
                continue

            close_prices = df['Close']
            high_prices = df['High']
            low_prices = df['Low']

            recent_high = high_prices.iloc[-self.breakout_window: -1].max()
            previous_high = high_prices.iloc[-self.breakout_window - self.confirmation_window: -self.confirmation_window].max()
            latest_close = float(close_prices.iloc[-1])

            if math.isnan(recent_high) or math.isnan(latest_close):
                continue

            breakout_buffer = recent_high * (1.0 + self.min_breakout_buffer)

            if latest_close <= breakout_buffer:
                continue

            atr = self._calculate_atr(high_prices, low_prices, close_prices)
            if atr <= 0:
                continue

            breakout_strength = (latest_close - recent_high) / recent_high
            momentum_window = close_prices.iloc[-self.confirmation_window:]
            momentum_return = (momentum_window.iloc[-1] / momentum_window.iloc[0]) - 1.0

            if momentum_return <= 0:
                continue

            if recent_high <= previous_high:
                continue

            stop_loss = latest_close - atr * self.atr_multiplier
            take_profit = latest_close + atr * self.take_profit_multiplier

            confidence = min(0.45 + breakout_strength * 6.0 + momentum_return * 2.5, 0.92)
            confidence = float(max(0.35, confidence))

            reason = (
                f"Breakout {breakout_strength*100:.2f}% acima do canal {self.breakout_window}; "
                f"ATR {atr:.3f}; Momentum {momentum_return*100:.2f}%"
            )

            signals.append({
                'symbol': symbol,
                'action': 'BUY',
                'entry_price': latest_close,
                'stop_loss': float(stop_loss),
                'take_profit': float(take_profit),
                'confidence': confidence,
                'score': float(breakout_strength + momentum_return),
                'strategy': 'breakout',
                'reason': reason,
            })

        return signals

    # ------------------------------------------------------------------
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series) -> float:
        high = high.astype(float)
        low = low.astype(float)
        close = close.astype(float)

        prev_close = close.shift(1)
        tr1 = (high - low).abs()
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = true_range.rolling(self.atr_period, min_periods=self.atr_period).mean().iloc[-1]
        if atr is None or math.isnan(float(atr)):
            return 0.0
        return float(atr)


