"""
================================================================================
FX MEAN REVERSION (AGGRESSIVE) - NUMEIA v6.0
================================================================================

Estratégia: captura reversões estatísticas em pares principais de FX utilizando
z-score de desvios em relação à média móvel, com gestão baseada em ATR.

Critérios matemáticos:
 - Média exponencial (EMA) de 20 períodos
 - Desvio padrão exponencial correspondente
 - Z-score absoluto acima do limiar gera sinal
 - Direção do trade segue o retorno à média (z>0 => vender, z<0 => comprar)
 - Stop e alvo proporcionais ao ATR

Sem placeholders: todos os cálculos são efetivos e replicáveis.
"""

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
import pandas as pd


class FXMeanReversionAggressive:
    def __init__(
        self,
        symbols: List[str],
        ema_period: int = 20,
        zscore_threshold: float = 1.0,
        atr_period: int = 14,
        atr_stop_multiplier: float = 1.6,
        atr_target_multiplier: float = 2.4,
    ) -> None:
        if ema_period <= 1:
            raise ValueError("EMA period must be greater than 1")

        self.symbols = symbols
        self.ema_period = ema_period
        self.zscore_threshold = zscore_threshold
        self.atr_period = atr_period
        self.atr_stop_multiplier = atr_stop_multiplier
        self.atr_target_multiplier = atr_target_multiplier

    # ------------------------------------------------------------------
    def generate_signals(self, data_dict: Dict[str, pd.DataFrame]) -> List[Dict]:
        signals: List[Dict] = []

        for symbol in self.symbols:
            df = data_dict.get(symbol)
            if df is None or df.empty:
                continue

            if not {'High', 'Low', 'Close'}.issubset(df.columns):
                continue

            if len(df) < max(self.ema_period + 5, self.atr_period + 5):
                continue

            close = df['Close'].astype(float)
            ema = close.ewm(span=self.ema_period, adjust=False).mean()
            ema_std = close.ewm(span=self.ema_period, adjust=False).std()

            latest_close = float(close.iloc[-1])
            latest_ema = float(ema.iloc[-1])
            latest_std = float(ema_std.iloc[-1])

            if latest_std <= 0 or math.isnan(latest_std):
                continue

            zscore = (latest_close - latest_ema) / latest_std
            if abs(zscore) < self.zscore_threshold:
                continue

            atr = self._calculate_atr(df['High'], df['Low'], df['Close'])
            if atr <= 0:
                continue

            if zscore > 0:
                action = 'SELL'
                stop_loss = latest_close + atr * self.atr_stop_multiplier
                take_profit = latest_close - atr * self.atr_target_multiplier
                direction = -1
            else:
                action = 'BUY'
                stop_loss = latest_close - atr * self.atr_stop_multiplier
                take_profit = latest_close + atr * self.atr_target_multiplier
                direction = 1

            revert_distance = abs(latest_close - latest_ema)
            normalized_distance = revert_distance / latest_close
            confidence = min(0.42 + (abs(zscore) - self.zscore_threshold) * 0.18 + normalized_distance * 6.0, 0.88)
            confidence = float(max(0.34, confidence))

            reason = (
                f"Z-score {zscore:.2f} (threshold {self.zscore_threshold}); "
                f"ATR {atr:.5f}; EMA gap {normalized_distance*100:.2f}%"
            )

            signals.append({
                'symbol': symbol,
                'action': action,
                'entry_price': latest_close,
                'stop_loss': float(stop_loss),
                'take_profit': float(take_profit),
                'confidence': confidence,
                'score': float(abs(zscore)),
                'strategy': 'mean_reversion',
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


