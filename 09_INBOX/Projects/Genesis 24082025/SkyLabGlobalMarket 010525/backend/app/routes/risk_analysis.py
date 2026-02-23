from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import pandas as pd

from app.db.session import get_db
from app.models.risk_metrics import RiskMetrics
from app.models.portfolio import Portfolio
from app.services.risk_analysis import RiskAnalyzer
from app.schemas.risk_metrics import RiskMetricsCreate, RiskMetricsResponse
from app.core.security import get_current_user

router = APIRouter()

@router.get("/portfolios/{portfolio_id}/risk", response_model=RiskMetricsResponse)
async def get_portfolio_risk(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the latest risk metrics for a portfolio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    risk_metrics = db.query(RiskMetrics).filter(
        RiskMetrics.portfolio_id == portfolio_id
    ).order_by(RiskMetrics.timestamp.desc()).first()
    
    if not risk_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk metrics found for this portfolio"
        )
    
    return risk_metrics.to_dict()

@router.get("/portfolios/{portfolio_id}/risk/history", response_model=List[RiskMetricsResponse])
async def get_portfolio_risk_history(
    portfolio_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get historical risk metrics for a portfolio within a date range.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    risk_metrics = db.query(RiskMetrics).filter(
        RiskMetrics.portfolio_id == portfolio_id,
        RiskMetrics.timestamp >= start_date,
        RiskMetrics.timestamp <= end_date
    ).order_by(RiskMetrics.timestamp.desc()).all()
    
    return [metric.to_dict() for metric in risk_metrics]

@router.post("/portfolios/{portfolio_id}/risk/calculate", response_model=RiskMetricsResponse)
async def calculate_portfolio_risk(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Calculate and store new risk metrics for a portfolio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Get portfolio returns (this would need to be implemented based on your data source)
    returns = get_portfolio_returns(portfolio_id, db)
    
    # Initialize risk analyzer
    risk_analyzer = RiskAnalyzer(returns)
    
    # Generate risk report
    risk_report = risk_analyzer.generate_risk_report()
    
    # Check for alerts
    thresholds = {
        'volatility_threshold': 0.3,
        'drawdown_threshold': 0.2,
        'var_threshold': 0.05
    }
    alerts = risk_analyzer.check_risk_alerts(thresholds)
    
    # Create new risk metrics record
    risk_metrics = RiskMetrics(
        portfolio_id=portfolio_id,
        timestamp=datetime.utcnow(),
        sharpe_ratio=risk_report['sharpe_ratio'],
        volatility=risk_report['volatility'],
        beta=risk_report.get('beta'),
        value_at_risk_95=risk_report['value_at_risk_95'],
        max_drawdown=risk_report['max_drawdown'],
        correlation_with_market=risk_report.get('correlation_with_market'),
        high_volatility_alert=alerts.get('high_volatility'),
        significant_drawdown_alert=alerts.get('significant_drawdown'),
        high_var_alert=alerts.get('high_var')
    )
    
    db.add(risk_metrics)
    db.commit()
    db.refresh(risk_metrics)
    
    return risk_metrics.to_dict()

@router.put("/portfolios/{portfolio_id}/risk/thresholds", response_model=RiskMetricsResponse)
async def update_risk_thresholds(
    portfolio_id: int,
    thresholds: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update risk alert thresholds for a portfolio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    risk_metrics = db.query(RiskMetrics).filter(
        RiskMetrics.portfolio_id == portfolio_id
    ).order_by(RiskMetrics.timestamp.desc()).first()
    
    if not risk_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk metrics found for this portfolio"
        )
    
    # Update thresholds
    risk_metrics.volatility_threshold = thresholds.get('volatility_threshold', risk_metrics.volatility_threshold)
    risk_metrics.drawdown_threshold = thresholds.get('drawdown_threshold', risk_metrics.drawdown_threshold)
    risk_metrics.var_threshold = thresholds.get('var_threshold', risk_metrics.var_threshold)
    
    db.commit()
    db.refresh(risk_metrics)
    
    return risk_metrics.to_dict()

def get_portfolio_returns(portfolio_id: int, db: Session) -> pd.Series:
    """
    Helper function to get portfolio returns from the database.
    This is a placeholder - implement based on your actual data structure.
    """
    # TODO: Implement actual portfolio returns calculation
    # This would typically involve:
    # 1. Getting all trades for the portfolio
    # 2. Calculating daily returns
    # 3. Returning a pandas Series of returns
    pass 