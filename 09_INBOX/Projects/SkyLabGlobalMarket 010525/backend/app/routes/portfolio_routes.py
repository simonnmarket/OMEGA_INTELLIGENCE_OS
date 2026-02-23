from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models import User, Portfolio, Trade, RiskMetrics
from ..schemas import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    TradeCreate,
    TradeResponse,
    RiskMetricsResponse
)
from ..database import get_db
from ..services.portfolio_service import (
    create_portfolio,
    update_portfolio,
    delete_portfolio,
    create_trade,
    get_trades,
    calculate_risk_metrics,
    get_portfolio_performance
)
from ..utils.rate_limiting import rate_limit
from ..utils.auth import get_current_user

router = APIRouter()

@router.post("/portfolios", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
@rate_limit("api")
async def create_user_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo portfólio para o usuário.
    """
    return await create_portfolio(db, current_user.id, portfolio)

@router.get("/portfolios", response_model=List[PortfolioResponse])
@rate_limit("api")
async def get_user_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todos os portfólios do usuário.
    """
    return current_user.portfolios

@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
@rate_limit("api")
async def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna um portfólio específico do usuário.
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfólio não encontrado"
        )
    
    return portfolio

@router.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
@rate_limit("api")
async def update_user_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um portfólio do usuário.
    """
    return await update_portfolio(db, portfolio_id, current_user.id, portfolio)

@router.delete("/portfolios/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
@rate_limit("api")
async def delete_user_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta um portfólio do usuário.
    """
    await delete_portfolio(db, portfolio_id, current_user.id)

@router.post("/portfolios/{portfolio_id}/trades", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
@rate_limit("api")
async def create_portfolio_trade(
    portfolio_id: int,
    trade: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo trade em um portfólio.
    """
    return await create_trade(db, portfolio_id, current_user.id, trade)

@router.get("/portfolios/{portfolio_id}/trades", response_model=List[TradeResponse])
@rate_limit("api")
async def get_portfolio_trades(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todos os trades de um portfólio.
    """
    return await get_trades(db, portfolio_id, current_user.id)

@router.get("/portfolios/{portfolio_id}/risk", response_model=RiskMetricsResponse)
@rate_limit("api")
async def get_portfolio_risk(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna as métricas de risco de um portfólio.
    """
    return await calculate_risk_metrics(db, portfolio_id, current_user.id)

@router.get("/portfolios/{portfolio_id}/performance")
@rate_limit("api")
async def get_portfolio_performance_metrics(
    portfolio_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna o desempenho do portfólio em um período.
    """
    return await get_portfolio_performance(
        db,
        portfolio_id,
        current_user.id,
        start_date,
        end_date
    ) 