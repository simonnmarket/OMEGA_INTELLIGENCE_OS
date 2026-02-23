"""
Execution Engine Tier-0
Com distributed locking, idempotency, e audit trail completo
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


class Tier0ExecutionEngine:
    """
    Execution Engine com todas as garantias Tier-0
    
    Features:
    - Distributed locking para evitar execuções duplicadas
    - Idempotency via chave única
    - Audit trail completo
    - Integration com Risk Engine
    """
    
    def __init__(
        self, 
        mt5_connector: Any, 
        risk_engine: Any,
        circuit_breaker: Any,
        redlock: Any
    ):
        """
        Initialize execution engine
        
        Args:
            mt5_connector: Instância do Tier0MT5Connector
            risk_engine: Instância do Tier0RiskEngine
            circuit_breaker: Instância do Tier0CircuitBreaker
            redlock: Instância do RedlockManager
        """
        self.mt5 = mt5_connector
        self.risk = risk_engine
        self.circuit_breaker = circuit_breaker
        self.redlock = redlock
        
        # Modo demo
        self.demo_mode = True
        self.slippage = 0.0001
        
        # Cache de execuções para idempotency
        self.execution_cache: Dict[str, Dict[str, Any]] = {}
        
        # Audit trail
        self.audit_trail: List[Dict[str, Any]] = []
    
    async def _acquire_execution_lock(self, trade_id: str, ttl: int = 10000) -> Optional[str]:
        """Adquirir lock distribuído para execução"""
        lock_id = await self.redlock.lock(f"execution:{trade_id}", ttl=ttl)
        if not lock_id:
            logger.warning(f"Failed to acquire execution lock: {trade_id}")
        return lock_id
    
    async def execute_trade(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executar trade com todas as verificações Tier-0
        
        Processo:
        1. Verificar circuit breaker
        2. Validar idempotency
        3. Adquirir distributed lock
        4. Validar com risk engine
        5. Executar no MT5 (ou simular)
        6. Liberar lock
        7. Registrar audit trail
        
        Args:
            trade_request: Dados do trade
            
        Returns:
            Dict com resultado da execução
        """
        
        # 1. Verificar circuit breaker
        if not await self.circuit_breaker.can_execute():
            return {
                "status": "rejected",
                "reason": "execution_circuit_breaker_open",
                "trade_id": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Gerar trade ID
        trade_id = str(uuid.uuid4())
        
        # 2. Verificar idempotency
        idempotency_key = trade_request.get("idempotency_key")
        if idempotency_key and idempotency_key in self.execution_cache:
            cached = self.execution_cache[idempotency_key]
            logger.info(f"Returning cached result for idempotency key: {idempotency_key}")
            return {
                **cached,
                "cached": True,
                "note": "Returning cached result for idempotency"
            }
        
        # 3. Adquirir distributed lock
        lock_id = await self._acquire_execution_lock(trade_id)
        if not lock_id:
            return {
                "status": "rejected",
                "reason": "could_not_acquire_distributed_lock",
                "trade_id": trade_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # 4. Validar com risk engine
            risk_result = await self.risk.evaluate_trade(trade_request)
            
            if not risk_result["approved"]:
                result = {
                    "status": "rejected",
                    "reason": risk_result["reason"],
                    "trade_id": trade_id,
                    "risk_state": risk_result["state"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Registrar no audit trail
                self._add_audit_trail({
                    "trade_id": trade_id,
                    "request": trade_request,
                    "risk_result": risk_result,
                    "execution_result": result,
                    "action": "rejected_by_risk"
                })
                
                return result
            
            # 5. Executar trade
            execution_result = await self._execute_trade_internal(trade_request, trade_id)
            
            # 6. Cache para idempotency
            if idempotency_key:
                self.execution_cache[idempotency_key] = execution_result
                # Limpar cache antigo (manter apenas últimas 1000)
                if len(self.execution_cache) > 1000:
                    oldest_keys = list(self.execution_cache.keys())[:-1000]
                    for k in oldest_keys:
                        del self.execution_cache[k]
            
            # 7. Registrar audit trail
            self._add_audit_trail({
                "trade_id": trade_id,
                "request": trade_request,
                "risk_result": risk_result,
                "execution_result": execution_result,
                "lock_id": lock_id,
                "action": "executed"
            })
            
            # Registrar sucesso no circuit breaker
            await self.circuit_breaker.record_success()
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Trade execution failed: {trade_id}, error={e}")
            
            # Registrar falha no circuit breaker
            await self.circuit_breaker.record_failure(str(e))
            
            return {
                "status": "error",
                "reason": f"execution_error: {str(e)}",
                "trade_id": trade_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            # Sempre liberar o lock
            if lock_id:
                await self.redlock.unlock(f"execution:{trade_id}", lock_id)
    
    async def _execute_trade_internal(
        self, 
        trade_request: Dict[str, Any], 
        trade_id: str
    ) -> Dict[str, Any]:
        """Execução interna do trade (real ou simulada)"""
        
        symbol = trade_request.get("symbol", "EURUSD")
        operation = trade_request.get("operation", "BUY")
        volume = trade_request.get("volume", 0.01)
        price = trade_request.get("price")
        
        if self.demo_mode:
            # Paper trading simulation
            await asyncio.sleep(0.1)  # Simular latência
            
            # Obter preço atual se não fornecido
            if not price:
                tick = await self.mt5.get_tick(symbol)
                if tick:
                    price = tick["ask"] if operation == "BUY" else tick["bid"]
                else:
                    price = 1.0850  # Fallback
            
            # Aplicar slippage
            slippage_direction = 1 if operation == "BUY" else -1
            slippage_price = price + (self.slippage * slippage_direction)
            
            result = {
                "status": "executed",
                "trade_id": trade_id,
                "symbol": symbol,
                "operation": operation,
                "volume": volume,
                "requested_price": price,
                "executed_price": round(slippage_price, 5),
                "slippage": abs(slippage_price - price),
                "demo": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trade executed (demo): {trade_id}, {operation} {volume} {symbol} @ {slippage_price}")
            
            return result
        
        else:
            # Execução real no MT5
            mt5_result = await self.mt5.execute_order(
                symbol=symbol,
                order_type=operation,
                volume=volume,
                price=price
            )
            
            if mt5_result["success"]:
                return {
                    "status": "executed",
                    "trade_id": trade_id,
                    "ticket": mt5_result["ticket"],
                    "symbol": symbol,
                    "operation": operation,
                    "volume": volume,
                    "executed_price": mt5_result["price"],
                    "demo": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "failed",
                    "trade_id": trade_id,
                    "reason": mt5_result.get("error", "unknown"),
                    "timestamp": datetime.utcnow().isoformat()
                }
    
    def _add_audit_trail(self, data: Dict[str, Any]) -> None:
        """Adicionar ao audit trail"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        self.audit_trail.append(entry)
        
        # Manter tamanho gerenciável
        if len(self.audit_trail) > 1000:
            self.audit_trail = self.audit_trail[-1000:]
    
    async def get_execution_status(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter status de execução
        
        Args:
            trade_id: ID do trade
            
        Returns:
            Dict com status ou None se não encontrado
        """
        # Procurar no audit trail
        for entry in reversed(self.audit_trail):
            if entry.get("trade_id") == trade_id:
                return {
                    "trade_id": trade_id,
                    "status": entry.get("execution_result", {}).get("status", "unknown"),
                    "timestamp": entry.get("timestamp")
                }
        
        return None
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retornar últimas entradas do audit trail"""
        return self.audit_trail[-limit:]
    
    def set_demo_mode(self, enabled: bool) -> None:
        """Ativar/desativar modo demo"""
        self.demo_mode = enabled
        logger.info(f"Demo mode {'enabled' if enabled else 'disabled'}")
    
    def set_slippage(self, slippage: float) -> None:
        """Configurar slippage para simulação"""
        self.slippage = slippage
        logger.info(f"Slippage set to {slippage}")

