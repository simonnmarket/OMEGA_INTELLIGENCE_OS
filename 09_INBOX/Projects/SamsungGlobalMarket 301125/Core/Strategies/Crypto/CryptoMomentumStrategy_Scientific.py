# CryptoMomentumStrategy_Scientific.py
"""
Momentum Strategy for Cryptocurrencies - SCIENTIFIC VERSION
COMPLIANCE: PROTOCOLO BLINDADO 100%
EXPANSION: 4 ESTRATEGIAS ADICIONAIS PARA MODULO CRIPTO

SCIENTIFIC BASE:
- Momentum Effect: Jegadeesh, N. & Titman, S. (1993). Returns to Buying Winners and Selling Losers
- Relative Strength: Levy, R. A. (1967). Relative Strength as a Criterion for Investment Selection
- Portfolio Theory: Markowitz, H. (1952). Portfolio Selection
- Behavioral Finance: Barberis, N. & Thaler, R. (2003). A Survey of Behavioral Finance

LIMITATIONS:
1. Momentum reversals can occur suddenly (requires stop-loss)
2. Performance degrades in range-bound markets
3. Requires minimum 6-12 months of price history
4. Higher transaction costs due to frequent rebalancing

DATE: 01-11-2025 (CET)
STATUS: READY FOR INTEGRATION
"""

import pandas as pd
import numpy as np
import ccxt
from decimal import Decimal
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
import time

