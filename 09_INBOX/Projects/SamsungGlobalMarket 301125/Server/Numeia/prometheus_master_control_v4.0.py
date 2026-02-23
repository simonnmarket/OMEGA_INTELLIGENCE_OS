#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA MESTRE DE CONTROLE PROMETHEUS v4.0
Sistema Autônomo de Trading - Operação, Monitoramento e Recuperação Automática

Diretiva: Sistema autônomo que opera, se monitora e se recupera sem intervenção.
Estratégia: Seletiva baseada em validação v3.6 (Baseline para XAUUSD/ETHUSD, Filtro para BTCUSD)
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
import sys
import time
import threading
import signal
import logging
from pathlib import Path

# --- CONFIGURAÇÕES GLOBAIS E ESTADO ---
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")
LOG_FILE = "prometheus_master_log.jsonl"
HEARTBEAT_FILE = "prometheus_heartbeat.tmp"
STATE_FILE = "prometheus_state.json"

# Configuração do Logger
logger = logging.getLogger("PrometheusMaster")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- ESTRATÉGIA SELETIVA FIXA (BASEADA NO RELATÓRIO AIC v3.6) ---
# Esta é a nossa verdade. Não deve ser alterada sem um novo backtest completo.
SELECTIVE_STRATEGY_CONFIG = {
    "XAUUSD": {"use_filter": False, "reason": "Filter worsened performance (PF: 4.6 -> 4.0)"},
    "ETHUSD": {"use_filter": False, "reason": "Excessive trade reduction (78.3%)"},
    "BTCUSD": {"use_filter": True, "reason": "Massive performance improvement (PF: 26 -> 999.99, WR: 92.86% -> 100%)"}
}

# --- FUNÇÕES DE ANÁLISE E UTILIDADES ---

