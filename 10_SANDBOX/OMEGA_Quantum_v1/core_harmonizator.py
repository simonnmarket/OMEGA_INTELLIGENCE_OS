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
        """
        Calculates the required cash delta to achieve the target weights.
        Returns a dictionary with assets and the amount to buy/sell (+ for buy, - for sell).
        """
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
        """
        Extracts localized thermal energy based on volume concentration.
        """
        if len(volumes) < period:
            return 0.0
        recent_v = volumes[-period:]
        total_v = np.sum(recent_v)
        if total_v == 0:
            return 0.0
        return (recent_v[-1] / total_v) * 100.0

    @staticmethod
    def identify_poc(prices: np.ndarray, volumes: np.ndarray, period: int = 20) -> float:
        """
        Point of Control (POC): Price level with maximum volume in lookback window.
        """
        if len(volumes) < period:
            return 0.0
        recent_v = volumes[-period:]
        recent_p = prices[-period:]
        max_idx = np.argmax(recent_v)
        return recent_p[max_idx]

    @staticmethod
    def measure_institutional_pulse(volumes: np.ndarray, period: int = 20) -> float:
        """
        Institutional Pulse: compares current volume against rolling average.
        """
        if len(volumes) < period:
            return 1.0
        avg_vol = np.mean(volumes[-period:])
        if avg_vol == 0:
            return 1.0
        pulse = volumes[-1] / avg_vol
        return pulse

# =====================================================================
# 3. QUANTUM SENSORY CORE: 5-SENSE MARKET PERCEPTION
# =====================================================================
class QuantumSensoryDetector:
    """
    Integrates 5 senses (Vision, Hearing, Touch, Smell, Taste) 
    to create a composite view of market regimes and flow.
    """
    
    @staticmethod
    def sense_vision(data: pd.DataFrame) -> float:
        """
        VISION (Order Flow / Blocks): Heavy block detection using volume spikes.
        Calculates confidence 0.0 to 1.0 based on current volume vs SMA Volume.
        """
        if len(data) < 20 or 'tick_volume' not in data:
            return 0.5
        avg_vol = data['tick_volume'].rolling(20).mean().iloc[-1]
        last_vol = data['tick_volume'].iloc[-1]
        if avg_vol == 0: return 0.0
        confidence = min(last_vol / avg_vol, 1.0)
        return confidence
        
    @staticmethod
    def sense_hearing(data: pd.DataFrame) -> float:
        """
        HEARING (Signal vs Noise): Analyzes clean market momentum using RSI.
        High RSI extremes or smooth trends represent clear 'sounds', chop is 'noise'.
        """
        if len(data) < 15 or 'close' not in data:
            return 0.5
        
        # Simple RSI calculation
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1]
        
        if pd.isna(rsi_val): return 0.5
        signal_strength = abs(50 - rsi_val) / 50.0  # Normalized 0 to 1
        return signal_strength
        
    @staticmethod
    def sense_touch(data: pd.DataFrame) -> float:
        """
        TOUCH (Resistance/Pressure): How hard the market hits SMA bounds or wicks.
        """
        if len(data) < 20: return 0.5
        sma = data['close'].rolling(20).mean().iloc[-1]
        close = data['close'].iloc[-1]
        pressure = abs((close - sma) / sma) * 1000 # Scaling factor
        return min(pressure, 1.0)

    @staticmethod
    def sense_smell(data: pd.DataFrame) -> float:
        """
        SMELL (Risk / Stress): Detects invisible danger using ATR spikes.
        High stress reduces confidence.
        """
        if len(data) < 15: return 0.5
        high_low = data['high'] - data['low']
        atr = high_low.rolling(14).mean()
        current_atr = atr.iloc[-1]
        max_atr = atr.rolling(20).max().iloc[-1]
        
        if max_atr == 0 or pd.isna(current_atr): return 0.5
        stress = current_atr / max_atr
        return max(1.0 - stress, 0.3) # Confidence inversely proportional to risk

    @staticmethod
    def sense_taste(data: pd.DataFrame) -> float:
        """
        TASTE (Quality of Flow): Stochastic measurement of flow quality.
        """
        if len(data) < 14: return 0.5
        low_min = data['low'].rolling(14).min()
        high_max = data['high'].rolling(14).max()
        stoch_k = 100 * (data['close'] - low_min) / (high_max - low_min)
        stoch_val = stoch_k.iloc[-1]
        
        if pd.isna(stoch_val): return 0.5
        quality = stoch_val / 100.0
        return quality

    @classmethod
    def synthesize_perception(cls, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Weighs all 5 senses to determine market conditions.
        """
        v = cls.sense_vision(data)
        h = cls.sense_hearing(data)
        t = cls.sense_touch(data)
        s = cls.sense_smell(data)
        ts = cls.sense_taste(data)
        
        overall = (v*0.30) + (h*0.20) + (t*0.25) + (s*0.15) + (ts*0.10)
        
        return {
            "vision_conf": v,
            "hearing_conf": h,
            "touch_conf": t,
            "smell_conf": s,
            "taste_conf": ts,
            "overall_coherence": overall,
            "regime": "HARMONIC_FLOW" if overall > 0.60 else "DISSONANT_NOISE"
        }

# =====================================================================
# 4. MASTER ORCHESTRATOR
# =====================================================================
class OMEGAHarmonizator:
    """
    The ultimate brain linking Numeia Asset Limits, Apollo11 Execution Logic, 
    and Quantum Sensory detection.
    """
    
    @classmethod
    def execute_global_scan(cls, mkt_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Accepts data stream for all targets and determines global bias,
        thermal energy distribution, and optimal entry avenues.
        """
        orchestration_map = {}
        for symbol, df in mkt_data_dict.items():
            if df.empty or len(df) < 50:
                continue
                
            prices = df['close'].values
            vols = df.get('tick_volume', pd.Series([1]*len(df))).values
            
            # 1. Sense Output
            sensory_output = QuantumSensoryDetector.synthesize_perception(df)
            
            # 2. Apollo Quantum Profile
            thermal = Apollo11QuantumEngine.calculate_thermal_energy(vols)
            pulse = Apollo11QuantumEngine.measure_institutional_pulse(vols)
            poc = Apollo11QuantumEngine.identify_poc(prices, vols)
            
            orchestration_map[symbol] = {
                "regime": sensory_output["regime"],
                "coherence": round(sensory_output["overall_coherence"], 3),
                "apollo_thermal": round(thermal, 2),
                "apollo_pulse": round(pulse, 2),
                "apollo_poc": poc
            }
            
        return orchestration_map
