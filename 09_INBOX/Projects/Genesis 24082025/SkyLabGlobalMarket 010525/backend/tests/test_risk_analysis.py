import pytest
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.models import User, Portfolio, Trade, RiskMetrics
from app.services import get_password_hash
from app.services.risk_analysis import RiskAnalyzer

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
def test_portfolio(db_session: Session, test_user):
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

@pytest.fixture
def test_trades(db_session: Session, test_portfolio):
    trades = [
        Trade(
            symbol="AAPL",
            type="buy",
            quantity=10,
            price=150.0,
            timestamp=datetime.utcnow() - timedelta(days=2),
            portfolio_id=test_portfolio.id
        ),
        Trade(
            symbol="AAPL",
            type="sell",
            quantity=5,
            price=160.0,
            timestamp=datetime.utcnow() - timedelta(days=1),
            portfolio_id=test_portfolio.id
        )
    ]
    for trade in trades:
        db_session.add(trade)
    db_session.commit()
    return trades

@pytest.fixture
def test_risk_metrics(db_session: Session, test_portfolio):
    risk_metrics = RiskMetrics(
        portfolio_id=test_portfolio.id,
        timestamp=datetime.utcnow(),
        sharpe_ratio=1.5,
        volatility=0.2,
        beta=1.1,
        value_at_risk_95=-0.05,
        max_drawdown=-0.15,
        correlation_with_market=0.8
    )
    db_session.add(risk_metrics)
    db_session.commit()
    return risk_metrics

def test_calculate_sharpe_ratio():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    analyzer = RiskAnalyzer(returns)
    sharpe = analyzer.calculate_sharpe_ratio()
    assert isinstance(sharpe, float)
    assert sharpe > 0

def test_calculate_volatility():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    analyzer = RiskAnalyzer(returns)
    volatility = analyzer.calculate_volatility()
    assert isinstance(volatility, float)
    assert volatility > 0

def test_calculate_beta():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    market_returns = pd.Series([0.02, -0.01, 0.02, -0.02, 0.01])
    analyzer = RiskAnalyzer(returns)
    beta = analyzer.calculate_beta(market_returns)
    assert isinstance(beta, float)

def test_calculate_var():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    analyzer = RiskAnalyzer(returns)
    var = analyzer.calculate_var()
    assert isinstance(var, float)
    assert var < 0

def test_calculate_max_drawdown():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    analyzer = RiskAnalyzer(returns)
    max_drawdown = analyzer.calculate_max_drawdown()
    assert isinstance(max_drawdown, float)
    assert max_drawdown < 0

def test_calculate_correlation():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    other_returns = pd.Series([0.02, -0.01, 0.02, -0.02, 0.01])
    analyzer = RiskAnalyzer(returns)
    correlation = analyzer.calculate_correlation(other_returns)
    assert isinstance(correlation, float)
    assert -1 <= correlation <= 1

def test_generate_risk_report():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    market_returns = pd.Series([0.02, -0.01, 0.02, -0.02, 0.01])
    analyzer = RiskAnalyzer(returns)
    report = analyzer.generate_risk_report(market_returns)
    assert isinstance(report, dict)
    assert 'sharpe_ratio' in report
    assert 'volatility' in report
    assert 'beta' in report
    assert 'value_at_risk_95' in report
    assert 'max_drawdown' in report
    assert 'correlation_with_market' in report

def test_check_risk_alerts():
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
    analyzer = RiskAnalyzer(returns)
    thresholds = {
        'volatility_threshold': 0.1,
        'drawdown_threshold': 0.1,
        'var_threshold': 0.05
    }
    alerts = analyzer.check_risk_alerts(thresholds)
    assert isinstance(alerts, dict)

def test_get_portfolio_risk(client, test_user, test_portfolio, test_risk_metrics):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/risk",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sharpe_ratio"] == test_risk_metrics.sharpe_ratio
    assert data["volatility"] == test_risk_metrics.volatility
    assert data["beta"] == test_risk_metrics.beta

def test_get_portfolio_risk_history(client, test_user, test_portfolio, test_risk_metrics):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    start_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    end_date = datetime.utcnow().isoformat()
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/risk/history",
        params={"start_date": start_date, "end_date": end_date},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["sharpe_ratio"] == test_risk_metrics.sharpe_ratio

def test_calculate_portfolio_risk(client, test_user, test_portfolio, test_trades):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.post(
        f"/portfolios/{test_portfolio.id}/risk/calculate",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sharpe_ratio" in data
    assert "volatility" in data
    assert "value_at_risk_95" in data
    assert "max_drawdown" in data

def test_update_risk_thresholds(client, test_user, test_portfolio, test_risk_metrics):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    new_thresholds = {
        "volatility_threshold": 0.25,
        "drawdown_threshold": 0.15,
        "var_threshold": 0.04
    }
    
    response = client.put(
        f"/portfolios/{test_portfolio.id}/risk/thresholds",
        json=new_thresholds,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["volatility_threshold"] == new_thresholds["volatility_threshold"]
    assert data["drawdown_threshold"] == new_thresholds["drawdown_threshold"]
    assert data["var_threshold"] == new_thresholds["var_threshold"]

def test_get_portfolio_risk_unauthorized(client, test_portfolio):
    response = client.get(
        f"/portfolios/{test_portfolio.id}/risk"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_portfolio_risk_nonexistent(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/portfolios/999/risk",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 