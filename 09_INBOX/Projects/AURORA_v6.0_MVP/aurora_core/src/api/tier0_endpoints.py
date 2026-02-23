"""
API Endpoints Tier-0
Com autenticação, rate limiting, e validação completa
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1", tags=["trading"])


# Modelos Pydantic para requests
class TradeRequest(BaseModel):
    """Request para execução de trade"""
    symbol: str = Field(..., min_length=3, max_length=10, description="Símbolo do instrumento")
    operation: str = Field(..., pattern="^(BUY|SELL)$", description="Tipo de operação")
    volume: float = Field(..., gt=0, le=100, description="Volume em lotes")
    price: Optional[float] = Field(None, gt=0, description="Preço (None para market order)")
    drawdown: float = Field(default=0.0, ge=-1.0, le=1.0, description="Drawdown atual")
    idempotency_key: Optional[str] = Field(None, description="Chave de idempotência")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "EURUSD",
                "operation": "BUY",
                "volume": 0.01,
                "idempotency_key": "unique-key-123"
            }
        }


class TradeResponse(BaseModel):
    """Response de execução de trade"""
    trade_id: Optional[str] = None
    status: str
    reason: Optional[str] = None
    executed_price: Optional[float] = None
    slippage: Optional[float] = None
    timestamp: str
    demo: bool = True
    cached: bool = False


class RiskStatusResponse(BaseModel):
    """Response de status do risk engine"""
    state: str
    metrics: Dict[str, Any]
    limits: Optional[Dict[str, float]] = None
    demo: bool = True


# Global instances (set by app startup)
_orchestrator = None
_auth_middleware = None


def set_orchestrator(orchestrator: Any) -> None:
    """Set global orchestrator instance"""
    global _orchestrator
    _orchestrator = orchestrator


def set_auth_middleware(middleware: Any) -> None:
    """Set global auth middleware instance"""
    global _auth_middleware
    _auth_middleware = middleware


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Dict[str, Any]:
    """Dependency para autenticação"""
    from src.auth.tier0_auth import authenticate_request
    
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    try:
        return await authenticate_request(
            authorization=authorization,
            api_key=x_api_key,
            client_ip=client_ip,
            auth_middleware=_auth_middleware
        )
    except Exception as e:
        # Se demo mode, permitir
        if os.getenv("DEMO_MODE", "false").lower() == "true":
            return {"auth_method": "demo", "user": {"name": "demo_user"}}
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/trade", response_model=TradeResponse)
async def execute_trade(
    request: TradeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> TradeResponse:
    """
    Executar trade com todas as verificações Tier-0
    
    Requer autenticação via:
    - JWT Bearer token, ou
    - X-API-Key header, ou
    - Demo mode (apenas para desenvolvimento)
    """
    global _orchestrator
    
    if not _orchestrator or not _orchestrator.execution:
        raise HTTPException(status_code=503, detail="Execution engine not ready")
    
    # Converter para dict para o execution engine
    trade_data = request.model_dump()
    
    # Adicionar informações de autenticação
    trade_data["user"] = current_user.get("user", {}).get("name", "unknown")
    trade_data["auth_method"] = current_user.get("auth_method", "unknown")
    
    # Executar trade
    result = await _orchestrator.execution.execute_trade(trade_data)
    
    # Converter para response model
    return TradeResponse(
        trade_id=result.get("trade_id"),
        status=result.get("status", "unknown"),
        reason=result.get("reason"),
        executed_price=result.get("executed_price"),
        slippage=result.get("slippage"),
        timestamp=result.get("timestamp", datetime.utcnow().isoformat()),
        demo=result.get("demo", True),
        cached=result.get("cached", False)
    )


@router.get("/trade/{trade_id}/status")
async def get_trade_status(
    trade_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter status de um trade"""
    global _orchestrator
    
    if not _orchestrator or not _orchestrator.execution:
        raise HTTPException(status_code=503, detail="Execution engine not ready")
    
    status = await _orchestrator.execution.get_execution_status(trade_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return status


@router.get("/risk/status", response_model=RiskStatusResponse)
async def get_risk_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> RiskStatusResponse:
    """Obter status atual do risk engine"""
    global _orchestrator
    
    if not _orchestrator or not _orchestrator.risk:
        raise HTTPException(status_code=503, detail="Risk engine not ready")
    
    state = _orchestrator.risk.get_state()
    
    # Demo users têm acesso limitado
    if current_user.get("auth_method") == "demo":
        return RiskStatusResponse(
            state=state["state"],
            metrics=state["metrics"],
            demo=True
        )
    
    # Usuários autenticados têm acesso completo
    return RiskStatusResponse(
        state=state["state"],
        metrics=state["metrics"],
        limits=state["limits"],
        demo=True
    )


@router.get("/risk/audit")
async def get_risk_audit(
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter audit trail do risk engine"""
    global _orchestrator
    
    if not _orchestrator or not _orchestrator.risk:
        raise HTTPException(status_code=503, detail="Risk engine not ready")
    
    # Apenas usuários autenticados podem ver audit trail
    if current_user.get("auth_method") == "demo":
        raise HTTPException(status_code=403, detail="Audit trail not available in demo mode")
    
    audit = _orchestrator.risk.get_audit_trail(limit)
    
    return {
        "count": len(audit),
        "entries": audit
    }


@router.get("/circuit-breakers")
async def get_circuit_breakers(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter status dos circuit breakers"""
    global _orchestrator
    
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    breakers = {}
    for name, cb in _orchestrator.circuit_breakers.items():
        state = await cb.get_state()
        breakers[name] = {
            "state": state["state"].value,
            "failure_count": state["failure_count"],
            "last_failure": state["last_failure"]
        }
    
    return {"circuit_breakers": breakers}


@router.post("/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(
    name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Reset manual de circuit breaker"""
    global _orchestrator
    
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    # Apenas usuários autenticados podem resetar
    if current_user.get("auth_method") == "demo":
        raise HTTPException(status_code=403, detail="Not allowed in demo mode")
    
    if name not in _orchestrator.circuit_breakers:
        raise HTTPException(status_code=404, detail=f"Circuit breaker '{name}' not found")
    
    _orchestrator.circuit_breakers[name].reset()
    
    return {
        "message": f"Circuit breaker '{name}' reset successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/account")
async def get_account_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter informações da conta MT5"""
    global _orchestrator
    
    if not _orchestrator or not _orchestrator.mt5:
        raise HTTPException(status_code=503, detail="MT5 connector not ready")
    
    return _orchestrator.mt5.get_account_info()