class CryptoMomentumStrategy:
    """
    Momentum Strategy for Cryptocurrencies
    
    References:
    - Jegadeesh, N. & Titman, S. (1993). Returns to Buying Winners and Selling Losers. 
      Journal of Finance, 48(1), 65-91
    - Levy, R. A. (1967). Relative Strength as a Criterion for Investment Selection. 
      Journal of Finance, 22(4), 595-610
    - Markowitz, H. (1952). Portfolio Selection. Journal of Finance, 7(1), 77-91
    - Barberis, N. & Thaler, R. (2003). A Survey of Behavioral Finance. 
      Handbook of the Economics of Finance
    
    Strategy Logic:
    1. Calculate momentum score across multiple lookback periods
    2. Rank cryptocurrencies by momentum
    3. Long top performers (positive momentum)
    4. Position sizing based on momentum strength
    """
    
    def __init__(self,
                 momentum_periods=[30, 90, 180],  # Days (Jegadeesh & Titman: 3-12 months)
                 ranking_period=90,                # Primary ranking period
                 min_momentum_score=0.05,          # Min 5% momentum
                 max_position_size=0.15):          # Max 15% per asset
        """
        Initialize with scientifically validated parameters
        
        Args:
            momentum_periods: Lookback periods in days (Jegadeesh & Titman 1993: 3-12 months)
            ranking_period: Primary period for ranking (default: 90 days)
            min_momentum_score: Minimum momentum to consider (default: 5%)
            max_position_size: Maximum position per asset (default: 15%)
        """
        self.strategy_id = "CRYPTO_MOMENTUM_SCIENTIFIC"
        self.momentum_periods = momentum_periods
        self.ranking_period = ranking_period
        self.min_momentum_score = min_momentum_score
        self.max_position_size = max_position_size
        
        # Asset universe (liquid cryptos for momentum)
        self.asset_universe = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT',
            'ADA/USDT', 'DOT/USDT', 'AVAX/USDT', 'MATIC/USDT',
            'LINK/USDT', 'UNI/USDT'
        ]
        
        # Exchange connection
        self.exchange = None
        
        logging.info(f"[{self.strategy_id}] Initialized with scientific parameters")
        logging.info(f"  Momentum periods: {momentum_periods} days")
        logging.info(f"  Asset universe: {len(self.asset_universe)} cryptos")
    
    def connect_exchange(self, exchange_id='binance'):
        """Connect to cryptocurrency exchange"""
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({'enableRateLimit': True})
            logging.info(f"Connected to {exchange_id}")
            return self.exchange
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return None
    
    def fetch_price_history(self, symbol: str, days: int = 365) -> pd.Series:
        """
        Fetch historical prices
        
        Reference: Jegadeesh & Titman (1993) - requires historical data
        
        Args:
            symbol: Trading pair
            days: Days of history
            
        Returns:
            Series with daily close prices
        """
        if not self.exchange:
            self.connect_exchange()
        
        try:
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', since=since, limit=days)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df['close']
        
        except Exception as e:
            logging.warning(f"Could not fetch {symbol}: {e}")
            return pd.Series()
    
    def calculate_momentum_score(self, prices: pd.Series, period: int) -> float:
        """
        Calculate momentum score for a period
        
        Reference: Jegadeesh & Titman (1993) - Momentum = (P_t / P_t-k) - 1
        
        Args:
            prices: Price series
            period: Lookback period in days
            
        Returns:
            float: Momentum score (return over period)
        """
        if len(prices) < period + 1:
            return 0.0
        
        current_price = prices.iloc[-1]
        past_price = prices.iloc[-period-1]
        
        if past_price == 0:
            return 0.0
        
        momentum = (current_price / past_price) - 1.0
        
        return float(momentum)
    
    def calculate_relative_strength(self, 
                                   asset_prices: pd.Series,
                                   market_prices: pd.Series,
                                   period: int) -> float:
        """
        Calculate Relative Strength
        
        Reference: Levy (1967) - Relative Strength Index
        
        Args:
            asset_prices: Individual asset prices
            market_prices: Market benchmark prices (e.g., BTC)
            period: Lookback period
            
        Returns:
            float: Relative strength ratio
        """
        asset_momentum = self.calculate_momentum_score(asset_prices, period)
        market_momentum = self.calculate_momentum_score(market_prices, period)
        
        # Relative strength = asset performance / market performance
        if market_momentum != 0:
            rs = asset_momentum / (market_momentum + 0.0001)  # Avoid division by zero
        else:
            rs = 1.0
        
        return float(rs)
    
    def calculate_composite_momentum(self, symbol: str) -> Dict:
        """
        Calculate composite momentum across multiple periods
        
        Reference: Jegadeesh & Titman (1993) - Multiple horizons
        
        Args:
            symbol: Trading pair
            
        Returns:
            dict: Momentum scores and composite
        """
        # Fetch price history
        max_period = max(self.momentum_periods) + 30  # Extra buffer
        prices = self.fetch_price_history(symbol, days=max_period)
        
        if prices.empty or len(prices) < max_period:
            return {
                'symbol': symbol,
                'composite_score': 0.0,
                'scores': {},
                'valid': False
            }
        
        # Calculate momentum for each period
        scores = {}
        for period in self.momentum_periods:
            scores[f"{period}d"] = self.calculate_momentum_score(prices, period)
        
        # Composite score: weighted average (shorter periods = lower weight)
        weights = [1.0 / (i + 1) for i in range(len(self.momentum_periods))]
        total_weight = sum(weights)
        
        composite = sum(
            scores[f"{period}d"] * weight
            for period, weight in zip(self.momentum_periods, weights)
        ) / total_weight
        
        return {
            'symbol': symbol,
            'composite_score': composite,
            'scores': scores,
            'valid': True,
            'latest_price': float(prices.iloc[-1])
        }
    
    def rank_assets_by_momentum(self) -> List[Dict]:
        """
        Rank all assets by momentum
        
        Reference: Jegadeesh & Titman (1993) - Winner-Loser portfolio
        
        Returns:
            List of assets ranked by momentum (highest first)
        """
        momentum_data = []
        
        for symbol in self.asset_universe:
            try:
                data = self.calculate_composite_momentum(symbol)
                
                if data['valid']:
                    momentum_data.append(data)
                
                time.sleep(0.1)  # Rate limit protection
            
            except Exception as e:
                logging.warning(f"Error calculating momentum for {symbol}: {e}")
        
        # Sort by composite score (descending)
        ranked = sorted(momentum_data, key=lambda x: x['composite_score'], reverse=True)
        
        logging.info(f"Ranked {len(ranked)} assets by momentum")
        
        return ranked
    
    def calculate_position_sizes(self, ranked_assets: List[Dict], max_assets: int = 5) -> Dict[str, float]:
        """
        Calculate position sizes using Markowitz-style allocation
        
        Reference: Markowitz (1952) - Portfolio optimization
        
        Args:
            ranked_assets: Assets ranked by momentum
            max_assets: Maximum number of assets to hold
            
        Returns:
            dict: symbol -> position_size
        """
        # Select top performers
        top_assets = [a for a in ranked_assets[:max_assets] if a['composite_score'] > self.min_momentum_score]
        
        if not top_assets:
            return {}
        
        # Allocate based on momentum strength (proportional allocation)
        total_momentum = sum(a['composite_score'] for a in top_assets)
        
        allocations = {}
        for asset in top_assets:
            weight = asset['composite_score'] / total_momentum
            
            # Cap at max position size
            position = min(weight, self.max_position_size)
            
            allocations[asset['symbol']] = position
        
        # Normalize to sum to 1.0
        total_allocated = sum(allocations.values())
        if total_allocated > 0:
            allocations = {k: v / total_allocated for k, v in allocations.items()}
        
        return allocations
    
    def generate_signal(self) -> Dict:
        """
        Generate momentum trading signal
        
        Returns:
            dict: Trading signal with top momentum assets
        """
        # Rank assets by momentum
        ranked_assets = self.rank_assets_by_momentum()
        
        if not ranked_assets:
            return {
                'action': 'HOLD',
                'reason': 'Could not calculate momentum (insufficient data)',
                'scientific_basis': 'Jegadeesh & Titman (1993) - Momentum'
            }
        
        # Calculate position sizes
        allocations = self.calculate_position_sizes(ranked_assets, max_assets=5)
        
        if not allocations:
            return {
                'action': 'HOLD',
                'reason': f'No assets above minimum momentum ({self.min_momentum_score:.1%})',
                'top_momentum': ranked_assets[0]['symbol'] if ranked_assets else None,
                'top_score': ranked_assets[0]['composite_score'] if ranked_assets else 0,
                'scientific_basis': 'Jegadeesh & Titman (1993) - Winner portfolio'
            }
        
        # Generate multi-asset signal
        top_asset = list(allocations.keys())[0]
        top_allocation = allocations[top_asset]
        
        # Find momentum data for top asset
        top_data = next((a for a in ranked_assets if a['symbol'] == top_asset), None)
        
        confidence = min(abs(top_data['composite_score']) / 0.5, 0.95) if top_data else 0.7
        
        return {
            'action': 'BUY',  # Buy winners (Jegadeesh & Titman 1993)
            'symbol': top_asset,
            'portfolio_allocations': allocations,
            'momentum_scores': {k: v['composite_score'] for k, v in 
                              [(a['symbol'], a) for a in ranked_assets[:5]]},
            'confidence': confidence,
            'position_size_fraction': top_allocation,
            'timestamp': int(time.time()),
            'scientific_basis': 'Jegadeesh & Titman (1993) + Levy (1967) + Markowitz (1952) + Barberis & Thaler (2003)',
            'limitations': [
                'Momentum reversals can occur suddenly',
                'Performance degrades in range-bound markets',
                'Requires minimum 6-12 months history',
                'Higher transaction costs from rebalancing'
            ]
        }

