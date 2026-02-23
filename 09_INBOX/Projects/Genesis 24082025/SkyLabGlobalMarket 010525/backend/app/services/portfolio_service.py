from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import numpy as np

from ..models import Portfolio, Trade, RiskMetrics
from ..schemas import PortfolioCreate, PortfolioUpdate, TradeCreate, PortfolioPerformance

async def create_portfolio(db: Session, user_id: int, portfolio: PortfolioCreate) -> Portfolio:
    """
    Cria um novo portfólio para o usuário.
    """
    db_portfolio = Portfolio(
        **portfolio.dict(),
        user_id=user_id,
        current_balance=portfolio.initial_balance
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

async def update_portfolio(
    db: Session,
    portfolio_id: int,
    user_id: int,
    portfolio: PortfolioUpdate
) -> Portfolio:
    """
    Atualiza um portfólio existente.
    """
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    for field, value in portfolio.dict(exclude_unset=True).items():
        setattr(db_portfolio, field, value)
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

async def delete_portfolio(db: Session, portfolio_id: int, user_id: int) -> None:
    """
    Deleta um portfólio.
    """
    db_portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    db.delete(db_portfolio)
    db.commit()

async def create_trade(
    db: Session,
    portfolio_id: int,
    user_id: int,
    trade: TradeCreate
) -> Trade:
    """
    Cria um novo trade em um portfólio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    db_trade = Trade(**trade.dict(), portfolio_id=portfolio_id)
    db.add(db_trade)
    
    # Atualiza o saldo do portfólio
    trade_value = trade.quantity * trade.price
    if trade.type == "buy":
        portfolio.current_balance -= trade_value
    else:
        portfolio.current_balance += trade_value
    
    db.commit()
    db.refresh(db_trade)
    return db_trade

async def get_trades(
    db: Session,
    portfolio_id: int,
    user_id: int
) -> List[Trade]:
    """
    Retorna todos os trades de um portfólio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    return portfolio.trades

async def calculate_risk_metrics(
    db: Session,
    portfolio_id: int,
    user_id: int
) -> RiskMetrics:
    """
    Calcula as métricas de risco de um portfólio.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    trades = portfolio.trades
    if not trades:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há trades suficientes para calcular métricas de risco"
        )
    
    # Cálculos de métricas de risco
    returns = [trade.price for trade in trades]
    returns = np.array(returns)
    
    volatility = np.std(returns)
    sharpe_ratio = np.mean(returns) / volatility if volatility != 0 else 0
    
    cumulative_returns = np.cumsum(returns)
    max_drawdown = np.min(cumulative_returns - np.maximum.accumulate(cumulative_returns))
    
    # Value at Risk (VaR) - 95% confidence
    var_95 = np.percentile(returns, 5)
    
    # Beta e Alpha (simplificado)
    market_returns = np.random.normal(0.01, 0.02, len(returns))  # Exemplo
    beta = np.cov(returns, market_returns)[0, 1] / np.var(market_returns)
    alpha = np.mean(returns) - beta * np.mean(market_returns)
    
    # Atualiza ou cria métricas de risco
    risk_metrics = portfolio.risk_metrics
    if not risk_metrics:
        risk_metrics = RiskMetrics(portfolio_id=portfolio_id)
    
    risk_metrics.volatility = volatility
    risk_metrics.sharpe_ratio = sharpe_ratio
    risk_metrics.max_drawdown = max_drawdown
    risk_metrics.value_at_risk = var_95
    risk_metrics.beta = beta
    risk_metrics.alpha = alpha
    
    db.add(risk_metrics)
    db.commit()
    db.refresh(risk_metrics)
    
    return risk_metrics

async def get_portfolio_performance(
    db: Session,
    portfolio_id: int,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> PortfolioPerformance:
    """
    Calcula o desempenho do portfólio em um período.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    # Filtra trades por período
    query = db.query(Trade).filter(Trade.portfolio_id == portfolio_id)
    if start_date:
        query = query.filter(Trade.timestamp >= start_date)
    if end_date:
        query = query.filter(Trade.timestamp <= end_date)
    
    trades = query.all()
    
    if not trades:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há trades no período especificado"
        )
    
    # Cálculos de desempenho
    initial_balance = portfolio.initial_balance
    current_balance = portfolio.current_balance
    total_return = current_balance - initial_balance
    return_percentage = (total_return / initial_balance) * 100
    
    # Estatísticas de trades
    trades_count = len(trades)
    winning_trades = sum(1 for trade in trades if trade.type == "sell" and trade.price > 0)
    losing_trades = trades_count - winning_trades
    win_rate = (winning_trades / trades_count) * 100 if trades_count > 0 else 0
    
    # Médias de ganhos e perdas
    winning_prices = [trade.price for trade in trades if trade.type == "sell" and trade.price > 0]
    losing_prices = [trade.price for trade in trades if trade.type == "sell" and trade.price <= 0]
    
    average_win = np.mean(winning_prices) if winning_prices else 0
    average_loss = np.mean(losing_prices) if losing_prices else 0
    
    # Fator de lucro
    profit_factor = abs(average_win / average_loss) if average_loss != 0 else float('inf')
    
    return PortfolioPerformance(
        portfolio_id=portfolio_id,
        start_date=start_date or trades[0].timestamp,
        end_date=end_date or trades[-1].timestamp,
        initial_balance=initial_balance,
        current_balance=current_balance,
        total_return=total_return,
        return_percentage=return_percentage,
        trades_count=trades_count,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        average_win=average_win,
        average_loss=average_loss,
        profit_factor=profit_factor
    ) 