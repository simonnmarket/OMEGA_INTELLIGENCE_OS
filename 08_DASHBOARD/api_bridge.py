"""
OMEGA OS - Flask API Bridge (Crypto Orbit Protocol)
Calculates real CTI indicators using MT5 Tick Data.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import MetaTrader5 as mt5
import pandas as pd

app = Flask(__name__)
CORS(app)

if not mt5.initialize():
    print("[SERVER] API Bridge Error: MT5 not initialized.")

def calculate_cti_metrics(symbol):
    # Fetch last 1000 ticks for Order Flow & Volume Analysis
    ticks = mt5.copy_ticks_from_pos(symbol, mt5.COPY_TICKS_ALL, 0, 1000)
    
    if ticks is None or len(ticks) == 0:
        return {
            "price": 0.0, 
            "volume_delta": "0", 
            "order_flow": "No Liquidity", 
            "absorption": "N/A", 
            "volatility": "0",
            "trend": "N/A"
        }
    
    df = pd.DataFrame(ticks)
    
    price = float(ticks[-1]['ask']) if ticks[-1]['ask'] > 0 else float(ticks[-1]['last'])
    
    # Process Order Flow (Approximation via MT5 Flags)
    # 2 = Sell, 4 = Buy / 56 = Buy+Volume, 88 = Sell+Volume
    buy_vol = 0
    sell_vol = 0
    for t in ticks:
        flags = t['flags']
        if (flags & mt5.TICK_FLAG_BUY) or (flags & 4):
            buy_vol += t['volume']
        elif (flags & mt5.TICK_FLAG_SELL) or (flags & 2):
            sell_vol += t['volume']
            
    delta = buy_vol - sell_vol
    delta_str = f"+{int(delta)}" if delta > 0 else str(int(delta))
    flow = "Bullish" if delta > 0 else "Bearish" if delta < 0 else "Neutral"
    
    # Trend based on price action over 1000 ticks
    start_price = float(ticks[0]['last'])
    end_price = float(ticks[-1]['last'])
    trend = "Upward" if end_price > start_price else "Downward"
    
    # Volatility Check
    high = df['ask'].max()
    low = df['bid'].min()
    volatility = round((high - low), 2)
    
    # Absorption Detection (High volume, low price movement)
    price_diff = abs(end_price - start_price)
    absorption = "Detected" if (price_diff < (price * 0.001) and (buy_vol+sell_vol) > 500) else "Clear"

    return {
        "price": price,
        "volume_delta": delta_str,
        "order_flow": flow,
        "absorption": absorption,
        "volatility": f"{volatility}",
        "trend": trend
    }

@app.route('/api/account', methods=['GET'])
def get_account_data():
    account_info = mt5.account_info()
    if account_info is None:
        return jsonify({"error": "No account bound in terminal.", "balance": 0, "equity": 0}), 400
        
    return jsonify({
        "balance": account_info.balance,
        "equity": account_info.equity,
        "server": account_info.server,
        "login": account_info.login
    })

@app.route('/api/scan/crypto', methods=['GET'])
def scan_crypto():
    symbols_to_check = ["BTCUSD", "ETHUSD", "SOLUSD"]
    multi_asset_data = {}
    
    for req_sym in symbols_to_check:
        found = mt5.symbols_get(group=f"*{req_sym[:3]}*")
        target_sym = req_sym
        
        if found:
            # Try to match a USD pair precisely
            for s in found:
                if "USD" in s.name:
                    target_sym = s.name
                    break
            
            metrics = calculate_cti_metrics(target_sym)
            metrics["symbol"] = target_sym
            multi_asset_data[req_sym] = metrics
        else:
            # Symbol totally unavailable
            multi_asset_data[req_sym] = {
                "symbol": target_sym,
                "price": 0.0, 
                "volume_delta": "0", 
                "order_flow": "Offline", 
                "absorption": "-", 
                "volatility": "0",
                "trend": "-"
            }
            
    return jsonify(multi_asset_data)

if __name__ == '__main__':
    print("[SERVER] OMEGA Orbit Protocol Running on http://127.0.0.1:5000 ...")
    app.run(port=5000, debug=False)
