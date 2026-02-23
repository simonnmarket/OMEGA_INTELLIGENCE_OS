#!/usr/bin/env python3
"""
🏦 BASE STRATEGY - TEMPLATE GOLDMAN SACHS TIER-0
Interface obrigatória para todas as estratégias NCNT
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from decimal import Decimal


@dataclass
class TradeSignal:
    """Sinal de trade no formato NCNTTransmission"""
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: Decimal
    price: Decimal
    confidence: float  # 0.0 to 1.0
    strategy_id: str
    checksum: str
    
    def calculate_checksum(self) -> str:
        """Calcular checksum SHA3-256 do sinal"""
        data = f"{self.timestamp.isoformat()}{self.symbol}{self.action}{self.quantity}{self.price}{self.confidence}{self.strategy_id}"
        return hashlib.sha3_256(data.encode()).hexdigest()[:32]


class BaseStrategy(ABC):
    """Interface base para estratégias Goldman Sachs Tier-0"""
    
    def __init__(self, strategy_id: str, capital_allocation: Decimal):
        self.strategy_id = strategy_id
        self.capital_allocation = capital_allocation
        self.version = "1.0"
        self.required_params = []
        
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> List[TradeSignal]:
        """
        Analisar dados de mercado e gerar sinais
        RETORNO: Lista de TradeSignal com checksum válido
        """
        pass
    
    @abstractmethod
    def validate_parameters(self) -> bool:
        """
        Validar parâmetros da estratégia
        RETORNO: True se todos parâmetros são válidos
        """
        pass
    
    @abstractmethod
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """
        Calcular métricas de risco
        RETORNO: Dict com Sharpe, MaxDD, WinRate, etc.
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Retornar informações da estratégia"""
        return {
            "strategy_id": self.strategy_id,
            "version": self.version,
            "capital_allocation": str(self.capital_allocation),
            "required_params": self.required_params,
            "interface_version": "NCNT_TIER0_v2"
        }

