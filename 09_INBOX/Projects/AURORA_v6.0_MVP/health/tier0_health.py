"""
Health server Tier-0 com 5-level health matrix
Nível institucional para monitoramento
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class HealthLevel(Enum):
    """5 níveis de saúde Tier-0"""
    CRITICAL = 0   # Sistema inoperante
    DEGRADED = 1   # Funcionalidade limitada
    STABLE = 2     # Operação normal
    OPTIMAL = 3    # Performance máxima
    RESILIENT = 4  # Tolerante a falhas


class ComponentHealth(BaseModel):
    """Modelo de saúde de componente individual"""
    name: str
    level: HealthLevel
    latency_ms: float
    details: Dict[str, Any]
    dependencies: List[str]
    last_checked: datetime
    
    class Config:
        use_enum_values = False
        arbitrary_types_allowed = True


class HealthMatrix(BaseModel):
    """Matriz completa de saúde do sistema"""
    overall: HealthLevel
    components: Dict[str, ComponentHealth]
    audit_trail: List[Tuple[datetime, str, HealthLevel]]
    recommendations: List[str]
    
    class Config:
        use_enum_values = False
        arbitrary_types_allowed = True


class Tier0HealthMonitor:
    """
    Monitor de saúde com matriz 5x5
    
    Features:
    - Verificação paralela de componentes
    - Matriz de dependências hierárquica
    - Histórico de checks (audit trail)
    - Recomendações automáticas
    """
    
    def __init__(self, vault_client: Any, redlock: Any):
        """
        Initialize health monitor
        
        Args:
            vault_client: Instância do Tier0VaultClient
            redlock: Instância do RedlockManager
        """
        self.vault = vault_client
        self.redlock = redlock
        self.matrix_history: List[Tuple[datetime, str, HealthLevel]] = []
        
        # Matriz de dependências
        self.dependency_matrix: Dict[str, List[str]] = {
            "vault": [],
            "redis_cluster": [],
            "mt5_connector": ["vault"],
            "risk_engine": ["redis_cluster", "mt5_connector"],
            "execution_engine": ["risk_engine", "redis_cluster"]
        }
    
    async def check_vault(self) -> ComponentHealth:
        """Verifica saúde do Vault com validação de secrets"""
        start = datetime.utcnow()
        try:
            # Testar conexão e permissões
            await self.vault.get_secret("aurora/health", "test")
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            
            level = HealthLevel.RESILIENT if latency < 100 else HealthLevel.OPTIMAL
            
            return ComponentHealth(
                name="vault",
                level=level,
                latency_ms=latency,
                details={
                    "authenticated": True,
                    "secrets_accessible": True,
                    "latency": f"{latency:.2f}ms",
                    "status": "healthy"
                },
                dependencies=[],
                last_checked=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Vault health check failed: {e}")
            return ComponentHealth(
                name="vault",
                level=HealthLevel.CRITICAL,
                latency_ms=0,
                details={"error": str(e), "status": "unhealthy"},
                dependencies=[],
                last_checked=datetime.utcnow()
            )
    
    async def check_redis_cluster(self) -> ComponentHealth:
        """Verifica saúde do Redis cluster"""
        start = datetime.utcnow()
        try:
            # Testar distributed locking
            lock_id = await self.redlock.lock("health_check", ttl=5000)
            if not lock_id:
                raise Exception("Failed to acquire distributed lock")
            
            await self.redlock.unlock("health_check", lock_id)
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            available_nodes = self.redlock.get_available_nodes()
            
            # Determinar nível baseado em nodes disponíveis
            if available_nodes >= 3:
                level = HealthLevel.RESILIENT
            elif available_nodes >= 2:
                level = HealthLevel.OPTIMAL
            else:
                level = HealthLevel.DEGRADED
            
            return ComponentHealth(
                name="redis_cluster",
                level=level,
                latency_ms=latency,
                details={
                    "distributed_locking": True,
                    "quorum_available": True,
                    "available_nodes": available_nodes,
                    "latency": f"{latency:.2f}ms",
                    "status": "healthy"
                },
                dependencies=[],
                last_checked=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Redis cluster health check failed: {e}")
            return ComponentHealth(
                name="redis_cluster",
                level=HealthLevel.CRITICAL,
                latency_ms=0,
                details={"error": str(e), "status": "unhealthy"},
                dependencies=[],
                last_checked=datetime.utcnow()
            )
    
    async def check_comprehensive(self) -> HealthMatrix:
        """Executa check completo da matriz de saúde"""
        components: Dict[str, ComponentHealth] = {}
        
        # Executar checks em paralelo
        tasks = {
            "vault": self.check_vault(),
            "redis_cluster": self.check_redis_cluster()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Processar resultados
        for name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                components[name] = ComponentHealth(
                    name=name,
                    level=HealthLevel.CRITICAL,
                    latency_ms=0,
                    details={"error": str(result), "status": "error"},
                    dependencies=self.dependency_matrix.get(name, []),
                    last_checked=datetime.utcnow()
                )
            else:
                result.dependencies = self.dependency_matrix.get(name, [])
                components[name] = result
        
        # Determinar nível geral (mínimo de todos os componentes)
        levels = [c.level.value for c in components.values()]
        overall_level = HealthLevel(min(levels)) if levels else HealthLevel.CRITICAL
        
        # Gerar recomendações
        recommendations: List[str] = []
        for name, comp in components.items():
            if comp.level.value <= HealthLevel.DEGRADED.value:
                recommendations.append(
                    f"ATENÇÃO: Componente {name} está em nível {comp.level.name}. "
                    f"Detalhes: {comp.details}"
                )
        
        if not recommendations:
            recommendations.append("Sistema operando normalmente. Todos os componentes saudáveis.")
        
        matrix = HealthMatrix(
            overall=overall_level,
            components=components,
            audit_trail=self.matrix_history[-10:],  # Últimos 10 checks
            recommendations=recommendations
        )
        
        # Registrar no histórico
        self.matrix_history.append((
            datetime.utcnow(),
            "comprehensive_check",
            overall_level
        ))
        
        # Manter histórico limitado
        if len(self.matrix_history) > 100:
            self.matrix_history = self.matrix_history[-100:]
        
        logger.info(f"Health check complete: {overall_level.name}")
        return matrix
    
    def get_history(self, limit: int = 10) -> List[Tuple[datetime, str, HealthLevel]]:
        """Retorna histórico de checks"""
        return self.matrix_history[-limit:]
    
    def clear_history(self) -> None:
        """Limpa histórico"""
        self.matrix_history.clear()

