import pytest
from fastapi import status

def test_calculate_value_at_risk(client, auth_headers, test_portfolio):
    """Testa o cálculo do Value at Risk"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/value-at-risk",
        params={
            "confidence_level": 0.95,
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "value_at_risk" in data
    assert "confidence_level" in data
    assert "time_horizon" in data
    assert isinstance(data["value_at_risk"], float)
    assert data["confidence_level"] == 0.95
    assert data["time_horizon"] == 1

def test_calculate_expected_shortfall(client, auth_headers, test_portfolio):
    """Testa o cálculo do Expected Shortfall"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/expected-shortfall",
        params={
            "confidence_level": 0.95,
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "expected_shortfall" in data
    assert "confidence_level" in data
    assert "time_horizon" in data
    assert isinstance(data["expected_shortfall"], float)
    assert data["confidence_level"] == 0.95
    assert data["time_horizon"] == 1

def test_calculate_sharpe_ratio(client, auth_headers, test_portfolio):
    """Testa o cálculo do Sharpe Ratio"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/sharpe-ratio",
        params={
            "risk_free_rate": 0.02,
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sharpe_ratio" in data
    assert "risk_free_rate" in data
    assert "time_horizon" in data
    assert isinstance(data["sharpe_ratio"], float)
    assert data["risk_free_rate"] == 0.02
    assert data["time_horizon"] == 1

def test_calculate_sortino_ratio(client, auth_headers, test_portfolio):
    """Testa o cálculo do Sortino Ratio"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/sortino-ratio",
        params={
            "risk_free_rate": 0.02,
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sortino_ratio" in data
    assert "risk_free_rate" in data
    assert "time_horizon" in data
    assert isinstance(data["sortino_ratio"], float)
    assert data["risk_free_rate"] == 0.02
    assert data["time_horizon"] == 1

def test_calculate_max_drawdown(client, auth_headers, test_portfolio):
    """Testa o cálculo do Maximum Drawdown"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/max-drawdown",
        params={
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "max_drawdown" in data
    assert "time_horizon" in data
    assert isinstance(data["max_drawdown"], float)
    assert data["time_horizon"] == 1

def test_calculate_volatility(client, auth_headers, test_portfolio):
    """Testa o cálculo da Volatilidade"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/volatility",
        params={
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "volatility" in data
    assert "time_horizon" in data
    assert isinstance(data["volatility"], float)
    assert data["time_horizon"] == 1

def test_calculate_correlation_matrix(client, auth_headers, test_portfolio):
    """Testa o cálculo da Matriz de Correlação"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/correlation-matrix",
        params={
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "correlation_matrix" in data
    assert "time_horizon" in data
    assert isinstance(data["correlation_matrix"], dict)
    assert data["time_horizon"] == 1

def test_calculate_exposures(client, auth_headers, test_portfolio):
    """Testa o cálculo das Exposições"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/exposures",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sector_exposures" in data
    assert "country_exposures" in data
    assert "currency_exposures" in data
    assert isinstance(data["sector_exposures"], dict)
    assert isinstance(data["country_exposures"], dict)
    assert isinstance(data["currency_exposures"], dict)

def test_run_stress_test(client, auth_headers, test_portfolio):
    """Testa a execução do Stress Test"""
    response = client.post(
        f"/risk/portfolios/{test_portfolio.id}/stress-test",
        json={
            "scenarios": [
                {
                    "name": "Market Crash",
                    "description": "Simulação de queda do mercado",
                    "parameters": {
                        "market_decline": 0.2,
                        "volatility_increase": 0.5
                    }
                }
            ]
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert "scenario" in data["results"][0]
    assert "impact" in data["results"][0]
    assert "metrics" in data["results"][0]

def test_calculate_risk_metrics(client, auth_headers, test_portfolio):
    """Testa o cálculo de todas as métricas de risco"""
    response = client.get(
        f"/risk/portfolios/{test_portfolio.id}/metrics",
        params={
            "confidence_level": 0.95,
            "risk_free_rate": 0.02,
            "time_horizon": 1
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "value_at_risk" in data
    assert "expected_shortfall" in data
    assert "sharpe_ratio" in data
    assert "sortino_ratio" in data
    assert "max_drawdown" in data
    assert "volatility" in data
    assert "correlation_matrix" in data
    assert "exposures" in data
    assert isinstance(data["value_at_risk"], float)
    assert isinstance(data["expected_shortfall"], float)
    assert isinstance(data["sharpe_ratio"], float)
    assert isinstance(data["sortino_ratio"], float)
    assert isinstance(data["max_drawdown"], float)
    assert isinstance(data["volatility"], float)
    assert isinstance(data["correlation_matrix"], dict)
    assert isinstance(data["exposures"], dict) 