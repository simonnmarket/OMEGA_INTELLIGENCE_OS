from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class AlertBase(BaseModel):
    """Base alert schema."""
    symbol: str = Field(..., description="Symbol for the alert")
    alert_type: str = Field(..., description="Type of alert")
    message: str = Field(..., description="Alert message")
    severity: AlertSeverity = Field(..., description="Alert severity")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional alert data")

class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    pass

class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    status: Optional[AlertStatus] = Field(None, description="New alert status")
    message: Optional[str] = Field(None, description="Updated alert message")
    data: Optional[Dict[str, Any]] = Field(None, description="Updated alert data")

class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int = Field(..., description="Alert ID")
    status: AlertStatus = Field(..., description="Alert status")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Alert resolution timestamp")
    
    class Config:
        orm_mode = True

class AlertThresholdBase(BaseModel):
    """Base alert threshold schema."""
    symbol: str = Field(..., description="Symbol for the threshold")
    alert_type: str = Field(..., description="Type of alert")
    threshold_value: float = Field(..., description="Threshold value")
    comparison: str = Field(..., description="Comparison operator (gt, lt, eq)")

class AlertThresholdCreate(AlertThresholdBase):
    """Schema for creating a new alert threshold."""
    pass

class AlertThresholdUpdate(BaseModel):
    """Schema for updating an alert threshold."""
    threshold_value: Optional[float] = Field(None, description="New threshold value")
    comparison: Optional[str] = Field(None, description="New comparison operator")

class AlertThresholdResponse(AlertThresholdBase):
    """Schema for alert threshold response."""
    id: int = Field(..., description="Threshold ID")
    created_at: datetime = Field(..., description="Threshold creation timestamp")
    updated_at: datetime = Field(..., description="Threshold update timestamp")
    
    class Config:
        orm_mode = True

class AlertNotificationBase(BaseModel):
    """Base alert notification schema."""
    alert_id: int = Field(..., description="Alert ID")
    user_id: int = Field(..., description="User ID")
    read: bool = Field(False, description="Notification read status")

class AlertNotificationCreate(AlertNotificationBase):
    """Schema for creating a new alert notification."""
    pass

class AlertNotificationUpdate(BaseModel):
    """Schema for updating an alert notification."""
    read: Optional[bool] = Field(None, description="New read status")

class AlertNotificationResponse(AlertNotificationBase):
    """Schema for alert notification response."""
    id: int = Field(..., description="Notification ID")
    created_at: datetime = Field(..., description="Notification creation timestamp")
    
    class Config:
        orm_mode = True

class AlertStats(BaseModel):
    """Schema for alert statistics."""
    total_alerts: int = Field(..., description="Total number of alerts")
    active_alerts: int = Field(..., description="Number of active alerts")
    resolved_alerts: int = Field(..., description="Number of resolved alerts")
    alert_types: Dict[str, int] = Field(..., description="Count of alerts by type") 