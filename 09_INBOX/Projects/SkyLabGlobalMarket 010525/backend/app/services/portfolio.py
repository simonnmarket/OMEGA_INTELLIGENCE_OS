from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Portfolio, Position, Trade
from ..services.trading import calculate_position_metrics

def get_portfolio(db: Session, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
    return db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()

def get_user_portfolios(db: Session, user_id: int) -> List[Portfolio]:
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

def create_portfolio(
    db: Session,
    name: str,
    user_id: int,
    description: Optional[str] = None,
    initial_balance: float = 0.0
) -> Portfolio:
    portfolio = Portfolio(
        name=name,
        description=description,
        initial_balance=initial_balance,
        current_balance=initial_balance,
        user_id=user_id
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio

def update_portfolio(
    db: Session,
    portfolio_id: int,
    user_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[Portfolio]:
    portfolio = get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        return None
    
    if name:
        portfolio.name = name
    if description:
        portfolio.description = description
    
    db.commit()
    db.refresh(portfolio)
    return portfolio

def delete_portfolio(db: Session, portfolio_id: int, user_id: int) -> bool:
    portfolio = get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        return False
    
    db.delete(portfolio)
    db.commit()
    return True

def get_portfolio_positions(db: Session, portfolio_id: int, user_id: int) -> List[Position]:
    portfolio = get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        return []
    
    return portfolio.positions

def update_portfolio_balance(db: Session, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
    portfolio = get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        return None
    
    # Calcula o saldo atual baseado nas posições
    total_value = sum(
        position.quantity * position.current_price
        for position in portfolio.positions
    )
    
    portfolio.current_balance = total_value
    db.commit()
    db.refresh(portfolio)
    return portfolio

def get_portfolio_performance(
    db: Session,
    portfolio_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    portfolio = get_portfolio(db, portfolio_id, user_id)
    if not portfolio:
        return {}
    
    # Filtra trades por período
    query = db.query(Trade).filter(
        Trade.portfolio_id == portfolio_id,
        Trade.status == "executed"
    )
    
    if start_date:
        query = query.filter(Trade.execution_time >= start_date)
    if end_date:
        query = query.filter(Trade.execution_time <= end_date)
    
    trades = query.all()
    
    # Calcula métricas de performance
    initial_value = portfolio.initial_balance
    current_value = portfolio.current_balance
    total_return = (current_value - initial_value) / initial_value if initial_value > 0 else 0
    
    return {
        "initial_value": initial_value,
        "current_value": current_value,
        "total_return": total_return,
        "trade_count": len(trades),
        "positions": [
            calculate_position_metrics(position)
            for position in portfolio.positions
        ]
    } 