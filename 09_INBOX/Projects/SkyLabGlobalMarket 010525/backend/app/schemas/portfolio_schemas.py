from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeCreate(BaseModel):
    symbol: str = Field(..., description="Símbolo do ativo")
    type: TradeType = Field(..., description="Tipo da operação (compra/venda)")
    quantity: float = Field(..., gt=0, description="Quantidade de ativos")
    price: float = Field(..., gt=0, description="Preço por unidade")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da operação")
    notes: Optional[str] = Field(None, description="Observações sobre a operação")

class TradeResponse(TradeCreate):
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nome do portfólio")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do portfólio")
    initial_balance: float = Field(..., gt=0, description="Saldo inicial do portfólio")
    currency: str = Field(default="USD", description="Moeda do portfólio")

class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    initial_balance: float
    current_balance: float
    currency: str
    is_active: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
    trades: List[TradeResponse] = []

    class Config:
        orm_mode = True

class RiskMetricsResponse(BaseModel):
    portfolio_id: int
    volatility: float = Field(..., description="Volatilidade do portfólio")
    sharpe_ratio: float = Field(..., description="Índice de Sharpe")
    max_drawdown: float = Field(..., description="Máxima perda em sequência")
    value_at_risk: float = Field(..., description="Value at Risk (VaR)")
    beta: float = Field(..., description="Beta do portfólio")
    alpha: float = Field(..., description="Alpha do portfólio")
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PortfolioPerformance(BaseModel):
    portfolio_id: int
    start_date: datetime
    end_date: datetime
    initial_balance: float
    current_balance: float
    total_return: float
    return_percentage: float
    trades_count: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float 