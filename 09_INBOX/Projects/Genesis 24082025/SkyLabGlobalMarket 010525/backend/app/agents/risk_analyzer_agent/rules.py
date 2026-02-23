from typing import Dict, Any, List
from datetime import datetime

class RiskRules:
    """Risk rules and thresholds for portfolio monitoring."""
    
    def __init__(self):
        self.thresholds = {
            "volatility": 0.2,  # Maximum acceptable volatility (20%)
            "drawdown": 0.1,    # Maximum acceptable drawdown (10%)
            "var_95": 0.05,    # Maximum acceptable VaR at 95% confidence (5%)
            "beta": 1.5,       # Maximum acceptable beta
            "correlation": 0.7  # Maximum acceptable correlation with market
        }
        
        self.alert_levels = {
            "warning": 0.8,    # 80% of threshold
            "critical": 0.9    # 90% of threshold
        }
    
    async def initialize(self) -> None:
        """Initialize risk rules and thresholds."""
        # TODO: Load thresholds from configuration
        pass
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        pass
    
    async def check_risk_alerts(self, risk_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check risk metrics against thresholds and generate alerts."""
        alerts = []
        
        for metric, value in risk_metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                warning_level = threshold * self.alert_levels["warning"]
                critical_level = threshold * self.alert_levels["critical"]
                
                if value >= threshold:
                    alerts.append(self._create_alert(
                        metric=metric,
                        value=value,
                        threshold=threshold,
                        level="critical",
                        message=f"{metric} exceeds maximum threshold"
                    ))
                elif value >= critical_level:
                    alerts.append(self._create_alert(
                        metric=metric,
                        value=value,
                        threshold=threshold,
                        level="warning",
                        message=f"{metric} approaching critical threshold"
                    ))
                elif value >= warning_level:
                    alerts.append(self._create_alert(
                        metric=metric,
                        value=value,
                        threshold=threshold,
                        level="info",
                        message=f"{metric} approaching warning threshold"
                    ))
        
        return alerts
    
    def _create_alert(
        self,
        metric: str,
        value: float,
        threshold: float,
        level: str,
        message: str
    ) -> Dict[str, Any]:
        """Create a risk alert."""
        return {
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update risk thresholds."""
        for metric, value in new_thresholds.items():
            if metric in self.thresholds:
                self.thresholds[metric] = value
    
    def validate_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Validate if thresholds are within acceptable ranges."""
        valid_ranges = {
            "volatility": (0.0, 1.0),
            "drawdown": (0.0, 1.0),
            "var_95": (0.0, 1.0),
            "beta": (0.0, 3.0),
            "correlation": (-1.0, 1.0)
        }
        
        for metric, value in thresholds.items():
            if metric in valid_ranges:
                min_val, max_val = valid_ranges[metric]
                if not (min_val <= value <= max_val):
                    return False
        
        return True
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current risk thresholds."""
        return self.thresholds.copy()
    
    def get_alert_levels(self) -> Dict[str, float]:
        """Get current alert levels."""
        return self.alert_levels.copy() 