from typing import Dict, Any, List
from datetime import datetime
from app.agents.base_agent import BaseAgent
from .data_loader import MarketDataLoader

class MarketMonitorAgent(BaseAgent):
    """Agent responsible for monitoring market data and generating alerts."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "market_monitor")
        self.data_loader = MarketDataLoader()
        self.monitored_symbols: List[str] = []
        self.alert_thresholds: Dict[str, float] = {}
    
    async def initialize(self) -> None:
        """Initialize the market monitor agent."""
        self.update_status("initializing")
        await self.data_loader.initialize()
        await self._load_configuration()
        self.update_status("ready")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process market monitoring tasks."""
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")
            
            self.update_status("processing")
            
            action = data.get("action")
            
            if action == "monitor":
                result = await self._handle_monitoring(data)
            elif action == "add_symbol":
                result = await self._handle_add_symbol(data)
            elif action == "remove_symbol":
                result = await self._handle_remove_symbol(data)
            elif action == "update_thresholds":
                result = await self._handle_update_thresholds(data)
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
        await self.data_loader.shutdown()
        self.update_status("stopped")
    
    async def _handle_monitoring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market data monitoring."""
        symbols = data.get("symbols", self.monitored_symbols)
        if not symbols:
            raise ValueError("No symbols to monitor")
        
        # Get market data
        market_data = await self.data_loader.get_market_data(symbols)
        
        # Check for alerts
        alerts = []
        for symbol, data in market_data.items():
            symbol_alerts = await self._check_alerts(symbol, data)
            alerts.extend(symbol_alerts)
        
        return {
            "action": "monitor",
            "market_data": market_data,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_add_symbol(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle adding a symbol to monitor."""
        symbol = data.get("symbol")
        if not symbol:
            raise ValueError("Missing symbol")
        
        if symbol not in self.monitored_symbols:
            self.monitored_symbols.append(symbol)
            # TODO: Save configuration to database
        
        return {
            "action": "add_symbol",
            "symbol": symbol,
            "monitored_symbols": self.monitored_symbols,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_remove_symbol(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle removing a symbol from monitoring."""
        symbol = data.get("symbol")
        if not symbol:
            raise ValueError("Missing symbol")
        
        if symbol in self.monitored_symbols:
            self.monitored_symbols.remove(symbol)
            # TODO: Save configuration to database
        
        return {
            "action": "remove_symbol",
            "symbol": symbol,
            "monitored_symbols": self.monitored_symbols,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_update_thresholds(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle updating alert thresholds."""
        thresholds = data.get("thresholds")
        if not thresholds:
            raise ValueError("Missing thresholds")
        
        self.alert_thresholds.update(thresholds)
        # TODO: Save configuration to database
        
        return {
            "action": "update_thresholds",
            "thresholds": self.alert_thresholds,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _load_configuration(self) -> None:
        """Load monitoring configuration."""
        # TODO: Load configuration from database
        self.monitored_symbols = ["AAPL", "MSFT", "GOOGL"]  # Example symbols
        self.alert_thresholds = {
            "price_change": 0.05,  # 5% price change
            "volume_spike": 2.0,   # 2x average volume
            "volatility": 0.02     # 2% daily volatility
        }
    
    async def _check_alerts(self, symbol: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check market data for alert conditions."""
        alerts = []
        
        # Check price change
        if "price_change" in self.alert_thresholds:
            price_change = data.get("price_change", 0)
            if abs(price_change) >= self.alert_thresholds["price_change"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    type="price_change",
                    value=price_change,
                    threshold=self.alert_thresholds["price_change"]
                ))
        
        # Check volume spike
        if "volume_spike" in self.alert_thresholds:
            volume_ratio = data.get("volume_ratio", 1.0)
            if volume_ratio >= self.alert_thresholds["volume_spike"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    type="volume_spike",
                    value=volume_ratio,
                    threshold=self.alert_thresholds["volume_spike"]
                ))
        
        # Check volatility
        if "volatility" in self.alert_thresholds:
            volatility = data.get("volatility", 0)
            if volatility >= self.alert_thresholds["volatility"]:
                alerts.append(self._create_alert(
                    symbol=symbol,
                    type="volatility",
                    value=volatility,
                    threshold=self.alert_thresholds["volatility"]
                ))
        
        return alerts
    
    def _create_alert(
        self,
        symbol: str,
        type: str,
        value: float,
        threshold: float
    ) -> Dict[str, Any]:
        """Create a market alert."""
        return {
            "symbol": symbol,
            "type": type,
            "value": value,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        } 