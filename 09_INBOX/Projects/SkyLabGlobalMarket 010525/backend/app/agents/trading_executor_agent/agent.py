from typing import Dict, Any, List
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.models.trade import Trade
from app.models.portfolio import Portfolio
from .mt5_integration import MT5Integration

class TradingExecutorAgent(BaseAgent):
    """Agent responsible for executing trades and managing trading operations."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "trading_executor")
        self.mt5 = MT5Integration()
        self.pending_trades: List[Dict[str, Any]] = []
    
    async def initialize(self) -> None:
        """Initialize the trading executor agent."""
        self.update_status("initializing")
        await self.mt5.initialize()
        self.update_status("ready")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process trading execution tasks."""
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")
            
            self.update_status("processing")
            
            action = data.get("action")
            
            if action == "execute":
                result = await self._handle_execution(data)
            elif action == "cancel":
                result = await self._handle_cancellation(data)
            elif action == "status":
                result = await self._handle_status_check(data)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            self.update_status("idle")
            return result
            
        except Exception as e:
            self.update_status("error")
            return await self.handle_error(e)
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        self.update_status("shutting_down")
        await self.mt5.shutdown()
        self.update_status("stopped")
    
    async def _handle_execution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trade execution."""
        trade_data = data.get("trade")
        if not trade_data:
            raise ValueError("Missing trade data")
        
        # Validate trade parameters
        if not self._validate_trade(trade_data):
            raise ValueError("Invalid trade parameters")
        
        # Execute trade through MT5
        execution_result = await self.mt5.execute_trade(
            symbol=trade_data["symbol"],
            volume=trade_data["volume"],
            trade_type=trade_data["type"],
            price=trade_data.get("price"),
            stop_loss=trade_data.get("stop_loss"),
            take_profit=trade_data.get("take_profit")
        )
        
        # Create trade record
        trade = Trade(
            portfolio_id=trade_data["portfolio_id"],
            symbol=trade_data["symbol"],
            trade_type=trade_data["type"],
            volume=trade_data["volume"],
            price=execution_result["price"],
            stop_loss=trade_data.get("stop_loss"),
            take_profit=trade_data.get("take_profit"),
            status="executed",
            execution_time=datetime.utcnow()
        )
        
        # TODO: Save trade to database
        
        return {
            "trade_id": trade.id,
            "status": "executed",
            "execution_result": execution_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_cancellation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trade cancellation."""
        trade_id = data.get("trade_id")
        if not trade_id:
            raise ValueError("Missing trade_id")
        
        # TODO: Retrieve trade from database
        trade = None
        
        if not trade:
            raise ValueError("Trade not found")
        
        if trade.status != "pending":
            raise ValueError("Can only cancel pending trades")
        
        # Cancel trade through MT5
        cancellation_result = await self.mt5.cancel_trade(trade_id)
        
        # Update trade status
        trade.status = "cancelled"
        trade.cancellation_time = datetime.utcnow()
        
        # TODO: Update trade in database
        
        return {
            "trade_id": trade_id,
            "status": "cancelled",
            "cancellation_result": cancellation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_status_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trade status check."""
        trade_id = data.get("trade_id")
        if not trade_id:
            raise ValueError("Missing trade_id")
        
        # TODO: Retrieve trade from database
        trade = None
        
        if not trade:
            raise ValueError("Trade not found")
        
        # Check trade status through MT5
        status_result = await self.mt5.check_trade_status(trade_id)
        
        return {
            "trade_id": trade_id,
            "status": status_result["status"],
            "details": status_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _validate_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Validate trade parameters."""
        required_fields = ["symbol", "volume", "type", "portfolio_id"]
        
        # Check required fields
        if not all(field in trade_data for field in required_fields):
            return False
        
        # Validate trade type
        if trade_data["type"] not in ["buy", "sell"]:
            return False
        
        # Validate volume
        if trade_data["volume"] <= 0:
            return False
        
        # Validate price if provided
        if "price" in trade_data and trade_data["price"] <= 0:
            return False
        
        # Validate stop loss and take profit if provided
        if "stop_loss" in trade_data and trade_data["stop_loss"] <= 0:
            return False
        if "take_profit" in trade_data and trade_data["take_profit"] <= 0:
            return False
        
        return True 