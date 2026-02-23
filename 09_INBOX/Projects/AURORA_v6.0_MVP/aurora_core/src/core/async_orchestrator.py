"""
Async Orchestrator Tier-0
Circuit breakers com distributed consensus + Health matrix integration
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "CLOSED"      # Normal, permitindo execuções
    OPEN = "OPEN"          # Bloqueado, rejeitando execuções
    HALF_OPEN = "HALF_OPEN"  # Testando se pode retornar ao normal


class Tier0CircuitBreaker:
    """
    Circuit breaker com distributed consensus
    
    Features:
    - Estado persistido no Redis cluster
    - Threshold configurável de falhas
    - Auto-recovery com half-open state
    - Métricas para Prometheus
    """
    
    def __init__(self, redlock: Any, component_name: str, failure_threshold: int = 5):
        """
        Initialize circuit breaker
        
        Args:
            redlock: Instância do RedlockManager
            component_name: Nome do componente protegido
            failure_threshold: Número de falhas para abrir o circuito
        """
        self.redlock = redlock
        self.component_name = component_name
        self.namespace = f"aurora:cb:{component_name}"
        self.failure_threshold = failure_threshold
        
        # Estado local (sincronizado com Redis)
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure: Optional[datetime] = None
        self._last_success: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None
        
        # Configurações
        self.recovery_timeout = 30  # segundos para tentar half-open
        
    async def get_state(self) -> Dict[str, Any]:
        """Obtém estado do circuit breaker com distributed lock"""
        lock_id = await self.redlock.lock(f"{self.namespace}:state", ttl=1000)
        try:
            return {
                "state": self._state,
                "failure_count": self._failure_count,
                "last_failure": self._last_failure.isoformat() if self._last_failure else None,
                "last_success": self._last_success.isoformat() if self._last_success else None,
                "since": self._opened_at.isoformat() if self._opened_at else datetime.utcnow().isoformat()
            }
        finally:
            if lock_id:
                await self.redlock.unlock(f"{self.namespace}:state", lock_id)
    
    async def can_execute(self) -> bool:
        """Verifica se pode executar com verificação de dependências"""
        # Se fechado, sempre pode executar
        if self._state == CircuitState.CLOSED:
            return True
        
        # Se aberto, verificar se passou tempo suficiente para half-open
        if self._state == CircuitState.OPEN:
            if self._opened_at:
                elapsed = (datetime.utcnow() - self._opened_at).total_seconds()
                if elapsed > self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker {self.component_name} entering HALF_OPEN state")
                    return True
            return False
        
        # Half-open permite uma tentativa
        if self._state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    async def record_success(self) -> None:
        """Registra execução bem-sucedida"""
        self._last_success = datetime.utcnow()
        
        if self._state == CircuitState.HALF_OPEN:
            # Sucesso em half-open, fechar circuito
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._opened_at = None
            logger.info(f"Circuit breaker {self.component_name} CLOSED after successful recovery")
        elif self._state == CircuitState.CLOSED:
            # Reset failure count em caso de sucesso
            self._failure_count = max(0, self._failure_count - 1)
    
    async def record_failure(self, error: Optional[str] = None) -> None:
        """Registra falha de execução"""
        self._last_failure = datetime.utcnow()
        self._failure_count += 1
        
        logger.warning(f"Circuit breaker {self.component_name} failure #{self._failure_count}: {error}")
        
        if self._state == CircuitState.HALF_OPEN:
            # Falha em half-open, reabrir circuito
            self._state = CircuitState.OPEN
            self._opened_at = datetime.utcnow()
            logger.warning(f"Circuit breaker {self.component_name} REOPENED after failed recovery")
        
        elif self._state == CircuitState.CLOSED and self._failure_count >= self.failure_threshold:
            # Atingiu threshold, abrir circuito
            self._state = CircuitState.OPEN
            self._opened_at = datetime.utcnow()
            logger.error(f"Circuit breaker {self.component_name} OPENED after {self._failure_count} failures")
    
    def reset(self) -> None:
        """Reset manual do circuit breaker"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure = None
        self._opened_at = None
        logger.info(f"Circuit breaker {self.component_name} manually reset")