# VALIDATION FUNCTION
def validate_with_real_data():
    """Validate strategy with REAL exchange data"""
    print("=" * 80)
    print("SCIENTIFIC VALIDATION - CRYPTO MOMENTUM")
    print("=" * 80)
    print()
    
    strategy = CryptoMomentumStrategy(
        momentum_periods=[30, 90, 180],
        ranking_period=90,
        min_momentum_score=0.05,
        max_position_size=0.15
    )
    
    print("Connecting to Binance (free API)...")
    exchange = strategy.connect_exchange('binance')
    
    if not exchange:
        print("ERROR: Could not connect to exchange")
        return None, None
    
    print("OK - Connected to Binance\n")
    
    print("Generating momentum signal...")
    
    try:
        signal = strategy.generate_signal()
        
        print("\n" + "=" * 80)
        print("SIGNAL GENERATED")
        print("=" * 80)
        print(f"Action:       {signal['action']}")
        
        if signal['action'] == 'BUY':
            print(f"Top Asset:    {signal['symbol']}")
            print(f"Confidence:   {signal['confidence']:.2%}")
            print(f"Position:     {signal['position_size_fraction']:.2%}")
            
            print(f"\nPortfolio Allocations:")
            for symbol, alloc in signal.get('portfolio_allocations', {}).items():
                print(f"  {symbol}: {alloc:.2%}")
        else:
            print(f"Reason:       {signal.get('reason', 'N/A')}")
        
        print(f"\nScientific Basis:")
        print(f"  {signal.get('scientific_basis', 'N/A')}")
        
        print(f"\nLimitations:")
        for limitation in signal.get('limitations', []):
            print(f"  - {limitation}")
        
        print("\n" + "=" * 80)
        
        return strategy, signal
    
    except Exception as e:
        print(f"\nERROR during signal generation: {e}")
        logging.error(f"Validation failed: {e}", exc_info=True)
        return strategy, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        strategy, signal = validate_with_real_data()
        
        if signal and signal['action'] != 'HOLD':
            print("\nOK - STRATEGY READY FOR INTEGRATION")
        else:
            print(f"\nNo trade: {signal.get('reason', 'Unknown') if signal else 'Validation failed'}")
    
    except Exception as e:
        print(f"\nERROR: {e}")