def calculate_ma(data: pd.DataFrame, period: int) -> float:
    """Calcula média móvel simples"""
    return data['close'].rolling(window=period).mean().iloc[-1]

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
    """Calcula RSI (Relative Strength Index)"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_volume_average(data: pd.DataFrame, period: int = 20) -> float:
    """Calcula média de volume"""
    return data['tick_volume'].rolling(window=period).mean().iloc[-1]

def is_optimal_trading_window() -> bool:
    """
    Verifica se estamos na janela ideal de trading (Londres/NY).
    Londres: 08:00-12:00 GMT
    NY: 13:00-17:00 GMT
    Sobreposição: 13:00-17:00 GMT (melhor liquidez)
    """
    try:
        now = datetime.utcnow()
        hour = now.hour
        
        # Janela de Londres (08:00-12:00 GMT)
        london_window = 8 <= hour < 12
        
        # Janela de NY (13:00-17:00 GMT)
        ny_window = 13 <= hour < 17
        
        # Sobreposição (13:00-17:00 GMT) - melhor janela
        overlap_window = 13 <= hour < 17
        
        # Retornar True se estiver em qualquer janela ideal
        return london_window or ny_window or overlap_window
    except:
        return True  # Se erro, permitir trading (não bloquear)

def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """Calcula Profit Factor"""
    if trades.empty:
        return 0.0
    
    profits = trades['profit'].values
    winning = profits[profits > 0]
    losing = abs(profits[profits < 0])
    
    total_profit = winning.sum() if len(winning) > 0 else 0
    total_loss = losing.sum() if len(losing) > 0 else 0
    
    if total_loss == 0:
        return float('inf') if total_profit > 0 else 0.0
    
    return total_profit / total_loss

def calculate_win_rate(trades: pd.DataFrame) -> float:
    """Calcula Win Rate (%)"""
    if trades.empty:
        return 0.0
    winning = (trades['profit'] > 0).sum()
    return (winning / len(trades)) * 100

def calculate_expectancy(trades: pd.DataFrame) -> float:
    """Calcula Expectancy"""
    if trades.empty:
        return 0.0
    return trades['profit'].mean()

# --- MÓDULO DE EXECUÇÃO DE ORDENS ---

def send_order(signal: Dict, config: Dict) -> Optional[Dict]:
    """
    Envia ordem usando SL/TP da estratégia.
    Retorna dict com informações da ordem ou None se falhar.
    """
    symbol = signal['symbol']
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(json.dumps({"event": "symbol_not_found", "symbol": symbol}))
        return None

    if not symbol_info.visible:
        logger.warning(json.dumps({"event": "symbol_not_visible", "symbol": symbol}))
        return None
    
    # Obtém tick atual
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(json.dumps({"event": "tick_unavailable", "symbol": symbol}))
        return None
    
    # Usa preço atual do tick
    if signal['action'] == "buy":
        price = tick.ask
    else:
        price = tick.bid
    
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": signal['volume'],
        "type": mt5.ORDER_TYPE_BUY if signal['action'] == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": signal['sl'],
        "tp": signal['tp'],
        "deviation": 10,
        "magic": 789012,
        "comment": "Prometheus Master v4.0",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(order_request)
    if result is None:
        error = mt5.last_error()
        logger.error(json.dumps({"event": "order_send_failed", "symbol": symbol, "error": str(error)}))
        return None
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        order_data = {
            "event": "ORDER_EXECUTED",
            "symbol": symbol,
            "action": signal['action'],
            "volume": signal['volume'],
            "entry_price": result.price,
            "sl": signal['sl'],
            "tp": signal['tp'],
            "order_id": result.order,
            "deal_id": result.deal,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(json.dumps(order_data))
        return order_data
    else:
        logger.error(json.dumps({
            "event": "order_failed",
            "symbol": symbol,
            "retcode": result.retcode,
            "comment": result.comment
        }))
        return None

# --- MÓDULO DE GERAÇÃO DE SINAIS (COM ESTRATÉGIA SELETIVA) ---

def generate_signals(config: Dict) -> List[Dict]:
    """
    Gera sinais de trading usando estratégia seletiva fixa.
    Aplica filtro de inteligência apenas para símbolos configurados.
    """
    signals = []
    
    for symbol in config.get('TRADING_SYMBOLS', ['XAUUSD', 'BTCUSD', 'ETHUSD']):
        # Aplicar a estratégia seletiva FIXA
        strategy = SELECTIVE_STRATEGY_CONFIG.get(symbol)
        if not strategy:
            logger.warning(json.dumps({"event": "symbol_not_in_strategy", "symbol": symbol}))
            continue
        
        use_filter = strategy['use_filter']
        
        # Se o filtro deve ser usado e a janela não é ideal, pular
        if use_filter and not is_optimal_trading_window():
            logger.debug(json.dumps({"event": "filter_skipped", "symbol": symbol, "reason": "not_optimal_window"}))
            continue
        
        try:
            # Obter dados multi-timeframe
            h4_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 100)
            h1_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
            m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
            
            if h4_data is None or h1_data is None or m5_data is None or len(h4_data) < 50:
                logger.warning(json.dumps({"event": "insufficient_data", "symbol": symbol}))
                continue
            
            # Converter para DataFrame
            h4_df = pd.DataFrame(h4_data)
            h1_df = pd.DataFrame(h1_data)
            m5_df = pd.DataFrame(m5_data)
            
            # Calcular indicadores
            h4_ma20 = calculate_ma(h4_df, 20)
            h4_ma50 = calculate_ma(h4_df, 50)
            h1_ma20 = calculate_ma(h1_df, 20)
            h1_ma50 = calculate_ma(h1_df, 50)
            m5_ma20 = calculate_ma(m5_df, 20)
            m5_rsi = calculate_rsi(m5_df)
            m5_volume_avg = calculate_volume_average(m5_df)
            
            # Verificar se há valores NaN
            if pd.isna(h4_ma20) or pd.isna(h4_ma50) or pd.isna(h1_ma20) or pd.isna(h1_ma50) or pd.isna(m5_ma20) or pd.isna(m5_rsi):
                logger.warning(json.dumps({"event": "indicators_not_ready", "symbol": symbol}))
                continue
            
            # Condições de alta probabilidade
            h4_trend_up = h4_ma20 > h4_ma50
            h1_confirmation_up = h1_ma20 > h1_ma50
            m5_entry_up = m5_df['close'].iloc[-1] > m5_ma20
            rsi_ok = 40 < m5_rsi < 60
            volume_spike = m5_df['tick_volume'].iloc[-1] > m5_volume_avg
            
            # Sinal de COMPRA
            if h4_trend_up and h1_confirmation_up and m5_entry_up and rsi_ok and volume_spike:
                tick = mt5.symbol_info_tick(symbol)
                symbol_info = mt5.symbol_info(symbol)
                
                if tick is None or symbol_info is None:
                    logger.error(json.dumps({"event": "tick_unavailable", "symbol": symbol}))
                    continue
                
                entry_price = tick.ask
                point = symbol_info.point
                
                if point <= 0:
                    logger.error(json.dumps({"event": "invalid_point", "symbol": symbol, "point": point}))
                    continue
                
                # SL de 50 pontos, TP de 100 pontos - Risk/Reward 1:2
                sl = entry_price - 50 * point
                tp = entry_price + 100 * point
                
                signal = {
                    "symbol": symbol,
                    "action": "buy",
                    "price": entry_price,
                    "sl": sl,
                    "tp": tp,
                    "volume": config.get('ORDER_VOLUME', 0.02),
                    "confidence": 0.85,
                    "strategy": "selective_multi_timeframe",
                    "filter_used": use_filter
                }
                
                signals.append(signal)
                logger.info(json.dumps({
                    "event": "signal_generated",
                    "symbol": symbol,
                    "action": "buy",
                    "entry_price": entry_price,
                    "sl": sl,
                    "tp": tp,
                    "volume": signal['volume'],
                    "filter_used": use_filter,
                    "strategy": "selective_multi_timeframe"
                }))
        
        except Exception as e:
            logger.error(json.dumps({"event": "signal_generation_error", "symbol": symbol, "error": str(e)}))
            import traceback
            logger.error(json.dumps({"event": "signal_generation_traceback", "traceback": traceback.format_exc()}))
    
    return signals

# --- WATCHDOG OBRIGATÓRIO ---

class PrometheusWatchdog(threading.Thread):
    def __init__(self, main_thread_id):
        super().__init__(daemon=True)
        self.main_thread_id = main_thread_id
        self.last_heartbeat_time = time.time()
        self.running = True

    def run(self):
        logger.info(json.dumps({"event": "WATCHDOG_STARTED", "message": "Iniciando monitoramento do sistema."}))
        while self.running:
            time.sleep(30)  # Verificar a cada 30 segundos
            
            # 1. Verificar se a thread principal ainda está viva
            if not threading.main_thread().is_alive():
                logger.critical(json.dumps({"event": "WATCHDOG_CRITICAL", "message": "Thread principal morreu. Desligando sistema."}))
                self.shutdown_system()
                break

            # 2. Verificar se o heartbeat foi atualizado
            try:
                if os.path.exists(HEARTBEAT_FILE):
                    last_mod = os.path.getmtime(HEARTBEAT_FILE)
                    if last_mod > self.last_heartbeat_time:
                        self.last_heartbeat_time = last_mod
                    else:
                        # Se o heartbeat não for atualizado em 90 segundos, é um problema
                        if time.time() - self.last_heartbeat_time > 90:
                            logger.critical(json.dumps({"event": "WATCHDOG_CRITICAL", "message": "Heartbeat parou. Sistema travado. Desligando."}))
                            self.shutdown_system()
                            break
                else:
                    logger.error(json.dumps({"event": "WATCHDOG_ERROR", "message": "Arquivo de heartbeat não encontrado."}))
                    # Aguardar um pouco antes de desligar (pode estar sendo criado)
                    if time.time() - self.last_heartbeat_time > 90:
                        self.shutdown_system()
                        break
            except Exception as e:
                logger.error(json.dumps({"event": "WATCHDOG_ERROR", "error": str(e)}))
                if time.time() - self.last_heartbeat_time > 90:
                    self.shutdown_system()
                    break

    def shutdown_system(self):
        logger.critical(json.dumps({"event": "WATCHDOG_SHUTDOWN", "message": "Iniciando desligamento de emergência."}))
        self.running = False
        mt5.shutdown()
        # O script principal irá terminar logo após
        os._exit(1)  # Força saída imediata

# --- FUNÇÕES PRINCIPAIS DO SISTEMA ---

def load_config() -> Dict:
    """Carrega e valida config.json"""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        
        # Garantir símbolos padrão se não especificados
        if 'TRADING_SYMBOLS' not in config or not config['TRADING_SYMBOLS']:
            config['TRADING_SYMBOLS'] = ['XAUUSD', 'BTCUSD', 'ETHUSD']
        
        logger.info(json.dumps({"event": "config_loaded", "config": config}))
        return config
    except FileNotFoundError:
        logger.critical(json.dumps({"event": "config_not_found", "path": CONFIG_PATH}))
        # Config padrão
        return {
            "TRADING_SYMBOLS": ["XAUUSD", "BTCUSD", "ETHUSD"],
            "ORDER_VOLUME": 0.02,
            "EXECUTION_CYCLE_SECONDS": 15,
            "MAX_ORDER_ATTEMPTS": 3
        }
    except Exception as e:
        logger.critical(json.dumps({"event": "config_load_error", "error": str(e)}))
        return {
            "TRADING_SYMBOLS": ["XAUUSD", "BTCUSD", "ETHUSD"],
            "ORDER_VOLUME": 0.02,
            "EXECUTION_CYCLE_SECONDS": 15,
            "MAX_ORDER_ATTEMPTS": 3
        }

def update_heartbeat():
    """Atualiza o arquivo de heartbeat"""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(json.dumps({"event": "heartbeat_update_failed", "error": str(e)}))

def run_production_cycle(config: Dict):
    """Executa um ciclo de produção"""
    logger.info(json.dumps({"event": "PRODUCTION_CYCLE_START", "message": "Iniciando ciclo de execução."}))
    
    # Verificar conexão MT5
    terminal_info = mt5.terminal_info()
    if terminal_info is None or not terminal_info.connected:
        logger.error(json.dumps({"event": "mt5_disconnected", "message": "MT5 desconectado! Tentando restabelecer..."}))
        if not mt5.initialize():
            logger.error(json.dumps({"event": "mt5_reconnect_failed", "message": "Falha ao reconectar."}))
            return
    
    signals = generate_signals(config)
    if not signals:
        logger.info(json.dumps({"event": "PRODUCTION_NO_SIGNALS", "message": "Nenhum sinal gerado neste ciclo."}))
        update_heartbeat()
        return
    
    logger.info(json.dumps({"event": "PRODUCTION_SIGNALS_GENERATED", "count": len(signals), "symbols": [s['symbol'] for s in signals]}))
    
    for signal in signals:
        attempts = 0
        success = False
        while attempts < config.get('MAX_ORDER_ATTEMPTS', 3) and not success:
            order_result = send_order(signal, config)
            if order_result is not None:
                success = True
            else:
                attempts += 1
                if attempts < config.get('MAX_ORDER_ATTEMPTS', 3):
                    time.sleep(2)
        
        if not success:
            logger.error(json.dumps({
                "event": "order_failed_after_attempts",
                "symbol": signal['symbol'],
                "action": signal['action'],
                "attempts": config.get('MAX_ORDER_ATTEMPTS', 3)
            }))
    
    update_heartbeat()
    logger.info(json.dumps({"event": "PRODUCTION_CYCLE_COMPLETE", "message": "Ciclo concluído."}))

def run_backtest_mode():
    """Executa modo de backtest integrado"""
    logger.info(json.dumps({"event": "BACKTEST_START", "message": "Iniciando modo de backtest."}))
    
    # Implementação simplificada - pode ser expandida
    asset_basket = ["XAUUSD", "BTCUSD", "ETHUSD"]
    all_results = []
    
    for asset in asset_basket:
        logger.info(json.dumps({"event": "BACKTEST_SYMBOL", "symbol": asset}))
        # Lógica de backtest aqui (simplificada)
        # Por enquanto, apenas log
        all_results.append({
            "symbol": asset,
            "status": "completed"
        })
    
    # Salvar resultados
    results_file = "prometheus_backtest_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(json.dumps({"event": "BACKTEST_COMPLETE", "message": "Backtest concluído.", "results_file": results_file}))

def signal_handler(sig, frame):
    """Handler para desligamento graceful"""
    logger.info(json.dumps({"event": "SHUTDOWN_SIGNAL", "message": "Sinal de interrupção recebido. Desligando com segurança."}))
    mt5.shutdown()
    if os.path.exists(HEARTBEAT_FILE):
        os.remove(HEARTBEAT_FILE)
    sys.exit(0)

# --- BLOCO PRINCIPAL DE CONTROLE ---

if __name__ == "__main__":
    # Registrar handler para desligamento graceful
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(json.dumps({"event": "MASTER_START", "message": "="*80}))
    logger.info(json.dumps({"event": "MASTER_START", "message": "PROGRAMA MESTRE DE CONTROLE PROMETHEUS v4.0 INICIADO"}))
    logger.info(json.dumps({"event": "MASTER_START", "message": "="*80}))

    # Iniciar o Watchdog Obrigatório
    watchdog = PrometheusWatchdog(threading.get_ident())
    watchdog.start()
    logger.info(json.dumps({"event": "WATCHDOG_INITIALIZED", "message": "Watchdog iniciado."}))

    if not mt5.initialize():
        logger.critical(json.dumps({"event": "MT5_INIT_FAILED", "error": str(mt5.last_error())}))
        sys.exit(1)
    logger.info(json.dumps({"event": "MT5_INITIALIZED", "message": "MT5 inicializado com sucesso."}))

    # Verificar modo de operação via linha de comando
    mode = sys.argv[1] if len(sys.argv) > 1 else "production"
    logger.info(json.dumps({"event": "MODE_SELECTED", "mode": mode}))

    config = load_config()

    if mode == "backtest":
        run_backtest_mode()
    elif mode == "production":
        logger.info(json.dumps({"event": "PRODUCTION_MODE", "message": "Iniciando modo de produção autônomo."}))
        try:
            while True:
                run_production_cycle(config)
                cycle_sleep = config.get('EXECUTION_CYCLE_SECONDS', 15)
                time.sleep(cycle_sleep)
        except KeyboardInterrupt:
            logger.info(json.dumps({"event": "USER_INTERRUPT", "message": "Interrompido pelo usuário."}))
        except Exception as e:
            logger.critical(json.dumps({"event": "FATAL_ERROR", "error": str(e)}))
            import traceback
            logger.critical(json.dumps({"event": "FATAL_ERROR_TRACEBACK", "traceback": traceback.format_exc()}))
    else:
        logger.error(json.dumps({"event": "UNKNOWN_MODE", "mode": mode}))

    mt5.shutdown()
    if os.path.exists(HEARTBEAT_FILE):
        os.remove(HEARTBEAT_FILE)
    logger.info(json.dumps({"event": "MASTER_SHUTDOWN", "message": "PROGRAMA MESTRE FINALIZADO."}))

