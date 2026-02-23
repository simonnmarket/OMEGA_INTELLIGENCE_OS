# -*- coding: utf-8 -*-
"""
Serial Executor - Execução Serial de Ordens
Usa o TradingExecutor existente para execução sequencial
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import time
import uuid

# Importar TradingExecutor do sistema existente
server_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(server_dir))

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("prometheus_brain_v1_1", server_dir / "prometheus_brain_v1.1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    TradingExecutor = module.TradingExecutor
    SystemConfig = module.SystemConfig
    EXECUTOR_AVAILABLE = True
except Exception as e:
    logger.warning(f"Erro ao importar TradingExecutor: {e}")
    EXECUTOR_AVAILABLE = False
    TradingExecutor = None
    SystemConfig = None

from .monitoring import ExecutionMonitor
from .capital_manager import CapitalManager

logger = logging.getLogger(__name__)


class SerialExecutor:
    """
    Executor serial usando TradingExecutor existente.
    Executa ordens sequencialmente uma por vez.
    """
    
    def __init__(
        self,
        monitor: ExecutionMonitor,
        capital_manager: CapitalManager,
        config: Optional[SystemConfig] = None
    ):
        self.monitor = monitor
        self.capital_manager = capital_manager
        
        if not EXECUTOR_AVAILABLE:
            raise RuntimeError("TradingExecutor não disponível. Verifique imports.")
        
        if config is None:
            config = SystemConfig()
        
        self.config = config
        self.executor = TradingExecutor(config)
        
        logger.info("SerialExecutor inicializado usando TradingExecutor existente.")
    
    def execute_order(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa uma ordem de forma serial.
        
        Args:
            signal: Dict com informações da ordem (symbol, action, volume, etc)
        
        Returns:
            Dict com resultado da execução
        """
        order_id = signal.get('order_id', str(uuid.uuid4()))
        symbol = signal.get('symbol', 'XAUUSD')
        action = signal.get('action', 'BUY')
        volume = signal.get('volume', 0.01)
        magic_number = signal.get('magic_number', self.config.TEST_SIGNAL_MAGIC)
        
        # Garantir que order_id está no signal
        signal['order_id'] = order_id
        signal['magic_number'] = magic_number
        
        start_time = time.time()
        
        try:
            # Executar ordem usando TradingExecutor existente
            result = self.executor._open_position(signal)
            
            latency_ms = result.get('latency_ms', (time.time() - start_time) * 1000)
            success = result.get('status') == 'SUCCESS'
            
            # Registrar métrica
            self.monitor.record_execution(
                order_id=order_id,
                latency_ms=latency_ms,
                success=success,
                symbol=symbol,
                volume=volume,
                error=result.get('result', {}).get('comment') if not success else None
            )
            
            # Adicionar order_id ao resultado
            result['order_id'] = order_id
            
            if success:
                logger.info(f"[{order_id}] ✅ ORDEM EXECUTADA: {result.get('result', {}).get('order')}")
            else:
                logger.error(f"[{order_id}] ❌ ORDEM FALHOU: {result.get('result', {}).get('comment')}")
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            logger.error(f"[{order_id}] Erro na execução serial: {error_msg}")
            
            self.monitor.record_execution(
                order_id=order_id,
                latency_ms=latency_ms,
                success=False,
                symbol=symbol,
                volume=volume,
                error=error_msg
            )
            
            return {
                'order_id': order_id,
                'status': 'FAILED',
                'error': error_msg,
                'latency_ms': latency_ms
            }

