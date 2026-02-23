from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..services import (
    get_portfolio_data,
    get_risk_metrics,
    execute_trade,
    get_trading_history,
    generate_report
)
from ..models import User, Portfolio, Trade, RiskMetrics
from ..config import settings
from ..database import get_db
from ..schemas import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    TradeCreate,
    TradeResponse,
    RiskMetricsResponse
)
from ..utils.rate_limiting import rate_limit

router = APIRouter()

# Configurações de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class TradeCreate(BaseModel):
    symbol: str
    type: str
    volume: float
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

# Funções de autenticação
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await User.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Rotas de autenticação
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = await User.create(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    return db_user

# Rotas de portfólio
@router.get("/portfolio/", response_model=List[Portfolio])
async def get_portfolio(current_user: User = Depends(get_current_user)):
    portfolio = await get_portfolio_data(current_user.id)
    return portfolio

@router.post("/portfolio/rebalance/")
async def rebalance_portfolio(
    allocations: dict,
    current_user: User = Depends(get_current_user)
):
    # Implementar lógica de rebalanceamento
    return {"message": "Portfolio rebalanced successfully"}

# Rotas de trading
@router.post("/trading/execute/", response_model=Trade)
async def create_trade(
    trade: TradeCreate,
    current_user: User = Depends(get_current_user)
):
    new_trade = await execute_trade(
        user_id=current_user.id,
        symbol=trade.symbol,
        trade_type=trade.type,
        volume=trade.volume,
        price=trade.price,
        stop_loss=trade.stop_loss,
        take_profit=trade.take_profit
    )
    return new_trade

@router.get("/trading/history/", response_model=List[Trade])
async def get_trading_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    history = await get_trading_history(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return history

# Rotas de análise de risco
@router.get("/risk/metrics/")
async def get_risk_metrics(current_user: User = Depends(get_current_user)):
    metrics = await get_risk_metrics(user_id=current_user.id)
    return metrics

@router.post("/risk/simulation/")
async def run_risk_simulation(
    scenario: dict,
    current_user: User = Depends(get_current_user)
):
    # Implementar simulação de risco
    return {"message": "Risk simulation completed"}

# Rotas de relatórios
@router.get("/reports/performance/")
async def get_performance_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    report = await generate_report(
        user_id=current_user.id,
        report_type="performance",
        start_date=start_date,
        end_date=end_date
    )
    return report

@router.get("/reports/risk/")
async def get_risk_report(
    current_user: User = Depends(get_current_user)
):
    report = await generate_report(
        user_id=current_user.id,
        report_type="risk"
    )
    return report

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