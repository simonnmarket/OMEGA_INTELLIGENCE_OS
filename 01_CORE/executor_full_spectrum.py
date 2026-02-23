import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging

# --- GLOBAL CONFIGURATION (OMA PHASE 13 CQO MANDATE) ---
MODE = "DEMO"
MAX_GLOBAL_POSITIONS = 3
MAX_CORRELATION = 0.7
DELTA_THRESHOLD = 0.05 # 5% Normalized Volume Delta for initial demo
BREAK_EVEN_ATR_MULT = 1.0 # CQO: Move SL to entry after 1.0x ATR_slow profit

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
TARGET_SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("executor_full_spectrum.log"),
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
            
        # 1. MT5 Global Position Hard Cap
        if len(positions) >= self.max_positions:
            return False, f"RiskController: Global position cap ({self.max_positions}) reached."
            
        # 2. Check for Hedging Overlap (No doubling down on same asset)
        for p in positions:
            if p.symbol == symbol:
                return False, f"RiskController: Already have open position on {symbol}."
                
        # 3. Correlation Matrix Filter
        corr = self.check_correlation(symbol, positions)
        if abs(corr) > self.max_correlation:
            return False, f"RiskController: Blocked due to high correlation ({corr:.2f}) with open positions."
            
        # 4. Global Margin Cap (Max Free Margin usage)
        cfg = get_symbol_config(symbol)
        margin_req = mt5.order_calc_margin(action_type, symbol, volume, price)
        acct = mt5.account_info()
        
        if margin_req is None or acct is None:
            return False, "RiskController: Failed evaluating margin."
            
        max_allowed_margin = acct.margin_free * cfg["margin_pct"]
        if margin_req > max_allowed_margin:
            return False, f"RiskController: Margin {margin_req:.2f} exceeds local cap {max_allowed_margin:.2f}."
            
        return True, "Approved by CQO Logic"

def get_atr(symbol, period=14, sma=100):
   """GS Surgical Standard: ATR Smoothed to combat wicks & hunting"""
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
    import time
    ticks = mt5.copy_ticks_from(symbol, int(time.time()), ticks_check, mt5.COPY_TICKS_ALL)
    if ticks is None or len(ticks) == 0:
        return 0.0
    
    df = pd.DataFrame(ticks)
    
    # In Crypto/FX CFDs, Volume is often 0 (Quotes only).
    # We approximate Order Flow Delta using Price Tick Delta (Up-ticks vs Down-ticks)
    if 'bid' not in df.columns or len(df) < 2:
        return 0.0
        
    diffs = df['bid'].diff().dropna()
    up_ticks = (diffs > 0).sum()
    down_ticks = (diffs < 0).sum()
    
    total_moves = up_ticks + down_ticks
    if total_moves == 0:
        return 0.0
        
    return (up_ticks - down_ticks) / float(total_moves)

def protect_capital_break_even():
    """CQO Patch: Protect profits by trailing to entry + spread"""
    positions = mt5.positions_get()
    if not positions:
        return
        
    for pos in positions:
        symbol = pos.symbol
        atr_f, atr_s = get_atr(symbol)
        if not atr_s: continue
        
        point = mt5.symbol_info(symbol).point
        tick = mt5.symbol_info_tick(symbol)
        
        if pos.type == mt5.ORDER_TYPE_BUY:
            profit_points = (tick.bid - pos.price_open)
            if profit_points >= atr_s * BREAK_EVEN_ATR_MULT: 
                new_sl = pos.price_open + (10 * point) # Spread buffer
                if pos.sl == 0.0 or pos.sl < new_sl:
                    req = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "symbol": pos.symbol,
                        "sl": new_sl,
                        "tp": pos.tp
                    }
                    res = mt5.order_send(req)
                    if res.retcode == mt5.TRADE_RETCODE_DONE:
                        logging.info(f"[CQO PROTECT] BREAK-EVEN ATIVADO p/ {pos.ticket} ({symbol})")

        elif pos.type == mt5.ORDER_TYPE_SELL:
            profit_points = (pos.price_open - tick.ask)
            if profit_points >= atr_s * BREAK_EVEN_ATR_MULT:
                new_sl = pos.price_open - (10 * point)
                if pos.sl == 0.0 or pos.sl > new_sl:
                    req = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "symbol": pos.symbol,
                        "sl": new_sl,
                        "tp": pos.tp
                    }
                    res = mt5.order_send(req)
                    if res.retcode == mt5.TRADE_RETCODE_DONE:
                        logging.info(f"[CQO PROTECT] BREAK-EVEN ATIVADO p/ {pos.ticket} ({symbol})")


