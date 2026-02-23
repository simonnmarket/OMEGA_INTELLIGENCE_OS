import pytest
from fastapi import status

def test_create_portfolio(client, auth_headers):
    """Testa a criação de um novo portfólio"""
    response = client.post(
        "/portfolios/",
        json={
            "name": "New Portfolio",
            "description": "Test portfolio",
            "initial_balance": 10000.0
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Portfolio"
    assert data["description"] == "Test portfolio"
    assert data["initial_balance"] == 10000.0
    assert data["current_balance"] == 10000.0
    assert "id" in data
    assert "user_id" in data

def test_create_portfolio_duplicate_name(client, auth_headers, test_portfolio):
    """Testa a tentativa de criar um portfólio com nome duplicado"""
    response = client.post(
        "/portfolios/",
        json={
            "name": test_portfolio.name,
            "description": "Another portfolio",
            "initial_balance": 5000.0
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Portfolio name already exists" in response.json()["detail"]

def test_create_portfolio_negative_balance(client, auth_headers):
    """Testa a tentativa de criar um portfólio com saldo inicial negativo"""
    response = client.post(
        "/portfolios/",
        json={
            "name": "Negative Balance",
            "description": "Test portfolio",
            "initial_balance": -1000.0
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Initial balance cannot be negative" in response.json()["detail"]

def test_get_portfolio(client, auth_headers, test_portfolio):
    """Testa a obtenção de um portfólio"""
    response = client.get(
        f"/portfolios/{test_portfolio.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_portfolio.id
    assert data["name"] == test_portfolio.name
    assert data["description"] == test_portfolio.description
    assert data["initial_balance"] == test_portfolio.initial_balance
    assert data["current_balance"] == test_portfolio.current_balance

def test_get_nonexistent_portfolio(client, auth_headers):
    """Testa a obtenção de um portfólio inexistente"""
    response = client.get(
        "/portfolios/999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Portfolio not found" in response.json()["detail"]

def test_get_other_user_portfolio(client, auth_headers, test_portfolio):
    """Testa a tentativa de obter um portfólio de outro usuário"""
    # Criar um novo usuário e tentar acessar o portfólio do primeiro
    response = client.post(
        "/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "otherpassword"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Login com o novo usuário
    response = client.post(
        "/auth/login",
        data={
            "username": "otheruser",
            "password": "otherpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    other_auth_headers = {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }
    
    # Tentar acessar o portfólio do primeiro usuário
    response = client.get(
        f"/portfolios/{test_portfolio.id}",
        headers=other_auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Portfolio not found" in response.json()["detail"]

def test_update_portfolio(client, auth_headers, test_portfolio):
    """Testa a atualização de um portfólio"""
    response = client.put(
        f"/portfolios/{test_portfolio.id}",
        json={
            "name": "Updated Portfolio",
            "description": "Updated description",
            "current_balance": 15000.0
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Portfolio"
    assert data["description"] == "Updated description"
    assert data["current_balance"] == 15000.0
    assert data["initial_balance"] == test_portfolio.initial_balance

def test_delete_portfolio(client, auth_headers, test_portfolio):
    """Testa a exclusão de um portfólio"""
    response = client.delete(
        f"/portfolios/{test_portfolio.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Portfolio deleted successfully"
    
    # Verificar se o portfólio foi realmente excluído
    response = client.get(
        f"/portfolios/{test_portfolio.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_portfolio_positions(client, auth_headers, test_portfolio, test_position):
    """Testa a obtenção das posições de um portfólio"""
    response = client.get(
        f"/portfolios/{test_portfolio.id}/positions",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == test_position.symbol
    assert data[0]["quantity"] == test_position.quantity
    assert data[0]["average_price"] == test_position.average_price
    assert data[0]["current_price"] == test_position.current_price

def test_get_portfolio_performance(client, auth_headers, test_portfolio):
    """Testa a obtenção do desempenho de um portfólio"""
    response = client.get(
        f"/portfolios/{test_portfolio.id}/performance",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_return" in data
    assert "daily_returns" in data
    assert "cumulative_returns" in data
    assert "sharpe_ratio" in data
    assert "max_drawdown" in data 