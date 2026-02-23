from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
import json
import asyncio
from datetime import datetime

from ..services import get_portfolio, get_portfolio_positions
from ..utils import format_currency, format_percentage
from ..database import get_db
from sqlalchemy.orm import Session

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()

async def portfolio_updates(websocket: WebSocket, user_id: int, portfolio_id: int, db: Session):
    """Envia atualizações do portfólio em tempo real"""
    try:
        while True:
            portfolio = get_portfolio(db, portfolio_id, user_id)
            if not portfolio:
                break
            
            positions = get_portfolio_positions(db, portfolio_id, user_id)
            
            # Prepara os dados do portfólio
            portfolio_data = {
                "type": "portfolio_update",
                "portfolio_id": portfolio.id,
                "name": portfolio.name,
                "current_balance": format_currency(portfolio.current_balance),
                "initial_balance": format_currency(portfolio.initial_balance),
                "total_return": format_percentage(
                    (portfolio.current_balance - portfolio.initial_balance) / portfolio.initial_balance
                ),
                "positions": [
                    {
                        "symbol": position.symbol,
                        "quantity": position.quantity,
                        "average_price": format_currency(position.average_price),
                        "current_price": format_currency(position.current_price),
                        "value": format_currency(position.quantity * position.current_price),
                        "pnl": format_currency(
                            (position.current_price - position.average_price) * position.quantity
                        ),
                        "pnl_percentage": format_percentage(
                            (position.current_price - position.average_price) / position.average_price
                        )
                    }
                    for position in positions
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast_to_user(user_id, portfolio_data)
            await asyncio.sleep(5)  # Atualiza a cada 5 segundos
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        await manager.broadcast_to_user(user_id, {
            "type": "error",
            "message": str(e)
        })

async def market_data_updates(websocket: WebSocket, user_id: int):
    """Envia atualizações de dados de mercado em tempo real"""
    try:
        while True:
            # Aqui você implementaria a lógica para obter dados de mercado em tempo real
            # Por enquanto, vamos usar dados simulados
            market_data = {
                "type": "market_update",
                "symbols": {
                    "AAPL": {
                        "price": 150.25,
                        "change": 1.25,
                        "change_percentage": 0.84
                    },
                    "MSFT": {
                        "price": 280.50,
                        "change": -0.75,
                        "change_percentage": -0.27
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast_to_user(user_id, market_data)
            await asyncio.sleep(1)  # Atualiza a cada segundo
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        await manager.broadcast_to_user(user_id, {
            "type": "error",
            "message": str(e)
        })

async def risk_metrics_updates(websocket: WebSocket, user_id: int, portfolio_id: int, db: Session):
    """Envia atualizações de métricas de risco em tempo real"""
    try:
        while True:
            # Aqui você implementaria a lógica para calcular métricas de risco em tempo real
            # Por enquanto, vamos usar dados simulados
            risk_metrics = {
                "type": "risk_update",
                "portfolio_id": portfolio_id,
                "value_at_risk": -0.025,
                "expected_shortfall": -0.035,
                "sharpe_ratio": 1.5,
                "sortino_ratio": 2.0,
                "max_drawdown": -0.15,
                "volatility": 0.20,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast_to_user(user_id, risk_metrics)
            await asyncio.sleep(60)  # Atualiza a cada minuto
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        await manager.broadcast_to_user(user_id, {
            "type": "error",
            "message": str(e)
        }) 