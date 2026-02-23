import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict

import MetaTrader5 as mt5
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

# --- CONFIGURAÇÃO E LOGGER (SEM ALTERAÇÕES NECESSÁRIAS) ---
logger = logging.getLogger("numeia_v2")
logger.setLevel(logging.INFO)
# Garante que o handler não seja adicionado múltiplas vezes se o script for recarregado
if not logger.handlers:
    handler = logging.FileHandler("numeia_execution.jsonl")
    formatter = logging.Formatter('{"time":"%(asctime)s","level":"%(levelname)s","message":%(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Buscar config.json na raiz do projeto (2 níveis acima)
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")
HEARTBEAT_FILE = str(Path(__file__).parent / "executor_heartbeat.tmp")

class Config(BaseModel):
    EXECUTION_CYCLE_SECONDS: int = Field(15, ge=5, le=600)
    TRADING_SYMBOLS: List[str] = Field(default_factory=lambda: ["EURUSD", "GBPUSD", "BTCUSD", "ETHUSD"])
    ORDER_VOLUME: float = Field(0.01)
    MAX_ORDER_ATTEMPTS: int = Field(3)
    MAPeriodFast: int = Field(20)
    MAPeriodSlow: int = Field(50)

def load_config(path=CONFIG_PATH) -> Config:
    try:
        with open(path) as f:
            data = json.load(f)
        return Config(**data)
    except FileNotFoundError:
        logger.critical(json.dumps({"event": "config_not_found", "path": path}))
        sys.exit(1)
    except ValidationError as e:
        logger.critical(json.dumps({"event": "config_validation_error", "error": str(e)}))
        sys.exit(1)

class Task(BaseModel):
    symbol: str
    action: str  # 'buy' or 'sell'
    price: float

# --- CORREÇÕES E MELHORIAS CRÍTICAS ---

def check_mt5_connection():
    """Verifica se a conexão com MT5 está ativa e saudável."""
    if not mt5.initialize():
        error = mt5.last_error()
        logger.critical(json.dumps({"event": "mt5_init_failed", "error": str(error)}))
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        logger.critical(json.dumps({"event": "mt5_account_info_failed", "message": "Não foi possível obter informações da conta. MT5 pode estar desconectado."}))
        mt5.shutdown()
        return False
        
    logger.info(json.dumps({"event": "mt5_connection_verified", "account": account_info.login, "server": account_info.server}))
    return True

def generate_real_signals(symbols: List[str], config: Config) -> List[Task]:
    """
    CORREÇÃO CRÍTICA #1: Gera sinais baseados em análise técnica real (MA20/MA50),
    conforme validado nos relatórios anteriores.
    """
    tasks = []
    logger.info(json.dumps({"event": "generating_signals", "symbol_count": len(symbols)}))
    
    for symbol in symbols:
        try:
            # Obtém candles do último dia para garantir dados suficientes
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
            if rates is None or len(rates) < config.MAPeriodSlow:
                logger.warning(json.dumps({"event": "insufficient_data", "symbol": symbol, "rates_count": len(rates) if rates is not None else 0}))
                continue
            
            df = pd.DataFrame(rates)
            df['ma_fast'] = df['close'].rolling(window=config.MAPeriodFast).mean()
            df['ma_slow'] = df['close'].rolling(window=config.MAPeriodSlow).mean()
            
            # Verifica se temos dados suficientes para comparar os dois últimos candles
            if len(df) < 2 or pd.isna(df.iloc[-2]['ma_fast']) or pd.isna(df.iloc[-2]['ma_slow']) or pd.isna(df.iloc[-1]['ma_fast']) or pd.isna(df.iloc[-1]['ma_slow']):
                logger.warning(json.dumps({"event": "ma_not_ready", "symbol": symbol}))
                continue
            
            # Sinal de compra: MA rápida cruza acima da lenta
            if df.iloc[-2]['ma_fast'] < df.iloc[-2]['ma_slow'] and df.iloc[-1]['ma_fast'] > df.iloc[-1]['ma_slow']:
                tick = mt5.symbol_info_tick(symbol)
                if tick and tick.ask > 0:
                    tasks.append(Task(symbol=symbol, action="buy", price=tick.ask))
                    logger.info(json.dumps({"event": "signal_generated", "symbol": symbol, "action": "buy", "price": tick.ask, "strategy": "ma_cross_above"}))
            
            # Sinal de venda: MA rápida cruza abaixo da lenta
            elif df.iloc[-2]['ma_fast'] > df.iloc[-2]['ma_slow'] and df.iloc[-1]['ma_fast'] < df.iloc[-1]['ma_slow']:
                tick = mt5.symbol_info_tick(symbol)
                if tick and tick.bid > 0:
                    tasks.append(Task(symbol=symbol, action="sell", price=tick.bid))
                    logger.info(json.dumps({"event": "signal_generated", "symbol": symbol, "action": "sell", "price": tick.bid, "strategy": "ma_cross_below"}))

        except Exception as e:
            logger.error(json.dumps({"event": "signal_generation_error", "symbol": symbol, "error": str(e)}))
            
    return tasks

def send_order(task: Task, config: Config) -> bool:
    """
    CORREÇÃO CRÍTICA #4: Verificação robusta do símbolo e tratamento de erro aprimorado.
    """
    symbol_info = mt5.symbol_info(task.symbol)
    if symbol_info is None:
        logger.error(json.dumps({"event": "symbol_not_found", "symbol": task.symbol}))
        return False

    # Verifica se símbolo está disponível para trading
    if not symbol_info.visible:
        logger.warning(json.dumps({"event": "symbol_not_visible", "symbol": task.symbol}))
        return False

    # Garante que o preço é válido
    price = task.price
    if price <= 0:
        logger.error(json.dumps({"event": "invalid_price", "symbol": task.symbol, "price": price}))
        return False
        
    point = symbol_info.point
    if point <= 0:
        logger.error(json.dumps({"event": "invalid_point", "symbol": task.symbol, "point": point}))
        return False
    
    # Obtém o tick atual para garantir que o preço está atualizado
    tick = mt5.symbol_info_tick(task.symbol)
    if tick is None:
        logger.error(json.dumps({"event": "tick_unavailable", "symbol": task.symbol}))
        return False
    
    # Usa o preço atual do tick se o preço da task estiver desatualizado
    if task.action == "buy":
        price = tick.ask
    else:
        price = tick.bid
    
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": task.symbol,
        "volume": config.ORDER_VOLUME,
        "type": mt5.ORDER_TYPE_BUY if task.action == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - 100 * point if task.action == "buy" else price + 100 * point, # SL simples
        "tp": price + 200 * point if task.action == "buy" else price - 200 * point, # TP simples
        "deviation": 10,
        "magic": 123456,
        "comment": "Numeia Serial v2.1",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(order_request)
    if result is None:
        error = mt5.last_error()
        logger.error(json.dumps({"event": "order_send_failed", "symbol": task.symbol, "error": str(error)}))
        return False
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(json.dumps({"event": "order_success", "symbol": task.symbol, "action": task.action, "volume": config.ORDER_VOLUME, "price": result.price, "deal": result.deal, "order": result.order}))
        return True
    else:
        logger.error(json.dumps({"event": "order_failed", "symbol": task.symbol, "retcode": result.retcode, "comment": result.comment}))
        return False

def update_heartbeat():
    """Atualiza o timestamp do arquivo de heartbeat para o watchdog integrado."""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(json.dumps({"event": "heartbeat_update_failed", "error": str(e)}))

def signal_handler(sig, frame):
    """Permite desligamento gracefully com Ctrl+C."""
    logger.info(json.dumps({"event": "shutdown_signal_received"}))
    mt5.shutdown()
    if os.path.exists(HEARTBEAT_FILE):
        os.remove(HEARTBEAT_FILE)
    sys.exit(0)

# --- LOOP PRINCIPAL COM MELHORIAS ---

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not check_mt5_connection():
        sys.exit(1)
        
    config = load_config()
    logger.info(json.dumps({"event": "executor_serial_v2_started", "version": "2.1"}))
    logger.info(json.dumps({"event": "config_loaded", "config": config.dict()}))

    try:
        while True:
            start_cycle_time = time.time()
            update_heartbeat() # CORREÇÃO CRÍTICA #2: Heartbeat integrado
            
            # CORREÇÃO CRÍTICA #3: Verificação de conexão a cada ciclo
            terminal_info = mt5.terminal_info()
            if terminal_info is None or not terminal_info.connected:
                logger.error(json.dumps({"event": "mt5_disconnected", "message": "MT5 desconectado! Tentando restabelecer..."}))
                if not check_mt5_connection():
                    logger.error(json.dumps({"event": "mt5_reconnect_failed", "message": "Falha ao reconectar. Aguardando próximo ciclo."}))
                    time.sleep(config.EXECUTION_CYCLE_SECONDS)
                    continue

            task_list = generate_real_signals(config.TRADING_SYMBOLS, config)
            
            if task_list:
                logger.info(json.dumps({"event": "tasks_ready", "count": len(task_list), "symbols": [t.symbol for t in task_list]}))
                for task in task_list:
                    attempts = 0
                    success = False
                    while attempts < config.MAX_ORDER_ATTEMPTS and not success:
                        success = send_order(task, config)
                        attempts += 1
                        if not success:
                            time.sleep(2) # Espera um pouco mais antes de tentar novamente
                    if not success:
                        logger.error(json.dumps({"event": "order_failed_after_attempts", "symbol": task.symbol, "action": task.action, "attempts": config.MAX_ORDER_ATTEMPTS}))
            else:
                logger.info(json.dumps({"event": "no_signals_generated", "cycle": "current"}))
            
            cycle_duration = time.time() - start_cycle_time
            sleep_time = max(0, config.EXECUTION_CYCLE_SECONDS - cycle_duration)
            logger.info(json.dumps({"event": "cycle_completed", "duration": cycle_duration, "sleep_time": sleep_time}))
            time.sleep(sleep_time)

    except Exception as e:
        logger.critical(json.dumps({"event": "fatal_error", "error": str(e)}))
        import traceback
        logger.critical(json.dumps({"event": "fatal_error_traceback", "traceback": traceback.format_exc()}))
    finally:
        mt5.shutdown()
        if os.path.exists(HEARTBEAT_FILE):
            os.remove(HEARTBEAT_FILE)
        logger.info(json.dumps({"event": "executor_shutdown"}))

