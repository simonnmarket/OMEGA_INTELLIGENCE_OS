from typing import Optional, Dict, List
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from ..api.mt5_connector import MT5Connector
from ..core.database import Database

class TraderBot:
    """Trading execution agent."""
    
    def __init__(self, mt5_connector: MT5Connector, database: Database):
        """Initialize TraderBot with MT5 connection and database."""
        self.mt5 = mt5_connector
        self.db = database
        self.logger = logging.getLogger(__name__)
        self.positions = {}
        
    def fetch_market_data(self, symbol: str, timeframe: int, count: int) -> Optional[pd.DataFrame]:
        """Fetch market data from MT5."""
        try:
            data = self.mt5.get_market_data(symbol, timeframe, count)
            if data is not None:
                # Store in database
                for _, row in data.iterrows():
                    market_data = {
                        'symbol': symbol,
                        'timestamp': row['time'],
                        'open_price': row['open'],
                        'high_price': row['high'],
                        'low_price': row['low'],
                        'close_price': row['close'],
                        'volume': row['tick_volume'],
                        'timeframe': timeframe
                    }
                    self.db.add_market_data(market_data)
                return data
            return None
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
            
    def analyze_market(self, data: pd.DataFrame) -> Dict:
        """Analyze market data for trading signals."""
        try:
            # Calculate technical indicators
            data['sma_20'] = data['close'].rolling(window=20).mean()
            data['sma_50'] = data['close'].rolling(window=50).mean()
            data['rsi'] = self._calculate_rsi(data['close'])
            
            # Generate signals
            signals = {
                'trend': self._analyze_trend(data),
                'momentum': self._analyze_momentum(data),
                'volatility': self._analyze_volatility(data)
            }
            
            return signals
        except Exception as e:
            self.logger.error(f"Error analyzing market: {str(e)}")
            return {}
            
    def execute_trade(self, symbol: str, action: str, volume: float, 
                     sl: float = 0.0, tp: float = 0.0) -> Optional[Dict]:
        """Execute a trade based on analysis."""
        try:
            # Get current price
            current_price = self.mt5.get_market_data(symbol, mt5.TIMEFRAME_M1, 1)['close'].iloc[0]
            
            # Check if position already exists
            if symbol in self.positions:
                self.logger.warning(f"Position already exists for {symbol}")
                return None
                
            # Execute trade
            result = self.mt5.send_order(symbol, action, volume, current_price, sl, tp)
            if result:
                # Record transaction
                transaction = {
                    'symbol': symbol,
                    'action': action,
                    'entry_price': current_price,
                    'volume': volume,
                    'risk': abs(sl - current_price) * volume if sl else 0.0,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'magic_number': 100,
                    'comment': f"Trade executed by TraderBot"
                }
                self.db.add_transaction(transaction)
                
                # Update positions
                self.positions[symbol] = {
                    'ticket': result['ticket'],
                    'type': action,
                    'price': current_price,
                    'volume': volume,
                    'sl': sl,
                    'tp': tp
                }
                
                return result
            return None
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            return None
            
    def close_position(self, symbol: str) -> bool:
        """Close an existing position."""
        try:
            if symbol not in self.positions:
                self.logger.warning(f"No position found for {symbol}")
                return False
                
            position = self.positions[symbol]
            current_price = self.mt5.get_market_data(symbol, mt5.TIMEFRAME_M1, 1)['close'].iloc[0]
            
            # Execute opposite trade to close
            action = 'sell' if position['type'] == 'buy' else 'buy'
            result = self.mt5.send_order(symbol, action, position['volume'], current_price)
            
            if result:
                # Update transaction
                self.db.update_transaction(position['ticket'], {
                    'exit_price': current_price,
                    'profit': (current_price - position['price']) * position['volume'] * 
                             (-1 if position['type'] == 'buy' else 1),
                    'status': 'closed'
                })
                
                # Remove from positions
                del self.positions[symbol]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            return False
            
    def monitor_positions(self) -> None:
        """Monitor and manage open positions."""
        try:
            for symbol, position in list(self.positions.items()):
                current_price = self.mt5.get_market_data(symbol, mt5.TIMEFRAME_M1, 1)['close'].iloc[0]
                
                # Check stop loss
                if position['sl'] and (
                    (position['type'] == 'buy' and current_price <= position['sl']) or
                    (position['type'] == 'sell' and current_price >= position['sl'])
                ):
                    self.logger.info(f"Stop loss triggered for {symbol}")
                    self.close_position(symbol)
                    
                # Check take profit
                elif position['tp'] and (
                    (position['type'] == 'buy' and current_price >= position['tp']) or
                    (position['type'] == 'sell' and current_price <= position['tp'])
                ):
                    self.logger.info(f"Take profit triggered for {symbol}")
                    self.close_position(symbol)
        except Exception as e:
            self.logger.error(f"Error monitoring positions: {str(e)}")
            
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def _analyze_trend(self, data: pd.DataFrame) -> str:
        """Analyze market trend."""
        if data['sma_20'].iloc[-1] > data['sma_50'].iloc[-1]:
            return 'uptrend'
        elif data['sma_20'].iloc[-1] < data['sma_50'].iloc[-1]:
            return 'downtrend'
        return 'sideways'
        
    def _analyze_momentum(self, data: pd.DataFrame) -> str:
        """Analyze market momentum."""
        if data['rsi'].iloc[-1] > 70:
            return 'overbought'
        elif data['rsi'].iloc[-1] < 30:
            return 'oversold'
        return 'neutral'
        
    def _analyze_volatility(self, data: pd.DataFrame) -> float:
        """Calculate market volatility."""
        return data['close'].pct_change().std() * np.sqrt(252)  # Annualized volatility 