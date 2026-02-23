# -*- coding: utf-8 -*-
"""
MT5 Connection Pool - Singleton Pattern
Gerencia pool de conexões MT5 para execução paralela
"""

import threading
import logging
from queue import Queue, Empty
from typing import Optional
import time

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

logger = logging.getLogger(__name__)


class MT5ConnectionPool:
    """
    Singleton connection pool para MT5.
    Thread-safe com locks e queue.
    """
    
    _lock = threading.Lock()
    _instance: Optional['MT5ConnectionPool'] = None
    
    def __init__(self, max_conn: int = 1):
        if not MT5_AVAILABLE:
            raise RuntimeError("MetaTrader5 não disponível. Instale com: pip install MetaTrader5")
        
        self.max_conn = max_conn
        self.pool = Queue(maxsize=max_conn)
        self.active_connections = 0
        self._initialized = False
        self._connection_metadata = []
        
        # Inicializar conexões
        self._initialize_pool()
        
        logger.info(f"MT5ConnectionPool inicializado com {max_conn} conexões.")
    
    @classmethod
    def get_instance(cls, max_conn: int = 1) -> 'MT5ConnectionPool':
        """Obter instância singleton do pool."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(max_conn)
        return cls._instance
    
    def _initialize_pool(self):
        """Inicializa pool com conexões MT5."""
        if not self._initialized:
            # Inicializar MT5 uma vez (compartilhado entre todas as conexões)
            if not mt5.initialize():
                error_code, error_details = mt5.last_error()
                logger.critical(f"Falha ao inicializar MT5 (código {error_code}: {error_details})")
                raise RuntimeError(f"MT5 não inicializado: {error_details}")
            
            self._initialized = True
            logger.info("MT5 inicializado globalmente.")
        
        # Preencher pool com indicadores de conexão (MT5 é compartilhado)
        for i in range(self.max_conn):
            conn_id = f"MT5_CONN_{i}_{int(time.time())}"
            self.pool.put(conn_id)
            self._connection_metadata.append({
                'id': conn_id,
                'created_at': time.time(),
                'acquired': False
            })
    
    def acquire(self, timeout: float = 5.0) -> str:
        """
        Adquire uma conexão do pool.
        
        Args:
            timeout: Tempo máximo para aguardar conexão disponível (segundos)
        
        Returns:
            Connection ID
        
        Raises:
            Empty: Se nenhuma conexão estiver disponível no timeout
        """
        try:
            conn_id = self.pool.get(timeout=timeout)
            self.active_connections += 1
            
            # Atualizar metadata
            for meta in self._connection_metadata:
                if meta['id'] == conn_id:
                    meta['acquired'] = True
                    meta['acquired_at'] = time.time()
                    break
            
            logger.debug(f"Conexão MT5 adquirida: {conn_id} (Ativas: {self.active_connections}/{self.max_conn})")
            return conn_id
            
        except Empty:
            logger.warning(f"Timeout ao adquirir conexão MT5 (timeout: {timeout}s)")
            raise
    
    def release(self, conn_id: str):
        """
        Libera uma conexão de volta ao pool.
        
        Args:
            conn_id: ID da conexão a ser liberada
        """
        self.pool.put(conn_id)
        self.active_connections -= 1
        
        # Atualizar metadata
        for meta in self._connection_metadata:
            if meta['id'] == conn_id:
                meta['acquired'] = False
                meta['released_at'] = time.time()
                break
        
        logger.debug(f"Conexão MT5 liberada: {conn_id} (Ativas: {self.active_connections}/{self.max_conn})")
    
    def get_active_count(self) -> int:
        """Retorna número de conexões ativas."""
        return self.active_connections
    
    def get_pool_status(self) -> dict:
        """Retorna status do pool."""
        return {
            'max_connections': self.max_conn,
            'active_connections': self.active_connections,
            'available_connections': self.pool.qsize(),
            'initialized': self._initialized
        }
    
    def shutdown(self):
        """Encerra todas as conexões e fecha o pool."""
        with self._lock:
            # Liberar todas as conexões pendentes
            while not self.pool.empty():
                try:
                    self.pool.get_nowait()
                except Empty:
                    break
            
            if self._initialized and MT5_AVAILABLE:
                mt5.shutdown()
                self._initialized = False
            
            self.active_connections = 0
            logger.info("MT5ConnectionPool encerrado.")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

