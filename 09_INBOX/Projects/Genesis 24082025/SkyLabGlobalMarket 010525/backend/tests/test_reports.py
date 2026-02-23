import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User, Portfolio, Trade, Report
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
def test_portfolio(db_session: Session, test_user):
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test Description",
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
            quantity=10,
            price=150.0,
            trade_type="buy",
            portfolio_id=test_portfolio.id
        ),
        Trade(
            symbol="GOOGL",
            quantity=5,
            price=2800.0,
            trade_type="buy",
            portfolio_id=test_portfolio.id
        )
    ]
    for trade in trades:
        db_session.add(trade)
    db_session.commit()
    return trades

@pytest.fixture
def test_report(db_session: Session, test_portfolio):
    report = Report(
        portfolio_id=test_portfolio.id,
        report_type="performance",
        content="Test Report Content",
        generated_at="2023-01-01T00:00:00"
    )
    db_session.add(report)
    db_session.commit()
    return report

def test_generate_performance_report(client, test_user, test_portfolio, test_trades):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.post(
        f"/portfolios/{test_portfolio.id}/reports/performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "report_id" in data
    assert "content" in data
    assert "generated_at" in data

def test_generate_risk_report(client, test_user, test_portfolio, test_trades):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.post(
        f"/portfolios/{test_portfolio.id}/reports/risk",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "report_id" in data
    assert "content" in data
    assert "generated_at" in data

def test_get_report(client, test_user, test_report):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/reports/{test_report.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_report.id
    assert data["report_type"] == test_report.report_type
    assert data["content"] == test_report.content

def test_get_reports(client, test_user, test_portfolio, test_report):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        f"/portfolios/{test_portfolio.id}/reports",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == test_report.id
    assert data[0]["report_type"] == test_report.report_type

def test_get_report_nonexistent(client, test_user):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.get(
        "/reports/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_report_unauthorized(client, test_report):
    response = client.get(f"/reports/{test_report.id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_report_other_user(client, test_user, test_report):
    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpassword"),
        full_name="Other User"
    )
    db_session.add(other_user)
    db_session.commit()
    
    token = get_auth_token(client, other_user.email, "otherpassword")
    
    response = client.get(
        f"/reports/{test_report.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_report(client, test_user, test_report):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.delete(
        f"/reports/{test_report.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify report was deleted
    response = client.get(
        f"/reports/{test_report.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_generate_report_invalid_type(client, test_user, test_portfolio):
    token = get_auth_token(client, test_user.email, "testpassword")
    
    response = client.post(
        f"/portfolios/{test_portfolio.id}/reports/invalid",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST 