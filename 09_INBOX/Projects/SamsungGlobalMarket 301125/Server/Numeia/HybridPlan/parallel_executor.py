# -*- coding: utf-8 -*-
"""
Parallel Executor - Execução Paralela de Ordens
Usa connection pool e ThreadPoolExecutor para execução simultânea
"""

import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
from typing import Dict, Any, List, Optional, Callable
import uuid

from .connection_pool import MT5ConnectionPool
from .monitoring import ExecutionMonitor
from .capital_manager import CapitalManager

logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None


class ParallelExecutor:
    """
    Executor paralelo usando connection pool e threads.
    Thread-safe com queue e monitoring de latência/falha.
    """
    
    def __init__(
        self,
        max_workers: int,
        connection_pool: MT5ConnectionPool,
        monitor: ExecutionMonitor,
        capital_manager: CapitalManager,
        stop_loss_points: int = 150,
        take_profit_points: int = 300,
        price_deviation_points: int = 10
    ):
        self.max_workers = max_workers
        self.connection_pool = connection_pool
        self.monitor = monitor
        self.capital_manager = capital_manager
        self.stop_loss_points = stop_loss_points
        self.take_profit_points = take_profit_points
        self.price_deviation_points = price_deviation_points
        
        self._stop_event = threading.Event()
        self._task_queue: Queue = Queue()
        self._executor: Optional[ThreadPoolExecutor] = None
        
        logger.info(f"ParallelExecutor inicializado: Max workers: {max_workers}")
    
    def _execute_single_order(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa uma única ordem usando connection pool.
        
        Args:
            task: Dict com informações da ordem (symbol, action, volume, etc)
        
        Returns:
            Dict com resultado da execução
        """
        order_id = task.get('order_id', str(uuid.uuid4()))
        symbol = task.get('symbol', 'XAUUSD')
        action = task.get('action', 'BUY')
        volume = task.get('volume', 0.01)
        magic_number = task.get('magic_number', 1000)
        
        start_time = time.time()
        conn_id = None
        
        try:
            # Adquirir conexão do pool
            conn_id = self.connection_pool.acquire(timeout=5.0)
            
            # Obter informações do símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                raise ValueError(f"Símbolo {symbol} não encontrado no MT5")
            
            # Garantir que símbolo está visível
            if not symbol_info.visible:
                mt5.symbol_select(symbol, True)
            
            # Obter tick atual
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise ValueError(f"Tick indisponível para {symbol}")
            
            # Preparar requisição de ordem
            if action.upper() == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price - (self.stop_loss_points * symbol_info.point)
                tp = price + (self.take_profit_points * symbol_info.point)
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price + (self.stop_loss_points * symbol_info.point)
                tp = price - (self.take_profit_points * symbol_info.point)
            
            # Normalizar preços
            sl = round(sl, symbol_info.digits)
            tp = round(tp, symbol_info.digits)
            
            # Criar comentário
            comment = f"Numeia{magic_number}"[:32]
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": self.price_deviation_points,
                "magic": magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
                "sl": sl,
                "tp": tp,
            }
            
            # Enviar ordem
            logger.info(f"[{order_id}] Enviando ordem MT5: {symbol} {action} {volume} @ {price:.5f}")
            result = mt5.order_send(request)
            
            latency_ms = (time.time() - start_time) * 1000
            
            if result is None:
                error_code, error_details = mt5.last_error()
                error_msg = f"Erro {error_code}: {error_details}"
                logger.error(f"[{order_id}] Falha ao enviar ordem: {error_msg}")
                
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
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"retcode={result.retcode}, comment={result.comment}"
                logger.error(f"[{order_id}] Ordem rejeitada: {error_msg}")
                
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
                    'retcode': result.retcode,
                    'error': result.comment,
                    'latency_ms': latency_ms
                }
            
            # Sucesso
            logger.info(
                f"[{order_id}] ✅ ORDEM EXECUTADA: Ticket {result.order}, "
                f"Deal {result.deal}, Latência: {latency_ms:.2f}ms"
            )
            
            self.monitor.record_execution(
                order_id=order_id,
                latency_ms=latency_ms,
                success=True,
                symbol=symbol,
                volume=volume
            )
            
            return {
                'order_id': order_id,
                'status': 'SUCCESS',
                'order': result.order,
                'deal': result.deal,
                'volume': result.volume,
                'price': result.price,
                'latency_ms': latency_ms
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            logger.error(f"[{order_id}] Erro na execução: {error_msg}")
            
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
            
        finally:
            # Sempre liberar conexão
            if conn_id:
                self.connection_pool.release(conn_id)
    
    def submit_task(self, task: Dict[str, Any]) -> str:
        """
        Adiciona tarefa à fila de execução.
        
        Args:
            task: Dict com informações da ordem
        
        Returns:
            order_id da tarefa
        """
        order_id = task.get('order_id', str(uuid.uuid4()))
        task['order_id'] = order_id
        self._task_queue.put(task)
        logger.debug(f"Tarefa adicionada à fila: {order_id}")
        return order_id
    
    def run(self, max_tasks: Optional[int] = None):
        """
        Executa tarefas da fila em paralelo.
        
        Args:
            max_tasks: Número máximo de tarefas a processar (None = todas)
        """
        if not MT5_AVAILABLE:
            logger.error("MetaTrader5 não disponível. Execução desabilitada.")
            return
        
        tasks_processed = 0
        futures = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self._stop_event.is_set():
                try:
                    # Obter tarefa da fila (com timeout)
                    task = self._task_queue.get(timeout=1.0)
                    
                    # Submeter para execução paralela
                    future = executor.submit(self._execute_single_order, task)
                    futures.append(future)
                    
                    tasks_processed += 1
                    
                    # Limitar número de tarefas se especificado
                    if max_tasks and tasks_processed >= max_tasks:
                        break
                    
                except Empty:
                    # Fila vazia, aguardar um pouco
                    continue
                except Exception as e:
                    logger.error(f"Erro ao processar tarefa: {e}")
            
            # Aguardar conclusão de todas as tarefas
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30.0)
                    logger.debug(f"Tarefa concluída: {result.get('order_id')}")
                except Exception as e:
                    logger.error(f"Erro ao obter resultado da tarefa: {e}")
    
    def stop(self):
        """Para a execução de novas tarefas."""
        self._stop_event.set()
        logger.info("ParallelExecutor parado.")
    
    def get_queue_size(self) -> int:
        """Retorna tamanho atual da fila."""
        return self._task_queue.qsize()

