import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User, MarketData
from app.services import get_password_hash

def get_auth_token(client, email: str, password: str):
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_user(db_session: Session):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_market_data(db_session: Session):
    market_data = MarketData(
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        timestamp="2023-01-01T00:00:00",
        open=149.0,
        high=151.0,
        low=148.0,
        close=150.0
    )
    db_session.add(market_data)
    db_session.commit()
    return market_data

def test_get_market_data(client, test_user, test_market_data):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/market-data/AAPL",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == test_market_data.symbol
    assert data["price"] == test_market_data.price
    assert data["volume"] == test_market_data.volume

def test_get_market_data_history(client, test_user, test_market_data):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/market-data/AAPL/history",
        params={"start_date": "2023-01-01", "end_date": "2023-01-02"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["symbol"] == test_market_data.symbol

def test_get_market_data_nonexistent_symbol(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/market-data/INVALID",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_market_data_unauthorized(client):
    response = client.get("/market-data/AAPL")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_market_data_invalid_date_range(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/market-data/AAPL/history",
        params={"start_date": "2023-01-02", "end_date": "2023-01-01"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_market_data_missing_date(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/market-data/AAPL/history",
        params={"start_date": "2023-01-01"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 