#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA MESTRE DE CONTROLE PROMETHEUS v5.0
Sistema Sincronizado com Realidade do Mercado - Inteligência Adaptativa e Risco Dinâmico

Diretiva: Sincronizar estratégia com condições reais de mercado e gerenciar risco de forma adaptativa.
- Market Intelligence: Detecção em tempo real de ativos negociáveis
- Estratégia Adaptativa: Buy/Sell baseado em tendência e condições de mercado
- Risco Dinâmico: SL/TP baseado em ATR (Average True Range)
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

# Importar módulo de Market Intelligence
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("market_intelligence_v5_0", "market_intelligence_v5.0.py")
    market_intel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(market_intel)
    get_real_time_market_state = market_intel.get_real_time_market_state
    filter_tradable_assets = market_intel.filter_tradable_assets
    get_market_status = market_intel.get_market_status
except Exception as e:
    # Fallback: definir funções inline se módulo não encontrado
    def get_real_time_market_state(symbols):
        if not mt5.initialize():
            return []
        
        # Carregar limites de spread do config.json
        max_spread_config = {}
        try:
            import json
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                max_spread_config = config.get('MAX_SPREAD_PIPS', {})
        except:
            pass
        
        market_state = []
        for symbol in symbols:
            try:
                if not mt5.symbol_select(symbol, True):
                    continue
                tick = mt5.symbol_info_tick(symbol)
                symbol_info = mt5.symbol_info(symbol)
                if tick is None or symbol_info is None:
                    continue
                point = symbol_info.point
                if point <= 0:
                    continue
                
                spread_points = (tick.ask - tick.bid) / point if point > 0 else float('inf')
                tick_volume = getattr(tick, 'volume', 0)
                
                # Determinar max_spread baseado no símbolo (usar config.json se disponível)
                max_spread = max_spread_config.get(symbol, 
                    max_spread_config.get('default', 
                        2000 if 'BTC' in symbol or 'ETH' in symbol else
                        1500 if 'CRYPTO' in symbol.upper() else
                        500 if 'XAU' in symbol or 'GOLD' in symbol else
                        100 if 'US' in symbol or 'SPX' in symbol or 'NAS' in symbol else
                        50  # Default mais permissivo para forex
                    ))
                
                # Critérios MUITO mais permissivos: apenas verificar se spread não é infinito
                # Volume mínimo removido (muitos ativos não reportam volume corretamente)
                is_tradable = spread_points < max_spread and spread_points != float('inf')
                
                # Classificar liquidez (mais permissivo)
                if not is_tradable:
                    status = 'CLOSED'
                elif spread_points < (max_spread * 0.3):  # 30% do máximo = alta liquidez
                    status = 'LIQUIDITY_HIGH'
                elif spread_points < (max_spread * 0.7):  # 70% do máximo = liquidez média
                    status = 'LIQUIDITY_MEDIUM'
                else:
                    status = 'LIQUIDITY_LOW'
                
                market_state.append({
                    'symbol': symbol, 
                    'is_tradable': is_tradable, 
                    'status': status,
                    'spread_points': spread_points, 
                    'tick_volume': tick_volume
                })
            except Exception as e:
                continue
        return market_state
    
    def filter_tradable_assets(market_state):
        return [asset['symbol'] for asset in market_state if asset['is_tradable']]
    
    def get_market_status(symbol, market_state):
        for asset in market_state:
            if asset['symbol'] == symbol:
                return asset
        return None

# --- CONFIGURAÇÕES GLOBAIS ---
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")
LOG_FILE = "prometheus_master_log.jsonl"
HEARTBEAT_FILE = "prometheus_heartbeat.tmp"
STATE_FILE = "prometheus_state.json"
TRADEABLE_ASSETS_FILE = "TRADEABLE_ASSETS.json"

# --- CONFIGURAÇÕES DE RISCO DINÂMICO ---
RISK_CONFIG = {
    "risk_per_trade_percent": 0.01,  # 1% de risco por trade
    "max_daily_drawdown_percent": 0.03,  # 3% de drawdown diário máximo
    "max_open_positions": 5,  # Máximo de posições abertas simultâneas
    "atr_period": 14,  # Período para cálculo do ATR
    "atr_sl_multiplier": 2.0,  # SL = 2x ATR
    "atr_tp_multiplier": 4.0,  # TP = 4x ATR (Risk/Reward 1:2)
    "min_sl_points": 100,  # SL mínimo em pontos (para evitar "Invalid stops")
    "min_tp_points": 200  # TP mínimo em pontos
}

