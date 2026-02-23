#!/usr/bin/env python3
"""
🏦 ENDPOINTS DE ESTRATÉGIAS - API REST TIER-0
Endpoints objetivos e mensuráveis
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import sys
import importlib.util
from pathlib import Path

# Adicionar caminho do projeto
project_root = Path(__file__).parent.parent.parent.parent
strategies_path = project_root / "01-Departamentos" / "Execution-Trading" / "strategies"

# Importar estratégias dinamicamente (evita problemas com hífens em nomes de diretórios)
spec_alpha = importlib.util.spec_from_file_location(
    "alpha_momentum",
    strategies_path / "alpha_momentum.py"
)
alpha_momentum = importlib.util.module_from_spec(spec_alpha)
spec_alpha.loader.exec_module(alpha_momentum)

spec_mean = importlib.util.spec_from_file_location(
    "mean_reversion",
    strategies_path / "mean_reversion.py"
)
mean_reversion = importlib.util.module_from_spec(spec_mean)
spec_mean.loader.exec_module(mean_reversion)

spec_breakout = importlib.util.spec_from_file_location(
    "breakout_detection",
    strategies_path / "breakout_detection.py"
)
breakout_detection = importlib.util.module_from_spec(spec_breakout)
spec_breakout.loader.exec_module(breakout_detection)

AlphaMomentumStrategy = alpha_momentum.AlphaMomentumStrategy
MeanReversionStrategy = mean_reversion.MeanReversionStrategy
BreakoutDetectionStrategy = breakout_detection.BreakoutDetectionStrategy

from ..database.connection import check_db_connection

router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])

# Mapa de estratégias (singleton)
strategy_map = {
    "ALPHA_MOMENTUM_v1": AlphaMomentumStrategy(),
    "MEAN_REVERSION_v1": MeanReversionStrategy(),
    "BREAKOUT_DETECTION_v1": BreakoutDetectionStrategy()
}


# MODELOS PYDANTIC (VALIDATION STRICT)
class StrategyExecuteRequest(BaseModel):
    """Request para execução de estratégia"""
    strategy_id: str
    market_data: Dict[str, Any]
    timestamp: datetime
    
    @validator('strategy_id')
    def validate_strategy_id(cls, v):
        allowed_strategies = ["ALPHA_MOMENTUM_v1", "MEAN_REVERSION_v1", "BREAKOUT_DETECTION_v1"]
        if v not in allowed_strategies:
            raise ValueError(f"Strategy must be one of {allowed_strategies}")
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        if v > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
        return v


class TradeSignalResponse(BaseModel):
    """Response formatado de sinal de trade"""
    signal_id: str
    timestamp: datetime
    symbol: str
    action: str
    quantity: float
    price: float
    confidence: float
    strategy_id: str
    checksum: str
    execution_required: bool


# ENDPOINTS CRÍTICOS
@router.post("/execute", response_model=List[TradeSignalResponse])
async def execute_strategy(request: StrategyExecuteRequest):
    """
    EXECUTAR ESTRATÉGIA - Endpoint principal
    """
    # 1. VALIDAÇÃO DE DADOS DE ENTRADA
    required_market_fields = ["close", "high", "low", "volume", "timestamp", "symbol"]
    for field in required_market_fields:
        if field not in request.market_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required market data field: {field}"
            )
    
    # 2. SELEÇÃO DA ESTRATÉGIA (DECISÃO OBJETIVA)
    if request.strategy_id not in strategy_map:
        raise HTTPException(
            status_code=404,
            detail=f"Strategy {request.strategy_id} not implemented"
        )
    
    # 3. EXECUÇÃO DA ESTRATÉGIA
    strategy = strategy_map[request.strategy_id]
    signals = strategy.analyze(request.market_data)
    
    # 4. FORMATAR RESPOSTA
    response_signals = []
    for i, signal in enumerate(signals):
        response_signals.append(TradeSignalResponse(
            signal_id=f"SIG_{request.strategy_id}_{int(request.timestamp.timestamp())}_{i}",
            timestamp=signal.timestamp,
            symbol=signal.symbol,
            action=signal.action,
            quantity=float(signal.quantity),
            price=float(signal.price),
            confidence=signal.confidence,
            strategy_id=signal.strategy_id,
            checksum=signal.checksum,
            execution_required=signal.confidence > 0.7
        ))
    
    return response_signals


@router.get("/health")
async def health_check():
    """
    HEALTH CHECK - Endpoint de monitoramento
    RETORNO: Status objetivo do sistema
    """
    checks = {
        "database": check_db_connection(),
        "strategies_loaded": len(strategy_map) == 3,
        "api_responding": True,
        "timestamp": datetime.now().isoformat(),
        "system_version": "NCNT_TIER0_v2"
    }
    
    status = "HEALTHY" if all(checks.values()) else "UNHEALTHY"
    
    return {
        "status": status,
        "checks": checks,
        "checksum": hashlib.sha3_256(str(checks).encode()).hexdigest()[:32]
    }


# ENDPOINT DE MÉTRICAS (OBJETIVO)
@router.get("/metrics/{strategy_id}")
async def get_strategy_metrics(strategy_id: str):
    """
    OBTER MÉTRICAS DA ESTRATÉGIA
    """
    # DADOS PRÉ-DEFINIDOS PARA TESTE
    metrics = {
        "ALPHA_MOMENTUM_v1": {
            "sharpe_ratio": 1.82,
            "max_drawdown": 0.12,
            "win_rate": 0.57,
            "total_trades": 142,
            "profit_factor": 1.62,
            "avg_trade_duration_hours": 26.3
        },
        "MEAN_REVERSION_v1": {
            "sharpe_ratio": 1.65,
            "max_drawdown": 0.14,
            "win_rate": 0.61,
            "total_trades": 189,
            "profit_factor": 1.48,
            "avg_trade_duration_hours": 18.7
        },
        "BREAKOUT_DETECTION_v1": {
            "sharpe_ratio": 1.91,
            "max_drawdown": 0.11,
            "win_rate": 0.53,
            "total_trades": 97,
            "profit_factor": 1.73,
            "avg_trade_duration_hours": 32.1
        }
    }
    
    if strategy_id not in metrics:
        raise HTTPException(status_code=404, detail="Strategy metrics not found")
    
    return {
        "strategy_id": strategy_id,
        "metrics": metrics[strategy_id],
        "timestamp": datetime.now().isoformat()
    }
