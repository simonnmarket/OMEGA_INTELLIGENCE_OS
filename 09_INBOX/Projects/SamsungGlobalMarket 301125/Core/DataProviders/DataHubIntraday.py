"""
================================================================================
DATA HUB INTRADAY - NUMEIA v6.0
================================================================================

Função: Camada unificada de aquisição de dados intradiários/multi-timeframe para o
        servidor tático. Prioriza MetaTrader5; aplica fallback automático para
        yfinance e mantém cache local dos últimos resultados válidos.

Protocolo: ASC-AQ - Falsificação ativa de feeds e monitoramento contínuo.
Versão: 1.0.0
Autor: Cursor_Omega
Data: 07-11-2025 (CET)
Checksum: (gerado na auditoria)
"""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

try:  # MetaTrader5 pode não estar instalado no ambiente local
    import MetaTrader5 as mt5  # type: ignore
except ImportError:  # pragma: no cover - fallback será acionado
    mt5 = None

try:
    import yfinance as yf  # type: ignore
except ImportError:  # pragma: no cover
    yf = None


# ==============================================================================
# CONFIGURAÇÃO DE LOGGING
# ==============================================================================
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# ==============================================================================
# ESTRUTURAS DE DADOS
# ==============================================================================
@dataclass
class MarketDataBundle:
    """Pacote estruturado de dados multi-timeframe para um símbolo."""

    symbol: str
    timeframe_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    fetched_from: str = "unknown"
    last_update: datetime = field(default_factory=datetime.utcnow)

    def is_valid(self) -> bool:
        return bool(self.timeframe_data) and all(
            isinstance(df, pd.DataFrame) and not df.empty
            for df in self.timeframe_data.values()
        )