# Configuração do Logger
logger = logging.getLogger("PrometheusMaster")
logger.setLevel(logging.INFO)
logger.handlers.clear()
handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
formatter = logging.Formatter('{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}')
handler.setFormatter(formatter)
logger.addHandler(handler)

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

def calculate_atr(data: pd.DataFrame, period: int = 14) -> float:
    """Calcula o Average True Range (ATR)"""
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()
    return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.0

def calculate_position_size(symbol: str, stop_loss_points: float) -> float:
    """Calcula o volume da posição baseado no risco percentual da conta."""
    try:
        account_info = mt5.account_info()
        if account_info is None:
            return 0.01  # Fallback seguro
        
        balance = account_info.balance
        risk_amount = balance * RISK_CONFIG["risk_per_trade_percent"]
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.01
        
        point = symbol_info.point
        if point <= 0:
            return 0.01
        
        tick_value = symbol_info.trade_tick_value
        if tick_value is None or tick_value == 0:
            tick_value = point * symbol_info.trade_contract_size
        
        if tick_value == 0:
            return 0.01
        
        # Calcular volume baseado no risco
        volume = risk_amount / (stop_loss_points * tick_value)
        
        # Ajustar volume para lotes padrão do broker
        if symbol_info.volume_min > 0:
            volume = round(volume / symbol_info.volume_min) * symbol_info.volume_min
        else:
            volume = round(volume, 2)
        
        # Garantir volume mínimo e máximo
        volume = max(volume, symbol_info.volume_min if symbol_info.volume_min > 0 else 0.01)
        if symbol_info.volume_max > 0:
            volume = min(volume, symbol_info.volume_max)
        
        logger.info(json.dumps({
            "event": "POSITION_SIZE_CALCULATED",
            "symbol": symbol,
            "volume": volume,
            "risk_amount": risk_amount,
            "stop_loss_points": stop_loss_points,
            "balance": balance
        }))
        
        return volume
    except Exception as e:
        logger.error(json.dumps({"event": "position_size_calculation_error", "symbol": symbol, "error": str(e)}))
        return 0.01  # Fallback seguro

def calculate_dynamic_sl_tp(symbol: str, entry_price: float, action: str) -> Dict:
    """Calcula SL/TP dinâmicos baseados em ATR"""
    try:
        # Obter dados M15 para cálculo de ATR
        m15_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
        if m15_data is None or len(m15_data) < RISK_CONFIG["atr_period"]:
            # Fallback: usar spread mínimo
            symbol_info = mt5.symbol_info(symbol)
            point = symbol_info.point if symbol_info else 0.01
            sl_points = RISK_CONFIG["min_sl_points"]
            tp_points = RISK_CONFIG["min_tp_points"]
        else:
            m15_df = pd.DataFrame(m15_data)
            atr = calculate_atr(m15_df, RISK_CONFIG["atr_period"])
            
            if atr <= 0 or pd.isna(atr):
                # Fallback
                symbol_info = mt5.symbol_info(symbol)
                point = symbol_info.point if symbol_info else 0.01
                sl_points = RISK_CONFIG["min_sl_points"]
                tp_points = RISK_CONFIG["min_tp_points"]
            else:
                symbol_info = mt5.symbol_info(symbol)
                point = symbol_info.point if symbol_info else 0.01
                
                # Calcular SL/TP em pontos
                sl_points = max(atr * RISK_CONFIG["atr_sl_multiplier"] / point, RISK_CONFIG["min_sl_points"])
                tp_points = max(atr * RISK_CONFIG["atr_tp_multiplier"] / point, RISK_CONFIG["min_tp_points"])
        
        # Aplicar SL/TP baseado na ação
        if action == "buy":
            sl = entry_price - (sl_points * point)
            tp = entry_price + (tp_points * point)
        else:  # sell
            sl = entry_price + (sl_points * point)
            tp = entry_price - (tp_points * point)
        
        return {
            "sl": sl,
            "tp": tp,
            "sl_points": sl_points,
            "tp_points": tp_points,
            "atr": atr if 'atr' in locals() else 0.0
        }
    except Exception as e:
        logger.error(json.dumps({"event": "dynamic_sl_tp_error", "symbol": symbol, "error": str(e)}))
        # Fallback seguro
        symbol_info = mt5.symbol_info(symbol)
        point = symbol_info.point if symbol_info else 0.01
        if action == "buy":
            return {
                "sl": entry_price - (RISK_CONFIG["min_sl_points"] * point),
                "tp": entry_price + (RISK_CONFIG["min_tp_points"] * point),
                "sl_points": RISK_CONFIG["min_sl_points"],
                "tp_points": RISK_CONFIG["min_tp_points"],
                "atr": 0.0
            }
        else:
            return {
                "sl": entry_price + (RISK_CONFIG["min_sl_points"] * point),
                "tp": entry_price - (RISK_CONFIG["min_tp_points"] * point),
                "sl_points": RISK_CONFIG["min_sl_points"],
                "tp_points": RISK_CONFIG["min_tp_points"],
                "atr": 0.0
            }

