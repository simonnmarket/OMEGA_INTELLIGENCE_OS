from typing import Optional, Dict, List
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from ..core.database import Database

class AnalystAgent:
    """Market analysis agent."""
    
    def __init__(self, database: Database):
        """Initialize AnalystAgent with database connection."""
        self.db = database
        self.logger = logging.getLogger(__name__)
        
    def analyze_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze trading performance for a given period."""
        try:
            # Get transactions for the period
            transactions = self.db.get_transactions({
                'timestamp': {'$gte': start_date, '$lte': end_date}
            })
            
            if not transactions:
                return {}
                
            # Calculate performance metrics
            total_trades = len(transactions)
            winning_trades = sum(1 for t in transactions if t.profit > 0)
            losing_trades = total_trades - winning_trades
            
            total_profit = sum(t.profit for t in transactions if t.profit > 0)
            total_loss = abs(sum(t.profit for t in transactions if t.profit < 0))
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
            
            # Calculate risk metrics
            returns = [t.profit for t in transactions]
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            max_drawdown = self._calculate_max_drawdown(returns)
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_loss': total_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            }
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {str(e)}")
            return {}
            
    def analyze_market_conditions(self, symbol: str, timeframe: str) -> Dict:
        """Analyze current market conditions."""
        try:
            # Get market data
            market_data = self.db.get_market_data(symbol, timeframe, 100)
            if not market_data:
                return {}
                
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': m.timestamp,
                'open': m.open_price,
                'high': m.high_price,
                'low': m.low_price,
                'close': m.close_price,
                'volume': m.volume
            } for m in market_data])
            
            # Calculate technical indicators
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            df['macd'], df['signal'] = self._calculate_macd(df['close'])
            
            # Analyze market conditions
            conditions = {
                'trend': self._analyze_trend(df),
                'momentum': self._analyze_momentum(df),
                'volatility': self._analyze_volatility(df),
                'volume': self._analyze_volume(df),
                'support_resistance': self._find_support_resistance(df)
            }
            
            return conditions
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {str(e)}")
            return {}
            
    def generate_signals(self, symbol: str, timeframe: str) -> Dict:
        """Generate trading signals based on analysis."""
        try:
            conditions = self.analyze_market_conditions(symbol, timeframe)
            if not conditions:
                return {}
                
            signals = {
                'entry': self._generate_entry_signals(conditions),
                'exit': self._generate_exit_signals(conditions),
                'strength': self._calculate_signal_strength(conditions)
            }
            
            return signals
        except Exception as e:
            self.logger.error(f"Error generating signals: {str(e)}")
            return {}
            
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if not returns:
            return 0.0
            
        returns = np.array(returns)
        mean_return = np.mean(returns)
        std_dev = np.std(returns)
        
        if std_dev == 0:
            return 0.0
            
        return (mean_return - risk_free_rate) / std_dev
        
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not returns:
            return 0.0
            
        returns = np.array(returns)
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (running_max - cumulative) / running_max
        
        return np.max(drawdown) if len(drawdown) > 0 else 0.0
        
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD indicator."""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line
        
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze market trend."""
        if df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
            return 'uptrend'
        elif df['sma_20'].iloc[-1] < df['sma_50'].iloc[-1]:
            return 'downtrend'
        return 'sideways'
        
    def _analyze_momentum(self, df: pd.DataFrame) -> str:
        """Analyze market momentum."""
        if df['rsi'].iloc[-1] > 70:
            return 'overbought'
        elif df['rsi'].iloc[-1] < 30:
            return 'oversold'
        return 'neutral'
        
    def _analyze_volatility(self, df: pd.DataFrame) -> float:
        """Calculate market volatility."""
        return df['close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
        
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze trading volume."""
        avg_volume = df['volume'].mean()
        current_volume = df['volume'].iloc[-1]
        
        if current_volume > avg_volume * 1.5:
            return 'high'
        elif current_volume < avg_volume * 0.5:
            return 'low'
        return 'normal'
        
    def _find_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Find support and resistance levels."""
        highs = df['high'].rolling(window=window).max()
        lows = df['low'].rolling(window=window).min()
        
        return {
            'support': lows.iloc[-1],
            'resistance': highs.iloc[-1]
        }
        
    def _generate_entry_signals(self, conditions: Dict) -> List[str]:
        """Generate entry signals based on market conditions."""
        signals = []
        
        if conditions['trend'] == 'uptrend' and conditions['momentum'] == 'oversold':
            signals.append('buy')
        elif conditions['trend'] == 'downtrend' and conditions['momentum'] == 'overbought':
            signals.append('sell')
            
        return signals
        
    def _generate_exit_signals(self, conditions: Dict) -> List[str]:
        """Generate exit signals based on market conditions."""
        signals = []
        
        if conditions['trend'] == 'uptrend' and conditions['momentum'] == 'overbought':
            signals.append('sell')
        elif conditions['trend'] == 'downtrend' and conditions['momentum'] == 'oversold':
            signals.append('buy')
            
        return signals
        
    def _calculate_signal_strength(self, conditions: Dict) -> float:
        """Calculate signal strength based on multiple factors."""
        strength = 0.0
        
        # Trend strength
        if conditions['trend'] in ['uptrend', 'downtrend']:
            strength += 0.3
            
        # Momentum strength
        if conditions['momentum'] in ['overbought', 'oversold']:
            strength += 0.3
            
        # Volume strength
        if conditions['volume'] == 'high':
            strength += 0.2
            
        # Volatility strength
        if conditions['volatility'] > 0.2:  # High volatility
            strength += 0.2
            
        return min(strength, 1.0)  # Cap at 1.0 