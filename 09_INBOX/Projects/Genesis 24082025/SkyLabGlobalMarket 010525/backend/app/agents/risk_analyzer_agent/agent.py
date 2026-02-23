from typing import Dict, Any, List
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.models.portfolio import Portfolio
from app.services.risk_analysis import RiskAnalyzer
from .rules import RiskRules

class RiskAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing portfolio risk and monitoring risk metrics."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "risk_analyzer")
        self.risk_analyzer = RiskAnalyzer()
        self.rules = RiskRules()
    
    async def initialize(self) -> None:
        """Initialize the risk analyzer agent."""
        self.update_status("initializing")
        await self.rules.initialize()
        self.update_status("ready")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process risk analysis tasks."""
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")
            
            self.update_status("processing")
            
            portfolio_id = data.get("portfolio_id")
            action = data.get("action")
            
            if action == "analyze":
                result = await self._handle_analysis(portfolio_id)
            elif action == "monitor":
                result = await self._handle_monitoring(portfolio_id)
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
        await self.rules.shutdown()
        self.update_status("stopped")
    
    async def _handle_analysis(self, portfolio_id: int) -> Dict[str, Any]:
        """Handle portfolio risk analysis."""
        portfolio = await self._get_portfolio(portfolio_id)
        risk_metrics = await self.risk_analyzer.calculate_risk_metrics(portfolio)
        alerts = await self.rules.check_risk_alerts(risk_metrics)
        
        return {
            "portfolio_id": portfolio_id,
            "action": "analyze",
            "risk_metrics": risk_metrics,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_monitoring(self, portfolio_id: int) -> Dict[str, Any]:
        """Handle continuous risk monitoring."""
        portfolio = await self._get_portfolio(portfolio_id)
        risk_metrics = await self.risk_analyzer.calculate_risk_metrics(portfolio)
        alerts = await self.rules.check_risk_alerts(risk_metrics)
        
        # Check for significant changes in risk metrics
        historical_metrics = await self._get_historical_metrics(portfolio_id)
        changes = self._analyze_metric_changes(risk_metrics, historical_metrics)
        
        return {
            "portfolio_id": portfolio_id,
            "action": "monitor",
            "risk_metrics": risk_metrics,
            "alerts": alerts,
            "metric_changes": changes,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_portfolio(self, portfolio_id: int) -> Portfolio:
        """Retrieve portfolio from database."""
        # TODO: Implement database query
        pass
    
    async def _get_historical_metrics(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Retrieve historical risk metrics."""
        # TODO: Implement database query
        pass
    
    def _analyze_metric_changes(
        self,
        current_metrics: Dict[str, float],
        historical_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze changes in risk metrics over time."""
        changes = {}
        
        if not historical_metrics:
            return changes
        
        # Get the most recent historical metrics
        last_metrics = historical_metrics[-1]
        
        for metric, current_value in current_metrics.items():
            if metric in last_metrics:
                last_value = last_metrics[metric]
                change = (current_value - last_value) / last_value
                
                # Only report significant changes (>5%)
                if abs(change) > 0.05:
                    changes[metric] = {
                        "change": change,
                        "current_value": current_value,
                        "previous_value": last_value
                    }
        
        return changes 