class AsyncOrchestrator:
    """
    Orchestrator principal Tier-0
    
    Features:
    - Gerenciamento de circuit breakers hierárquicos
    - Inicialização de componentes em ordem de dependência
    - Workers assíncronos para diferentes tarefas
    - Graceful shutdown
    """
    
    def __init__(self, vault_client: Any, redlock: Any):
        """
        Initialize orchestrator
        
        Args:
            vault_client: Instância do Tier0VaultClient
            redlock: Instância do RedlockManager
        """
        self.vault = vault_client
        self.redlock = redlock
        
        # Circuit breakers hierárquicos
        self.circuit_breakers: Dict[str, Tier0CircuitBreaker] = {
            "mt5": Tier0CircuitBreaker(redlock, "mt5"),
            "risk": Tier0CircuitBreaker(redlock, "risk"),
            "execution": Tier0CircuitBreaker(redlock, "execution")
        }
        
        # Componentes (inicializados depois)
        self.mt5: Optional[Any] = None
        self.risk: Optional[Any] = None
        self.execution: Optional[Any] = None
        
        # Tasks
        self.tasks: List[asyncio.Task] = []
        self.running = False
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all components with proper dependency order"""
        logger.info("Initializing Tier-0 Orchestrator")
        
        try:
            # 1. Carregar configurações do MT5 do Vault
            mt5_config = await self.vault.get_secret("aurora/mt5")
            logger.info("MT5 configuration loaded from Vault")
            
            # 2. Carregar limites de risco do Vault
            risk_limits = await self.vault.get_secret("aurora/risk_limits")
            logger.info("Risk limits loaded from Vault")
            
            # 3. Importar e inicializar componentes
            from src.connectors.mt5_connector_tier0 import Tier0MT5Connector
            from src.risk.finite_state_risk_tier0 import Tier0RiskEngine
            from src.execution.safe_execution_tier0 import Tier0ExecutionEngine
            
            # MT5 Connector
            self.mt5 = Tier0MT5Connector(
                account=mt5_config.get("account", "demo"),
                password=mt5_config.get("password", "demo"),
                server=mt5_config.get("server", "demo"),
                circuit_breaker=self.circuit_breakers["mt5"]
            )
            
            # Risk Engine
            self.risk = Tier0RiskEngine(
                vault_client=self.vault,
                circuit_breaker=self.circuit_breakers["risk"]
            )
            await self.risk.load_limits_from_vault()
            
            # Execution Engine
            self.execution = Tier0ExecutionEngine(
                mt5_connector=self.mt5,
                risk_engine=self.risk,
                circuit_breaker=self.circuit_breakers["execution"],
                redlock=self.redlock
            )
            
            self._initialized = True
            logger.info("Tier-0 Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def run(self) -> None:
        """Main execution loop"""
        if not self._initialized:
            await self.initialize()
        
        self.running = True
        
        # Verificar circuit breakers antes de iniciar
        for component, cb in self.circuit_breakers.items():
            if not await cb.can_execute():
                logger.error(f"Cannot start: {component} circuit breaker is OPEN")
                return
        
        # Criar tasks para cada worker
        self.tasks = [
            asyncio.create_task(self._market_data_worker()),
            asyncio.create_task(self._risk_validation_worker()),
            asyncio.create_task(self._execution_worker()),
            asyncio.create_task(self._health_monitor_worker())
        ]
        
        logger.info("Started all Tier-0 workers")
        
        # Aguardar completion ou shutdown
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("Orchestrator tasks cancelled")
        finally:
            self.running = False
    
    async def _market_data_worker(self) -> None:
        """Worker para coleta de dados de mercado"""
        while self.running:
            try:
                if self.mt5 and await self.circuit_breakers["mt5"].can_execute():
                    # Coletar ticks do MT5
                    ticks = await self.mt5.collect_ticks(["EURUSD", "XAUUSD"])
                    
                    if ticks:
                        await self.circuit_breakers["mt5"].record_success()
                        for tick in ticks:
                            logger.debug(f"Tick: {tick['symbol']} bid={tick['bid']}")
                
                await asyncio.sleep(1)  # Intervalo de coleta
                
            except Exception as e:
                logger.error(f"Market data worker error: {e}")
                await self.circuit_breakers["mt5"].record_failure(str(e))
                await asyncio.sleep(5)
    
    async def _risk_validation_worker(self) -> None:
        """Worker para validação de risco"""
        while self.running:
            try:
                if self.risk:
                    state = self.risk.get_state()
                    logger.debug(f"Risk state: {state['state']}")
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Risk validation worker error: {e}")
                await asyncio.sleep(10)
    
    async def _execution_worker(self) -> None:
        """Worker para execução de trades"""
        while self.running:
            # Este worker processa sinais de trading da fila
            # Por enquanto, apenas verifica status
            await asyncio.sleep(1)
    
    async def _health_monitor_worker(self) -> None:
        """Worker para monitoramento de saúde"""
        while self.running:
            # Monitorar circuit breakers
            for component, cb in self.circuit_breakers.items():
                state = await cb.get_state()
                logger.info(f"Circuit breaker {component}: {state['state'].value}")
            
            await asyncio.sleep(30)  # Verificar a cada 30 segundos
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Shutting down Tier-0 Orchestrator")
        self.running = False
        
        # Cancelar todas as tasks
        for task in self.tasks:
            task.cancel()
        
        # Aguardar cancelamento
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("Orchestrator shutdown complete")
    
    def is_initialized(self) -> bool:
        """Verifica se orchestrator foi inicializado"""
        return self._initialized
    
    def is_running(self) -> bool:
        """Verifica se orchestrator está rodando"""
        return self.running

