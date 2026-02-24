"""
OMEGA Intelligence OS - Experimental Sandbox
Asset Signature Matrix, Multisensory Market Perception, and Quantum Portfolio Balancing.
Integrates the finest algorithms from Numeia, Apollo11, and Quantum Sensory OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("Omega.Harmonization")

# =====================================================================
# 1. NUMEIA CORE: MULTI-ASSET PORTFOLIO ALLOCATION
# =====================================================================
class NumeiaPortfolioManager:
    """
    Incorporates the Numeia v5.1 Multi-Asset Portfolio logic.
    Focus: Maximum Diversification across Indices, Commodities, and Forex.
    """
    PORTFOLIO_TARGETS = {
        "INDEX_US500": 0.20,
        "INDEX_GER40": 0.15,
        "INDEX_UK100": 0.15,
        "COMM_XAUUSD": 0.15,
        "COMM_XAGUSD": 0.05,
        "COMM_UKOIL":  0.05,
        "FOREX_EURUSD": 0.07,
        "FOREX_GBPUSD": 0.07,
        "FOREX_USDJPY": 0.06,
        "CASH_RESERVE": 0.05
    }
    
    MAX_DRAWDOWN_KILL_SWITCH = 0.30  # 30% System Kill-Switch
    DEVIATION_THRESHOLD = 0.05      # 5% Deviation triggers Rebalance
    
    @classmethod
    def calculate_rebalance(cls, current_equity: float, current_positions: Dict[str, float]) -> Dict[str, float]:
        target_values = {asset: current_equity * weight for asset, weight in cls.PORTFOLIO_TARGETS.items() if "CASH" not in asset}
        adjustments = {}
        
        for asset, target_value in target_values.items():
            current_value = current_positions.get(asset, 0.0)
            deviation_pct = abs(current_value - target_value) / current_equity
            
            if deviation_pct > cls.DEVIATION_THRESHOLD:
                delta = target_value - current_value
                adjustments[asset] = delta
                logger.info(f"[NUMEIA] Rebalance required for {asset}: Delta = {delta:.2f} (Dev: {deviation_pct*100:.2f}%)")
                
        return adjustments

    @classmethod
    def check_kill_switch(cls, initial_balance: float, current_equity: float) -> bool:
        drawdown = (initial_balance - current_equity) / initial_balance
        if drawdown >= cls.MAX_DRAWDOWN_KILL_SWITCH:
            logger.critical(f"[NUMEIA] KILL SWITCH ACTIVATED. Drawdown {drawdown*100:.1f}% exceeds max allowed.")
            return True
        return False

# =====================================================================
# 2. APOLLO11 CORE: QUANTUM GRAVITATIONAL & INSTITUTIONAL PULSE
# =====================================================================
class Apollo11QuantumEngine:
    """
    Engine mimicking the Apollo11 QE v3.2 mapping logic.
    Calculates Thermal Energy, Point of Control (POC), and Institutional Pulse.
    """
    
    @staticmethod
    def calculate_thermal_energy(volumes: np.ndarray, period: int = 20) -> float:
        if len(volumes) < period:
            return 0.0
        recent_v = volumes[-period:]
        total_v = np.sum(recent_v)
        if total_v == 0:
            return 0.0
        return (recent_v[-1] / total_v) * 100.0

    @staticmethod
    def identify_poc(prices: np.ndarray, volumes: np.ndarray, period: int = 20) -> float:
        if len(volumes) < period:
            return 0.0
        recent_v = volumes[-period:]
        recent_p = prices[-period:]
        max_idx = np.argmax(recent_v)
        return recent_p[max_idx]

    @staticmethod
    def measure_institutional_pulse(volumes: np.ndarray, period: int = 20) -> float:
        if len(volumes) < period:
            return 1.0
        avg_vol = np.mean(volumes[-period:])
        if avg_vol == 0:
            return 1.0
        pulse = volumes[-1] / avg_vol
        return pulse

# =====================================================================
# 3. VOLATILITY & WHALE DETECTOR CORE (Sourced from Inbox Concepts)
# =====================================================================
class WhaleAndVolatilityScanner:
    """
    Replaces the flawed QuantumSensory with proven logic from:
    - VolatilityFilter.txt (Blocks whipsaw via ATR bounds)
    - WhaleDetector.mqh (Enforces Institutional Volume Surge)
    """
    
    @staticmethod
    def check_volatility_filter(data: pd.DataFrame, max_atr_pct: float = 0.02) -> float:
        """
        VolatilityFilter (from VolatilityFilter.txt): 
        If average ATR > MaxVolatility of asset price, the market is too erratic (whipsaw).
        """
        if len(data) < 20: return 0.5
        high_low = data['high'] - data['low']
        current_atr = high_low.rolling(14).mean().iloc[-1]
        close = data['close'].iloc[-1]
        
        if pd.isna(current_atr) or close == 0: 
            return 0.5
            
        atr_pct = current_atr / close
        
        # Absolute limit cutoff
        if atr_pct > max_atr_pct:
            return 0.0 # Whipsaw! Kill signal.
            
        return 1.0

    @staticmethod
    def check_whale_imbalance(data: pd.DataFrame) -> float:
        """
        WhaleDetector: Checks directional volume flows (Volume Accumulation).
        """
        if len(data) < 20 or 'tick_volume' not in data:
            return 0.5
        
        # Look for steady volume accumulation (positive slope)
        vol_tail = data['tick_volume'].tail(15).values
        x = np.arange(15)
        slope, _ = np.polyfit(x, vol_tail, 1)
        
        if slope > 0:
            # Volume is growing directionally (Whale shadow)
            return 1.0
        else:
            # Stagnant or falling volume
            return 0.3

    @classmethod
    def synthesize_perception(cls, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Synthesizes the Institutional Inbox rules.
        """
        volatility_conf = cls.check_volatility_filter(data, max_atr_pct=0.03) # 3% limit for test
        whale_conf = cls.check_whale_imbalance(data)
        
        # Whipsaw instantly fails the coherence matrix
        if volatility_conf == 0.0:
            overall = 0.0 # Trapped in Noise
        else:
            overall = (volatility_conf * 0.3) + (whale_conf * 0.7)
            
        return {
            "volatility_status": "SAFE" if volatility_conf > 0.0 else "WHIPSAW",
            "whale_confidence": whale_conf,
            "overall_coherence": overall,
            "regime": "HARMONIC_FLOW" if overall >= 0.60 else "DISSONANT_NOISE"
        }

