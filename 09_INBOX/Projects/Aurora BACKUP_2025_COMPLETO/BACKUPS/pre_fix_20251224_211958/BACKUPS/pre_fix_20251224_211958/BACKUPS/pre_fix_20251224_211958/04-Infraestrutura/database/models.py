#!/usr/bin/env python3
"""
🏦 DATABASE MODELS - NCNT Tier-0
Modelos SQLAlchemy para persistência
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal

Base = declarative_base()


class StrategyExecution(Base):
    """Tabela de execuções de estratégias"""
    __tablename__ = "strategy_executions"
    
    execution_id = Column(String(64), primary_key=True)
    strategy_id = Column(String(64), nullable=False, index=True)
    symbol = Column(String(32), nullable=False)
    action = Column(String(8), nullable=False)  # BUY, SELL, HOLD
    quantity = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8), nullable=False)
    confidence = Column(Float, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)
    executed_at = Column(DateTime, default=func.now(), nullable=False)
    status = Column(String(16), default="PENDING")  # PENDING, EXECUTED, FAILED
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Trade(Base):
    """Tabela de trades executados"""
    __tablename__ = "trades"
    
    trade_id = Column(String(64), primary_key=True)
    execution_id = Column(String(64), nullable=False, index=True)
    strategy_id = Column(String(64), nullable=False, index=True)
    symbol = Column(String(32), nullable=False)
    side = Column(String(8), nullable=False)  # BUY, SELL
    quantity = Column(Numeric(18, 8), nullable=False)
    entry_price = Column(Numeric(18, 8), nullable=False)
    exit_price = Column(Numeric(18, 8), nullable=True)
    pnl = Column(Numeric(18, 8), nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    opened_at = Column(DateTime, default=func.now(), nullable=False)
    closed_at = Column(DateTime, nullable=True)
    status = Column(String(16), default="OPEN")  # OPEN, CLOSED, CANCELLED
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PerformanceMetrics(Base):
    """Tabela de métricas de performance"""
    __tablename__ = "performance_metrics"
    
    metric_id = Column(String(64), primary_key=True)
    strategy_id = Column(String(64), nullable=False, index=True)
    metric_date = Column(DateTime, default=func.now(), nullable=False, index=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    total_trades = Column(Integer, default=0)
    total_pnl = Column(Numeric(18, 8), default=0)
    avg_trade_duration_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