def check_global_risk() -> bool:
    """Verifica se o sistema atingiu os limites de risco globais"""
    try:
        positions = mt5.positions_get()
        if positions is None:
            positions = []
        
        if not positions:
            return True
        
        account_info = mt5.account_info()
        if account_info is None:
            return False
        
        # Verificar drawdown diário
        total_profit = sum(p.profit for p in positions)
        daily_drawdown = (account_info.balance + account_info.profit) - (account_info.balance + total_profit)
        
        if daily_drawdown < -account_info.balance * RISK_CONFIG["max_daily_drawdown_percent"]:
            logger.critical(json.dumps({"event": "RISK_LIMIT_HIT", "reason": "Daily Drawdown", "drawdown": daily_drawdown}))
            return False
        
        # Verificar número de posições abertas
        if len(positions) >= RISK_CONFIG["max_open_positions"]:
            logger.warning(json.dumps({"event": "RISK_LIMIT_HIT", "reason": "Max Open Positions", "count": len(positions)}))
            return False
        
        return True
    except Exception as e:
        logger.error(json.dumps({"event": "global_risk_check_error", "error": str(e)}))
        return False

def has_open_position(symbol: str) -> bool:
    """Verifica se já existe posição aberta para o símbolo"""
    try:
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return False
        return len(positions) > 0
    except:
        return False

# --- MÓDULO DE GERAÇÃO DE SINAIS ADAPTATIVA ---

