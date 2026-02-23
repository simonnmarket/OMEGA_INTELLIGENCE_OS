from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
import re

class TradeValidation(BaseModel):
    """Validação de dados de trade"""
    symbol: str
    type: str
    volume: float
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]+$', v):
            raise ValueError('Symbol must contain only uppercase letters')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['buy', 'sell']:
            raise ValueError('Type must be either "buy" or "sell"')
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        if v <= 0:
            raise ValueError('Volume must be greater than 0')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @validator('stop_loss')
    def validate_stop_loss(cls, v, values):
        if v is not None and 'price' in values:
            if values['type'] == 'buy' and v >= values['price']:
                raise ValueError('Stop loss must be below price for buy orders')
            if values['type'] == 'sell' and v <= values['price']:
                raise ValueError('Stop loss must be above price for sell orders')
        return v
    
    @validator('take_profit')
    def validate_take_profit(cls, v, values):
        if v is not None and 'price' in values:
            if values['type'] == 'buy' and v <= values['price']:
                raise ValueError('Take profit must be above price for buy orders')
            if values['type'] == 'sell' and v >= values['price']:
                raise ValueError('Take profit must be below price for sell orders')
        return v

class PortfolioValidation(BaseModel):
    """Validação de dados de portfólio"""
    name: str
    description: Optional[str] = None
    initial_balance: float
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters long')
        return v
    
    @validator('initial_balance')
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Initial balance cannot be negative')
        return v

class UserValidation(BaseModel):
    """Validação de dados de usuário"""
    username: str
    email: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

def validate_trade_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dados de trade"""
    try:
        return TradeValidation(**data).dict()
    except ValidationError as e:
        raise ValueError(str(e))

def validate_portfolio_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dados de portfólio"""
    try:
        return PortfolioValidation(**data).dict()
    except ValidationError as e:
        raise ValueError(str(e))

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida dados de usuário"""
    try:
        return UserValidation(**data).dict()
    except ValidationError as e:
        raise ValueError(str(e))

def validate_date_range(start_date: Optional[datetime], end_date: Optional[datetime]) -> None:
    """Valida um intervalo de datas"""
    if start_date and end_date and start_date > end_date:
        raise ValueError('Start date must be before end date')
    if start_date and start_date > datetime.utcnow():
        raise ValueError('Start date cannot be in the future')
    if end_date and end_date > datetime.utcnow():
        raise ValueError('End date cannot be in the future')

def validate_risk_parameters(
    confidence_level: float,
    risk_free_rate: float,
    time_horizon: int
) -> None:
    """Valida parâmetros de risco"""
    if not 0 < confidence_level < 1:
        raise ValueError('Confidence level must be between 0 and 1')
    if not 0 <= risk_free_rate < 1:
        raise ValueError('Risk-free rate must be between 0 and 1')
    if time_horizon <= 0:
        raise ValueError('Time horizon must be positive') 