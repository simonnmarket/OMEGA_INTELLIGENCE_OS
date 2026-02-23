"""
================================================================================
REGIME DETECTOR - NUMEIA v6.0
================================================================================

Objetivo: Classificar o regime de mercado em tempo real a partir de dados
          multi-timeframe e fornecer ajustes dinâmicos de confiança/risco
          para o servidor tático.

Paradigma: ASC-AQ (Falsificação rápida + adaptação contínua)
Versão: 1.0.0
Autor: Cursor_Omega
Data: 07-11-2025 (CET)
Checksum: (gerado na auditoria)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd

try:  # Dependência opcional para clustering
    from sklearn.cluster import KMeans  # type: ignore
except ImportError:  # pragma: no cover
    KMeans = None


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


@dataclass
class RegimeAssessment:
    label: str
    confidence_adjuster: float
    risk_multiplier: float
    features_snapshot: Dict[str, float]


class RegimeDetector:
    """Classificador de regimes baseado em features estatísticas simples."""

    def __init__(self, window_short: int = 21, window_long: int = 63) -> None:
        self.window_short = window_short
        self.window_long = window_long
        self._kmeans_model: Optional[KMeans] = None

    def calibrate(self, history: pd.Series) -> None:
        if KMeans is None or history.empty:
            logger.warning("⚠️ KMeans indisponível - usando heurísticas determinísticas")
            return

        features = self._compute_feature_matrix(history)
        if len(features) < 3:
            return

        self._kmeans_model = KMeans(n_clusters=3, random_state=42, n_init="auto")
        self._kmeans_model.fit(features)
        logger.info("✅ RegimeDetector calibrado com KMeans (3 clusters)")

    def assess(self, price_series: pd.Series) -> RegimeAssessment:
        if price_series is None or price_series.empty:
            raise ValueError("Série de preços inválida para detecção de regime")

        features = self._compute_features(price_series)
        label = self._determine_regime_label(features)
        adjustments = self._confidence_risk_adjustments(label)

        return RegimeAssessment(
            label=label,
            confidence_adjuster=adjustments["confidence_adjuster"],
            risk_multiplier=adjustments["risk_multiplier"],
            features_snapshot=features,
        )

    def _compute_features(self, prices: pd.Series) -> Dict[str, float]:
        returns = prices.pct_change().dropna()

        vol_short = returns.tail(self.window_short).std() * np.sqrt(252)
        vol_long = returns.tail(self.window_long).std() * np.sqrt(252)
        slope_short = self._annualized_slope(prices.tail(self.window_short))
        slope_long = self._annualized_slope(prices.tail(self.window_long))
        drawdown = self._max_drawdown(prices)

        features = {
            "vol_short": float(vol_short if not np.isnan(vol_short) else 0.0),
            "vol_long": float(vol_long if not np.isnan(vol_long) else 0.0),
            "slope_short": float(slope_short),
            "slope_long": float(slope_long),
            "vol_ratio": float(vol_short / vol_long) if vol_long else 0.0,
            "drawdown": float(drawdown),
        }

        return features

    def _compute_feature_matrix(self, prices: pd.Series) -> np.ndarray:
        window = max(self.window_long * 3, 180)
        if len(prices) < window:
            return np.empty((0, 5))

        feature_rows = []
        for idx in range(window, len(prices)):
            slice_series = prices.iloc[idx - window: idx]
            feat = self._compute_features(slice_series)
            feature_rows.append([
                feat["vol_ratio"],
                feat["slope_short"],
                feat["slope_long"],
                feat["drawdown"],
                feat["vol_short"],
            ])

        return np.array(feature_rows)

    def _determine_regime_label(self, features: Dict[str, float]) -> str:
        if self._kmeans_model is not None:
            vector = np.array([
                features["vol_ratio"],
                features["slope_short"],
                features["slope_long"],
                features["drawdown"],
                features["vol_short"],
            ]).reshape(1, -1)
            cluster = int(self._kmeans_model.predict(vector)[0])
            return ["TREND_UP_VOL_LOW", "TREND_DOWN_VOL_HIGH", "SIDEWAYS_VOL_MED"][cluster]

        slope = features["slope_short"]
        vol_ratio = features["vol_ratio"]
        drawdown = features["drawdown"]

        if slope > 0.15 and vol_ratio <= 1.2:
            return "TREND_UP_VOL_LOW"
        if slope < -0.10 and (vol_ratio >= 1.1 or drawdown < -0.12):
            return "TREND_DOWN_VOL_HIGH"
        if vol_ratio >= 1.5:
            return "VOLATILITY_BREAKOUT"
        return "SIDEWAYS_VOL_MED"

    def _confidence_risk_adjustments(self, regime: str) -> Dict[str, float]:
        mapping = {
            "TREND_UP_VOL_LOW": {"confidence_adjuster": 1.25, "risk_multiplier": 1.1},
            "TREND_DOWN_VOL_HIGH": {"confidence_adjuster": 0.75, "risk_multiplier": 0.7},
            "VOLATILITY_BREAKOUT": {"confidence_adjuster": 0.9, "risk_multiplier": 0.8},
            "SIDEWAYS_VOL_MED": {"confidence_adjuster": 1.0, "risk_multiplier": 0.95},
        }

        return mapping.get(regime, {"confidence_adjuster": 1.0, "risk_multiplier": 1.0})

    @staticmethod
    def _annualized_slope(prices: pd.Series) -> float:
        if len(prices) < 2:
            return 0.0

        x = np.arange(len(prices))
        y = np.log(prices.values)
        coef = np.polyfit(x, y, 1)
        slope_daily = coef[0]
        return float(slope_daily * 252)

    @staticmethod
    def _max_drawdown(prices: pd.Series) -> float:
        cumulative = prices / prices.cummax() - 1.0
        return float(cumulative.min())


def _self_test() -> None:  # pragma: no cover
    prices = pd.Series(np.cumprod(1 + np.random.normal(0.0005, 0.01, 500)))
    detector = RegimeDetector()
    assessment = detector.assess(prices)
    print(assessment)


if __name__ == "__main__":  # pragma: no cover
    _self_test()


