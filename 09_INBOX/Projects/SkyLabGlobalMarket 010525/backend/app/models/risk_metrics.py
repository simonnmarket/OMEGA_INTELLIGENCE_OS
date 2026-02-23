from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RiskMetrics(Base):
    __tablename__ = "risk_metrics"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    timestamp = Column(DateTime, nullable=False)
    
    # Basic metrics
    sharpe_ratio = Column(Float)
    volatility = Column(Float)
    beta = Column(Float)
    value_at_risk_95 = Column(Float)
    max_drawdown = Column(Float)
    
    # Correlation metrics
    correlation_with_market = Column(Float)
    
    # Alert thresholds
    volatility_threshold = Column(Float, default=0.3)
    drawdown_threshold = Column(Float, default=0.2)
    var_threshold = Column(Float, default=0.05)
    
    # Alert status
    high_volatility_alert = Column(String, nullable=True)
    significant_drawdown_alert = Column(String, nullable=True)
    high_var_alert = Column(String, nullable=True)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="risk_metrics")
    
    def to_dict(self):
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "timestamp": self.timestamp.isoformat(),
            "sharpe_ratio": self.sharpe_ratio,
            "volatility": self.volatility,
            "beta": self.beta,
            "value_at_risk_95": self.value_at_risk_95,
            "max_drawdown": self.max_drawdown,
            "correlation_with_market": self.correlation_with_market,
            "alerts": {
                "high_volatility": self.high_volatility_alert,
                "significant_drawdown": self.significant_drawdown_alert,
                "high_var": self.high_var_alert
            }
        } 