def run_executor():
    logging.info(f"=== OMEGA OS V2.5 FULL SPECTRUM EXECUTOR [{MODE}] ===")
    if not mt5.initialize():
        logging.error("Failed to init MT5")
        return
        
    risk_controller = RiskController()
    
    try:
        while True:
            # 1. Manage Active Positions (Break-Even / Trailing)
            protect_capital_break_even()
            
            # 2. Scanning Loop
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
                
                # Indicator: Smoothed ATR Volatility
                atr_fast, atr_slow = get_atr(symbol)
                if atr_slow is None: continue
                
                # Indicator: Normalized Volume Delta
                delta_pct = get_normalized_delta(symbol)
                
                # Filter: Night Watch Flow (Z-Score approximation)
                logging.info(f"[{symbol}] SCAN: Fluxo Atual = {delta_pct*100:.1f}%. Limite = {DELTA_THRESHOLD*100:.1f}%.")
                if abs(delta_pct) < DELTA_THRESHOLD:
                    continue 
                    
                action = mt5.ORDER_TYPE_BUY if delta_pct > 0 else mt5.ORDER_TYPE_SELL
                action_str = "BUY" if delta_pct > 0 else "SELL"
                price = tick.ask if action == mt5.ORDER_TYPE_BUY else tick.bid
                vol = sym_info.volume_min
                
                # Risk Controller Check
                approved, reason = risk_controller.validate_new_trade(symbol, action, vol, price)
                
                if not approved:
                    continue
                    
                # Calculate SL/TP Dynamically via ATR
                cfg = get_symbol_config(symbol)
                sl_dist = atr_slow * cfg["sl_mult"]
                tp_dist = atr_slow * cfg["tp_mult"]
                
                sl = price - sl_dist if action == mt5.ORDER_TYPE_BUY else price + sl_dist
                tp = price + tp_dist if action == mt5.ORDER_TYPE_BUY else price - tp_dist
                
                logging.info(f"[{symbol}] ALERTA FLUXO! Delta: {delta_pct*100:.1f}%. ATR_S: {atr_slow:.4f}")
                logging.info(f"[{symbol}] Disparo {action_str} {vol}. Razao RC: {reason}")
                
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": vol,
                    "type": action,
                    "price": price,
                    "sl": sl,
                    "tp": tp,
                    "deviation": 20,
                    "magic": 234130, # Phase 13 Target
                    "comment": "OMEGA_V2_FULL",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                res = mt5.order_send(req)
                if res.retcode != mt5.TRADE_RETCODE_DONE:
                    # Fallbacks
                    req["type_filling"] = mt5.ORDER_FILLING_RETURN
                    res = mt5.order_send(req)
                    if res.retcode != mt5.TRADE_RETCODE_DONE:
                        req["type_filling"] = mt5.ORDER_FILLING_FOK
                        res = mt5.order_send(req)
                        if res.retcode != mt5.TRADE_RETCODE_DONE:
                            logging.error(f"Failed entry {symbol}. Retcode: {res.retcode}")
                        else:
                            logging.info(f"[SUCESSO] Ordem Executada {symbol}. Ticket: {res.order}")
                    else:
                        logging.info(f"[SUCESSO] Ordem Executada {symbol}. Ticket: {res.order}")
                else:
                    logging.info(f"[SUCESSO] Ordem Executada {symbol}. Ticket: {res.order}")
                
            time.sleep(5) 
            
    except KeyboardInterrupt:
        logging.info("Executor Full Spectrum Desligado pelo Operador.")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    run_executor()
