from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.alerts import Alert, AlertThreshold, AlertNotification
from ..schemas.alerts import (
    AlertCreate,
    AlertUpdate,
    AlertThresholdCreate,
    AlertThresholdUpdate,
    AlertNotificationCreate,
    AlertNotificationUpdate
)

def create_alert(db: Session, alert: AlertCreate) -> Alert:
    """Create a new alert."""
    db_alert = Alert(
        symbol=alert.symbol,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        data=alert.data
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """Get an alert by ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()

def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    status: Optional[str] = None
) -> List[Alert]:
    """Get alerts with optional filters."""
    query = db.query(Alert)
    
    if symbol:
        query = query.filter(Alert.symbol == symbol)
    if status:
        query = query.filter(Alert.status == status)
    
    return query.offset(skip).limit(limit).all()

def update_alert(
    db: Session,
    alert_id: int,
    alert: AlertUpdate
) -> Optional[Alert]:
    """Update an alert."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    update_data = alert.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    if alert.status == "resolved":
        db_alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

def delete_alert(db: Session, alert_id: int) -> bool:
    """Delete an alert."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return False
    
    db.delete(db_alert)
    db.commit()
    return True

def create_alert_threshold(
    db: Session,
    threshold: AlertThresholdCreate
) -> AlertThreshold:
    """Create a new alert threshold."""
    db_threshold = AlertThreshold(
        symbol=threshold.symbol,
        alert_type=threshold.alert_type,
        threshold_value=threshold.threshold_value,
        comparison=threshold.comparison
    )
    db.add(db_threshold)
    db.commit()
    db.refresh(db_threshold)
    return db_threshold

def get_alert_threshold(
    db: Session,
    threshold_id: int
) -> Optional[AlertThreshold]:
    """Get an alert threshold by ID."""
    return db.query(AlertThreshold).filter(AlertThreshold.id == threshold_id).first()

def get_alert_thresholds(
    db: Session,
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None
) -> List[AlertThreshold]:
    """Get alert thresholds with optional filters."""
    query = db.query(AlertThreshold)
    
    if symbol:
        query = query.filter(AlertThreshold.symbol == symbol)
    if alert_type:
        query = query.filter(AlertThreshold.alert_type == alert_type)
    
    return query.all()

def update_alert_threshold(
    db: Session,
    threshold_id: int,
    threshold: AlertThresholdUpdate
) -> Optional[AlertThreshold]:
    """Update an alert threshold."""
    db_threshold = get_alert_threshold(db, threshold_id)
    if not db_threshold:
        return None
    
    update_data = threshold.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_threshold, field, value)
    
    db_threshold.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_threshold)
    return db_threshold

def delete_alert_threshold(db: Session, threshold_id: int) -> bool:
    """Delete an alert threshold."""
    db_threshold = get_alert_threshold(db, threshold_id)
    if not db_threshold:
        return False
    
    db.delete(db_threshold)
    db.commit()
    return True

def create_alert_notification(
    db: Session,
    notification: AlertNotificationCreate
) -> AlertNotification:
    """Create a new alert notification."""
    db_notification = AlertNotification(
        alert_id=notification.alert_id,
        user_id=notification.user_id,
        read=notification.read
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_alert_notification(
    db: Session,
    notification_id: int
) -> Optional[AlertNotification]:
    """Get an alert notification by ID."""
    return db.query(AlertNotification).filter(AlertNotification.id == notification_id).first()

def get_user_notifications(
    db: Session,
    user_id: int,
    read: Optional[bool] = None
) -> List[AlertNotification]:
    """Get user notifications with optional read status filter."""
    query = db.query(AlertNotification).filter(AlertNotification.user_id == user_id)
    
    if read is not None:
        query = query.filter(AlertNotification.read == read)
    
    return query.all()

def update_alert_notification(
    db: Session,
    notification_id: int,
    notification: AlertNotificationUpdate
) -> Optional[AlertNotification]:
    """Update an alert notification."""
    db_notification = get_alert_notification(db, notification_id)
    if not db_notification:
        return None
    
    update_data = notification.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification

def delete_alert_notification(db: Session, notification_id: int) -> bool:
    """Delete an alert notification."""
    db_notification = get_alert_notification(db, notification_id)
    if not db_notification:
        return False
    
    db.delete(db_notification)
    db.commit()
    return True

def get_alert_stats(db: Session) -> Dict[str, Any]:
    """Get alert statistics."""
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.status == "active").count()
    resolved_alerts = db.query(Alert).filter(Alert.status == "resolved").count()
    
    alert_types = {}
    for alert in db.query(Alert).all():
        alert_type = alert.alert_type
        alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
    
    return {
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "resolved_alerts": resolved_alerts,
        "alert_types": alert_types
    } 