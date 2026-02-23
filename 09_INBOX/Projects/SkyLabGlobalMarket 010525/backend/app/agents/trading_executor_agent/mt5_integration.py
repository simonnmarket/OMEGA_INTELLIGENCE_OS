import MetaTrader5 as mt5
from typing import Dict, Any, Optional
import logging

class MT5Integration:
    """Integration with MetaTrader 5 trading platform."""
    
    def __init__(self):
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize connection to MetaTrader 5."""
        if not mt5.initialize():
            error = mt5.last_error()
            self.logger.error(f"Failed to initialize MT5: {error}")
            raise ConnectionError(f"Failed to initialize MT5: {error}")
        
        self.initialized = True
        self.logger.info("Successfully initialized MT5 connection")
    
    async def shutdown(self) -> None:
        """Shutdown connection to MetaTrader 5."""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            self.logger.info("Successfully shutdown MT5 connection")
    
    async def execute_trade(
        self,
        symbol: str,
        volume: float,
        trade_type: str,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a trade through MetaTrader 5."""
        if not self.initialized:
            raise ConnectionError("MT5 not initialized")
        
        # Get symbol information
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise ValueError(f"Symbol {symbol} not found")
        
        # Prepare trade request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if trade_type == "buy" else mt5.ORDER_TYPE_SELL,
            "price": price or (symbol_info.ask if trade_type == "buy" else symbol_info.bid),
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 234000,
            "comment": "Python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send trade request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error = mt5.last_error()
            self.logger.error(f"Trade execution failed: {error}")
            raise RuntimeError(f"Trade execution failed: {error}")
        
        return {
            "order_id": result.order,
            "price": result.price,
            "volume": result.volume,
            "status": "executed"
        }
    
    async def cancel_trade(self, order_id: int) -> Dict[str, Any]:
        """Cancel a pending order."""
        if not self.initialized:
            raise ConnectionError("MT5 not initialized")
        
        # Prepare cancel request
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order_id,
            "comment": "Order cancelled by Python script"
        }
        
        # Send cancel request
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error = mt5.last_error()
            self.logger.error(f"Order cancellation failed: {error}")
            raise RuntimeError(f"Order cancellation failed: {error}")
        
        return {
            "order_id": order_id,
            "status": "cancelled"
        }
    
    async def check_trade_status(self, order_id: int) -> Dict[str, Any]:
        """Check the status of an order."""
        if not self.initialized:
            raise ConnectionError("MT5 not initialized")
        
        # Get order information
        order = mt5.order_get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        
        return {
            "order_id": order_id,
            "symbol": order.symbol,
            "volume": order.volume,
            "price": order.price,
            "type": "buy" if order.type == mt5.ORDER_TYPE_BUY else "sell",
            "status": self._get_order_status(order.state),
            "time": order.time_setup
        }
    
    def _get_order_status(self, state: int) -> str:
        """Convert MT5 order state to status string."""
        status_map = {
            mt5.ORDER_STATE_STARTED: "started",
            mt5.ORDER_STATE_PLACED: "placed",
            mt5.ORDER_STATE_CANCELED: "cancelled",
            mt5.ORDER_STATE_PARTIAL: "partial",
            mt5.ORDER_STATE_FILLED: "filled",
            mt5.ORDER_STATE_REJECTED: "rejected",
            mt5.ORDER_STATE_EXPIRED: "expired",
            mt5.ORDER_STATE_REQUEST_ADD: "request_add",
            mt5.ORDER_STATE_REQUEST_MODIFY: "request_modify",
            mt5.ORDER_STATE_REQUEST_CANCEL: "request_cancel"
        }
        return status_map.get(state, "unknown")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        if not self.initialized:
            raise ConnectionError("MT5 not initialized")
        
        account_info = mt5.account_info()
        if account_info is None:
            error = mt5.last_error()
            self.logger.error(f"Failed to get account info: {error}")
            raise RuntimeError(f"Failed to get account info: {error}")
        
        return {
            "login": account_info.login,
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "free_margin": account_info.margin_free,
            "margin_level": account_info.margin_level,
            "currency": account_info.currency,
            "leverage": account_info.leverage
        }
    
    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information."""
        if not self.initialized:
            raise ConnectionError("MT5 not initialized")
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise ValueError(f"Symbol {symbol} not found")
        
        return {
            "symbol": symbol_info.name,
            "bid": symbol_info.bid,
            "ask": symbol_info.ask,
            "spread": symbol_info.spread,
            "volume_min": symbol_info.volume_min,
            "volume_max": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "digits": symbol_info.digits,
            "trade_mode": symbol_info.trade_mode,
            "trade_exemode": symbol_info.trade_exemode,
            "trade_calcmode": symbol_info.trade_calcmode
        } 