def generate_signals_adaptive(config: Dict, tradeable_symbols: List[str], market_state: List[Dict]) -> List[Dict]:
    """Gera sinais de trading com estratégia adaptativa e filtro de liquidez"""
    signals = []
    
    # Verificar risco global antes de gerar sinais
    if not check_global_risk():
        logger.warning(json.dumps({"event": "GLOBAL_RISK_LIMIT", "message": "Limite de risco global atingido. Não gerando novos sinais."}))
        return []
    
    for symbol in tradeable_symbols:
        # Verificar se já existe posição aberta
        if has_open_position(symbol):
            logger.debug(json.dumps({"event": "position_already_open", "symbol": symbol}))
            continue
        
        # Verificar status de mercado em tempo real
        asset_status = get_market_status(symbol, market_state)
        if asset_status is None:
            continue
        
        # BLOQUEAR apenas se não estiver negociável (permitir LIQUIDITY_LOW e MEDIUM também)
        if not asset_status['is_tradable']:
            logger.debug(json.dumps({
                "event": "asset_not_tradable",
                "symbol": symbol,
                "status": asset_status['status'],
                "spread_points": asset_status.get('spread_points', 0)
            }))
            continue
        
        # Operar em qualquer nível de liquidez (HIGH, MEDIUM, LOW) - apenas não operar se CLOSED
        if asset_status['status'] == 'CLOSED':
            continue
        
        try:
            # Obter dados multi-timeframe
            h4_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 100)
            h1_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
            m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
            
            if h4_data is None or h1_data is None or m5_data is None or len(h4_data) < 50:
                logger.warning(json.dumps({"event": "insufficient_data", "symbol": symbol}))
                continue
            
            h4_df = pd.DataFrame(h4_data)
            h1_df = pd.DataFrame(h1_data)
            m5_df = pd.DataFrame(m5_data)
            
            h4_ma20 = calculate_ma(h4_df, 20)
            h4_ma50 = calculate_ma(h4_df, 50)
            h1_ma20 = calculate_ma(h1_df, 20)
            h1_ma50 = calculate_ma(h1_df, 50)
            m5_ma20 = calculate_ma(m5_df, 20)
            m5_rsi = calculate_rsi(m5_df)
            m5_volume_avg = calculate_volume_average(m5_df)
            
            if pd.isna(h4_ma20) or pd.isna(h4_ma50) or pd.isna(h1_ma20) or pd.isna(h1_ma50) or pd.isna(m5_ma20) or pd.isna(m5_rsi):
                logger.warning(json.dumps({"event": "indicators_not_ready", "symbol": symbol}))
                continue
            
            # Análise de tendência
            h4_trend_up = h4_ma20 > h4_ma50
            h1_confirmation_up = h1_ma20 > h1_ma50
            m5_entry_up = m5_df['close'].iloc[-1] > m5_ma20
            
            h4_trend_down = h4_ma20 < h4_ma50
            h1_confirmation_down = h1_ma20 < h1_ma50
            m5_entry_down = m5_df['close'].iloc[-1] < m5_ma20
            
            # Filtros de qualidade
            rsi_ok = 30 < m5_rsi < 70
            volume_ok = m5_df['tick_volume'].iloc[-1] > m5_volume_avg * 0.8
            
            tick = mt5.symbol_info_tick(symbol)
            symbol_info = mt5.symbol_info(symbol)
            
            if tick is None or symbol_info is None:
                continue
            
            point = symbol_info.point
            if point <= 0:
                continue
            
            # SINAL DE COMPRA (tendência de alta)
            if h4_trend_up and h1_confirmation_up and m5_entry_up and rsi_ok and volume_ok:
                entry_price = tick.ask
                sl_tp = calculate_dynamic_sl_tp(symbol, entry_price, "buy")
                volume = calculate_position_size(symbol, sl_tp['sl_points'])
                
                signal = {
                    "symbol": symbol,
                    "action": "buy",
                    "price": entry_price,
                    "sl": sl_tp['sl'],
                    "tp": sl_tp['tp'],
                    "volume": volume,
                    "atr": sl_tp['atr'],
                    "sl_points": sl_tp['sl_points'],
                    "tp_points": sl_tp['tp_points'],
                    "confidence": 0.85,
                    "strategy": "adaptive_multi_timeframe_atr",
                    "market_status": asset_status['status']
                }
                signals.append(signal)
                logger.info(json.dumps({
                    "event": "BUY_SIGNAL_GENERATED",
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "sl": sl_tp['sl'],
                    "tp": sl_tp['tp'],
                    "atr": sl_tp['atr'],
                    "volume": volume
                }))
            
            # SINAL DE VENDA (tendência de baixa)
            elif h4_trend_down and h1_confirmation_down and m5_entry_down and rsi_ok and volume_ok:
                entry_price = tick.bid
                sl_tp = calculate_dynamic_sl_tp(symbol, entry_price, "sell")
                volume = calculate_position_size(symbol, sl_tp['sl_points'])
                
                signal = {
                    "symbol": symbol,
                    "action": "sell",
                    "price": entry_price,
                    "sl": sl_tp['sl'],
                    "tp": sl_tp['tp'],
                    "volume": volume,
                    "atr": sl_tp['atr'],
                    "sl_points": sl_tp['sl_points'],
                    "tp_points": sl_tp['tp_points'],
                    "confidence": 0.85,
                    "strategy": "adaptive_multi_timeframe_atr",
                    "market_status": asset_status['status']
                }
                signals.append(signal)
                logger.info(json.dumps({
                    "event": "SELL_SIGNAL_GENERATED",
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "sl": sl_tp['sl'],
                    "tp": sl_tp['tp'],
                    "atr": sl_tp['atr'],
                    "volume": volume
                }))
        
        except Exception as e:
            logger.error(json.dumps({"event": "signal_generation_error", "symbol": symbol, "error": str(e)}))
            import traceback
            logger.error(json.dumps({"event": "signal_generation_traceback", "traceback": traceback.format_exc()}))
    
    return signals

# --- MÓDULO DE EXECUÇÃO DE ORDENS ---

