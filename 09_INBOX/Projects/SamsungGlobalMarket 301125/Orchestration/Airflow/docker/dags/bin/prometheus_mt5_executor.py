# MEMORY_ID: OP_PROMETHEUS_MT5_EXECUTOR
# TIMESTAMP: 2025-11-12T10:25:00+01:00
# AUTHOR: Cursor_Omega
"""
Executor MT5 com exportação Prometheus e kill-switch institucional.

Requisitos:
- MetaTrader5 conectado ao broker institucional (hedge ou netting).
- Prometheus coletando em http://localhost:63000/metrics.
- webhook Slack válido configurado em `config/config.yaml` (alerts.slack_webhook).
"""

from __future__ import annotations

import logging
import math
import os
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import MetaTrader5 as mt5
import requests
import yaml
from prometheus_client import CollectorRegistry, Gauge, start_http_server


ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "logs" / "prometheus_mt5_executor.log"
CONFIG_FILE = ROOT_DIR / "config" / "config.yaml"
METRICS_PORT = 63000

# Parâmetros táticos (valores em pontos)
STOP_LOSS_POINTS = 30
TAKE_PROFIT_POINTS = 80
COOLDOWN_SECONDS = 300
PRICE_DEVIATION_POINTS = 10
DEFAULT_KILL_SWITCH_THRESHOLD = -1000.0


def _setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        logging.critical("Arquivo de configuração inexistente em %s", CONFIG_FILE)
        raise SystemExit(1)
    with CONFIG_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def _resolve_slack_webhook(cfg: dict) -> Optional[str]:
    env_webhook = os.environ.get("PROMETHEUS_SLACK_WEBHOOK")
    if env_webhook:
        logging.info("Webhook Slack carregado da variável de ambiente PROMETHEUS_SLACK_WEBHOOK.")
        return env_webhook

    webhook = (cfg.get("alerts") or {}).get("slack_webhook")
    if not webhook:
        logging.warning("Webhook Slack não configurado em config.yaml (alerts.slack_webhook).")
        return None
    return webhook


def _resolve_kill_switch_threshold(cfg: dict) -> float:
    env_value = os.environ.get("PROMETHEUS_KILL_SWITCH_THRESHOLD")
    if env_value:
        try:
            threshold = float(env_value)
            logging.info(
                "Kill-switch threshold carregado da variável de ambiente PROMETHEUS_KILL_SWITCH_THRESHOLD: %.2f",
                threshold,
            )
            return threshold
        except ValueError:
            logging.error(
                "Valor inválido em PROMETHEUS_KILL_SWITCH_THRESHOLD: %s. Utilizando configuração.",
                env_value,
            )
    risk_section = cfg.get("risk") or {}
    threshold_cfg = risk_section.get("kill_switch_balance", DEFAULT_KILL_SWITCH_THRESHOLD)
    try:
        threshold = float(threshold_cfg)
    except (TypeError, ValueError):
        logging.error(
            "Valor inválido em risk.kill_switch_balance (%s). Usando padrão %.2f.",
            threshold_cfg,
            DEFAULT_KILL_SWITCH_THRESHOLD,
        )
        threshold = DEFAULT_KILL_SWITCH_THRESHOLD
    logging.info("Kill-switch threshold configurado em %.2f.", threshold)
    return threshold


def _send_slack_alert(webhook: Optional[str], message: str) -> None:
    if not webhook:
        return
    try:
        response = requests.post(webhook, json={"text": message}, timeout=10)
        if response.status_code >= 400:
            logging.error(
                "Falha ao enviar alerta Slack (%s): %s",
                response.status_code,
                response.text,
            )
    except requests.RequestException as exc:
        logging.error("Erro de rede ao enviar alerta Slack: %s", exc)


def _initialize_mt5() -> None:
    if not mt5.initialize():
        error_code, error_details = mt5.last_error()
        logging.critical("Falha ao conectar MT5 (código %s: %s)", error_code, error_details)
        raise SystemExit(1)
    logging.info("Conexão MT5 estabelecida com sucesso.")


