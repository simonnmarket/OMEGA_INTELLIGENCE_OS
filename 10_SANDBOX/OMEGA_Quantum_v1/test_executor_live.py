import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
import sys
import os

from core_harmonizator import OMEGAHarmonizator, NumeiaPortfolioManager

# --- GLOBAL EXPERIMENTAL CONFIGURATION ---
MODE = "SIMULATION"
MAX_GLOBAL_POSITIONS = 5
MAX_CORRELATION = 0.8
DELTA_THRESHOLD = 0.02 # 2% Normalized Volume Delta
BREAK_EVEN_ATR_MULT = 1.5

# Hub Parametrization
HUB_CONFIG = {
    "BTCUSD": {"margin_pct": 0.25, "sl_mult": 1.0, "tp_mult": 2.5},
    "ETHUSD": {"margin_pct": 0.25, "sl_mult": 1.2, "tp_mult": 2.5},
    "SOLUSD": {"margin_pct": 0.25, "sl_mult": 1.0, "tp_mult": 2.0},
    "XRPUSD": {"margin_pct": 0.25, "sl_mult": 1.2, "tp_mult": 2.5},
    "XAUUSD": {"margin_pct": 0.15, "sl_mult": 2.0, "tp_mult": 4.0},
    "EURUSD": {"margin_pct": 0.15, "sl_mult": 1.5, "tp_mult": 3.0},
    "DEFAULT": {"margin_pct": 0.15, "sl_mult": 1.5, "tp_mult": 3.0}
}
TARGET_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "SOLUSD"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def get_symbol_config(symbol):
    for key in HUB_CONFIG.keys():
        if key in symbol:
            return HUB_CONFIG[key]
    return HUB_CONFIG["DEFAULT"]

class RiskController:
    def __init__(self, max_positions=MAX_GLOBAL_POSITIONS, max_correlation=MAX_CORRELATION):
        self.max_positions = max_positions
        self.max_correlation = max_correlation
        
    def check_correlation(self, new_symbol, open_positions):
        count = 100
        rates_new = mt5.copy_rates_from_pos(new_symbol, mt5.TIMEFRAME_M1, 0, count)
        if rates_new is None or len(rates_new) < count:
            return 0.0
        
        df_new = pd.DataFrame(rates_new)
        returns_new = df_new['close'].pct_change().dropna()
        
        max_corr = 0.0
        for pos in open_positions:
            rates_open = mt5.copy_rates_from_pos(pos.symbol, mt5.TIMEFRAME_M1, 0, count)
            if rates_open is None or len(rates_open) < count:
                continue
            df_open = pd.DataFrame(rates_open)
            returns_open = df_open['close'].pct_change().dropna()
            
            min_len = min(len(returns_new), len(returns_open))
            corr = returns_new[-min_len:].corr(returns_open[-min_len:])
            if not np.isnan(corr) and abs(corr) > abs(max_corr):
                max_corr = corr
        return max_corr

    def validate_new_trade(self, symbol, action_type, volume, price):
        positions = mt5.positions_get()
        if positions is None:
            positions = []
            
        if len(positions) >= self.max_positions:
            return False, f"RiskController: Global position cap ({self.max_positions}) reached."
            
        for p in positions:
            if p.symbol == symbol:
                return False, f"RiskController: Already have open position on {symbol}."
                
        corr = self.check_correlation(symbol, positions)
        if abs(corr) > self.max_correlation:
            return False, f"RiskController: Blocked due to high correlation ({corr:.2f}) with open positions."
            
        cfg = get_symbol_config(symbol)
        margin_req = mt5.order_calc_margin(action_type, symbol, volume, price)
        acct = mt5.account_info()
        
        if margin_req is None or acct is None:
            return False, "RiskController: Failed evaluating margin."
            
        max_allowed_margin = acct.margin_free * cfg["margin_pct"]
        if margin_req > max_allowed_margin:
            return False, f"RiskController: Margin {margin_req:.2f} exceeds local cap {max_allowed_margin:.2f}."
            
        return True, "Approved by QC Logic"

