"""
Multi-Timeframe Analysis Framework
Numeia Trading System v3.1

Baseado em:
- Elder, A. (1993). "Trading for a Living" - Triple Screen System
- Murphy, J. J. (1999). "Technical Analysis of the Financial Markets"
- Gann, W. D. (1935). "Master Time Factor"
- Lo & MacKinlay (1988). "Stock Market Prices Do Not Follow Random Walks"

Aplicável a: Crypto, Forex, Equities, Gold, Futures
"""

from .multi_timeframe_analyzer import MultiTimeframeAnalyzer
from .timeframe_config import TimeframeConfig, MultiTimeframeSignal

__version__ = "1.0.0"
__all__ = ['MultiTimeframeAnalyzer', 'TimeframeConfig', 'MultiTimeframeSignal']

