import MetaTrader5 as mt5
import pandas as pd
from typing import Optional, Dict, List, Union
import logging
from datetime import datetime

class MT5Connector:
    def __init__(self, login: int, password: str, server: str):
        """Initialize MT5 connection with credentials."""
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Establish connection to MT5."""
        try:
            if not mt5.initialize():
                self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
                
            if not mt5.login(self.login, password=self.password, server=self.server):
                self.logger.error(f"MT5 login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
                
            self.connected = True
            self.logger.info("Successfully connected to MT5")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False
            
    def disconnect(self) -> None:
        """Close MT5 connection."""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MT5")
            
    def get_market_data(self, symbol: str, timeframe: int, count: int) -> Optional[pd.DataFrame]:
        """Get historical market data."""
        if not self.connected:
            self.logger.error("Not connected to MT5")
            return None
            
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                self.logger.error(f"Failed to get rates: {mt5.last_error()}")
                return None
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None
            
    def get_account_info(self) -> Optional[Dict]:
        """Get account information."""
        if not self.connected:
            self.logger.error("Not connected to MT5")
            return None
            
        try:
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.error(f"Failed to get account info: {mt5.last_error()}")
                return None
                
            return {
                'login': account_info.login,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level
            }
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None
            
    def get_positions(self) -> Optional[List[Dict]]:
        """Get open positions."""
        if not self.connected:
            self.logger.error("Not connected to MT5")
            return None
            
        try:
            positions = mt5.positions_get()
            if positions is None:
                self.logger.error(f"Failed to get positions: {mt5.last_error()}")
                return None
                
            return [{
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'buy' if pos.type == mt5.POSITION_TYPE_BUY else 'sell',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'swap': pos.swap
            } for pos in positions]
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return None
            
    def send_order(self, symbol: str, order_type: str, volume: float, 
                  price: float, sl: float = 0.0, tp: float = 0.0) -> Optional[Dict]:
        """Send order to MT5."""
        if not self.connected:
            self.logger.error("Not connected to MT5")
            return None
            
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 100,
                "comment": "Order from SkyLab Global Market",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Order failed: {result.comment}")
                return None
                
            return {
                'ticket': result.order,
                'price': result.price,
                'volume': result.volume,
                'comment': result.comment
            }
            
        except Exception as e:
            self.logger.error(f"Error sending order: {str(e)}")
            return None 