# =====================================================================
# 4. MASTER ORCHESTRATOR
# =====================================================================
class OMEGAHarmonizator:
    """
    The ultimate brain linking Numeia Asset Limits, Apollo11 Execution Logic, 
    and the new Whale & Volatility Scanner.
    """
    
    @classmethod
    def execute_global_scan(cls, mkt_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        orchestration_map = {}
        for symbol, df in mkt_data_dict.items():
            if df.empty or len(df) < 50:
                continue
                
            prices = df['close'].values
            vols = df.get('tick_volume', pd.Series([1]*len(df))).values
            
            # 1. Sense Output using INBOX Concepts
            sensory_output = WhaleAndVolatilityScanner.synthesize_perception(df)
            
            # 2. Apollo Quantum Profile
            thermal = Apollo11QuantumEngine.calculate_thermal_energy(vols)
            pulse = Apollo11QuantumEngine.measure_institutional_pulse(vols)
            poc = Apollo11QuantumEngine.identify_poc(prices, vols)
            
            orchestration_map[symbol] = {
                "regime": sensory_output["regime"],
                "coherence": round(sensory_output["overall_coherence"], 3),
                "vol_status": sensory_output["volatility_status"],
                "apollo_thermal": round(thermal, 2),
                "apollo_pulse": round(pulse, 2),
                "apollo_poc": poc
            }
            
        return orchestration_map
