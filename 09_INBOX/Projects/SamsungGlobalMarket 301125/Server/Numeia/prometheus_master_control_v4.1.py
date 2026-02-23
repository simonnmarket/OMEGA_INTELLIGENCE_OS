#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA MESTRE DE CONTROLE PROMETHEUS v4.1
Sistema Autônomo de Descoberta e Execução - Operação em Todo o Market Watch

Diretiva: Descobrir e operar em todos os ativos viáveis do Market Watch de forma autônoma.
Fase I: Descoberta, Filtragem e Triagem de Ativos
Fase II: Execução Autônoma nos Top Ativos Ranqueados
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

# --- CONFIGURAÇÕES GLOBAIS ---
_BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = str(_BASE_DIR / "config.json")
LOG_FILE = "prometheus_master_log.jsonl"
HEARTBEAT_FILE = "prometheus_heartbeat.tmp"
STATE_FILE = "prometheus_state.json"
TRADEABLE_ASSETS_FILE = "TRADEABLE_ASSETS.json"

# --- CONFIGURAÇÕES DE DESCOBERTA E FILTRAGEM ---
DISCOVERY_CONFIG = {
    "max_spread_points": 500,  # Aumentado para 500 pontos (mais permissivo)
    "min_tick_volume": 0,       # Removido filtro de volume mínimo
    "triage_data_days": 30,    # Usar 30 dias para o backtest de triagem (rápido)
    "top_assets_to_trade": 10  # Operar apenas nos top 10 ativos ranqueados
}

# --- ESTRATÉGIA SELETIVA FIXA (BASEADA NO RELATÓRIO AIC v3.6) ---
SELECTIVE_STRATEGY_CONFIG = {
    "XAUUSD": {"use_filter": False, "reason": "Filter worsened performance (PF: 4.6 -> 4.0)"},
    "ETHUSD": {"use_filter": False, "reason": "Excessive trade reduction (78.3%)"},
    "BTCUSD": {"use_filter": True, "reason": "Massive performance improvement (PF: 26 -> 999.99, WR: 92.86% -> 100%)"}
}

# Configuração do Logger
logger = logging.getLogger("PrometheusMaster")
logger.setLevel(logging.INFO)
logger.handlers.clear()  # Limpar handlers existentes
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
        
        london_window = 8 <= hour < 12
        ny_window = 13 <= hour < 17
        overlap_window = 13 <= hour < 17
        
        return london_window or ny_window or overlap_window
    except:
        return True

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

# --- NOVAS FUNÇÕES: DESCOBERTA E TRIAGEM ---

def discover_all_assets() -> List[str]:
    """Descobre todos os ativos disponíveis no Market Watch do MT5."""
    logger.info(json.dumps({"event": "DISCOVERY_START", "message": "Iniciando descoberta de ativos no Market Watch."}))
    
    if not mt5.initialize():
        logger.critical(json.dumps({"event": "DISCOVERY_FAILED", "error": "Falha ao inicializar MT5."}))
        return []
    
    all_symbols_info = mt5.symbols_get()
    if all_symbols_info is None:
        logger.critical(json.dumps({"event": "DISCOVERY_FAILED", "error": "Falha ao obter símbolos do MT5."}))
        mt5.shutdown()
        return []
    
    symbols = [s.name for s in all_symbols_info]
    mt5.shutdown()
    logger.info(json.dumps({"event": "DISCOVERY_COMPLETE", "count": len(symbols), "message": f"{len(symbols)} símbolos encontrados no Market Watch."}))
    return symbols