def send_order(signal: Dict, config: Dict) -> Optional[Dict]:
    """Envia ordem usando SL/TP dinâmicos"""
    symbol = signal['symbol']
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(json.dumps({"event": "symbol_not_found", "symbol": symbol}))
        return None

    if not symbol_info.visible:
        logger.warning(json.dumps({"event": "symbol_not_visible", "symbol": symbol}))
        return None
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(json.dumps({"event": "tick_unavailable", "symbol": symbol}))
        return None
    
    if signal['action'] == "buy":
        price = tick.ask
    else:
        price = tick.bid
    
    # Normalizar SL/TP para garantir que estão corretos
    point = symbol_info.point
    sl = round(signal['sl'] / point) * point
    tp = round(signal['tp'] / point) * point
    
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": signal['volume'],
        "type": mt5.ORDER_TYPE_BUY if signal['action'] == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 789013,
        "comment": "Prometheus v5.0 ATR",
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
            "sl": sl,
            "tp": tp,
            "atr": signal.get('atr', 0),
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

# --- WATCHDOG OBRIGATÓRIO ---

class PrometheusWatchdog(threading.Thread):
    def __init__(self, main_thread_id):
        super().__init__(daemon=True)
        self.main_thread_id = main_thread_id
        self.last_heartbeat_time = time.time()
        self.running = True

    def run(self):
        logger.info(json.dumps({"event": "WATCHDOG_STARTED", "message": "Iniciando monitoramento do sistema."}))
        main_thread = threading.main_thread()
        while self.running:
            time.sleep(30)
            
            try:
                if not main_thread.is_alive():
                    logger.critical(json.dumps({"event": "WATCHDOG_CRITICAL", "message": "Thread principal morreu. Desligando sistema."}))
                    self.shutdown_system()
                    break
            except AttributeError:
                pass

            try:
                if os.path.exists(HEARTBEAT_FILE):
                    last_mod = os.path.getmtime(HEARTBEAT_FILE)
                    if last_mod > self.last_heartbeat_time:
                        self.last_heartbeat_time = last_mod
                    else:
                        if time.time() - self.last_heartbeat_time > 90:
                            logger.critical(json.dumps({"event": "WATCHDOG_CRITICAL", "message": "Heartbeat parou. Sistema travado. Desligando."}))
                            self.shutdown_system()
                            break
                else:
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
        os._exit(1)

# --- FUNÇÕES PRINCIPAIS DO SISTEMA ---

def load_config() -> Dict:
    """Carrega e valida config.json"""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        
        if 'TRADING_SYMBOLS' not in config or not config['TRADING_SYMBOLS']:
            config['TRADING_SYMBOLS'] = []
        
        logger.info(json.dumps({"event": "config_loaded", "config": config}))
        return config
    except FileNotFoundError:
        logger.warning(json.dumps({"event": "config_not_found", "path": CONFIG_PATH, "message": "Usando configuração padrão."}))
        return {
            "TRADING_SYMBOLS": [],
            "ORDER_VOLUME": 0.02,
            "EXECUTION_CYCLE_SECONDS": 15,
            "MAX_ORDER_ATTEMPTS": 3
        }
    except Exception as e:
        logger.error(json.dumps({"event": "config_load_error", "error": str(e)}))
        return {
            "TRADING_SYMBOLS": [],
            "ORDER_VOLUME": 0.02,
            "EXECUTION_CYCLE_SECONDS": 15,
            "MAX_ORDER_ATTEMPTS": 3
        }

def discover_all_market_watch_assets() -> List[str]:
    """Descobre TODOS os ativos do Market Watch do MT5 - SEM LIMITES"""
    if not mt5.initialize():
        logger.error(json.dumps({"event": "MT5_INIT_FAILED_DISCOVERY", "error": "Falha ao inicializar MT5 para descoberta"}))
        return []
    
    all_symbols_info = mt5.symbols_get()
    if all_symbols_info is None:
        logger.error(json.dumps({"event": "SYMBOLS_GET_FAILED", "error": "Falha ao obter símbolos do MT5"}))
        return []
    
    symbols = [s.name for s in all_symbols_info]
    logger.info(json.dumps({
        "event": "MARKET_WATCH_DISCOVERED",
        "count": len(symbols),
        "message": f"TODOS os {len(symbols)} ativos do Market Watch serão testados e operados"
    }))
    return symbols

