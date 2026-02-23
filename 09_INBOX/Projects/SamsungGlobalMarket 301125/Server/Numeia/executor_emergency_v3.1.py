#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTOR DE EMERGÊNCIA PROMETHEUS v3.1
Protocolo de Emergência - Validação de Lucro em 72 Horas

Diretiva: Gerar Profit Factor > 1.3 em 48 horas com mínimo de 20 trades
Foco: XAUUSD (Ouro) exclusivamente
Estratégia: Multi-timeframe (H4/H1/M5) com confirmação de tendência
"""

import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, ValidationError

# --- CONFIGURAÇÃO E LOGGER ---
logger = logging.getLogger("numeia_emergency_v3.1")
logger.setLevel(logging.INFO)
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
    TRADING_SYMBOLS: List[str] = Field(default_factory=lambda: ["XAUUSD"])
    ORDER_VOLUME: float = Field(0.02)  # 2% do capital conforme diretiva
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

class EmergencySignal(BaseModel):
    symbol: str
    action: str  # 'buy' or 'sell'
    price: float
    sl: float
    tp: float
    volume: float
    confidence: float

# --- HELPER FUNCTIONS PARA ESTRATÉGIA ---

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

# --- FUNÇÃO PRINCIPAL DE GERAÇÃO DE SINAIS (SUBSTITUI generate_real_signals) ---

def generate_profit_signals_emergency(config: Config) -> List[EmergencySignal]:
    """
    Estratégia de emergência focada em validação de lucro.
    Multi-timeframe: H4 (tendência), H1 (confirmação), M5 (entrada)
    Retorna uma lista de sinais de alta probabilidade.
    """
    signals = []
    
    # Foco exclusivo em XAUUSD conforme Fase I
    symbol = 'XAUUSD'
    
    try:
        # Obter dados multi-timeframe
        h4_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 100)
        h1_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
        m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
        
        if h4_data is None or h1_data is None or m5_data is None or len(h4_data) < 50:
            logger.warning(json.dumps({"event": "insufficient_data", "symbol": symbol, 
                                     "h4_count": len(h4_data) if h4_data is not None else 0,
                                     "h1_count": len(h1_data) if h1_data is not None else 0,
                                     "m5_count": len(m5_data) if m5_data is not None else 0}))
            return []
        
        # Converter para DataFrame do pandas
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
            return []
        
        # Condições de alta probabilidade (LÓGICA EXATA conforme diretiva)
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
                return []
            
            entry_price = tick.ask
            point = symbol_info.point
            
            if point <= 0:
                logger.error(json.dumps({"event": "invalid_point", "symbol": symbol, "point": point}))
                return []
            
            # SL de 50 pontos (0.5%), TP de 100 pontos (1.0%) - Risk/Reward 1:2
            sl = entry_price - 50 * point
            tp = entry_price + 100 * point
            
            signal = EmergencySignal(
                symbol=symbol,
                action="buy",
                price=entry_price,
                sl=sl,
                tp=tp,
                volume=config.ORDER_VOLUME,  # 0.02 (2% do capital)
                confidence=0.85
            )
            
            signals.append(signal)
            logger.info(json.dumps({
                "event": "emergency_signal_generated",
                "symbol": symbol,
                "action": "buy",
                "entry_price": entry_price,
                "sl": sl,
                "tp": tp,
                "volume": config.ORDER_VOLUME,
                "confidence": 0.85,
                "strategy": "multi_timeframe_emergency"
            }))
        
        # (Opcional: Adicionar lógica para SELL se a tendência for baixista)
        # Por enquanto, focar apenas em compra para simplificar a validação
        
    except Exception as e:
        logger.error(json.dumps({"event": "signal_generation_error", "symbol": symbol, "error": str(e)}))
        import traceback
        logger.error(json.dumps({"event": "signal_generation_traceback", "traceback": traceback.format_exc()}))
    
    return signals

# --- FUNÇÕES DE CONEXÃO E ORDENS ---

def check_mt5_connection():
    """Verifica se a conexão com MT5 está ativa e saudável."""
    if not mt5.initialize():
        error = mt5.last_error()
        logger.critical(json.dumps({"event": "mt5_init_failed", "error": str(error)}))
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        logger.critical(json.dumps({"event": "mt5_account_info_failed", 
                                  "message": "Não foi possível obter informações da conta. MT5 pode estar desconectado."}))
        mt5.shutdown()
        return False
        
    logger.info(json.dumps({"event": "mt5_connection_verified", 
                          "account": account_info.login, 
                          "server": account_info.server,
                          "balance": account_info.balance}))
    return True

def send_order(signal: EmergencySignal, config: Config) -> Optional[Dict]:
    """
    Envia ordem usando SL/TP da estratégia de emergência.
    Retorna dict com informações da ordem ou None se falhar.
    """
    symbol_info = mt5.symbol_info(signal.symbol)
    if symbol_info is None:
        logger.error(json.dumps({"event": "symbol_not_found", "symbol": signal.symbol}))
        return None

    if not symbol_info.visible:
        logger.warning(json.dumps({"event": "symbol_not_visible", "symbol": signal.symbol}))
        return None
    
    # Obtém tick atual
    tick = mt5.symbol_info_tick(signal.symbol)
    if tick is None:
        logger.error(json.dumps({"event": "tick_unavailable", "symbol": signal.symbol}))
        return None
    
    # Usa preço atual do tick
    if signal.action == "buy":
        price = tick.ask
    else:
        price = tick.bid
    
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": signal.symbol,
        "volume": signal.volume,
        "type": mt5.ORDER_TYPE_BUY if signal.action == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": signal.sl,
        "tp": signal.tp,
        "deviation": 10,
        "magic": 789012,  # Magic diferente para identificar ordens de emergência
        "comment": "Prometheus Emergency v3.1",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(order_request)
    if result is None:
        error = mt5.last_error()
        logger.error(json.dumps({"event": "order_send_failed", "symbol": signal.symbol, "error": str(error)}))
        return None
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        # NOVO LOGGING: ORDER_EXECUTED conforme diretiva
        order_data = {
            "event": "ORDER_EXECUTED",
            "symbol": signal.symbol,
            "action": signal.action,
            "volume": signal.volume,
            "entry_price": result.price,
            "sl": signal.sl,
            "tp": signal.tp,
            "order_id": result.order,
            "deal_id": result.deal,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(json.dumps(order_data))
        return order_data
    else:
        logger.error(json.dumps({
            "event": "order_failed",
            "symbol": signal.symbol,
            "retcode": result.retcode,
            "comment": result.comment
        }))
        return None

def monitor_closed_orders():
    """
    Monitora ordens fechadas e loga ORDER_CLOSED conforme diretiva.
    Esta função deve ser chamada periodicamente para verificar ordens fechadas.
    """
    try:
        # Busca ordens fechadas nas últimas 24 horas
        from_date = datetime.now().timestamp() - 86400
        deals = mt5.history_deals_get(from_date, datetime.now().timestamp())
        
        if deals is None:
            return
        
        # Filtra apenas ordens do nosso magic number
        our_deals = [d for d in deals if d.magic == 789012 and d.entry == mt5.DEAL_ENTRY_OUT]
        
        for deal in our_deals:
            # Loga ORDER_CLOSED
            order_data = {
                "event": "ORDER_CLOSED",
                "order_id": deal.order,
                "deal_id": deal.deal,
                "symbol": deal.symbol,
                "profit": deal.profit,
                "close_price": deal.price,
                "reason": "TP" if deal.profit > 0 else "SL",
                "volume": deal.volume,
                "timestamp": datetime.fromtimestamp(deal.time).isoformat()
            }
            logger.info(json.dumps(order_data))
            
    except Exception as e:
        logger.error(json.dumps({"event": "monitor_closed_orders_error", "error": str(e)}))

def update_heartbeat():
    """Atualiza o timestamp do arquivo de heartbeat."""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(json.dumps({"event": "heartbeat_update_failed", "error": str(e)}))

def signal_handler(sig, frame):
    """Permite desligamento gracefully com Ctrl+C."""
    logger.info(json.dumps({"event": "emergency_executor_shutdown", "version": "3.1"}))
    mt5.shutdown()
    if os.path.exists(HEARTBEAT_FILE):
        os.remove(HEARTBEAT_FILE)
    sys.exit(0)

# --- LOOP PRINCIPAL ---

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(json.dumps({"event": "emergency_executor_v3.1_started", 
                          "version": "3.1",
                          "protocol": "PROMETHEUS_EMERGENCY",
                          "objective": "Profit Factor > 1.3 in 48h",
                          "symbol": "XAUUSD"}))
    
    if not check_mt5_connection():
        sys.exit(1)
        
    config = load_config()
    logger.info(json.dumps({"event": "config_loaded", "config": config.model_dump()}))
    
    # Verifica se símbolo está disponível
    if "XAUUSD" not in config.TRADING_SYMBOLS:
        logger.critical(json.dumps({"event": "xauusd_not_in_config", 
                                  "message": "XAUUSD deve estar em TRADING_SYMBOLS"}))
        sys.exit(1)
    
    last_monitor_time = time.time()
    
    try:
        while True:
            start_cycle_time = time.time()
            update_heartbeat()
            
            # Verificação de conexão a cada ciclo
            terminal_info = mt5.terminal_info()
            if terminal_info is None or not terminal_info.connected:
                logger.error(json.dumps({"event": "mt5_disconnected", 
                                      "message": "MT5 desconectado! Tentando restabelecer..."}))
                if not check_mt5_connection():
                    logger.error(json.dumps({"event": "mt5_reconnect_failed", 
                                          "message": "Falha ao reconectar. Aguardando próximo ciclo."}))
                    time.sleep(config.EXECUTION_CYCLE_SECONDS)
                    continue
            
            # Gera sinais usando estratégia de emergência
            signals = generate_profit_signals_emergency(config)
            
            if signals:
                logger.info(json.dumps({"event": "emergency_signals_ready", 
                                      "count": len(signals), 
                                      "symbols": [s.symbol for s in signals]}))
                
                for signal in signals:
                    attempts = 0
                    success = False
                    while attempts < config.MAX_ORDER_ATTEMPTS and not success:
                        order_result = send_order(signal, config)
                        if order_result is not None:
                            success = True
                        else:
                            attempts += 1
                            if attempts < config.MAX_ORDER_ATTEMPTS:
                                time.sleep(2)
                    
                    if not success:
                        logger.error(json.dumps({
                            "event": "order_failed_after_attempts",
                            "symbol": signal.symbol,
                            "action": signal.action,
                            "attempts": config.MAX_ORDER_ATTEMPTS
                        }))
            else:
                logger.info(json.dumps({"event": "no_emergency_signals", "cycle": "current"}))
            
            # Monitora ordens fechadas a cada 30 segundos
            if time.time() - last_monitor_time > 30:
                monitor_closed_orders()
                last_monitor_time = time.time()
            
            cycle_duration = time.time() - start_cycle_time
            sleep_time = max(0, config.EXECUTION_CYCLE_SECONDS - cycle_duration)
            logger.info(json.dumps({"event": "cycle_completed", 
                                  "duration": cycle_duration, 
                                  "sleep_time": sleep_time}))
            time.sleep(sleep_time)

    except Exception as e:
        logger.critical(json.dumps({"event": "fatal_error", "error": str(e)}))
        import traceback
        logger.critical(json.dumps({"event": "fatal_error_traceback", "traceback": traceback.format_exc()}))
    finally:
        mt5.shutdown()
        if os.path.exists(HEARTBEAT_FILE):
            os.remove(HEARTBEAT_FILE)
        logger.info(json.dumps({"event": "emergency_executor_shutdown_complete"}))