def filter_viable_assets(symbols: List[str]) -> List[str]:
    """Filtra ativos com base em critérios de viabilidade de negociação."""
    logger.info(json.dumps({"event": "FILTER_START", "message": "Iniciando filtragem de viabilidade."}))
    
    if not mt5.initialize():
        logger.critical(json.dumps({"event": "FILTER_FAILED", "error": "Falha ao inicializar MT5."}))
        return []
    
    viable_assets = []
    for symbol in symbols:
        try:
            if not mt5.symbol_select(symbol, True):
                continue
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                continue
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                continue
            
            point = symbol_info.point
            if point <= 0:
                continue
            
            spread = tick.ask - tick.bid
            spread_points = spread / point if point != 0 else float('inf')
            
            if spread_points > DISCOVERY_CONFIG["max_spread_points"]:
                continue
            
            if tick.volume < DISCOVERY_CONFIG["min_tick_volume"]:
                continue
            
            viable_assets.append(symbol)
        except Exception as e:
            logger.warning(json.dumps({"event": "FILTER_SYMBOL_ERROR", "symbol": symbol, "error": str(e)}))
            continue
    
    mt5.shutdown()
    logger.info(json.dumps({"event": "FILTER_COMPLETE", "count": len(viable_assets), "message": f"{len(viable_assets)} ativos considerados viáveis."}))
    return viable_assets

def run_triage_backtest(symbol: str) -> Optional[Dict]:
    """Executa um backtest rápido para triagem de um ativo."""
    try:
        if not mt5.initialize():
            return None
        
        if not mt5.symbol_select(symbol, True):
            mt5.shutdown()
            return None
        
        # Obter dados históricos
        from_date = datetime.now() - timedelta(days=DISCOVERY_CONFIG["triage_data_days"])
        to_date = datetime.now()
        
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, from_date, to_date)
        
        # Fallback se não conseguir dados por range
        if rates is None or len(rates) < 50:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 200)
        
        if rates is None or len(rates) < 50:
            mt5.shutdown()
            return None
        
        df = pd.DataFrame(rates)
        df['MA20'] = df['close'].rolling(20).mean()
        df['MA50'] = df['close'].rolling(50).mean()
        
        # Simulação de trades simplificada
        trades = []
        position = None
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            mt5.shutdown()
            return None
        
        point = symbol_info.point
        
        for i in range(50, len(df)):
            # Sinal de compra: MA20 cruza acima de MA50
            if position is None and df['MA20'].iloc[i-1] < df['MA50'].iloc[i-1] and df['MA20'].iloc[i] > df['MA50'].iloc[i]:
                entry_price = df['close'].iloc[i]
                position = {'entry_price': entry_price, 'entry_time': df['time'].iloc[i]}
            
            # Saída por TP ou SL
            if position is not None:
                sl = position['entry_price'] - 50 * point
                tp = position['entry_price'] + 100 * point
                
                if df['low'].iloc[i] <= sl or df['high'].iloc[i] >= tp:
                    exit_price = tp if df['high'].iloc[i] >= tp else sl
                    profit = (exit_price - position['entry_price']) / point  # Profit em pontos
                    trades.append(profit)
                    position = None
        
        mt5.shutdown()
        
        if not trades:
            return {"symbol": symbol, "score": -1, "trades": 0, "profit_factor": 0.0}
        
        # Calcular métricas
        trades_df = pd.DataFrame({'profit': trades})
        profit_factor = calculate_profit_factor(trades_df)
        win_rate = calculate_win_rate(trades_df)
        expectancy = calculate_expectancy(trades_df)
        
        # Score baseado em Profit Factor (principal) e outros fatores
        score = profit_factor * (1 + win_rate / 100) * (1 + abs(expectancy) / 100) if expectancy > 0 else profit_factor * (1 + win_rate / 100)
        
        return {
            "symbol": symbol,
            "score": score,
            "trades": len(trades),
            "profit_factor": profit_factor,
            "win_rate": win_rate,
            "expectancy": expectancy
        }
    except Exception as e:
        logger.error(json.dumps({"event": "TRIAGE_ERROR", "symbol": symbol, "error": str(e)}))
        if mt5.terminal_info() is not None:
            mt5.shutdown()
        return None

