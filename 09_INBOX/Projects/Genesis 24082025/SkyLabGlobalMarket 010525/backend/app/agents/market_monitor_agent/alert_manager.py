from typing import Dict, Any, List
from datetime import datetime
import json
import asyncio
from fastapi import WebSocket
from sqlalchemy.orm import Session

class AlertManager:
    """Manages market alerts and notifications."""
    
    def __init__(self, db: Session):
        self.db = db
        self.active_alerts: Dict[str, List[Dict[str, Any]]] = {}
        self.websocket_clients: List[WebSocket] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    async def initialize(self) -> None:
        """Initialize the alert manager."""
        # Load active alerts from database
        # TODO: Implement database loading
        pass
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        # Save active alerts to database
        # TODO: Implement database saving
        pass
    
    async def add_alert(
        self,
        symbol: str,
        alert_type: str,
        message: str,
        severity: str = "info",
        data: Dict[str, Any] = None
    ) -> None:
        """Add a new alert."""
        alert = {
            "symbol": symbol,
            "type": alert_type,
            "message": message,
            "severity": severity,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # Add to active alerts
        if symbol not in self.active_alerts:
            self.active_alerts[symbol] = []
        self.active_alerts[symbol].append(alert)
        
        # Add to history
        self.alert_history.append(alert)
        
        # Notify clients
        await self._notify_clients(alert)
        
        # Save to database
        # TODO: Implement database saving
    
    async def resolve_alert(
        self,
        symbol: str,
        alert_type: str,
        resolution: str = "resolved"
    ) -> None:
        """Resolve an active alert."""
        if symbol not in self.active_alerts:
            return
        
        for alert in self.active_alerts[symbol]:
            if alert["type"] == alert_type:
                alert["status"] = resolution
                alert["resolved_at"] = datetime.utcnow().isoformat()
                
                # Notify clients of resolution
                await self._notify_clients(alert)
                
                # Save to database
                # TODO: Implement database saving
    
    async def get_active_alerts(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get active alerts, optionally filtered by symbol."""
        if symbol:
            return self.active_alerts.get(symbol, [])
        
        all_alerts = []
        for alerts in self.active_alerts.values():
            all_alerts.extend(alerts)
        return all_alerts
    
    async def get_alert_history(
        self,
        symbol: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get alert history with optional filters."""
        filtered_history = self.alert_history
        
        if symbol:
            filtered_history = [
                alert for alert in filtered_history
                if alert["symbol"] == symbol
            ]
        
        if start_date:
            filtered_history = [
                alert for alert in filtered_history
                if datetime.fromisoformat(alert["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_history = [
                alert for alert in filtered_history
                if datetime.fromisoformat(alert["timestamp"]) <= end_date
            ]
        
        return filtered_history
    
    async def register_websocket(self, websocket: WebSocket) -> None:
        """Register a new WebSocket client for real-time alerts."""
        self.websocket_clients.append(websocket)
    
    async def unregister_websocket(self, websocket: WebSocket) -> None:
        """Unregister a WebSocket client."""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
    
    async def _notify_clients(self, alert: Dict[str, Any]) -> None:
        """Notify all connected WebSocket clients of an alert."""
        message = json.dumps(alert)
        
        for client in self.websocket_clients:
            try:
                await client.send_text(message)
            except Exception as e:
                print(f"Error sending alert to client: {e}")
                await self.unregister_websocket(client)
    
    async def cleanup_resolved_alerts(self) -> None:
        """Remove resolved alerts from active alerts."""
        for symbol in list(self.active_alerts.keys()):
            self.active_alerts[symbol] = [
                alert for alert in self.active_alerts[symbol]
                if alert["status"] == "active"
            ]
            
            if not self.active_alerts[symbol]:
                del self.active_alerts[symbol]
    
    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get statistics about alerts."""
        total_alerts = len(self.alert_history)
        active_alerts = sum(len(alerts) for alerts in self.active_alerts.values())
        resolved_alerts = total_alerts - active_alerts
        
        alert_types = {}
        for alert in self.alert_history:
            alert_type = alert["type"]
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "alert_types": alert_types
        } 