def _start_prometheus_server(registry: CollectorRegistry) -> None:
    start_http_server(METRICS_PORT, registry=registry)
    logging.info("Exporter Prometheus iniciado na porta %d.", METRICS_PORT)


def _modify_position_sl_tp(
    position, symbol_info, stop_loss_points: int, take_profit_points: int
) -> tuple[bool, bool]:
    point = symbol_info.point
    if math.isclose(point, 0.0):
        logging.error("Point para %s é zero, impossibilitando SL/TP.", position.symbol)
        return False, False

    sl_offset = stop_loss_points * point
    tp_offset = take_profit_points * point

    if position.type == mt5.POSITION_TYPE_BUY:
        expected_sl = position.price_open - sl_offset
        expected_tp = position.price_open + tp_offset
    else:
        expected_sl = position.price_open + sl_offset
        expected_tp = position.price_open - tp_offset

    tolerance = max(point, symbol_info.point * 0.5)
    sl_needs_update = position.sl is None or abs(position.sl - expected_sl) > tolerance
    tp_needs_update = position.tp is None or abs(position.tp - expected_tp) > tolerance

    if not (sl_needs_update or tp_needs_update):
        return False, True

    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": position.symbol,
        "position": position.ticket,
        "sl": expected_sl,
        "tp": expected_tp,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            "Erro ao ajustar SL/TP de %s (ticket %d). retcode=%s comment=%s",
            position.symbol,
            position.ticket,
            result.retcode,
            result.comment,
        )
        return True, False

    logging.info(
        "SL/TP ajustados para %s (ticket %d) => SL %.5f | TP %.5f",
        position.symbol,
        position.ticket,
        expected_sl,
        expected_tp,
    )
    return True, True


def _close_all_positions(slack_webhook: Optional[str]) -> None:
    positions = mt5.positions_get()
    if positions:
        logging.info("Fechando %d posições abertas.", len(positions))
    for position in positions or []:
        symbol = position.symbol
        volume = position.volume
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logging.error("Informações ausentes para símbolo %s; não foi possível fechar posição.", symbol)
            continue
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logging.error("Tick indisponível para %s; não foi possível fechar posição.", symbol)
            continue

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "price": tick.bid if position.type == mt5.POSITION_TYPE_BUY else tick.ask,
            "deviation": PRICE_DEVIATION_POINTS,
            "comment": "Prometheus KillSwitch Close",
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(
                "Falha ao fechar posição %d (%s). retcode=%s comment=%s",
                position.ticket,
                symbol,
                result.retcode,
                result.comment,
            )
            _send_slack_alert(
                slack_webhook,
                f"[CRÍTICO] Falha ao encerrar posição {symbol} ticket {position.ticket}: {result.comment}",
            )

    pending_orders = mt5.orders_get()
    for order in pending_orders or []:
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order.ticket,
            "comment": "Prometheus KillSwitch Remove",
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(
                "Falha ao remover ordem pendente %d (%s). retcode=%s comment=%s",
                order.ticket,
                order.symbol,
                result.retcode,
                result.comment,
            )


def _shutdown_mt5() -> None:
    try:
        mt5.shutdown()
        logging.info("Conexão MT5 encerrada.")
    except Exception as exc:
        logging.error("Erro ao encerrar MT5: %s", exc)


@dataclass
class Metrics:
    registry: CollectorRegistry
    fx_balance: Gauge
    fx_equity: Gauge
    fx_open_positions: Gauge
    fx_open_orders: Gauge
    fx_sl_tp_fails: Gauge
    fx_killswitch_activations: Gauge
    fx_cooldown_status: Gauge