def run_discovery_and_ranking():
    """Executa a Fase I completa: Descoberta, Filtragem e Triagem."""
    logger.info(json.dumps({"event": "PHASE_I_START", "message": "="*80}))
    logger.info(json.dumps({"event": "PHASE_I_START", "message": "INICIANDO FASE I: DESCOBERTA E RANQUEAMENTO DE ATIVOS"}))
    logger.info(json.dumps({"event": "PHASE_I_START", "message": "="*80}))
    
    all_assets = discover_all_assets()
    if not all_assets:
        logger.error(json.dumps({"event": "PHASE_I_FAILED", "message": "Nenhum ativo encontrado no Market Watch."}))
        return
    
    viable_assets = filter_viable_assets(all_assets)
    if not viable_assets:
        logger.warning(json.dumps({"event": "FILTER_TOO_RESTRICTIVE", "message": "Filtro muito restritivo. Usando símbolos do config.json como fallback."}))
        # Fallback: usar símbolos do config.json
        try:
            import json as json_lib
            with open(CONFIG_PATH, 'r') as f:
                config = json_lib.load(f)
            viable_assets = config.get('TRADING_SYMBOLS', ['XAUUSD', 'BTCUSD', 'ETHUSD'])
            logger.info(json.dumps({"event": "USING_FALLBACK_SYMBOLS", "symbols": viable_assets}))
        except:
            viable_assets = ['XAUUSD', 'BTCUSD', 'ETHUSD']  # Fallback final
            logger.info(json.dumps({"event": "USING_DEFAULT_SYMBOLS", "symbols": viable_assets}))
    
    logger.info(json.dumps({"event": "TRIAGE_START", "count": len(viable_assets), "message": f"Iniciando backtest de triagem para {len(viable_assets)} ativos..."}))
    
    triage_results = []
    for i, asset in enumerate(viable_assets, 1):
        logger.info(json.dumps({"event": "TRIAGE_PROGRESS", "current": i, "total": len(viable_assets), "symbol": asset}))
        result = run_triage_backtest(asset)
        if result and result['score'] > 0:
            triage_results.append(result)
            logger.info(json.dumps({
                "event": "TRIAGE_RESULT",
                "symbol": asset,
                "score": round(result['score'], 2),
                "trades": result['trades'],
                "profit_factor": round(result.get('profit_factor', 0), 2)
            }))
    
    if not triage_results:
        logger.error(json.dumps({"event": "PHASE_I_FAILED", "message": "Nenhum ativo passou no backtest de triagem."}))
        return
    
    # Ranquear e salvar
    df_results = pd.DataFrame(triage_results)
    df_results = df_results.sort_values(by='score', ascending=False)
    
    top_assets = df_results.head(DISCOVERY_CONFIG["top_assets_to_trade"])
    
    # Converter para dict para JSON
    top_assets_dict = top_assets.to_dict('records')
    
    with open(TRADEABLE_ASSETS_FILE, 'w') as f:
        json.dump(top_assets_dict, f, indent=2)
    
    logger.info(json.dumps({"event": "PHASE_I_SUCCESS", "count": len(top_assets), "file": TRADEABLE_ASSETS_FILE}))
    logger.info(json.dumps({"event": "PHASE_I_TOP_ASSETS", "assets": top_assets[['symbol', 'score', 'profit_factor']].to_dict('records')}))

# --- MÓDULO DE EXECUÇÃO DE ORDENS ---

def send_order(signal: Dict, config: Dict) -> Optional[Dict]:
    """Envia ordem usando SL/TP da estratégia."""
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
        "comment": "Prometheus Master v4.1",
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