def load_tradeable_assets() -> List[str]:
    """Carrega TODOS os ativos do Market Watch - SEM LIMITES DE QUANTIDADE"""
    # PRIORIDADE 1: Descobrir TODOS os ativos do Market Watch
    try:
        all_assets = discover_all_market_watch_assets()
        if all_assets and len(all_assets) > 0:
            logger.info(json.dumps({
                "event": "USING_ALL_MARKET_WATCH_ASSETS",
                "count": len(all_assets),
                "message": f"✅ Sistema configurado para operar em TODOS os {len(all_assets)} ativos do Market Watch (SEM LIMITES)"
            }))
            return all_assets
    except Exception as e:
        logger.error(json.dumps({"event": "MARKET_WATCH_DISCOVERY_ERROR", "error": str(e)}))
    
    # FALLBACK 1: Tentar TRADEABLE_ASSETS.json
    try:
        with open(TRADEABLE_ASSETS_FILE, 'r') as f:
            assets = json.load(f)
        symbols = [item['symbol'] for item in assets]
        if symbols:
            logger.info(json.dumps({"event": "tradeable_assets_loaded", "count": len(symbols), "symbols": symbols}))
            return symbols
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(json.dumps({"event": "tradeable_assets_load_error", "error": str(e)}))
    
    # FALLBACK 2: config.json
    try:
        config = load_config()
        symbols = config.get('TRADING_SYMBOLS', [])
        if symbols and len(symbols) > 0:
            logger.info(json.dumps({"event": "using_config_symbols_fallback", "count": len(symbols), "symbols": symbols}))
            return symbols
    except:
        pass
    
    # Último fallback
    default_symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
    logger.info(json.dumps({"event": "using_default_symbols", "symbols": default_symbols}))
    return default_symbols

def update_heartbeat():
    """Atualiza o arquivo de heartbeat"""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(json.dumps({"event": "heartbeat_update_failed", "error": str(e)}))

def run_production_cycle(config: Dict, tradeable_symbols: List[str]):
    """Executa um ciclo de produção com Market Intelligence e Risco Dinâmico - TODOS OS ATIVOS"""
    logger.info(json.dumps({
        "event": "PRODUCTION_CYCLE_START",
        "message": "Iniciando ciclo de execução.",
        "total_assets": len(tradeable_symbols),
        "mode": "ALL_MARKET_WATCH_ASSETS"
    }))
    
    terminal_info = mt5.terminal_info()
    if terminal_info is None or not terminal_info.connected:
        logger.error(json.dumps({"event": "mt5_disconnected", "message": "MT5 desconectado! Tentando restabelecer..."}))
        if not mt5.initialize():
            logger.error(json.dumps({"event": "mt5_reconnect_failed", "message": "Falha ao reconectar."}))
            return
    
    # Obter estado de mercado em tempo real para TODOS os símbolos
    # O Market Intelligence filtra automaticamente por spread/liquidez
    market_state = get_real_time_market_state(tradeable_symbols)
    tradable_now = filter_tradable_assets(market_state)
    
    if not tradable_now:
        logger.warning(json.dumps({
            "event": "NO_TRADABLE_ASSETS",
            "message": "Nenhum ativo negociável no momento (spread/liquidez).",
            "total_checked": len(tradeable_symbols)
        }))
        update_heartbeat()
        return
    
    logger.info(json.dumps({
        "event": "MARKET_INTELLIGENCE_UPDATE",
        "total_symbols_checked": len(tradeable_symbols),
        "tradable_now": len(tradable_now),
        "filtered_out": len(tradeable_symbols) - len(tradable_now),
        "message": f"Market Intelligence: {len(tradable_now)} de {len(tradeable_symbols)} ativos negociáveis agora"
    }))
    
    # Gerar sinais com estratégia adaptativa
    signals = generate_signals_adaptive(config, tradable_now, market_state)
    if not signals:
        logger.info(json.dumps({"event": "PRODUCTION_NO_SIGNALS", "message": "Nenhum sinal gerado neste ciclo."}))
        update_heartbeat()
        return
    
    logger.info(json.dumps({"event": "PRODUCTION_SIGNALS_GENERATED", "count": len(signals), "symbols": [s['symbol'] for s in signals]}))
    
    for signal in signals:
        # Verificar risco novamente antes de cada ordem
        if not check_global_risk():
            logger.warning(json.dumps({"event": "RISK_LIMIT_BEFORE_ORDER", "symbol": signal['symbol']}))
            break
        
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

