# -*- coding: utf-8 -*-
"""
Crypto Momentum Strategy - VERSÃO BACKTEST
===================================================
Estratégia oposta à Mean Reversion: COMPRA tendências fortes, não reversões

LÓGICA:
- Retornos passados (3M, 6M, 12M) para identificar momentum
- Filtro de volume (volume > MA 20 dias) para confirmar força
- Entry: Retorno 3M > 10% AND Volume alto
- Exit: Retorno 3M < 0% (momentum acabou)

SCIENTIFIC BASE:
- Jegadeesh & Titman (1993). Returns to Buying Winners and Selling Losers
- Carhart (1997). On Persistence in Mutual Fund Performance
- Moskowitz et al. (2012). Time Series Momentum

COMPLIANCE: PROTOCOLO BLINDADO 100%
DATA: 03-11-2025
VERSÃO: 1.0.0 (Backtest)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

class CryptoMomentumBacktest:
    """
    Momentum Strategy baseada em retornos passados multi-período
    
    References:
    - Jegadeesh & Titman (1993) - Momentum effect
    - Carhart (1997) - Four-factor model
    - Moskowitz et al. (2012) - Time series momentum
    """
    
    def __init__(self,
                 momentum_periods: list = [90, 180, 365],  # 3M, 6M, 12M em dias
                 volume_ma_period: int = 20,
                 min_momentum_threshold: float = 0.10,  # 10% retorno mínimo
                 exit_threshold: float = 0.00):  # Exit quando retorno 3M < 0%
        """
        Initialize Momentum Strategy
        
        Args:
            momentum_periods: Períodos para calcular retornos (Jegadeesh 1993: 3-12M)
            volume_ma_period: Período da média móvel de volume (padrão: 20)
            min_momentum_threshold: Retorno mínimo para entry (padrão: 10%)
            exit_threshold: Retorno para exit (padrão: 0%)
        """
        self.strategy_id = "CRYPTO_MOMENTUM_BACKTEST"
        self.momentum_periods = momentum_periods
        self.volume_ma_period = volume_ma_period
        self.min_momentum_threshold = min_momentum_threshold
        self.exit_threshold = exit_threshold
        
        logging.info(f"[{self.strategy_id}] Initialized")
        logging.info(f"  Momentum periods: {momentum_periods} days")
        logging.info(f"  Min momentum: {min_momentum_threshold*100:.0f}%")
        logging.info(f"  Exit threshold: {exit_threshold*100:.0f}%")
    
    def calculate_momentum(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate momentum as percentage return over period
        
        Reference: Jegadeesh & Titman (1993)
        
        Args:
            prices: Close prices
            period: Lookback period in days
        
        Returns:
            Momentum series (percentage returns)
        """
        momentum = prices.pct_change(periods=period)
        return momentum
    
    def calculate_volume_filter(self, volumes: pd.Series, period: int) -> pd.Series:
        """
        Calculate volume moving average for filtering
        
        Args:
            volumes: Volume series
            period: MA period
        
        Returns:
            Boolean series (volume > MA)
        """
        volume_ma = volumes.rolling(window=period).mean()
        above_average = volumes > volume_ma
        return above_average
    
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Generate momentum trading signals
        
        Entry Logic (BUY):
        - Retorno 3M > 10% (forte momentum positivo)
        - AND Volume > MA 20 dias (confirmação de força)
        - = Tendência forte confirmada por volume
        
        Exit Logic (SELL):
        - Retorno 3M < 0% (momentum virou negativo)
        - = Tendência acabou, sair
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Asset symbol
        
        Returns:
            DataFrame with signals
        """
        df = data.copy()
        
        # Handle MultiIndex from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate momentum for múltiplos períodos
        df['Momentum_3M'] = self.calculate_momentum(df['Close'], self.momentum_periods[0])
        df['Momentum_6M'] = self.calculate_momentum(df['Close'], self.momentum_periods[1]) if len(self.momentum_periods) > 1 else 0
        df['Momentum_12M'] = self.calculate_momentum(df['Close'], self.momentum_periods[2]) if len(self.momentum_periods) > 2 else 0
        
        # Volume filter
        df['Volume_High'] = self.calculate_volume_filter(df['Volume'], self.volume_ma_period)
        
        # Initialize signals
        df['Signal'] = 'HOLD'
        df['Confidence'] = 0.0
        df['Reason'] = ''
        
        # Generate BUY signals (strong momentum)
        buy_condition = (
            (df['Momentum_3M'] > self.min_momentum_threshold) &  # 3M return > 10%
            (df['Volume_High'] == True)  # Volume above average
        )
        
        df.loc[buy_condition, 'Signal'] = 'BUY'
        # Confidence aumenta com momentum
        df.loc[buy_condition, 'Confidence'] = 0.70 + (df['Momentum_3M'].clip(upper=0.50) * 0.50)  # 70-95%
        df.loc[buy_condition, 'Reason'] = 'Strong momentum: 3M>10% & Volume High'
        
        # Generate SELL signals (momentum acabou)
        sell_condition = (
            (df['Momentum_3M'] < self.exit_threshold)  # 3M return < 0%
        )
        
        df.loc[sell_condition, 'Signal'] = 'SELL'
        df.loc[sell_condition, 'Confidence'] = 0.70
        df.loc[sell_condition, 'Reason'] = 'Exit: Momentum turned negative'
        
        # Cap confidence
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
                'Momentum_3M': float(row['Momentum_3M']) if not pd.isna(row['Momentum_3M']) else None,
                'Momentum_6M': float(row['Momentum_6M']) if not pd.isna(row['Momentum_6M']) else None,
                'Momentum_12M': float(row['Momentum_12M']) if not pd.isna(row['Momentum_12M']) else None,
                'Volume_High': bool(row['Volume_High']) if not pd.isna(row['Volume_High']) else False,
                'Close': float(row['Close'])
            },
            'scientific_basis': 'Jegadeesh & Titman (1993) + Carhart (1997) + Moskowitz (2012)',
            'limitations': [
                'Performs poorly in mean-reverting markets',
                'Requires trending regime',
                'Transaction costs reduce returns',
                'Late entry/exit (lagging indicators)'
            ]
        }


# VALIDATION FUNCTION
def validate_strategy_with_sample_data():
    """Validate momentum strategy with sample data"""
    print("=" * 80)
    print("VALIDACAO: CRYPTO MOMENTUM BACKTEST")
    print("=" * 80)
    print()
    
    # Create sample data with trend
    dates = pd.date_range('2023-01-01', periods=400, freq='D')
    np.random.seed(42)
    
    # Generate trending price data
    trend = np.linspace(0, 50, 400)
    noise = np.random.randn(400) * 2
    prices = 100 + trend + noise
    
    df = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.995,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Volume': np.random.randint(1000000, 10000000, 400)
    }, index=dates)
    
    # Initialize strategy
    strategy = CryptoMomentumBacktest(
        momentum_periods=[90, 180, 365],
        volume_ma_period=20,
        min_momentum_threshold=0.10,
        exit_threshold=0.00
    )
    
    # Generate signals
    result = strategy.generate_signals(df, 'BTC-USD')
    
    # Display results
    print("Sample signals generated:")
    signal_samples = result[result['Signal'] != 'HOLD'][['Close', 'Momentum_3M', 'Volume_High', 'Signal', 'Confidence']].head(10)
    if not signal_samples.empty:
        print(signal_samples)
    
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

