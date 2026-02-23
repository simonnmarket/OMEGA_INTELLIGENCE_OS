from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..crud import alerts as crud
from ..schemas import alerts as schemas
from ..agents.market_monitor_agent.alert_manager import AlertManager

router = APIRouter()
alert_manager = None

@router.on_event("startup")
async def startup_event():
    """Initialize the alert manager on startup."""
    global alert_manager
    db = next(get_db())
    alert_manager = AlertManager(db)
    await alert_manager.initialize()

@router.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    if alert_manager:
        await alert_manager.shutdown()

@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await websocket.accept()
    await alert_manager.register_websocket(websocket)
    
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await alert_manager.unregister_websocket(websocket)

@router.post("/alerts/", response_model=schemas.AlertResponse)
async def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert."""
    db_alert = crud.create_alert(db, alert)
    if alert_manager:
        await alert_manager.add_alert(
            symbol=alert.symbol,
            alert_type=alert.alert_type,
            message=alert.message,
            severity=alert.severity,
            data=alert.data
        )
    return db_alert

@router.get("/alerts/", response_model=List[schemas.AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filters."""
    return crud.get_alerts(db, skip=skip, limit=limit, symbol=symbol, status=status)

@router.get("/alerts/{alert_id}", response_model=schemas.AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get an alert by ID."""
    db_alert = crud.get_alert(db, alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

@router.put("/alerts/{alert_id}", response_model=schemas.AlertResponse)
async def update_alert(
    alert_id: int,
    alert: schemas.AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert."""
    db_alert = crud.update_alert(db, alert_id, alert)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert."""
    success = crud.delete_alert(db, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success"}

@router.post("/alerts/thresholds/", response_model=schemas.AlertThresholdResponse)
async def create_alert_threshold(
    threshold: schemas.AlertThresholdCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert threshold."""
    return crud.create_alert_threshold(db, threshold)

@router.get("/alerts/thresholds/", response_model=List[schemas.AlertThresholdResponse])
async def get_alert_thresholds(
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alert thresholds with optional filters."""
    return crud.get_alert_thresholds(db, symbol=symbol, alert_type=alert_type)

@router.put("/alerts/thresholds/{threshold_id}", response_model=schemas.AlertThresholdResponse)
async def update_alert_threshold(
    threshold_id: int,
    threshold: schemas.AlertThresholdUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert threshold."""
    db_threshold = crud.update_alert_threshold(db, threshold_id, threshold)
    if db_threshold is None:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    return db_threshold

@router.delete("/alerts/thresholds/{threshold_id}")
async def delete_alert_threshold(threshold_id: int, db: Session = Depends(get_db)):
    """Delete an alert threshold."""
    success = crud.delete_alert_threshold(db, threshold_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    return {"status": "success"}

@router.get("/alerts/notifications/", response_model=List[schemas.AlertNotificationResponse])
async def get_user_notifications(
    user_id: int,
    read: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get user notifications with optional read status filter."""
    return crud.get_user_notifications(db, user_id, read)

@router.put("/alerts/notifications/{notification_id}", response_model=schemas.AlertNotificationResponse)
async def update_alert_notification(
    notification_id: int,
    notification: schemas.AlertNotificationUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert notification."""
    db_notification = crud.update_alert_notification(db, notification_id, notification)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Alert notification not found")
    return db_notification

@router.get("/alerts/stats/", response_model=schemas.AlertStats)
async def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics."""
    return crud.get_alert_stats(db) 