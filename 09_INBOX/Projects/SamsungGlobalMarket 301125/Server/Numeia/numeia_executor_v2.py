import os
import json
import logging
import threading
import time
import signal
import sys
from pathlib import Path
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError
import MetaTrader5 as mt5
import prometheus_client
from prometheus_client import Gauge, Counter, Histogram, start_http_server
import requests
import numpy as np
import pandas as pd

# Configuração de logger JSON para análise forense e machine learning futura
logger = logging.getLogger("numeia")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("numeia_execution.jsonl")
formatter = logging.Formatter('{"time":"%(asctime)s","level":"%(levelname)s","message":%(message)s}')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Buscar config.json na raiz do projeto (2 níveis acima)
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")

class Config(BaseModel):
    EMERGENCY_MODE_ENABLED: bool = Field(..., description="Habilita execução paralela")
    MAX_PARALLEL_WORKERS: int = Field(10, ge=1, le=100)
    EXECUTION_CYCLE_SECONDS: int = Field(15, ge=10, le=600)
    MAX_LATENCY_MS_P95: int = Field(300, ge=100, le=2000)
    MAX_FAILURE_RATE: float = Field(0.03, ge=0, le=1)
    ROLLBACK_WINDOW_SECONDS: int = Field(600, ge=60, le=3600)
    NOTIFICATION_WEBHOOK_URL: Optional[str] = Field(None, description="URL para notificações")
    TRADING_SYMBOLS: List[str]
    RISK_PARAMETERS: Dict[str, Any]
    MONITORING: Dict[str, Any]
    MAX_SPREAD_PIPS: Optional[Dict[str, float]] = Field(None, description="Limite de spread por símbolo em pips")

def load_config(path=CONFIG_PATH) -> Config:
    try:
        with open(path) as f:
            data = json.load(f)
        return Config(**data)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise

# Métricas Prometheus
LATENCY_HISTOGRAM = Histogram('numeia_order_latency_ms', 'Latency per order in ms', buckets=[50,100,200,300,500,1000])
FAILURE_COUNTER = Counter('numeia_order_failures_total', 'Total failed orders')
SUCCESS_COUNTER = Counter('numeia_order_success_total', 'Total successful orders')
ROLLBACK_COUNTER = Counter('numeia_rollbacks_total', 'Rollbacks triggered')
DRAWDOWN_GAUGE = Gauge('numeia_drawdown_current', 'Current portfolio drawdown')
SHARPE_RATIO_GAUGE = Gauge('numeia_sharpe_ratio_30d', '30-day Sharpe ratio')
SLIPPAGE_GAUGE = Gauge('numeia_slippage_avg_bps', 'Average slippage in basis points')
FILL_RATE_GAUGE = Gauge('numeia_fill_rate_percentage', 'Order fill rate percentage')
LEVERAGE_RATIO_GAUGE = Gauge('numeia_leverage_ratio', 'Current portfolio leverage ratio')

class HealthyMT5ConnectionPool:
    _instance_lock = threading.Lock()
    _instance = None

    def __init__(self, max_conns=1):
        self.max_conns = max_conns
        self.pool = Queue(max_conns)
        self._create_all_connections()
        self._health_check_interval = load_config().MONITORING["health_check_interval"]
        self._stop_event = threading.Event()
        self._health_check_thread = threading.Thread(target=self._health_monitor, daemon=True)
        self._health_check_thread.start()
        logger.info(json.dumps({"event":"connection_pool_initialized","count":max_conns}))

    @classmethod
    def get_instance(cls, max_conns=1):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = HealthyMT5ConnectionPool(max_conns)
        return cls._instance

    def _create_connection(self):
        if not mt5.initialize():
            raise RuntimeError(f"MT5 initialize failed, error code: {mt5.last_error()}")
        if not mt5.terminal_info().connected:
            raise RuntimeError("MT5 terminal is not connected to broker")
        return mt5

    def _create_all_connections(self):
        for _ in range(self.max_conns):
            try:
                self.pool.put(self._create_connection())
            except Exception as e:
                logger.error(f"Failed to create initial MT5 connection: {e}")
                raise

    def _is_connection_healthy(self, conn) -> bool:
        try:
            account_info = conn.account_info()
            return account_info is not None
        except Exception:
            return False

    def _health_monitor(self):
        while not self._stop_event.is_set():
            time.sleep(self._health_check_interval)
            temp_connections = []
            healthy_count = 0
            
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    if self._is_connection_healthy(conn):
                        temp_connections.append(conn)
                        healthy_count += 1
                    else:
                        logger.warning("Unhealthy MT5 connection detected, replacing...")
                        temp_connections.append(self._create_connection())
                except Empty:
                    break
            
            for conn in temp_connections:
                self.pool.put(conn)
                
            logger.info(json.dumps({"event": "health_check_completed", "healthy_connections": healthy_count}))

    def acquire(self):
        return self.pool.get()

    def release(self, conn):
        self.pool.put(conn)

    def shutdown(self):
        self._stop_event.set()
        self._health_check_thread.join()

