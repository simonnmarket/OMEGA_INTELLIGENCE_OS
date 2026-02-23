"""
Test Script: Orchestral Harmonization across different Assets
"""
import time
from architecture.hub import OmegaEcosystemHub

if __name__ == "__main__":
    hub = OmegaEcosystemHub()
    print("\n" + "="*50)
    
    # Tick 1: XAUUSD (Gold)
    print("\n[MAESTRO] PLAYING THE FIRST SHEET MUSIC: GOLD (XAUUSD)")
    tick_gold = {"symbol": "XAUUSD", "timestamp": time.time(), "price": 2050.00, "volatility": 0.9}
    hub.run_cycle(tick_gold)
    
    print("\n" + "="*50)
    
    # Tick 2: AUDJPY (Forex - High Frequency)
    print("\n[MAESTRO] PLAYING THE SECOND SHEET MUSIC: FOREX (AUDJPY)")
    tick_aj = {"symbol": "AUDJPY", "timestamp": time.time(), "price": 98.50, "volatility": 0.5}
    hub.run_cycle(tick_aj)
    
    print("\n" + "="*50)
    
    # Tick 3: BTCUSD (Crypto - Deep Latency)
    print("\n[MAESTRO] PLAYING THE THIRD SHEET MUSIC: CRYPTO (BTCUSD)")
    tick_btc = {"symbol": "BTCUSD", "timestamp": time.time(), "price": 65000.00, "volatility": 1.2}
    hub.run_cycle(tick_btc)
    
    print("\n" + "="*50)