def _build_metrics() -> Metrics:
    registry = CollectorRegistry()
    return Metrics(
        registry=registry,
        fx_balance=Gauge("fx_balance", "Saldo geral da conta MT5", registry=registry),
        fx_equity=Gauge("fx_equity", "Equity MT5", registry=registry),
        fx_open_positions=Gauge(
            "fx_open_positions", "Quantidade de posições abertas MT5", registry=registry
        ),
        fx_open_orders=Gauge("fx_open_orders", "Ordens pendentes MT5", registry=registry),
        fx_sl_tp_fails=Gauge("fx_sl_tp_fails", "Falhas ao ajustar SL/TP no executor", registry=registry),
        fx_killswitch_activations=Gauge(
            "fx_killswitch_activations", "Ativações do kill-switch", registry=registry
        ),
        fx_cooldown_status=Gauge(
            "fx_cooldown_status", "Status do cooldown do executor (1 durante cooldown, 0 fora)", registry=registry
        ),
    )


def _killswitch_check(
    acc_info,
    metrics: Metrics,
    slack_webhook: Optional[str],
    kill_switch_threshold: float,
) -> None:
    if acc_info is None:
        logging.error("account_info() retornou None; investigue conexão MT5.")
        return
    if acc_info.balance < kill_switch_threshold:
        logging.critical("Kill-switch acionado! Saldo %.2f < %.2f", acc_info.balance, kill_switch_threshold)
        metrics.fx_killswitch_activations.inc()
        _send_slack_alert(
            slack_webhook,
            f"[CRÍTICO] Kill-switch Prometheus acionado. Saldo {acc_info.balance:.2f} abaixo do limite {kill_switch_threshold:.2f}.",
        )
        _close_all_positions(slack_webhook)
        _shutdown_mt5()
        raise SystemExit(2)


def _apply_risk_controls(metrics: Metrics) -> None:
    positions = mt5.positions_get()
    fails = 0
    for position in positions or []:
        symbol_info = mt5.symbol_info(position.symbol)
        if symbol_info is None:
            logging.error("symbol_info() retornou None para %s", position.symbol)
            continue
        updated, success = _modify_position_sl_tp(
            position, symbol_info, STOP_LOSS_POINTS, TAKE_PROFIT_POINTS
        )
        if updated and not success:
            fails += 1
    metrics.fx_sl_tp_fails.set(fails)
    metrics.fx_open_positions.set(len(positions) if positions else 0)
    orders = mt5.orders_get()
    metrics.fx_open_orders.set(len(orders) if orders else 0)


def _graceful_exit(signum, frame) -> None:
    logging.info("Sinal %s recebido. Encerrando executor com segurança.", signum)
    _shutdown_mt5()
    sys.exit(0)


def main() -> None:
    _setup_logging()
    config = _load_config()
    slack_webhook = _resolve_slack_webhook(config)
    kill_switch_threshold = _resolve_kill_switch_threshold(config)

    signal.signal(signal.SIGINT, _graceful_exit)
    signal.signal(signal.SIGTERM, _graceful_exit)

    _initialize_mt5()
    metrics = _build_metrics()
    _start_prometheus_server(metrics.registry)

    try:
        while True:
            acc_info = mt5.account_info()
            _killswitch_check(acc_info, metrics, slack_webhook, kill_switch_threshold)
            if acc_info:
                metrics.fx_balance.set(acc_info.balance)
                metrics.fx_equity.set(acc_info.equity)

            _apply_risk_controls(metrics)

            metrics.fx_cooldown_status.set(1)
            logging.info("Ciclo concluído. Iniciando cooldown de %d segundos.", COOLDOWN_SECONDS)
            time.sleep(COOLDOWN_SECONDS)
            metrics.fx_cooldown_status.set(0)
    except Exception as exc:
        logging.exception("Erro crítico no executor: %s", exc)
        _send_slack_alert(slack_webhook, f"[CRÍTICO] Erro no executor Prometheus/MT5: {exc}")
        raise
    finally:
        _shutdown_mt5()


if __name__ == "__main__":
    main()

