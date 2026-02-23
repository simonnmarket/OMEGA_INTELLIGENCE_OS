# -*- coding: utf-8 -*-
"""
Execution Monitor - Monitoramento de Latência e Taxa de Falha
Detecta problemas e aciona rollback automático para modo serial
"""

import logging
import time
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetric:
    """Métrica de execução individual."""
    order_id: str
    timestamp: float
    latency_ms: float
    success: bool
    error: Optional[str] = None
    symbol: Optional[str] = None
    volume: Optional[float] = None


class ExecutionMonitor:
    """
    Monitora execuções e detecta problemas de latência/falha.
    Aciona rollback automático se necessário.
    """
    
    def __init__(
        self,
        latency_threshold_ms: float = 500.0,
        failure_rate_threshold: float = 0.05,  # 5%
        monitoring_window_seconds: int = 300,  # 5 minutos
        failure_window_seconds: int = 600,  # 10 minutos
        enable_rollback: bool = True
    ):
        self.latency_threshold_ms = latency_threshold_ms
        self.failure_rate_threshold = failure_rate_threshold
        self.monitoring_window_seconds = monitoring_window_seconds
        self.failure_window_seconds = failure_window_seconds
        self.enable_rollback = enable_rollback
        
        # Histórico de métricas (mantém apenas últimas N execuções)
        self.metrics_history: deque = deque(maxlen=1000)
        
        # Estado atual
        self.rollback_triggered = False
        self.rollback_reason: Optional[str] = None
        self.last_rollback_time: Optional[float] = None
        
        logger.info(
            f"ExecutionMonitor inicializado: "
            f"Latência threshold: {latency_threshold_ms}ms, "
            f"Taxa de falha threshold: {failure_rate_threshold*100}%, "
            f"Rollback: {'Habilitado' if enable_rollback else 'Desabilitado'}"
        )
    
    def record_execution(
        self,
        order_id: str,
        latency_ms: float,
        success: bool,
        symbol: Optional[str] = None,
        volume: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        Registra métrica de execução.
        
        Args:
            order_id: ID único da ordem
            latency_ms: Latência em milissegundos
            success: Se execução foi bem-sucedida
            symbol: Símbolo negociado
            volume: Volume negociado
            error: Mensagem de erro (se houver)
        """
        metric = ExecutionMetric(
            order_id=order_id,
            timestamp=time.time(),
            latency_ms=latency_ms,
            success=success,
            error=error,
            symbol=symbol,
            volume=volume
        )
        
        self.metrics_history.append(metric)
        
        # Log estruturado JSON
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'latency_ms': latency_ms,
            'success': success,
            'symbol': symbol,
            'volume': volume,
            'error': error
        }
        
        if success:
            logger.info(f"Execution metric: {json.dumps(log_entry)}")
        else:
            logger.error(f"Execution metric (FAILED): {json.dumps(log_entry)}")
        
        # Verificar se precisa acionar rollback
        if self.enable_rollback and not self.rollback_triggered:
            self._check_rollback_conditions()
    
    def _check_rollback_conditions(self):
        """Verifica condições para acionar rollback."""
        current_time = time.time()
        
        # Filtrar métricas dentro da janela de monitoramento
        recent_metrics = [
            m for m in self.metrics_history
            if current_time - m.timestamp <= self.monitoring_window_seconds
        ]
        
        if len(recent_metrics) < 5:  # Precisa de pelo menos 5 execuções
            return
        
        # Verificar latência alta contínua
        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        high_latency_count = sum(1 for m in recent_metrics if m.latency_ms > self.latency_threshold_ms)
        high_latency_ratio = high_latency_count / len(recent_metrics)
        
        if avg_latency > self.latency_threshold_ms and high_latency_ratio > 0.5:
            self._trigger_rollback(
                reason=f"Latência alta contínua: Média={avg_latency:.2f}ms, "
                       f"Threshold={self.latency_threshold_ms}ms, "
                       f"Taxa de latência alta={high_latency_ratio*100:.1f}%"
            )
            return
        
        # Verificar taxa de falha alta (janela maior)
        failure_metrics = [
            m for m in self.metrics_history
            if current_time - m.timestamp <= self.failure_window_seconds
        ]
        
        if len(failure_metrics) >= 10:  # Precisa de pelo menos 10 execuções
            failure_count = sum(1 for m in failure_metrics if not m.success)
            failure_rate = failure_count / len(failure_metrics)
            
            if failure_rate > self.failure_rate_threshold:
                self._trigger_rollback(
                    reason=f"Taxa de falha alta: {failure_rate*100:.2f}%, "
                           f"Threshold={self.failure_rate_threshold*100:.2f}%, "
                           f"Falhas={failure_count}/{len(failure_metrics)}"
                )
    
    def _trigger_rollback(self, reason: str):
        """Aciona rollback para modo serial."""
        self.rollback_triggered = True
        self.rollback_reason = reason
        self.last_rollback_time = time.time()
        
        logger.critical(
            f"🚨 ROLLBACK ACIONADO: {reason}\n"
            f"🔄 Sistema será revertido para modo serial."
        )
    
    def should_use_parallel_mode(self) -> bool:
        """Verifica se deve usar modo paralelo."""
        if not self.enable_rollback:
            return True
        
        # Se rollback foi acionado, aguardar período de cooldown antes de retentar
        if self.rollback_triggered:
            if self.last_rollback_time:
                cooldown_period = 3600  # 1 hora
                if time.time() - self.last_rollback_time < cooldown_period:
                    return False
        
        # Resetar rollback se condições melhoraram
        if self.rollback_triggered:
            self._check_recovery_conditions()
        
        return not self.rollback_triggered
    
    def _check_recovery_conditions(self):
        """Verifica se condições melhoraram para sair do rollback."""
        current_time = time.time()
        
        # Verificar últimas execuções (janela menor para recovery)
        recovery_window = self.monitoring_window_seconds // 2
        recent_metrics = [
            m for m in self.metrics_history
            if current_time - m.timestamp <= recovery_window
        ]
        
        if len(recent_metrics) >= 10:
            # Verificar se latência e taxa de falha melhoraram
            avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
            failure_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
            
            if avg_latency < self.latency_threshold_ms * 0.8 and failure_rate < self.failure_rate_threshold * 0.5:
                logger.info("✅ Condições melhoraram. Rollback pode ser removido após período de cooldown.")
                # Aguardar cooldown antes de resetar
                if self.last_rollback_time and time.time() - self.last_rollback_time >= 3600:
                    self.rollback_triggered = False
                    self.rollback_reason = None
                    logger.info("✅ Rollback removido. Sistema pode retornar ao modo paralelo.")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de monitoramento."""
        current_time = time.time()
        
        recent_metrics = [
            m for m in self.metrics_history
            if current_time - m.timestamp <= self.monitoring_window_seconds
        ]
        
        if not recent_metrics:
            return {
                'total_executions': 0,
                'avg_latency_ms': 0,
                'failure_rate': 0,
                'rollback_triggered': self.rollback_triggered,
                'rollback_reason': self.rollback_reason
            }
        
        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        max_latency = max(m.latency_ms for m in recent_metrics)
        min_latency = min(m.latency_ms for m in recent_metrics)
        success_count = sum(1 for m in recent_metrics if m.success)
        failure_rate = (len(recent_metrics) - success_count) / len(recent_metrics)
        
        return {
            'total_executions': len(self.metrics_history),
            'recent_executions': len(recent_metrics),
            'avg_latency_ms': avg_latency,
            'min_latency_ms': min_latency,
            'max_latency_ms': max_latency,
            'success_count': success_count,
            'failure_count': len(recent_metrics) - success_count,
            'failure_rate': failure_rate,
            'rollback_triggered': self.rollback_triggered,
            'rollback_reason': self.rollback_reason,
            'last_rollback_time': datetime.fromtimestamp(self.last_rollback_time).isoformat() if self.last_rollback_time else None
        }

