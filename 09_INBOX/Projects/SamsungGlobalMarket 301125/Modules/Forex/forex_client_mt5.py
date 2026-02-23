# MEMORY_ID: TASK_FOREX_MT5_CLIENT
# TIMESTAMP: 2025-11-11T23:45:00+01:00
# AUTHOR: Cursor_Omega

"""
Cliente Forex integrado ao MetaTrader 5 com exportação de métricas Prometheus.

Utiliza o terminal MT5 conectado ao broker Hantec para obter cotações bid/ask,
publicando métricas `forex_mid_price` e `forex_spread` em um HTTP server compatível
com Prometheus.
"""

from __future__ import annotations

import logging
import time
from typing import Iterable

import MetaTrader5 as mt5  # type: ignore
from prometheus_client import CollectorRegistry, Gauge, start_http_server

logger = logging.getLogger(__name__)


class ForexClientMT5:
    """
    Coletor de preços Forex via terminal MetaTrader 5.

    Parameters
    ----------
    symbols : Iterable[str]
        Lista de símbolos do Market Watch a monitorar.
    metrics_port : int, optional
        Porta HTTP para expor métricas Prometheus, default 8003.
    interval_seconds : int, optional
        Intervalo de coleta (segundos), default 15.
    """

    def __init__(
        self,
        symbols: Iterable[str],
        *,
        metrics_port: int = 8003,
        interval_seconds: int = 15,
    ) -> None:
        if not mt5.initialize():
            error_msg = f"Falha ao inicializar MT5: {mt5.last_error()}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        self.symbols = list(symbols)
        self.metrics_port = metrics_port
        self.interval_seconds = interval_seconds
        self.registry = CollectorRegistry()
        self.price_gauge = Gauge(
            "forex_mid_price",
            "Preço médio (bid/ask) por símbolo Forex",
            ["symbol"],
            registry=self.registry,
        )
        self.spread_gauge = Gauge(
            "forex_spread",
            "Spread (ask-bid) por símbolo Forex",
            ["symbol"],
            registry=self.registry,
        )

        logger.info(
            "ForexClientMT5 inicializado. Símbolos: %s | Porta métricas: %s | Intervalo: %ss",
            ", ".join(self.symbols),
            self.metrics_port,
            self.interval_seconds,
        )

    def fetch_and_update(self) -> None:
        """Atualiza métricas para todos os símbolos configurados."""
        for symbol in self.symbols:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.warning("Dados indisponíveis para %s", symbol)
                continue

            bid = tick.bid
            ask = tick.ask
            if bid is None or ask is None:
                logger.warning("Tick inválido para %s: bid=%s ask=%s", symbol, bid, ask)
                continue

            mid = (bid + ask) / 2.0
            spread = ask - bid

            self.price_gauge.labels(symbol=symbol).set(mid)
            self.spread_gauge.labels(symbol=symbol).set(spread)
            logger.debug("Atualizado %s | mid=%f | spread=%f", symbol, mid, spread)

    def serve_metrics(self) -> None:
        """Inicia o servidor HTTP para Prometheus e atualiza métricas periodicamente."""
        start_http_server(self.metrics_port, registry=self.registry)
        logger.info("Servidor de métricas Forex iniciado em 0.0.0.0:%s", self.metrics_port)

        try:
            while True:
                self.fetch_and_update()
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            logger.info("Interrupção recebida. Encerrando ForexClientMT5.")
        finally:
            self.shutdown()

    @staticmethod
    def shutdown() -> None:
        """Finaliza o terminal MT5 com segurança."""
        mt5.shutdown()
        logger.info("Conexão com MT5 encerrada.")


def main() -> None:
    """Ponto de entrada padrão."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    symbols = ["EURUSD", "GBPUSD"]
    client = ForexClientMT5(symbols)
    client.serve_metrics()


if __name__ == "__main__":
    main()


