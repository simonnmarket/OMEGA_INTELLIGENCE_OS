from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats

from ..models import Portfolio, Position, Trade, RiskMetrics
from ..services.trading import calculate_position_metrics

def calculate_value_at_risk(
    returns: List[float],
    confidence_level: float = 0.95
) -> float:
    """Calcula o Value at Risk (VaR)"""
    return np.percentile(returns, (1 - confidence_level) * 100)

def calculate_expected_shortfall(
    returns: List[float],
    confidence_level: float = 0.95
) -> float:
    """Calcula o Expected Shortfall (ES)"""
    var = calculate_value_at_risk(returns, confidence_level)
    return np.mean([r for r in returns if r <= var])

def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """Calcula o Sharpe Ratio"""
    excess_returns = np.array(returns) - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0

def calculate_sortino_ratio(
    returns: List[float],
    risk_free_rate: float = 0.02
) -> float:
    """Calcula o Sortino Ratio"""
    excess_returns = np.array(returns) - risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
    return np.mean(excess_returns) / downside_std if downside_std != 0 else 0

def calculate_max_drawdown(returns: List[float]) -> float:
    """Calcula o Maximum Drawdown"""
    cumulative_returns = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - running_max) / running_max
    return np.min(drawdowns)

def calculate_volatility(returns: List[float]) -> float:
    """Calcula a Volatilidade"""
    return np.std(returns) * np.sqrt(252)  # Anualizada

def calculate_correlation_matrix(positions: List[Position]) -> Dict:
    """Calcula a matriz de correlação entre os ativos"""
    symbols = [p.symbol for p in positions]
    returns = {}
    
    for symbol in symbols:
        # Aqui você implementaria a lógica para obter os retornos históricos
        # Por enquanto, vamos usar dados simulados
        returns[symbol] = np.random.normal(0, 0.01, 100)
    
    df = pd.DataFrame(returns)
    return df.corr().to_dict()

def calculate_exposures(positions: List[Position]) -> Dict:
    """Calcula as exposições do portfólio"""
    total_value = sum(p.quantity * p.current_price for p in positions)
    
    # Exemplo de cálculo de exposição por setor
    sector_exposure = {}
    for position in positions:
        # Aqui você implementaria a lógica para obter o setor do ativo
        sector = "Technology"  # Exemplo
        value = position.quantity * position.current_price
        sector_exposure[sector] = sector_exposure.get(sector, 0) + value
    
    # Normaliza as exposições
    sector_exposure = {k: v/total_value for k, v in sector_exposure.items()}
    
    return {
        "sector": sector_exposure,
        "asset_class": {},  # Implementar similar ao setor
        "currency": {}      # Implementar similar ao setor
    }

def run_stress_test(
    positions: List[Position],
    scenarios: List[Dict]
) -> Dict:
    """Executa testes de estresse no portfólio"""
    results = {}
    
    for scenario in scenarios:
        scenario_name = scenario["name"]
        scenario_returns = scenario["returns"]
        
        # Calcula o impacto no portfólio
        portfolio_value = sum(
            p.quantity * p.current_price * (1 + scenario_returns.get(p.symbol, 0))
            for p in positions
        )
        
        results[scenario_name] = {
            "portfolio_value": portfolio_value,
            "impact": portfolio_value - sum(p.quantity * p.current_price for p in positions)
        }
    
    return results

def calculate_risk_metrics(
    db: Session,
    portfolio_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> RiskMetrics:
    """Calcula todas as métricas de risco para um portfólio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    # Obtém as posições
    positions = portfolio.positions
    
    # Obtém o histórico de trades
    trades = db.query(Trade).filter(
        Trade.portfolio_id == portfolio_id,
        Trade.status == "executed"
    ).all()
    
    # Calcula os retornos diários
    returns = []  # Implementar cálculo real dos retornos
    
    # Calcula as métricas
    metrics = RiskMetrics(
        user_id=user_id,
        portfolio_id=portfolio_id,
        value_at_risk=calculate_value_at_risk(returns),
        expected_shortfall=calculate_expected_shortfall(returns),
        sharpe_ratio=calculate_sharpe_ratio(returns),
        sortino_ratio=calculate_sortino_ratio(returns),
        max_drawdown=calculate_max_drawdown(returns),
        volatility=calculate_volatility(returns),
        correlation_matrix=calculate_correlation_matrix(positions),
        sector_exposure=calculate_exposures(positions)["sector"],
        asset_class_exposure=calculate_exposures(positions)["asset_class"],
        currency_exposure=calculate_exposures(positions)["currency"],
        stress_test_results=run_stress_test(positions, [
            {"name": "Market Crash", "returns": {"AAPL": -0.2, "MSFT": -0.15}},
            {"name": "Interest Rate Hike", "returns": {"AAPL": -0.1, "MSFT": -0.05}}
        ])
    )
    
    db.add(metrics)
    db.commit()
    db.refresh(metrics)
    
    return metrics 