class Task(BaseModel):
    id: int
    symbol: str
    action: str
    volume: float
    price: float = None
    sl: float = None
    tp: float = None
    deviation: int = 10
    magic: int = 123456

class Metrics:
    def __init__(self):
        self.latencies = []
        self.failures = 0
        self.successes = 0
        self.lock = threading.Lock()
        self.total_orders = 0
        self.filled_orders = 0

    def record_latency(self, latency_ms):
        with self.lock:
            LATENCY_HISTOGRAM.observe(latency_ms)
            self.latencies.append(latency_ms)
            if len(self.latencies) > 1000:
                self.latencies = self.latencies[-1000:]

    def record_result(self, success, filled=False):
        with self.lock:
            self.total_orders += 1
            if filled:
                self.filled_orders += 1
                
            if success:
                SUCCESS_COUNTER.inc()
                self.successes += 1
            else:
                FAILURE_COUNTER.inc()
                self.failures += 1
                
            fill_rate = (self.filled_orders / self.total_orders) * 100 if self.total_orders > 0 else 0
            FILL_RATE_GAUGE.set(fill_rate)

    def failure_rate(self):
        total = self.failures + self.successes
        return self.failures/total if total else 0

    def latency_percentile(self, percentile=95):
        with self.lock:
            if not self.latencies:
                return 0
            sorted_lat = sorted(self.latencies)
            idx = int(len(sorted_lat) * percentile / 100)
            return sorted_lat[min(idx, len(sorted_lat)-1)]

class CapitalManagement:
    def __init__(self, config: Config):
        self.config = config
        self.account_info = mt5.account_info()
        self.risk_params = config.RISK_PARAMETERS
        
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        balance = self.account_info.balance
        risk_per_trade = balance * self.risk_params["max_position_size_pct"]
        
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit == 0:
            return 0.01
            
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.01
            
        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        
        volume = risk_per_trade / (risk_per_unit / tick_size * tick_value)
        
        kelly_fraction = self.risk_params["kelly_fraction"]
        volume *= kelly_fraction
        
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        lot_step = symbol_info.volume_step
        
        volume = max(min_lot, min(volume, max_lot))
        volume = round(volume / lot_step) * lot_step
        
        return volume