# ==============================================================================
# CLASSE PRINCIPAL
# ==============================================================================
class DataHubIntraday:
    """Gerencia aquisição e padronização de dados intradiários."""

    def __init__(
        self,
        symbols: List[str],
        cache_dir: Optional[Path] = None,
        mt5_timeframes: Optional[List[str]] = None,
        bars_per_timeframe: int = 250,
    ) -> None:
        self.symbols = symbols
        self.bars_per_timeframe = max(50, bars_per_timeframe)
        self.cache_dir = cache_dir or (Path(__file__).resolve().parent / "Cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Timeframes default (strings para evitar dependência direta de mt5)
        self.mt5_timeframes = mt5_timeframes or ["M15", "H1", "D1"]
        self._last_successful_fetch: Optional[datetime] = None
        self._cache: Dict[str, MarketDataBundle] = {}

        logger.info("✅ DataHubIntraday inicializado")
        logger.info("   Símbolos monitorados: %s", ", ".join(self.symbols))
        logger.info("   Timeframes: %s", ", ".join(self.mt5_timeframes))

    @staticmethod
    def _normalize_scalar(value):
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, np.generic):
            return value.item()
        return value

    # ---------------------------------------------------------------------
    # APIs PÚBLICAS
    # ---------------------------------------------------------------------
    def fetch_market_data(self) -> Dict[str, MarketDataBundle]:
        """Obtém dados atualizados para todo o universo de símbolos."""

        logger.info("📡 Iniciando coleta intradiária (%d símbolos)", len(self.symbols))

        bundles: Dict[str, MarketDataBundle] = {}
        for symbol in self.symbols:
            bundle = self._fetch_symbol(symbol)
            if bundle and bundle.is_valid():
                bundles[symbol] = bundle
                self._cache[symbol] = bundle
                self._persist_cache(bundle)
            else:
                logger.warning("⚠️ Falha ao obter dados de %s - tentando cache", symbol)
                cache_bundle = self._load_from_cache(symbol)
                if cache_bundle and cache_bundle.is_valid():
                    bundles[symbol] = cache_bundle
                    logger.info("   ↪️ Cache aplicado para %s", symbol)

        if not bundles:
            logger.error("❌ Nenhum dado válido coletado - retornando cache completo")
            bundles = {
                sym: bundle
                for sym, bundle in self._cache.items()
                if bundle.is_valid()
            }

        self._last_successful_fetch = datetime.utcnow() if bundles else self._last_successful_fetch
        return bundles

    def get_last_fetch_timestamp(self) -> Optional[datetime]:
        return self._last_successful_fetch

    # ---------------------------------------------------------------------
    # MÉTODOS INTERNOS - COLETA
    # ---------------------------------------------------------------------
    def _fetch_symbol(self, symbol: str) -> Optional[MarketDataBundle]:
        if mt5 is not None:
            bundle = self._fetch_via_mt5(symbol)
            if bundle and bundle.is_valid():
                return bundle
            logger.warning("   ⚠️ MT5 indisponível p/ %s - fallback yfinance", symbol)

        if yf is not None:
            bundle = self._fetch_via_yfinance(symbol)
            if bundle and bundle.is_valid():
                return bundle

        logger.error("   ❌ Falha em todas as fontes para %s", symbol)
        return None

    def _fetch_via_mt5(self, symbol: str) -> Optional[MarketDataBundle]:
        try:
            if not mt5.initialize():
                logger.warning("   ⚠️ MetaTrader5.initialize() falhou: %s", mt5.last_error())
                return None

            if not mt5.symbol_select(symbol, True):
                logger.warning("   ⚠️ Símbolo %s não disponível no MT5", symbol)
                mt5.shutdown()
                return None

            timeframe_map = {
                "M15": getattr(mt5, "TIMEFRAME_M15", None),
                "H1": getattr(mt5, "TIMEFRAME_H1", None),
                "H4": getattr(mt5, "TIMEFRAME_H4", None),
                "D1": getattr(mt5, "TIMEFRAME_D1", None),
            }

            timeframe_data: Dict[str, pd.DataFrame] = {}
            for tf in self.mt5_timeframes:
                mt5_tf = timeframe_map.get(tf)
                if mt5_tf is None:
                    continue

                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, self.bars_per_timeframe)
                if rates is None or len(rates) == 0:
                    continue

                df = pd.DataFrame(rates)
                df["time"] = pd.to_datetime(df["time"], unit="s")
                df = df.rename(columns={
                    "time": "Date",
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "tick_volume": "Volume",
                })
                df.set_index("Date", inplace=True)

                timeframe_data[tf] = df

            mt5.shutdown()

            if not timeframe_data:
                return None

            return MarketDataBundle(
                symbol=symbol,
                timeframe_data=timeframe_data,
                fetched_from="mt5",
            )
        except Exception as exc:  # pragma: no cover - dependência externa
            logger.error("   ❌ Erro MT5 (%s): %s", symbol, exc)
            try:
                mt5.shutdown()
            except Exception:
                pass
            return None

    def _fetch_via_yfinance(self, symbol: str) -> Optional[MarketDataBundle]:
        if yf is None:
            return None

        try:
            period_map = {
                "M15": ("7d", "15m"),
                "H1": ("30d", "1h"),
                "H4": ("60d", "4h"),
                "D1": ("6mo", "1d"),
            }

            timeframe_data: Dict[str, pd.DataFrame] = {}
            for tf in self.mt5_timeframes:
                period, interval = period_map.get(tf, ("6mo", "1d"))
                data = yf.download(symbol, period=period, interval=interval, progress=False)
                if data.empty:
                    continue

                data.rename(columns=str.capitalize, inplace=True)
                timeframe_data[tf] = data

            if not timeframe_data:
                return None

            return MarketDataBundle(
                symbol=symbol,
                timeframe_data=timeframe_data,
                fetched_from="yfinance",
            )
        except Exception as exc:  # pragma: no cover
            logger.error("   ❌ Erro yfinance (%s): %s", symbol, exc)
            return None

    # ---------------------------------------------------------------------
    # CACHE
    # ---------------------------------------------------------------------
    def _persist_cache(self, bundle: MarketDataBundle) -> None:
        try:
            payload = {
                "symbol": bundle.symbol,
                "fetched_from": bundle.fetched_from,
                "last_update": bundle.last_update.isoformat(),
                "timeframes": {}
            }

            for tf, df in bundle.timeframe_data.items():
                if df is None or df.empty:
                    continue
                df_to_store = df.reset_index()
                df_to_store.columns = [str(col) for col in df_to_store.columns]
                for column in df_to_store.columns:
                    if pd.api.types.is_datetime64_any_dtype(df_to_store[column]):
                        df_to_store[column] = df_to_store[column].apply(
                            lambda x: x.isoformat() if pd.notna(x) else None
                        )
                    else:
                        df_to_store[column] = df_to_store[column].apply(
                            self._normalize_scalar
                        )
                payload["timeframes"][tf] = df_to_store.tail(200).to_dict(orient="records")

            cache_file = self.cache_dir / f"{bundle.symbol}_cache.json"
            cache_file.write_text(json.dumps(payload), encoding="utf-8")
        except Exception as exc:
            logger.warning("⚠️ Falha ao persistir cache de %s: %s", bundle.symbol, exc)

    def _load_from_cache(self, symbol: str) -> Optional[MarketDataBundle]:
        cache_file = self.cache_dir / f"{symbol}_cache.json"
        if not cache_file.exists():
            return None

        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            timeframe_data: Dict[str, pd.DataFrame] = {}
            for tf, rows in payload.get("timeframes", {}).items():
                df = pd.DataFrame(rows)
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                    df.set_index("Date", inplace=True)
                timeframe_data[tf] = df

            return MarketDataBundle(
                symbol=symbol,
                timeframe_data=timeframe_data,
                fetched_from=f"cache/{payload.get('fetched_from', 'unknown')}",
                last_update=datetime.fromisoformat(payload.get("last_update"))
                if payload.get("last_update")
                else datetime.utcnow(),
            )
        except Exception as exc:
            logger.warning("⚠️ Falha ao carregar cache de %s: %s", symbol, exc)
            return None


# ==============================================================================
# FUNÇÃO DE TESTE STANDALONE
# ==============================================================================
def _self_test() -> None:  # pragma: no cover - ferramenta operacional
    symbols = ["XAUUSD", "US500"]
    hub = DataHubIntraday(symbols)
    data = hub.fetch_market_data()
    for sym, bundle in data.items():
        logger.info("[TEST] %s -> %s", sym, list(bundle.timeframe_data.keys()))


if __name__ == "__main__":  # pragma: no cover
    _self_test()


