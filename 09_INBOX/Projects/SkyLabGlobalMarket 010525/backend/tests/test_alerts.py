import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..app.main import app
from ..app.database import get_db
from ..app.models.alerts import Alert, AlertThreshold, AlertNotification
from ..app.schemas.alerts import AlertSeverity, AlertStatus

client = TestClient(app)

@pytest.fixture
def test_alert(db: Session):
    """Create a test alert."""
    alert = Alert(
        symbol="AAPL",
        alert_type="price_change",
        message="Price increased by 5%",
        severity=AlertSeverity.WARNING,
        status=AlertStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

@pytest.fixture
def test_threshold(db: Session):
    """Create a test alert threshold."""
    threshold = AlertThreshold(
        symbol="AAPL",
        alert_type="price_change",
        threshold_value=5.0,
        comparison="gt",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(threshold)
    db.commit()
    db.refresh(threshold)
    return threshold

@pytest.fixture
def test_notification(db: Session, test_alert):
    """Create a test alert notification."""
    notification = AlertNotification(
        alert_id=test_alert.id,
        user_id=1,
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def test_create_alert(db: Session):
    """Test creating a new alert."""
    response = client.post(
        "/alerts/",
        json={
            "symbol": "AAPL",
            "alert_type": "price_change",
            "message": "Price increased by 5%",
            "severity": "warning",
            "data": {"change": 5.0}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["alert_type"] == "price_change"
    assert data["severity"] == "warning"
    assert data["status"] == "active"

def test_get_alerts(db: Session, test_alert):
    """Test getting alerts."""
    response = client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["symbol"] == test_alert.symbol

def test_get_alert(db: Session, test_alert):
    """Test getting a specific alert."""
    response = client.get(f"/alerts/{test_alert.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_alert.id
    assert data["symbol"] == test_alert.symbol

def test_update_alert(db: Session, test_alert):
    """Test updating an alert."""
    response = client.put(
        f"/alerts/{test_alert.id}",
        json={
            "status": "resolved",
            "message": "Updated message"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["message"] == "Updated message"

def test_delete_alert(db: Session, test_alert):
    """Test deleting an alert."""
    response = client.delete(f"/alerts/{test_alert.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify alert is deleted
    response = client.get(f"/alerts/{test_alert.id}")
    assert response.status_code == 404

def test_create_alert_threshold(db: Session):
    """Test creating a new alert threshold."""
    response = client.post(
        "/alerts/thresholds/",
        json={
            "symbol": "AAPL",
            "alert_type": "price_change",
            "threshold_value": 5.0,
            "comparison": "gt"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["alert_type"] == "price_change"
    assert data["threshold_value"] == 5.0
    assert data["comparison"] == "gt"

def test_get_alert_thresholds(db: Session, test_threshold):
    """Test getting alert thresholds."""
    response = client.get("/alerts/thresholds/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["symbol"] == test_threshold.symbol

def test_update_alert_threshold(db: Session, test_threshold):
    """Test updating an alert threshold."""
    response = client.put(
        f"/alerts/thresholds/{test_threshold.id}",
        json={
            "threshold_value": 10.0,
            "comparison": "lt"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["threshold_value"] == 10.0
    assert data["comparison"] == "lt"

def test_delete_alert_threshold(db: Session, test_threshold):
    """Test deleting an alert threshold."""
    response = client.delete(f"/alerts/thresholds/{test_threshold.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify threshold is deleted
    response = client.get(f"/alerts/thresholds/{test_threshold.id}")
    assert response.status_code == 404

def test_get_user_notifications(db: Session, test_notification):
    """Test getting user notifications."""
    response = client.get(f"/alerts/notifications/?user_id={test_notification.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["user_id"] == test_notification.user_id

def test_update_alert_notification(db: Session, test_notification):
    """Test updating an alert notification."""
    response = client.put(
        f"/alerts/notifications/{test_notification.id}",
        json={"read": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["read"] is True

def test_get_alert_stats(db: Session, test_alert):
    """Test getting alert statistics."""
    response = client.get("/alerts/stats/")
    assert response.status_code == 200
    data = response.json()
    assert "total_alerts" in data
    assert "active_alerts" in data
    assert "resolved_alerts" in data
    assert "alert_types" in data

def test_websocket_connection():
    """Test WebSocket connection for real-time alerts."""
    with client.websocket_connect("/ws/alerts") as websocket:
        # Connection should be established
        assert websocket.client is not None
        
        # Send a message to keep the connection alive
        websocket.send_text("ping")
        
        # Connection should remain open
        assert websocket.client is not None 