class SignalGenerator:
    def __init__(self, symbols: List[str], capital_manager: CapitalManagement, config: Config):
        self.symbols = symbols
        self.capital_manager = capital_manager
        self.config = config
        self.max_spread_pips = config.MAX_SPREAD_PIPS or {}
        
    def _get_max_spread_for_symbol(self, symbol: str) -> float:
        """Retorna o limite de spread para um símbolo específico"""
        # Primeiro tenta buscar limite específico do símbolo
        if symbol in self.max_spread_pips:
            return self.max_spread_pips[symbol]
        # Senão usa o padrão
        if "default" in self.max_spread_pips:
            return self.max_spread_pips["default"]
        # Fallback para 5 pips se não configurado
        return 5.0
        
    def generate_signals(self) -> List[Task]:
        tasks = []
        for i, symbol in enumerate(self.symbols):
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(json.dumps({"event": "symbol_not_found", "symbol": symbol}))
                continue
                
            if not symbol_info.visible:
                logger.warning(json.dumps({"event": "symbol_market_closed", "symbol": symbol}))
                continue
                
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.warning(json.dumps({"event": "no_tick_data", "symbol": symbol}))
                continue
                
            spread = (tick.ask - tick.bid) / symbol_info.point
            max_spread = self._get_max_spread_for_symbol(symbol)
            
            if spread > max_spread:
                logger.info(json.dumps({
                    "event": "spread_too_wide",
                    "symbol": symbol,
                    "spread_pips": round(spread, 2),
                    "max_spread_pips": max_spread
                }))
                continue
                
            # ESTRATÉGIA: Análise de Tendência usando Média Móvel Simples
            # Buscar dados históricos para análise
            timeframe = mt5.TIMEFRAME_M15  # 15 minutos
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 50)  # 50 candles
            
            if rates is None or len(rates) < 20:
                logger.warning(json.dumps({"event": "insufficient_data", "symbol": symbol}))
                continue
            
            # Calcular média móvel de 20 períodos (curto prazo) e 50 períodos (longo prazo)
            df = pd.DataFrame(rates)
            df['ma20'] = df['close'].rolling(window=min(20, len(df))).mean()
            df['ma50'] = df['close'].rolling(window=min(50, len(df))).mean()
            
            # Obter últimos valores
            current_price = tick.bid  # Preço médio atual
            ma20_current = df['ma20'].iloc[-1]
            ma50_current = df['ma50'].iloc[-1] if len(df) >= 50 else ma20_current
            
            # Estratégia: Tendência de alta quando MA20 > MA50 e preço acima de ambas
            # Tendência de baixa quando MA20 < MA50 e preço abaixo de ambas
            if pd.isna(ma20_current) or pd.isna(ma50_current):
                logger.warning(json.dumps({"event": "ma_calculation_error", "symbol": symbol}))
                continue
            
            # Determinar direção baseada em análise técnica
            if ma20_current > ma50_current and current_price > ma20_current:
                action = "buy"  # Tendência de alta
                signal_strength = "strong_uptrend"
            elif ma20_current < ma50_current and current_price < ma20_current:
                action = "sell"  # Tendência de baixa
                signal_strength = "strong_downtrend"
            elif ma20_current > ma50_current:
                action = "buy"  # Tendência de alta (MA20 acima de MA50)
                signal_strength = "uptrend"
            else:
                action = "sell"  # Tendência de baixa (MA20 abaixo de MA50)
                signal_strength = "downtrend"
            
            # Filtrar sinais fracos (evitar trades em mercado lateral)
            ma_diff_pct = abs(ma20_current - ma50_current) / ma50_current * 100 if ma50_current != 0 else 0
            if ma_diff_pct < 0.01:  # Menos de 0.01% de diferença (mercado lateral)
                logger.info(json.dumps({
                    "event": "lateral_market",
                    "symbol": symbol,
                    "ma_diff_pct": round(ma_diff_pct, 4),
                    "action": "skip"
                }))
                continue
            
            price = tick.ask if action == "buy" else tick.bid
            
            # Ajustar SL/TP baseado na volatilidade (ATR aproximado)
            high_low_range = df['high'].iloc[-20:].max() - df['low'].iloc[-20:].min()
            atr_approx = high_low_range / 20 if len(df) >= 20 else symbol_info.point * 150
            
            # SL: 1.5x ATR, TP: 2.5x ATR (mas mínimo de 150/300 pontos)
            point = symbol_info.point
            sl_distance = max(150 * point, atr_approx * 1.5)
            tp_distance = max(300 * point, atr_approx * 2.5)
            
            sl = price - sl_distance if action == "buy" else price + sl_distance
            tp = price + tp_distance if action == "buy" else price - tp_distance
            
            # Normalizar SL/TP para dígitos do símbolo
            digits = symbol_info.digits
            sl = round(sl, digits)
            tp = round(tp, digits)
            
            logger.info(json.dumps({
                "event": "signal_generated",
                "symbol": symbol,
                "action": action,
                "signal_strength": signal_strength,
                "price": round(price, digits),
                "ma20": round(ma20_current, digits),
                "ma50": round(ma50_current, digits),
                "ma_diff_pct": round(ma_diff_pct, 4),
                "sl": round(sl, digits),
                "tp": round(tp, digits)
            }))
            
            volume = self.capital_manager.calculate_position_size(symbol, price, sl)
            
            task = Task(
                id=int(time.time() * 1000) + i,
                symbol=symbol,
                action=action,
                volume=volume,
                price=price,
                sl=sl,
                tp=tp
            )
            tasks.append(task)
            
        return tasks