def get_atr(symbol, period=14, sma=100):
   rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period + sma + 5)
   if rates is None or len(rates) < period + sma:
       return None, None
   df = pd.DataFrame(rates)
   df['prev_close'] = df['close'].shift(1)
   df['tr1'] = df['high'] - df['low']
   df['tr2'] = abs(df['high'] - df['prev_close'])
   df['tr3'] = abs(df['low'] - df['prev_close'])
   df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
   
   df['atr'] = df['tr'].rolling(window=period).mean()
   df['atr_slow'] = df['atr'].rolling(window=sma).mean()
   
   return df['atr'].iloc[-1], df['atr_slow'].iloc[-1]

def get_normalized_delta(symbol, ticks_check=1000):
    ticks = mt5.copy_ticks_from(symbol, int(time.time()), ticks_check, mt5.COPY_TICKS_ALL)
    if ticks is None or len(ticks) == 0:
        return 0.0
    
    df = pd.DataFrame(ticks)
    if 'bid' not in df.columns or len(df) < 2:
        return 0.0
        
    diffs = df['bid'].diff().dropna()
    up_ticks = (diffs > 0).sum()
    down_ticks = (diffs < 0).sum()
    
    total_moves = up_ticks + down_ticks
    if total_moves == 0:
        return 0.0
        
    return (up_ticks - down_ticks) / float(total_moves)

def run_executor():
    logging.info(f"=== OMEGA EXPERIMENTAL LAB [{MODE}] ===")
    if not mt5.initialize():
        logging.error("Failed to init MT5")
        return
        
    risk_controller = RiskController()
    initial_balance = mt5.account_info().balance
    
    try:
        while True:
            # 0. Numeia Kill Switch
            current_equity = mt5.account_info().equity
            if NumeiaPortfolioManager.check_kill_switch(initial_balance, current_equity):
                logging.critical("SISTEMA DESLIGADO GLOBALMENTE: Limite Drawdown Atingido.")
                break

            # Coletando Dados para Harmonização Global
            mkt_data_dict = {}
            valid_symbols = []
            
            for target in TARGET_SYMBOLS:
                raw_syms = mt5.symbols_get(group=f"*{target[:3]}*")
                if not raw_syms: continue
                symbol = raw_syms[0].name
                for s in raw_syms:
                    if "USD" in s.name:
                        symbol = s.name
                        
                sym_info = mt5.symbol_info(symbol)
                tick = mt5.symbol_info_tick(symbol)
                if not sym_info or not tick or tick.ask == 0.0: continue
                
                # Coleta OHLCV para OS 5-Sentidos (Harmonization)
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 60)
                if rates is not None and len(rates) >= 50:
                    df = pd.DataFrame(rates)
                    mkt_data_dict[symbol] = df
                    valid_symbols.append((symbol, sym_info, tick))

            # Rodando o Maestro Harmonizador
            orchestration = OMEGAHarmonizator.execute_global_scan(mkt_data_dict)

            # Scanning Loop
            for symbol, sym_info, tick in valid_symbols:
                
                atr_fast, atr_slow = get_atr(symbol)
                if atr_slow is None: continue
                
                delta_pct = get_normalized_delta(symbol)
                
                # Integrando Harmonização
                harmonia = orchestration.get(symbol, {})
                regime = harmonia.get("regime", "UNKNOWN")
                sensory_coh = harmonia.get("coherence", 0.0)
                apollo_thermal = harmonia.get("apollo_thermal", 0.0)
                
                logging.info(f"[TEST LAB] {symbol} | Delta: {delta_pct*100:.1f}% | Regime: {regime} | Coherence: {sensory_coh:.2f} | Termal: {apollo_thermal:.1f}%")
                
            time.sleep(5) 
            
    except KeyboardInterrupt:
        logging.info("Executor Lab Desligado pelo Operador.")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    run_executor()