def generate_signals(config: Dict, tradeable_symbols: List[str]) -> List[Dict]:
    """Gera sinais de trading usando estratégia seletiva fixa."""
    signals = []
    
    for symbol in tradeable_symbols:
        # Aplicar a estratégia seletiva FIXA (se disponível)
        strategy = SELECTIVE_STRATEGY_CONFIG.get(symbol)
        use_filter = strategy['use_filter'] if strategy else False
        
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
            
            h4_trend_up = h4_ma20 > h4_ma50
            h1_confirmation_up = h1_ma20 > h1_ma50
            m5_entry_up = m5_df['close'].iloc[-1] > m5_ma20
            h4_trend_down = h4_ma20 < h4_ma50
            h1_confirmation_down = h1_ma20 < h1_ma50
            m5_entry_down = m5_df['close'].iloc[-1] < m5_ma20
            rsi_ok = 30 < m5_rsi < 70  # Relaxado de 40-60 para 30-70
            volume_ok = m5_df['tick_volume'].iloc[-1] > m5_volume_avg * 0.8  # Relaxado: 80% da média
            
            # SINAL DE COMPRA
            if h4_trend_up and h1_confirmation_up and m5_entry_up and rsi_ok and volume_ok:
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
                    "event": "BUY_SIGNAL_GENERATED",
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "sl": sl,
                    "tp": tp,
                    "volume": signal['volume'],
                    "filter_used": use_filter
                }))
            
            # SINAL DE VENDA
            elif h4_trend_down and h1_confirmation_down and m5_entry_down and rsi_ok and volume_ok:
                tick = mt5.symbol_info_tick(symbol)
                symbol_info = mt5.symbol_info(symbol)
                
                if tick is None or symbol_info is None:
                    continue
                
                entry_price = tick.bid
                point = symbol_info.point
                
                if point <= 0:
                    continue
                
                sl = entry_price + 50 * point
                tp = entry_price - 100 * point
                
                signal = {
                    "symbol": symbol,
                    "action": "sell",
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
                    "event": "SELL_SIGNAL_GENERATED",
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "sl": sl,
                    "tp": tp,
                    "volume": signal['volume']
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
        main_thread = threading.main_thread()
        while self.running:
            time.sleep(30)
            
            # Verificar se thread principal está viva (compatível com Python 3.11)
            try:
                if not main_thread.is_alive():
                    logger.critical(json.dumps({"event": "WATCHDOG_CRITICAL", "message": "Thread principal morreu. Desligando sistema."}))
                    self.shutdown_system()
                    break
            except AttributeError:
                # Fallback para versões mais antigas do Python
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

def load_tradeable_assets() -> List[str]:
    """Carrega a lista de ativos negociáveis do arquivo."""
    try:
        with open(TRADEABLE_ASSETS_FILE, 'r') as f:
            assets = json.load(f)
        symbols = [item['symbol'] for item in assets]
        logger.info(json.dumps({"event": "tradeable_assets_loaded", "count": len(symbols), "symbols": symbols}))
        return symbols
    except FileNotFoundError:
        logger.warning(json.dumps({"event": "tradeable_assets_not_found", "file": TRADEABLE_ASSETS_FILE, "message": "Arquivo não encontrado. Usando símbolos do config.json como fallback."}))
        # FALLBACK: Usar símbolos do config.json se discovery não foi executado
        try:
            config = load_config()
            symbols = config.get('TRADING_SYMBOLS', ['XAUUSD', 'BTCUSD', 'ETHUSD'])
            if symbols:
                logger.info(json.dumps({"event": "using_config_symbols_fallback", "count": len(symbols), "symbols": symbols}))
                return symbols
        except:
            pass
        # Fallback final: símbolos padrão
        default_symbols = ['XAUUSD', 'BTCUSD', 'ETHUSD']
        logger.info(json.dumps({"event": "using_default_symbols_fallback", "symbols": default_symbols}))
        return default_symbols
    except Exception as e:
        logger.error(json.dumps({"event": "tradeable_assets_load_error", "error": str(e)}))
        # Fallback em caso de erro
        try:
            config = load_config()
            return config.get('TRADING_SYMBOLS', ['XAUUSD', 'BTCUSD', 'ETHUSD'])
        except:
            return ['XAUUSD', 'BTCUSD', 'ETHUSD']

def update_heartbeat():
    """Atualiza o arquivo de heartbeat"""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.error(json.dumps({"event": "heartbeat_update_failed", "error": str(e)}))

def run_production_cycle(config: Dict, tradeable_symbols: List[str]):
    """Executa um ciclo de produção"""
    logger.info(json.dumps({"event": "PRODUCTION_CYCLE_START", "message": "Iniciando ciclo de execução."}))
    
    terminal_info = mt5.terminal_info()
    if terminal_info is None or not terminal_info.connected:
        logger.error(json.dumps({"event": "mt5_disconnected", "message": "MT5 desconectado! Tentando restabelecer..."}))
        if not mt5.initialize():
            logger.error(json.dumps({"event": "mt5_reconnect_failed", "message": "Falha ao reconectar."}))
            return
    
    signals = generate_signals(config, tradeable_symbols)
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
        logger.info(json.dumps({"event": "MASTER_START", "message": "PROGRAMA MESTRE DE CONTROLE PROMETHEUS v4.1 INICIADO"}))
        logger.info(json.dumps({"event": "MASTER_START", "message": "="*80}))
    except Exception as e:
        print(f"Erro ao inicializar logger: {e}")
        # Criar logger básico se falhar
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger("PrometheusMaster")

    mode = sys.argv[1] if len(sys.argv) > 1 else "production"
    print(f"Modo selecionado: {mode}")
    logger.info(json.dumps({"event": "MODE_SELECTED", "mode": mode}))

    if mode == "discovery":
        print("\n" + "="*80)
        print("INICIANDO MODO DISCOVERY...")
        print("="*80 + "\n")
        try:
            print("Inicializando MT5...")
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"\nERRO CRÍTICO: Falha ao inicializar MT5.")
                print(f"Erro: {error}")
                logger.critical(json.dumps({"event": "MT5_INIT_FAILED", "error": str(error)}))
                print("\nPressione ENTER para sair...")
                input()
                sys.exit(1)
            print("✓ MT5 inicializado com sucesso.\n")
            run_discovery_and_ranking()
            print("\n" + "="*80)
            print("DISCOVERY CONCLUÍDO COM SUCESSO!")
            print("="*80)
            mt5.shutdown()
        except Exception as e:
            print(f"\nERRO no modo discovery: {e}")
            import traceback
            print("\nTraceback completo:")
            traceback.print_exc()
            logger.critical(json.dumps({"event": "DISCOVERY_ERROR", "error": str(e), "traceback": traceback.format_exc()}))
            if mt5.terminal_info() is not None:
                mt5.shutdown()
            print("\nPressione ENTER para sair...")
            input()
            sys.exit(1)
    elif mode == "production":
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
            print("ERRO: Arquivo TRADEABLE_ASSETS.json não encontrado!")
            print("="*80)
            print("\nVocê precisa executar a Fase I (discovery) primeiro.")
            print("\nExecute este comando:")
            print("  python prometheus_master_control_v4.1.py discovery")
            print("\nIsso irá:")
            print("  - Descobrir todos os ativos do Market Watch")
            print("  - Filtrar ativos viáveis")
            print("  - Executar backtest de triagem")
            print("  - Gerar o arquivo TRADEABLE_ASSETS.json")
            print("\nDepois disso, você pode executar:")
            print("  python prometheus_master_control_v4.1.py production")
            print("\n" + "="*80)
            logger.critical(json.dumps({"event": "PRODUCTION_FAILED", "message": "Nenhum ativo negociável encontrado. Execute 'discovery' primeiro."}))
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
        print("Modos disponíveis: 'discovery' ou 'production'")
        print("\nExemplo de uso:")
        print("  python prometheus_master_control_v4.1.py discovery")
        print("  python prometheus_master_control_v4.1.py production")
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