class EnhancedParallelExecutor:
    def __init__(self, max_workers, metrics, config):
        self.max_workers = max_workers
        self.metrics = metrics
        self.config = config
        # Removido: connection_pool não é mais necessário - usamos mt5.order_send diretamente
        self._stop_event = threading.Event()
        self.signal_generator = SignalGenerator(config.TRADING_SYMBOLS, CapitalManagement(config), config)
        self.order_timeout = config.MONITORING["order_timeout_seconds"]

    def _handle_error_code(self, retcode: int):
        if retcode == mt5.TRADE_RETCODE_INVALID_VOLUME:
            logger.error("Invalid volume for trade")
        elif retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
            logger.error("Market is closed")
        elif retcode == mt5.TRADE_RETCODE_NO_MONEY:
            logger.error("Insufficient funds")
        elif retcode == mt5.TRADE_RETCODE_TRADE_DISABLED:
            logger.error("Trading is disabled")

    def _execute_task(self, task: Task) -> Tuple[bool, bool]:
        start = time.time()
        filled = False
        
        try:
            if not mt5.symbol_info(task.symbol):
                logger.error(json.dumps({"event": "symbol_not_exists", "symbol": task.symbol}))
                return False, False
                
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": task.symbol,
                "volume": task.volume,
                "type": mt5.ORDER_TYPE_BUY if task.action == 'buy' else mt5.ORDER_TYPE_SELL,
                "price": task.price or mt5.symbol_info_tick(task.symbol).ask,
                "sl": task.sl,
                "tp": task.tp,
                "deviation": task.deviation,
                "magic": task.magic,
                "comment": f"Numeia_{task.id}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Usar mt5.order_send diretamente (MetaTrader5 não precisa de pool de conexões ou threading)
            # Chamada direta é mais simples e confiável
            result = mt5.order_send(request)
            
            # Verificar se result é None (erro na chamada)
            if result is None:
                error_info = mt5.last_error()
                error_code = error_info[0] if isinstance(error_info, tuple) else error_info
                error_description = error_info[1] if isinstance(error_info, tuple) and len(error_info) > 1 else str(error_info)
                logger.error(json.dumps({
                    "event": "order_send_failed",
                    "symbol": task.symbol,
                    "task_id": task.id,
                    "error_code": error_code,
                    "error_description": error_description
                }))
                self.metrics.record_result(False, False)
                return False, False
            
            success_codes = [mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL]
            if result.retcode in success_codes:
                filled = result.volume > 0
                if filled:
                    slippage_bps = abs(result.price - task.price) / task.price * 10000
                    SLIPPAGE_GAUGE.set(slippage_bps)
                    
                logger.info(json.dumps({
                    "event": "order_success", "order_id": task.id, "symbol": task.symbol,
                    "price": result.price, "volume": result.volume, "deal": result.deal, "filled": filled
                }))
                self.metrics.record_result(True, filled)
                return True, filled
            else:
                logger.error(json.dumps({
                    "event": "order_fail", "order_id": task.id, "symbol": task.symbol,
                    "code": result.retcode, "comment": result.comment
                }))
                self._handle_error_code(result.retcode)
                self.metrics.record_result(False, False)
                return False, False
                
        except Exception as e:
            logger.error(json.dumps({"event":"exception", "order_id":task.id, "error": str(e)}))
            self.metrics.record_result(False, False)
            return False, False
        finally:
            self.metrics.record_latency((time.time()-start)*1000)

    def run(self):
        logger.info(json.dumps({"event": "executor_started", "workers": self.max_workers}))
        while not self._stop_event.is_set():
            cycle_start = time.time()
            tasks = self.signal_generator.generate_signals()
            
            if not tasks:
                logger.warning(json.dumps({"event": "no_tasks_generated"}))
            else:
                logger.info(json.dumps({"event": "tasks_ready_for_execution", "count": len(tasks), "symbols": [t.symbol for t in tasks]}))
                
            if tasks:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(self._execute_task, task) for task in tasks]
                    logger.info(json.dumps({"event": "tasks_submitted", "count": len(futures)}))
                    for future in as_completed(futures):
                        try:
                            success, filled = future.result()
                            logger.info(json.dumps({"event": "task_completed", "success": success, "filled": filled}))
                        except Exception as e:
                            logger.error(json.dumps({"event": "task_execution_error", "error": str(e)}))
                            import traceback
                            logger.error(json.dumps({"event": "task_execution_traceback", "traceback": traceback.format_exc()}))
            
            # check_rollback agora reseta métricas automaticamente e retorna False
            # Não precisa mais do loop de espera
            rollback_triggered = self.check_rollback()
            if rollback_triggered:
                logger.warning(json.dumps({"event": "rollback_triggered", "action": "metrics_reset", "next_cycle_in": self.config.EXECUTION_CYCLE_SECONDS}))
                # Esperar um ciclo antes de continuar (dar tempo para o rollback)
                time.sleep(self.config.EXECUTION_CYCLE_SECONDS)
                continue
                
            cycle_time = time.time() - cycle_start
            wait_time = max(0, self.config.EXECUTION_CYCLE_SECONDS - cycle_time)
            
            if wait_time > 0:
                logger.info(json.dumps({"event": "cycle_completed", "duration": cycle_time, "waiting": wait_time}))
                time.sleep(wait_time)

    def check_rollback(self) -> bool:
        fail_rate = self.metrics.failure_rate()
        latency_p95 = self.metrics.latency_percentile(95)
        
        # Verificar apenas se temos dados suficientes (pelo menos 3 tentativas)
        total_attempts = self.metrics.failures + self.metrics.successes
        if total_attempts < 3:
            # Não ativar rollback com poucos dados
            return False
        
        if fail_rate > self.config.MAX_FAILURE_RATE:
            logger.warning(json.dumps({"event": "rollback_condition_met", "reason": "failure_rate", "value": fail_rate, "threshold": self.config.MAX_FAILURE_RATE}))
            execute_rollback_enhanced(self.config)
            # Resetar métricas após rollback para permitir nova tentativa
            logger.info(json.dumps({"event": "metrics_reset_after_rollback", "previous_failures": self.metrics.failures, "previous_successes": self.metrics.successes}))
            self.metrics.failures = 0
            self.metrics.successes = 0
            self.metrics.total_orders = 0
            self.metrics.filled_orders = 0
            self.metrics.latencies = []
            return False  # Retornar False para não bloquear indefinidamente
            
        if latency_p95 > self.config.MAX_LATENCY_MS_P95:
            logger.warning(json.dumps({"event": "rollback_condition_met", "reason": "latency_p95", "value": latency_p95, "threshold": self.config.MAX_LATENCY_MS_P95}))
            execute_rollback_enhanced(self.config)
            # Resetar métricas após rollback
            logger.info(json.dumps({"event": "metrics_reset_after_rollback", "previous_failures": self.metrics.failures, "previous_successes": self.metrics.successes}))
            self.metrics.failures = 0
            self.metrics.successes = 0
            self.metrics.total_orders = 0
            self.metrics.filled_orders = 0
            self.metrics.latencies = []
            return False  # Retornar False para não bloquear indefinidamente
            
        return False

    def stop(self):
        logger.info(json.dumps({"event": "executor_stop_requested"}))
        self._stop_event.set()
        # Removido: connection_pool não é mais necessário - usamos mt5.order_send diretamente

