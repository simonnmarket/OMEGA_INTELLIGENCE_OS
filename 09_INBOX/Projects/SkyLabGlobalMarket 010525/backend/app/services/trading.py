from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import MetaTrader5 as mt5

from ..models import Trade, Position, TradeType, TradeStatus
from ..config import settings

def initialize_mt5():
    """Inicializa a conexão com o MetaTrader 5"""
    if not mt5.initialize(
        server=settings.MT5_SERVER,
        login=settings.MT5_LOGIN,
        password=settings.MT5_PASSWORD,
        port=settings.MT5_PORT
    ):
        raise Exception(f"Falha ao inicializar MT5: {mt5.last_error()}")

def calculate_position_metrics(position: Position) -> Dict:
    """Calcula métricas para uma posição"""
    current_value = position.quantity * position.current_price
    average_value = position.quantity * position.average_price
    pnl = current_value - average_value
    pnl_percentage = (pnl / average_value) * 100 if average_value > 0 else 0
    
    return {
        "symbol": position.symbol,
        "quantity": position.quantity,
        "average_price": position.average_price,
        "current_price": position.current_price,
        "current_value": current_value,
        "pnl": pnl,
        "pnl_percentage": pnl_percentage
    }

def execute_trade(
    db: Session,
    symbol: str,
    trade_type: TradeType,
    volume: float,
    price: float,
    user_id: int,
    portfolio_id: int,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> Trade:
    """Executa uma ordem de trade"""
    # Cria o registro do trade
    trade = Trade(
        symbol=symbol,
        type=trade_type,
        volume=volume,
        price=price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        status=TradeStatus.PENDING,
        user_id=user_id,
        portfolio_id=portfolio_id
    )
    db.add(trade)
    db.commit()
    
    try:
        # Inicializa MT5
        initialize_mt5()
        
        # Prepara a ordem
        order_type = mt5.ORDER_TYPE_BUY if trade_type == TradeType.BUY else mt5.ORDER_TYPE_SELL
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 234000,
            "comment": f"Trade {trade.id}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Envia a ordem
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            trade.status = TradeStatus.REJECTED
            db.commit()
            raise Exception(f"Falha ao executar ordem: {result.comment}")
        
        # Atualiza o status do trade
        trade.status = TradeStatus.EXECUTED
        trade.execution_time = datetime.utcnow()
        db.commit()
        
        # Atualiza a posição
        update_position(db, trade)
        
        return trade
        
    except Exception as e:
        trade.status = TradeStatus.REJECTED
        db.commit()
        raise e

def update_position(db: Session, trade: Trade) -> None:
    """Atualiza a posição após um trade"""
    position = db.query(Position).filter(
        Position.portfolio_id == trade.portfolio_id,
        Position.symbol == trade.symbol
    ).first()
    
    if trade.type == TradeType.BUY:
        if position:
            # Atualiza posição existente
            total_quantity = position.quantity + trade.volume
            total_value = (position.quantity * position.average_price) + (trade.volume * trade.price)
            position.average_price = total_value / total_quantity
            position.quantity = total_quantity
        else:
            # Cria nova posição
            position = Position(
                symbol=trade.symbol,
                quantity=trade.volume,
                average_price=trade.price,
                current_price=trade.price,
                portfolio_id=trade.portfolio_id
            )
            db.add(position)
    else:  # SELL
        if position:
            position.quantity -= trade.volume
            if position.quantity <= 0:
                db.delete(position)
    
    db.commit()

def get_trade_history(
    db: Session,
    user_id: int,
    portfolio_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Trade]:
    """Obtém histórico de trades"""
    query = db.query(Trade).filter(Trade.user_id == user_id)
    
    if portfolio_id:
        query = query.filter(Trade.portfolio_id == portfolio_id)
    if start_date:
        query = query.filter(Trade.execution_time >= start_date)
    if end_date:
        query = query.filter(Trade.execution_time <= end_date)
    
    return query.order_by(Trade.execution_time.desc()).all()

def cancel_trade(db: Session, trade_id: int, user_id: int) -> bool:
    """Cancela um trade pendente"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == user_id,
        Trade.status == TradeStatus.PENDING
    ).first()
    
    if not trade:
        return False
    
    trade.status = TradeStatus.CANCELLED
    db.commit()
    return True 