def signal_handler(sig, frame):
    """Handler para desligamento graceful"""
    logger.info(json.dumps({"event": "SHUTDOWN_SIGNAL", "message": "Sinal de interrupção recebido. Desligando com segurança."}))
    mt5.shutdown()
    if os.path.exists(HEARTBEAT_FILE):
        os.remove(HEARTBEAT_FILE)
    sys.exit(0)

# --- BLOCO PRINCIPAL DE CONTROLE ---

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception as e:
        print(f"Erro ao configurar handlers de sinal: {e}")

    # Configurar output para console também
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    try:
        logger.info(json.dumps({"event": "MASTER_START", "message": "="*80}))
        logger.info(json.dumps({"event": "MASTER_START", "message": "PROGRAMA MESTRE DE CONTROLE PROMETHEUS v5.0 INICIADO"}))
        logger.info(json.dumps({"event": "MASTER_START", "message": "Sistema Sincronizado com Realidade do Mercado"}))
        logger.info(json.dumps({"event": "MASTER_START", "message": "="*80}))
    except Exception as e:
        print(f"Erro ao inicializar logger: {e}")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger("PrometheusMaster")

    mode = sys.argv[1] if len(sys.argv) > 1 else "production"
    print(f"Modo selecionado: {mode}")
    logger.info(json.dumps({"event": "MODE_SELECTED", "mode": mode}))

    if mode == "production":
        # Iniciar watchdog
        watchdog = PrometheusWatchdog(threading.get_ident())
        watchdog.start()
        logger.info(json.dumps({"event": "WATCHDOG_INITIALIZED", "message": "Watchdog iniciado."}))

        if not mt5.initialize():
            logger.critical(json.dumps({"event": "MT5_INIT_FAILED", "error": str(mt5.last_error())}))
            sys.exit(1)
        logger.info(json.dumps({"event": "MT5_INITIALIZED", "message": "MT5 inicializado com sucesso."}))

        config = load_config()
        
        # Carregar ativos negociáveis
        tradeable_symbols = load_tradeable_assets()
        if not tradeable_symbols:
            print("\n" + "="*80)
            print("ERRO: Nenhum ativo negociável encontrado!")
            print("="*80)
            print("\nExecute discovery primeiro ou configure TRADING_SYMBOLS no config.json")
            logger.critical(json.dumps({"event": "PRODUCTION_FAILED", "message": "Nenhum ativo negociável encontrado."}))
            print("\nPressione ENTER para sair...")
            input()
            sys.exit(1)
        
        logger.info(json.dumps({"event": "PRODUCTION_MODE", "message": "Iniciando modo de produção autônomo.", "symbols": tradeable_symbols}))
        
        try:
            while True:
                run_production_cycle(config, tradeable_symbols)
                cycle_sleep = config.get('EXECUTION_CYCLE_SECONDS', 15)
                time.sleep(cycle_sleep)
        except KeyboardInterrupt:
            logger.info(json.dumps({"event": "USER_INTERRUPT", "message": "Interrompido pelo usuário."}))
        except Exception as e:
            logger.critical(json.dumps({"event": "FATAL_ERROR", "error": str(e)}))
            import traceback
            logger.critical(json.dumps({"event": "FATAL_ERROR_TRACEBACK", "traceback": traceback.format_exc()}))
    else:
        print(f"\nERRO: Modo desconhecido: {mode}")
        print("Modos disponíveis: 'production'")
        print("\nExemplo de uso:")
        print("  python prometheus_master_control_v5.0.py production")
        logger.error(json.dumps({"event": "UNKNOWN_MODE", "mode": mode}))
        print("\nPressione ENTER para sair...")
        input()
        sys.exit(1)

    try:
        if mt5.terminal_info() is not None:
            mt5.shutdown()
    except:
        pass
    
    if os.path.exists(HEARTBEAT_FILE):
        try:
            os.remove(HEARTBEAT_FILE)
        except:
            pass
    
    try:
        logger.info(json.dumps({"event": "MASTER_SHUTDOWN", "message": "PROGRAMA MESTRE FINALIZADO."}))
    except:
        print("Programa finalizado.")

