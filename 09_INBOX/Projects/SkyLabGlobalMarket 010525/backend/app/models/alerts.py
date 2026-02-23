from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class AlertSeverity(enum.Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(enum.Enum):
    """Alert status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class Alert(Base):
    """Database model for market alerts."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    alert_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE)
    data = Column(String)  # JSON string of additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    portfolio = relationship("Portfolio", back_populates="alerts")
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "type": self.alert_type,
            "message": self.message,
            "severity": self.severity.value,
            "status": self.status.value,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "portfolio_id": self.portfolio_id
        }

class AlertThreshold(Base):
    """Database model for alert thresholds."""
    __tablename__ = "alert_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    alert_type = Column(String, nullable=False)
    threshold_value = Column(Float, nullable=False)
    comparison = Column(String, nullable=False)  # "gt", "lt", "eq"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    portfolio = relationship("Portfolio", back_populates="alert_thresholds")
    
    def to_dict(self) -> dict:
        """Convert threshold to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "type": self.alert_type,
            "threshold_value": self.threshold_value,
            "comparison": self.comparison,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "portfolio_id": self.portfolio_id
        }

class AlertNotification(Base):
    """Database model for alert notifications."""
    __tablename__ = "alert_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = relationship("Alert", back_populates="notifications")
    user = relationship("User", back_populates="alert_notifications")
    
    def to_dict(self) -> dict:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "read": self.read,
            "created_at": self.created_at.isoformat()
        } 