def send_notification(message: str, webhook_url: str):
    try:
        response = requests.post(webhook_url, json={"text": message}, headers={"Content-type": "application/json"})
        if response.status_code != 200:
            logger.error(f"Failed to send notification: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

def execute_rollback_enhanced(config: Config):
    logger.warning(json.dumps({"event": "rollback_started"}))
    ROLLBACK_COUNTER.inc()
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 1, "action": "Deactivating emergency mode"}))
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 2, "action": "Canceling pending orders"}))
    orders = mt5.orders_get()
    if orders:
        for order in orders:
            request = {"action": mt5.TRADE_ACTION_REMOVE, "order": order.ticket, "magic": order.magic}
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(json.dumps({"event": "rollback_cancel_fail", "order": order.ticket, "code": result.retcode}))
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 3, "action": "Closing positions beyond risk limits"}))
    positions = mt5.positions_get()
    if positions:
        for position in positions:
            should_close = False
            if should_close:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL, "symbol": position.symbol, "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": position.ticket,
                    "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
                    "deviation": 20, "magic": position.magic, "comment": "Numeia rollback close",
                    "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
                }
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.error(json.dumps({"event": "rollback_close_fail", "position": position.ticket, "code": result.retcode}))
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 4, "action": "Notifying critical channels"}))
    if config.NOTIFICATION_WEBHOOK_URL:
        send_notification("🚨 Numeia System Rollback Triggered", config.NOTIFICATION_WEBHOOK_URL)
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 5, "action": "Registering forensic snapshot"}))
    
    logger.warning(json.dumps({"event": "rollback_step", "step": 6, "action": "Blocking new executions until review"}))
    
    logger.warning(json.dumps({"event": "rollback_completed"}))

def signal_handler(sig, frame):
    logger.info(json.dumps({"event": "shutdown_signal_received", "signal": sig}))
    if 'executor' in globals():
        executor.stop()
    sys.exit(0)

def main():
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        config = load_config()
        metrics = Metrics()

        if not config.EMERGENCY_MODE_ENABLED:
            logger.info(json.dumps({"event":"serial_mode_activated"}))
            return

        start_http_server(config.MONITORING["prometheus_port"])
        logger.info(json.dumps({"event":"prometheus_server_started", "port":config.MONITORING["prometheus_port"]}))

        global executor
        executor = EnhancedParallelExecutor(config.MAX_PARALLEL_WORKERS, metrics, config)

        try:
            executor.run()
        except KeyboardInterrupt:
            logger.info(json.dumps({"event":"interrupted_by_user"}))
        finally:
            executor.stop()
            
    except Exception as e:
        logger.error(json.dumps({"event": "system_error", "error": str(e)}))
        raise

if __name__ == "__main__":
    main()

