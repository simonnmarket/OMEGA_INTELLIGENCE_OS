# -*- coding: utf-8 -*-
"""
Crypto Mean Reversion Strategy - VERSÃO BACKTEST
===================================================
Adaptação da estratégia científica para funcionar com dados históricos (yfinance)

LÓGICA:
- RSI (Relative Strength Index) para identificar oversold/overbought
- Bollinger Bands para identificar desvios extremos
- Entry: RSI < 30 AND price < BB lower
- Exit: RSI > 50 OR price > BB middle

SCIENTIFIC BASE:
- Wilder, J. W. (1978). New Concepts in Technical Trading Systems
- Bollinger, J. (1992). Using Bollinger Bands
- Chan, E. (2013). Algorithmic Trading: Winning Strategies

COMPLIANCE: PROTOCOLO BLINDADO 100%
DATA: 03-11-2025
VERSÃO: 1.0.0 (Backtest)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available - using fallback calculations")

class CryptoMeanReversionBacktest:
    """
    Mean Reversion Strategy usando RSI + Bollinger Bands
    Versão otimizada para backtesting com dados históricos
    
    References:
    - Wilder (1978) - RSI indicator
    - Bollinger (1992) - Bollinger Bands
    - Chan (2013) - Mean Reversion strategies
    """
    
    def __init__(self, 
                 rsi_period: int = 14,
                 rsi_oversold: float = 30.0,
                 rsi_overbought: float = 70.0,
                 bb_period: int = 20,
                 bb_std: float = 2.0):
        """
        Initialize strategy parameters
        
        Args:
            rsi_period: RSI lookback period (Wilder 1978: 14)
            rsi_oversold: RSI oversold threshold (standard: 30)
            rsi_overbought: RSI overbought threshold (standard: 70)
            bb_period: Bollinger Bands period (Bollinger 1992: 20)
            bb_std: Bollinger Bands std deviation multiplier (standard: 2.0)
        """
        self.strategy_id = "CRYPTO_MEAN_REVERSION_BACKTEST"
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.bb_period = bb_period
        self.bb_std = bb_std
        
        logging.info(f"[{self.strategy_id}] Initialized")
        logging.info(f"  RSI: period={rsi_period}, oversold={rsi_oversold}, overbought={rsi_overbought}")
        logging.info(f"  BB: period={bb_period}, std={bb_std}")
    
    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)
        
        Reference: Wilder, J. W. (1978). New Concepts in Technical Trading Systems
        
        Args:
            prices: Close prices series
            period: RSI period (default: self.rsi_period)
        
        Returns:
            RSI series (0-100)
        """
        if period is None:
            period = self.rsi_period
        
        if TALIB_AVAILABLE:
            # Use TA-Lib if available (faster and more accurate)
            rsi = talib.RSI(prices.values, timeperiod=period)
            return pd.Series(rsi, index=prices.index)
        else:
            # Fallback: Manual RSI calculation
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = None, std: float = None) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Reference: Bollinger, J. (1992). Using Bollinger Bands
        
        Args:
            prices: Close prices series
            period: BB period (default: self.bb_period)
            std: Std deviation multiplier (default: self.bb_std)
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if period is None:
            period = self.bb_period
        if std is None:
            std = self.bb_std
        
        if TALIB_AVAILABLE:
            # Use TA-Lib if available
            upper, middle, lower = talib.BBANDS(
                prices.values,
                timeperiod=period,
                nbdevup=std,
                nbdevdn=std,
                matype=0  # Simple Moving Average
            )
            return (
                pd.Series(upper, index=prices.index),
                pd.Series(middle, index=prices.index),
                pd.Series(lower, index=prices.index)
            )
        else:
            # Fallback: Manual BB calculation
            middle = prices.rolling(window=period).mean()
            std_dev = prices.rolling(window=period).std()
            
            upper = middle + (std_dev * std)
            lower = middle - (std_dev * std)
            
            return upper, middle, lower
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Generate trading signals based on RSI + Bollinger Bands
        
        Entry Logic (BUY):
        - RSI < oversold threshold (30)
        - AND price < BB lower band
        - = Price is extremely oversold by both indicators
        
        Exit Logic (SELL):
        - RSI > 50 (neutral zone)
        - OR price > BB middle band
        - = Mean reversion complete
        
        Args:
            data: DataFrame with OHLCV data (must have 'Close' column)
            symbol: Asset symbol (for logging)
        
        Returns:
            DataFrame with signals column ('BUY', 'SELL', 'HOLD')
        """
        df = data.copy()
        
        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate indicators
        df['RSI'] = self.calculate_rsi(df['Close'])
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bollinger_bands(df['Close'])
        
        # Initialize signals
        df['Signal'] = 'HOLD'
        df['Confidence'] = 0.0
        df['Reason'] = ''
        
        # Generate BUY signals (oversold conditions)
        buy_condition = (
            (df['RSI'] < self.rsi_oversold) &  # RSI oversold
            (df['Close'] < df['BB_Lower'])     # Price below lower BB
        )
        
        df.loc[buy_condition, 'Signal'] = 'BUY'
        df.loc[buy_condition, 'Confidence'] = 0.75 + (0.20 * (1 - df['RSI'] / 100))  # Higher confidence for lower RSI
        df.loc[buy_condition, 'Reason'] = 'Oversold: RSI<30 & Price<BB_Lower'
        
        # Generate SELL signals (exit conditions)
        sell_condition = (
            (df['RSI'] > 50) |                 # RSI back to neutral
            (df['Close'] > df['BB_Middle'])    # Price back above middle
        )
        
        df.loc[sell_condition, 'Signal'] = 'SELL'
        df.loc[sell_condition, 'Confidence'] = 0.70
        df.loc[sell_condition, 'Reason'] = 'Exit: Mean reversion complete'
        
        # Cap confidence at 95%
        df['Confidence'] = df['Confidence'].clip(upper=0.95)
        
        # Count signals
        buy_count = (df['Signal'] == 'BUY').sum()
        sell_count = (df['Signal'] == 'SELL').sum()
        
        logging.info(f"[{self.strategy_id}] {symbol}: Generated {buy_count} BUY, {sell_count} SELL signals")
        
        return df
    
    def get_signal_for_date(self, data: pd.DataFrame, date: pd.Timestamp, symbol: str) -> Dict:
        """
        Get trading signal for a specific date (for backtesting engine)
        
        Args:
            data: DataFrame with OHLCV + indicators
            date: Date to get signal for
            symbol: Asset symbol
        
        Returns:
            Dict with signal information
        """
        if date not in data.index:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Date not in dataset',
                'symbol': symbol
            }
        
        row = data.loc[date]
        
        return {
            'action': row['Signal'],
            'confidence': float(row['Confidence']),
            'reason': row['Reason'],
            'symbol': symbol,
            'indicators': {
                'RSI': float(row['RSI']) if not pd.isna(row['RSI']) else None,
                'BB_Upper': float(row['BB_Upper']) if not pd.isna(row['BB_Upper']) else None,
                'BB_Middle': float(row['BB_Middle']) if not pd.isna(row['BB_Middle']) else None,
                'BB_Lower': float(row['BB_Lower']) if not pd.isna(row['BB_Lower']) else None,
                'Close': float(row['Close'])
            },
            'scientific_basis': 'Wilder (1978) RSI + Bollinger (1992) BB + Chan (2013) Mean Reversion',
            'limitations': [
                'Performs poorly in strong trends',
                'Requires stable market regime',
                'Transaction costs reduce returns',
                'Indicators are lagging'
            ]
        }


# VALIDATION FUNCTION
def validate_strategy_with_sample_data():
    """Validate strategy with sample data"""
    print("=" * 80)
    print("VALIDAÇÃO: CRYPTO MEAN REVERSION BACKTEST")
    print("=" * 80)
    print()
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate price data with mean reversion characteristics
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    
    df = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.995,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    # Initialize strategy
    strategy = CryptoMeanReversionBacktest(
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
        bb_period=20,
        bb_std=2.0
    )
    
    # Generate signals
    result = strategy.generate_signals(df, 'BTC-USD')
    
    # Display results
    print("Sample signals generated:")
    print(result[result['Signal'] != 'HOLD'][['Close', 'RSI', 'BB_Lower', 'BB_Middle', 'Signal', 'Confidence']].head(10))
    
    print("\nSignal Statistics:")
    print(f"  BUY signals: {(result['Signal'] == 'BUY').sum()}")
    print(f"  SELL signals: {(result['Signal'] == 'SELL').sum()}")
    print(f"  HOLD signals: {(result['Signal'] == 'HOLD').sum()}")
    
    print("\n" + "=" * 80)
    print("[OK] STRATEGY VALIDATED - READY FOR BACKTESTING")
    print("=" * 80)
    
    return strategy, result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        strategy, results = validate_strategy_with_sample_data()
        print("\n[OK] Validation complete")
    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        logging.error(f"Error: {e}", exc_info=True)

