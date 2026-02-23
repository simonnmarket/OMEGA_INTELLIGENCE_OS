from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class RiskMetricsBase(BaseModel):
    portfolio_id: int
    timestamp: datetime
    sharpe_ratio: float
    volatility: float
    beta: Optional[float] = None
    value_at_risk_95: float
    max_drawdown: float
    correlation_with_market: Optional[float] = None

class RiskMetricsCreate(RiskMetricsBase):
    pass

class RiskMetricsResponse(RiskMetricsBase):
    id: int
    volatility_threshold: float = Field(default=0.3)
    drawdown_threshold: float = Field(default=0.2)
    var_threshold: float = Field(default=0.05)
    high_volatility_alert: Optional[str] = None
    significant_drawdown_alert: Optional[str] = None
    high_var_alert: Optional[str] = None

    class Config:
        orm_mode = True

class RiskThresholds(BaseModel):
    volatility_threshold: Optional[float] = Field(default=0.3, ge=0, le=1)
    drawdown_threshold: Optional[float] = Field(default=0.2, ge=0, le=1)
    var_threshold: Optional[float] = Field(default=0.05, ge=0, le=1)

class RiskAlerts(BaseModel):
    high_volatility: Optional[Dict] = None
    significant_drawdown: Optional[Dict] = None
    high_var: Optional[Dict] = None

class RiskReport(BaseModel):
    sharpe_ratio: float
    volatility: float
    beta: Optional[float] = None
    value_at_risk_95: float
    max_drawdown: float
    correlation_with_market: Optional[float] = None
    alerts: RiskAlerts 