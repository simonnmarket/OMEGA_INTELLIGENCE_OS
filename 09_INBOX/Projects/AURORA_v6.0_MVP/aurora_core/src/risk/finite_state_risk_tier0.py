"""
Risk Engine Tier-0
Finite State Machine com validação Pydantic e audit trail
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)


class RiskState(Enum):
    """Estados da máquina de risco"""
    NORMAL = "NORMAL"       # Operação normal
    WARNING = "WARNING"     # Alerta, reduzir posições
    CRITICAL = "CRITICAL"   # Crítico, novas posições bloqueadas
    HALTED = "HALTED"       # Parado, todas operações bloqueadas


class TradeData(BaseModel):
    """Modelo Pydantic para validação de dados de trade"""
    symbol: str = Field(..., min_length=3, max_length=10)
    operation: str = Field(..., pattern="^(BUY|SELL)$")
    volume: float = Field(..., gt=0, le=100)
    price: float = Field(..., gt=0)
    drawdown: float = Field(default=0.0, ge=-1.0, le=1.0)
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v.isupper():
            raise ValueError('Symbol must be uppercase')
        return v
    
    @field_validator('drawdown')
    @classmethod
    def validate_drawdown(cls, v: float) -> float:
        if v < -0.5 or v > 0.5:
            raise ValueError('Drawdown outside reasonable bounds (-50% to +50%)')
        return v


class RiskMetrics(BaseModel):
    """Métricas de risco do sistema"""
    current_drawdown: float = Field(default=0.0, ge=-1.0, le=1.0)
    daily_pnl: float = Field(default=0.0)
    position_size: float = Field(default=0.0, ge=0, le=1.0)
    var_95: float = Field(default=0.02, ge=0)
    max_drawdown: float = Field(default=0.15, ge=0, le=1.0)
    total_exposure: float = Field(default=0.0, ge=0)
    open_positions: int = Field(default=0, ge=0)


class Tier0RiskEngine:
    """
    Risk Engine com FSM determinística e validação completa
    
    Features:
    - Máquina de estados (NORMAL → WARNING → CRITICAL → HALTED)
    - Validação Pydantic de todos os inputs
    - Audit trail completo
    - Limites configuráveis via Vault
    """
    
    def __init__(self, vault_client: Any, circuit_breaker: Any):
        """
        Initialize risk engine
        
        Args:
            vault_client: Instância do Tier0VaultClient
            circuit_breaker: Instância do Tier0CircuitBreaker
        """
        self.vault = vault_client
        self.circuit_breaker = circuit_breaker
        
        # Estado inicial
        self.state = RiskState.NORMAL
        self.metrics = RiskMetrics()
        
        # Audit trail
        self.audit_trail: List[Dict[str, Any]] = []
        
        # Limites padrão (sobrescritos pelo Vault)
        self.limits: Dict[str, float] = {
            "max_drawdown": 0.15,
            "daily_loss_limit": 0.05,
            "max_position_size": 0.10,
            "var_95_limit": 0.02,
            "max_positions": 5,
            "max_exposure": 0.30
        }
    
    async def load_limits_from_vault(self) -> None:
        """Carregar limites de risco do Vault"""
        try:
            limits = await self.vault.get_secret("aurora/risk_limits")
            if limits:
                self.limits.update(limits)
            logger.info("Risk limits loaded from Vault")
        except Exception as e:
            logger.warning(f"Failed to load risk limits from Vault, using defaults: {e}")
    
    def _add_audit_entry(self, action: str, details: Dict[str, Any]) -> None:
        """Adicionar entrada ao audit trail"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "state": self.state.value,
            "details": details
        }
        self.audit_trail.append(entry)
        
        # Manter apenas últimas 1000 entradas
        if len(self.audit_trail) > 1000:
            self.audit_trail = self.audit_trail[-1000:]
    
    def _transition_state(self, new_state: RiskState, reason: str) -> None:
        """Transicionar estado com logging e audit"""
        old_state = self.state
        self.state = new_state
        
        self._add_audit_entry("state_transition", {
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason,
            "metrics": self.metrics.model_dump()
        })
        
        logger.warning(f"Risk state transition: {old_state.value} → {new_state.value} ({reason})")
    
    async def evaluate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avaliar trade com validação completa
        
        Args:
            trade_data: Dados do trade a avaliar
            
        Returns:
            Dict com resultado (approved, reason, state)
        """
        # Verificar circuit breaker
        if not await self.circuit_breaker.can_execute():
            return {
                "approved": False,
                "reason": "risk_engine_circuit_breaker_open",
                "state": self.state.value
            }
        
        # Verificar estado atual
        if self.state == RiskState.HALTED:
            return {
                "approved": False,
                "reason": "risk_engine_halted",
                "state": self.state.value
            }
        
        try:
            # Validar dados de entrada
            validated_trade = TradeData(**trade_data)
            
            # Calcular impacto no risco
            new_drawdown = trade_data.get("drawdown", self.metrics.current_drawdown)
            new_position_size = self.metrics.position_size + (validated_trade.volume / 100)
            
            # Verificar limite de posições
            if self.metrics.open_positions >= self.limits.get("max_positions", 5):
                if self.state == RiskState.NORMAL:
                    self._transition_state(RiskState.WARNING, "max_positions_reached")
                return {
                    "approved": False,
                    "reason": "max_positions_reached",
                    "state": self.state.value
                }
            
            # Verificar drawdown máximo
            if new_drawdown >= self.limits["max_drawdown"]:
                self._transition_state(RiskState.HALTED, "max_drawdown_exceeded")
                return {
                    "approved": False,
                    "reason": "max_drawdown_exceeded",
                    "state": self.state.value
                }
            
            # Verificar aproximação do limite (80%)
            elif new_drawdown >= self.limits["max_drawdown"] * 0.8:
                self._transition_state(RiskState.CRITICAL, "approaching_max_drawdown")
                return {
                    "approved": False,
                    "reason": "approaching_max_drawdown",
                    "state": self.state.value
                }
            
            # Verificar warning (60%)
            elif new_drawdown >= self.limits["max_drawdown"] * 0.6:
                if self.state == RiskState.NORMAL:
                    self._transition_state(RiskState.WARNING, "elevated_drawdown")
            
            # Atualizar métricas
            self.metrics.current_drawdown = new_drawdown
            self.metrics.position_size = min(new_position_size, 1.0)
            
            # Trade aprovado
            self._add_audit_entry("trade_evaluated", {
                "trade": validated_trade.model_dump(),
                "approved": True,
                "metrics": self.metrics.model_dump()
            })
            
            return {
                "approved": True,
                "reason": "trade_within_limits",
                "state": self.state.value,
                "limits_used": {
                    "drawdown_remaining": self.limits["max_drawdown"] - self.metrics.current_drawdown,
                    "position_size_remaining": self.limits["max_position_size"] - self.metrics.position_size,
                    "positions_remaining": int(self.limits.get("max_positions", 5) - self.metrics.open_positions)
                }
            }
            
        except Exception as e:
            # Validação falhou
            self._add_audit_entry("validation_failed", {
                "trade_data": trade_data,
                "error": str(e)
            })
            
            return {
                "approved": False,
                "reason": f"validation_error: {str(e)}",
                "state": self.state.value
            }
    
    def update_metrics(
        self, 
        drawdown: Optional[float] = None,
        daily_pnl: Optional[float] = None,
        position_size: Optional[float] = None,
        open_positions: Optional[int] = None
    ) -> None:
        """
        Atualizar métricas de risco
        
        Args:
            drawdown: Novo valor de drawdown
            daily_pnl: Novo P&L diário
            position_size: Nova posição total
            open_positions: Número de posições abertas
        """
        if drawdown is not None:
            self.metrics.current_drawdown = drawdown
        if daily_pnl is not None:
            self.metrics.daily_pnl = daily_pnl
        if position_size is not None:
            self.metrics.position_size = position_size
        if open_positions is not None:
            self.metrics.open_positions = open_positions
        
        # Verificar se precisa transicionar estado
        self._check_state_transitions()
    
    def _check_state_transitions(self) -> None:
        """Verificar e aplicar transições de estado baseadas nas métricas"""
        dd = self.metrics.current_drawdown
        max_dd = self.limits["max_drawdown"]
        
        if dd >= max_dd:
            if self.state != RiskState.HALTED:
                self._transition_state(RiskState.HALTED, "max_drawdown_exceeded")
        elif dd >= max_dd * 0.8:
            if self.state not in [RiskState.CRITICAL, RiskState.HALTED]:
                self._transition_state(RiskState.CRITICAL, "approaching_max_drawdown")
        elif dd >= max_dd * 0.6:
            if self.state == RiskState.NORMAL:
                self._transition_state(RiskState.WARNING, "elevated_drawdown")
        elif dd < max_dd * 0.5:
            if self.state in [RiskState.WARNING, RiskState.CRITICAL]:
                self._transition_state(RiskState.NORMAL, "risk_normalized")
    
    def get_state(self) -> Dict[str, Any]:
        """Retornar estado atual do risk engine"""
        return {
            "state": self.state.value,
            "metrics": self.metrics.model_dump(),
            "limits": self.limits,
            "audit_trail_count": len(self.audit_trail)
        }
    
    def reset_state(self) -> None:
        """Reset do estado (apenas para emergências)"""
        self.state = RiskState.NORMAL
        self.metrics = RiskMetrics()
        self._add_audit_entry("manual_reset", {"reason": "emergency_reset"})
        logger.warning("Risk engine manually reset")
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retornar últimas entradas do audit trail"""
        return self.audit_trail[-limit:]

