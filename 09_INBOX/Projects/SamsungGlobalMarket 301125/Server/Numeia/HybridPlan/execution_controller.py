# -*- coding: utf-8 -*-
"""
Execution Controller - Controlador Principal do Plano Híbrido ΩΔ
Escolhe entre modo paralelo e serial baseado em configuração e monitoramento
"""

import logging
from typing import Dict, Any, List, Optional
from queue import Queue

from .connection_pool import MT5ConnectionPool
from .parallel_executor import ParallelExecutor
from .serial_executor import SerialExecutor
from .monitoring import ExecutionMonitor
from .capital_manager import CapitalManager

logger = logging.getLogger(__name__)


class ExecutionController:
    """
    Controlador principal que gerencia execução paralela/serial.
    Decide qual modo usar baseado em configuração e monitoramento.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        circuit_breaker: Optional[Any] = None  # CircuitBreaker do sistema existente
    ):
        self.config = config
        self.circuit_breaker = circuit_breaker
        
        # Configurações
        self.emergency_mode_enabled = config.get('EMERGENCY_MODE_ENABLED', False)
        self.max_parallel_workers = config.get('MAX_PARALLEL_WORKERS', 10)
        self.execution_cycle_seconds = config.get('EXECUTION_CYCLE_SECONDS', 300)
        self.latency_threshold_ms = config.get('LATENCY_THRESHOLD_MS', 500)
        self.failure_rate_threshold = config.get('FAILURE_RATE_THRESHOLD', 0.05)
        self.rollback_enabled = config.get('ROLLBACK_ENABLED', True)
        self.monitoring_window_seconds = config.get('MONITORING_WINDOW_SECONDS', 300)
        self.failure_window_seconds = config.get('FAILURE_WINDOW_SECONDS', 600)
        
        # Inicializar componentes
        self.capital_manager = CapitalManager()
        
        self.monitor = ExecutionMonitor(
            latency_threshold_ms=self.latency_threshold_ms,
            failure_rate_threshold=self.failure_rate_threshold,
            monitoring_window_seconds=self.monitoring_window_seconds,
            failure_window_seconds=self.failure_window_seconds,
            enable_rollback=self.rollback_enabled
        )
        
        # Connection pool (apenas se modo paralelo)
        self.connection_pool: Optional[MT5ConnectionPool] = None
        if self.emergency_mode_enabled:
            try:
                self.connection_pool = MT5ConnectionPool.get_instance(
                    max_conn=self.max_parallel_workers
                )
            except Exception as e:
                logger.warning(f"Falha ao criar connection pool: {e}. Usando modo serial.")
                self.emergency_mode_enabled = False
        
        # Executores
        self.parallel_executor: Optional[ParallelExecutor] = None
        self.serial_executor: Optional[SerialExecutor] = None
        
        # Estado atual
        self.current_mode: str = 'serial'  # 'parallel' ou 'serial'
        
        logger.info(
            f"ExecutionController inicializado: "
            f"Modo emergência: {'Ativado' if self.emergency_mode_enabled else 'Desativado'}, "
            f"Modo atual: {self.current_mode}"
        )
    
    def _should_use_parallel_mode(self) -> bool:
        """Determina se deve usar modo paralelo."""
        # Se modo emergência não está habilitado, usar serial
        if not self.emergency_mode_enabled:
            return False
        
        # Se monitor indica rollback, usar serial
        if not self.monitor.should_use_parallel_mode():
            return False
        
        # Se circuit breaker está aberto, usar serial
        if self.circuit_breaker and hasattr(self.circuit_breaker, 'state'):
            if self.circuit_breaker.state.value == 'OPEN':
                return False
        
        # Se connection pool não está disponível, usar serial
        if not self.connection_pool:
            return False
        
        return True
    
    def get_executor(self):
        """Retorna executor apropriado (paralelo ou serial)."""
        # Decidir modo
        should_use_parallel = self._should_use_parallel_mode()
        
        # Inicializar executores se necessário
        if should_use_parallel and self.parallel_executor is None:
            if self.connection_pool:
                try:
                    # Importar config do sistema existente
                    import importlib.util
                    from pathlib import Path
                    server_dir = Path(__file__).parent.parent.parent
                    spec = importlib.util.spec_from_file_location("prometheus_brain_v1_1", server_dir / "prometheus_brain_v1.1.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    SystemConfig = module.SystemConfig
                    sys_config = SystemConfig()
                    
                    self.parallel_executor = ParallelExecutor(
                        max_workers=self.max_parallel_workers,
                        connection_pool=self.connection_pool,
                        monitor=self.monitor,
                        capital_manager=self.capital_manager,
                        stop_loss_points=sys_config.STOP_LOSS_POINTS,
                        take_profit_points=sys_config.TAKE_PROFIT_POINTS,
                        price_deviation_points=sys_config.PRICE_DEVIATION_POINTS
                    )
                    self.current_mode = 'parallel'
                    logger.info("✅ Modo PARALELO ativado.")
                except Exception as e:
                    logger.error(f"Erro ao criar ParallelExecutor: {e}. Usando serial.")
                    should_use_parallel = False
        
        if not should_use_parallel:
            if self.serial_executor is None:
                try:
                    import importlib.util
                    from pathlib import Path
                    server_dir = Path(__file__).parent.parent.parent
                    spec = importlib.util.spec_from_file_location("prometheus_brain_v1_1", server_dir / "prometheus_brain_v1.1.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    SystemConfig = module.SystemConfig
                    sys_config = SystemConfig()
                    
                    self.serial_executor = SerialExecutor(
                        monitor=self.monitor,
                        capital_manager=self.capital_manager,
                        config=sys_config
                    )
                    self.current_mode = 'serial'
                    logger.info("✅ Modo SERIAL ativado.")
                except Exception as e:
                    logger.error(f"Erro ao criar SerialExecutor: {e}")
                    raise
            
            return self.serial_executor
        
        return self.parallel_executor
    
    def execute_order(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ordem usando executor apropriado.
        
        Args:
            signal: Dict com informações da ordem
        
        Returns:
            Dict com resultado da execução
        """
        executor = self.get_executor()
        
        if isinstance(executor, ParallelExecutor):
            # Modo paralelo: adicionar à fila
            order_id = executor.submit_task(signal)
            return {
                'order_id': order_id,
                'status': 'QUEUED',
                'mode': 'parallel'
            }
        else:
            # Modo serial: executar imediatamente
            return executor.execute_order(signal)
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do controller."""
        monitor_stats = self.monitor.get_monitoring_stats()
        portfolio_status = self.capital_manager.get_portfolio_status()
        
        return {
            'current_mode': self.current_mode,
            'emergency_mode_enabled': self.emergency_mode_enabled,
            'monitor': monitor_stats,
            'portfolio': portfolio_status,
            'connection_pool': self.connection_pool.get_pool_status() if self.connection_pool else None,
            'rollback_triggered': self.monitor.rollback_triggered,
            'rollback_reason': self.monitor.rollback_reason
        }
    
    def shutdown(self):
        """Encerra todos os componentes."""
        if self.parallel_executor:
            self.parallel_executor.stop()
        
        if self.connection_pool:
            self.connection_pool.shutdown()
        
        logger.info("ExecutionController encerrado.")

