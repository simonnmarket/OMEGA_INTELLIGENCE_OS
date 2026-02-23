import pytest
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import User, Portfolio, Trade
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
def test_portfolio(db_session: Session, test_user: User):
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
        initial_balance=10000.0,
        current_balance=10000.0,
        user_id=test_user.id
    )
    db_session.add(portfolio)
    db_session.commit()
    return portfolio

def test_create_portfolio(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    portfolio_data = {
        "name": "New Portfolio",
        "description": "New Description",
        "initial_balance": 5000.0,
        "currency": "USD"
    }
    
    response = client.post(
        "/portfolios",
        json=portfolio_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == portfolio_data["name"]
    assert data["description"] == portfolio_data["description"]
    assert data["initial_balance"] == portfolio_data["initial_balance"]
    assert data["current_balance"] == portfolio_data["initial_balance"]
    assert data["currency"] == portfolio_data["currency"]

def test_get_portfolios(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/portfolios",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_portfolio.id
    assert data[0]["name"] == test_portfolio.name

def test_get_portfolio(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_portfolio.id
    assert data["name"] == test_portfolio.name

def test_update_portfolio(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    update_data = {
        "name": "Updated Portfolio",
        "description": "Updated Description"
    }
    
    response = client.put(
        f"/portfolios/{test_portfolio.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_portfolio(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.delete(
        f"/portfolios/{test_portfolio.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_create_trade(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    trade_data = {
        "symbol": "AAPL",
        "type": "buy",
        "quantity": 10,
        "price": 150.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = client.post(
        f"/portfolios/{test_portfolio.id}/trades",
        json=trade_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == trade_data["symbol"]
    assert data["type"] == trade_data["type"]
    assert data["quantity"] == trade_data["quantity"]
    assert data["price"] == trade_data["price"]

def test_get_trades(client, test_user, test_portfolio, db_session: Session):
    # Cria alguns trades
    trade1 = Trade(
        symbol="AAPL",
        type="buy",
        quantity=10,
        price=150.0,
        timestamp=datetime.utcnow(),
        portfolio_id=test_portfolio.id
    )
    trade2 = Trade(
        symbol="GOOGL",
        type="sell",
        quantity=5,
        price=2800.0,
        timestamp=datetime.utcnow(),
        portfolio_id=test_portfolio.id
    )
    db_session.add_all([trade1, trade2])
    db_session.commit()
    
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/trades",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["symbol"] in ["AAPL", "GOOGL"]
    assert data[1]["symbol"] in ["AAPL", "GOOGL"]

def test_get_portfolio_risk(client, test_user, test_portfolio, db_session: Session):
    # Cria alguns trades para cálculo de risco
    trades = [
        Trade(
            symbol="AAPL",
            type="buy",
            quantity=10,
            price=150.0,
            timestamp=datetime.utcnow(),
            portfolio_id=test_portfolio.id
        ),
        Trade(
            symbol="GOOGL",
            type="sell",
            quantity=5,
            price=2800.0,
            timestamp=datetime.utcnow(),
            portfolio_id=test_portfolio.id
        )
    ]
    db_session.add_all(trades)
    db_session.commit()
    
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/risk",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "volatility" in data
    assert "sharpe_ratio" in data
    assert "max_drawdown" in data
    assert "value_at_risk" in data
    assert "beta" in data
    assert "alpha" in data

def test_get_portfolio_performance(client, test_user, test_portfolio, db_session: Session):
    # Cria alguns trades para cálculo de desempenho
    trades = [
        Trade(
            symbol="AAPL",
            type="buy",
            quantity=10,
            price=150.0,
            timestamp=datetime.utcnow(),
            portfolio_id=test_portfolio.id
        ),
        Trade(
            symbol="GOOGL",
            type="sell",
            quantity=5,
            price=2800.0,
            timestamp=datetime.utcnow(),
            portfolio_id=test_portfolio.id
        )
    ]
    db_session.add_all(trades)
    db_session.commit()
    
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "initial_balance" in data
    assert "current_balance" in data
    assert "total_return" in data
    assert "return_percentage" in data
    assert "trades_count" in data
    assert "winning_trades" in data
    assert "losing_trades" in data
    assert "win_rate" in data
    assert "average_win" in data
    assert "average_loss" in data
    assert "profit_factor" in data 