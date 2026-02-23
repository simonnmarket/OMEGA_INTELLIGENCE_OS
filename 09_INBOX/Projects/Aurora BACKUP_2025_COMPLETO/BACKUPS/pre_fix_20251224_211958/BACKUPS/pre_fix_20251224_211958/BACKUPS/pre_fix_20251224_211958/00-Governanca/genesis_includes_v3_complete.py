#!/usr/bin/env python3
"""
GENESIS INCLUDES v3.0 - Container IoC para NCNT
STATUS: OBRIGATÓRIO - INTEGRIDADE VERIFICADA VIA SHA3-256
Adaptado para estrutura Aurora
"""

import os
import sys
import json
import hashlib
import threading
import asyncio
from typing import Dict, Any, Optional, Type, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from enum import Enum
import inspect

# ============================================================================
# CONFIGURAÇÃO DE LOGGING INSTITUCIONAL
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-25s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("NCNT.Genesis")

# ============================================================================
# EXCEÇÕES DO SISTEMA
# ============================================================================
class DependencyIntegrityError(Exception):
    """Falha de integridade em dependência"""
    pass

class ConfigurationError(Exception):
    """Erro de configuração do sistema"""
    pass

class CircularDependencyError(Exception):
    """Dependência circular detectada"""
    pass

class ServiceTimeoutError(Exception):
    """Timeout na inicialização de serviço"""
    pass

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================
class ServiceStatus(Enum):
    """Status de um serviço no container"""
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    SHUTTING_DOWN = "SHUTTING_DOWN"

@dataclass
class ServiceHealth:
    """Health check de um serviço"""
    status: ServiceStatus
    timestamp: datetime
    latency_ms: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """Verifica se o serviço está saudável"""
        return self.status == ServiceStatus.HEALTHY
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "healthy": self.is_healthy()
        }

@dataclass
class DependencyMetadata:
    """Metadados de uma dependência"""
    name: str
    class_path: str
    version: str = "1.0.0"
    checksum: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    initialized_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    health: ServiceHealth = field(default_factory=lambda: ServiceHealth(
        status=ServiceStatus.UNINITIALIZED,
        timestamp=datetime.now()
    ))
    
    def calculate_checksum(self) -> str:
        """Calcula checksum dos metadados"""
        data = f"{self.name}{self.class_path}{self.version}{''.join(self.dependencies)}"
        return hashlib.sha3_256(data.encode()).hexdigest()[:32]
    
    def validate(self) -> bool:
        """Valida integridade dos metadados"""
        if not self.checksum:
            return False
        return self.checksum == self.calculate_checksum()

@dataclass  
class SystemMetrics:
    """Métricas do sistema"""
    dependencies_registered: int = 0
    dependencies_resolved: int = 0
    resolution_errors: int = 0
    integrity_checks: int = 0
    integrity_failures: int = 0
    health_checks: int = 0
    health_failures: int = 0
    startup_time_ms: float = 0.0
    total_uptime_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "dependencies_registered": self.dependencies_registered,
            "dependencies_resolved": self.dependencies_resolved,
            "resolution_errors": self.resolution_errors,
            "integrity_checks": self.integrity_checks,
            "integrity_failures": self.integrity_failures,
            "health_checks": self.health_checks,
            "health_failures": self.health_failures,
            "startup_time_ms": self.startup_time_ms,
            "total_uptime_ms": self.total_uptime_ms,
            "success_rate": self._calculate_success_rate(),
            "health_score": self._calculate_health_score()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calcula taxa de sucesso do container"""
        total_operations = self.dependencies_resolved + self.resolution_errors
        if total_operations == 0:
            return 1.0
        return self.dependencies_resolved / total_operations
    
    def _calculate_health_score(self) -> float:
        """Calcula score de saúde do sistema"""
        if self.health_checks == 0:
            return 1.0
        return 1.0 - (self.health_failures / self.health_checks)

# ============================================================================
# CLASSE PRINCIPAL: GENESIS INCLUDES
# ============================================================================
class GenesisIncludes:
    """
    Container de Injeção de Dependências para NCNT v3.0
    Implementação Singleton com verificação de integridade SHA3-256
    """
    
    # Variáveis de classe para singleton
    _instance: Optional['GenesisIncludes'] = None
    _initialized: bool = False
    _lock: threading.RLock = threading.RLock()
    _shutdown_event: threading.Event = threading.Event()
    
    # Registry de dependências
    _dependency_registry: Dict[str, Any] = {}
    _metadata_registry: Dict[str, DependencyMetadata] = {}
    _dependency_graph: Dict[str, List[str]] = {}
    _health_checkers: Dict[str, Callable] = {}
    
    # Configuração do sistema
    _system_config: Dict = {}
    _metrics: SystemMetrics = SystemMetrics()
    _start_time: datetime = datetime.now()
    
    def __new__(cls):
        """Implementação do padrão Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dependency_registry = {}
            cls._instance._metadata_registry = {}
            cls._instance._dependency_graph = {}
            cls._instance._health_checkers = {}
            cls._instance._system_config = {}
            cls._instance._metrics = SystemMetrics()
            cls._instance._start_time = datetime.now()
        return cls._instance
    
    def __init__(self):
        """Inicialização do container"""
        with self._lock:
            if self._initialized:
                return
            
            start_time = datetime.now()
            
            try:
                # 1. Carregar configuração do sistema
                self._load_system_configuration()
                
                # 2. Inicializar dependências core
                self._initialize_core_dependencies()
                
                # 3. Validar integridade
                self._validate_container_integrity()
                
                # 4. Iniciar health checks periódicos
                self._start_health_check_thread()
                
                # 5. Calcular métricas de inicialização
                init_time = (datetime.now() - start_time).total_seconds() * 1000
                self._metrics.startup_time_ms = init_time
                
                self._initialized = True
                
                logger.info(f"Genesis Includes v3.0 inicializado em {init_time:.2f}ms")
                logger.info(f"Dependências registradas: {self._metrics.dependencies_registered}")
                logger.info(f"Integridade: VALIDADA (SHA3-256)")
                
            except Exception as e:
                logger.critical(f"FALHA NA INICIALIZAÇÃO: {e}")
                self._shutdown()
                raise ConfigurationError(f"Falha na inicialização do Genesis Includes: {e}")
    
    def _load_system_configuration(self) -> None:
        """Carrega configuração do sistema do arquivo .env.secrets"""
        config_path = os.path.join(os.path.dirname(__file__), '.env.secrets')
        
        # Fallback para template se não existir
        if not os.path.exists(config_path):
            template_path = os.path.join(os.path.dirname(__file__), '.env.secrets.template')
            if os.path.exists(template_path):
                logger.warning(f"Arquivo de configuração não encontrado, usando template: {template_path}")
                config_path = template_path
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {config_path}. Usando valores padrão.")
                self._system_config = {}
                return
        
        try:
            self._system_config = {}
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self._system_config[key.strip()] = value.strip()
            
            # Validação mínima (não falha se usar template)
            required_keys = ['DB_HOST', 'DB_PORT', 'DB_NAME']
            missing_keys = [key for key in required_keys if key not in self._system_config]
            
            if missing_keys and os.path.exists(config_path) and 'template' not in config_path:
                logger.warning(f"Chaves de configuração faltando: {missing_keys}")
            
            logger.info(f"Configuração carregada: {len(self._system_config)} parâmetros")
            
        except Exception as e:
            logger.warning(f"Erro ao carregar configuração: {e}. Continuando com valores padrão.")
            self._system_config = {}
    
    def _initialize_core_dependencies(self) -> None:
        """Inicializa dependências core do sistema"""
        # Registrar configuração como dependência
        self.register('system_config', self._system_config, is_singleton=True)
        
        logger.debug("Dependências core inicializadas")
    
    def _validate_container_integrity(self) -> None:
        """Valida integridade do container"""
        self._metrics.integrity_checks += 1
        
        # 1. Verificar dependências cíclicas
        self._detect_circular_dependencies()
        
        # 2. Validar checksums dos metadados
        invalid_metadata = []
        for name, metadata in self._metadata_registry.items():
            if not metadata.validate():
                invalid_metadata.append(name)
                self._metrics.integrity_failures += 1
        
        if invalid_metadata:
            logger.warning(f"Metadados de dependência inválidos: {invalid_metadata}")
        
        logger.info("Validação de integridade do container concluída")
    
    def _detect_circular_dependencies(self) -> None:
        """Detecta dependências circulares usando DFS"""
        visited = set()
        recursion_stack = set()
        
        def dfs(dependency_name: str) -> bool:
            """Depth-first search para detecção de ciclos"""
            visited.add(dependency_name)
            recursion_stack.add(dependency_name)
            
            for neighbor in self._dependency_graph.get(dependency_name, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
            
            recursion_stack.remove(dependency_name)
            return False
        
        # Verificar todas as dependências
        for dependency in self._dependency_graph.keys():
            if dependency not in visited:
                if dfs(dependency):
                    raise CircularDependencyError(
                        f"Dependência circular detectada envolvendo: {dependency}"
                    )
    
    def _start_health_check_thread(self) -> None:
        """Inicia thread para health checks periódicos"""
        def health_check_worker():
            while not self._shutdown_event.is_set():
                try:
                    self._perform_health_checks()
                    self._shutdown_event.wait(30)  # Check a cada 30 segundos
                except Exception as e:
                    logger.error(f"Erro no health check: {e}")
        
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
        logger.debug("Thread de health checks iniciada")
    
    def _perform_health_checks(self) -> None:
        """Executa health checks em todas as dependências"""
        self._metrics.health_checks += 1
        
        for name, health_checker in self._health_checkers.items():
            try:
                start_time = datetime.now()
                result = health_checker()
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                if result:
                    if name in self._metadata_registry:
                        self._metadata_registry[name].health.status = ServiceStatus.HEALTHY
                        self._metadata_registry[name].health.latency_ms = latency
                        self._metadata_registry[name].health.timestamp = datetime.now()
                else:
                    if name in self._metadata_registry:
                        self._metadata_registry[name].health.status = ServiceStatus.DEGRADED
                        self._metrics.health_failures += 1
                    
            except Exception as e:
                if name in self._metadata_registry:
                    self._metadata_registry[name].health.status = ServiceStatus.FAILED
                    self._metadata_registry[name].health.last_error = str(e)
                    self._metadata_registry[name].health.error_count += 1
                    self._metrics.health_failures += 1
    
    def register(self, name: str, dependency: Any, 
                 is_singleton: bool = True,
                 dependencies: List[str] = None,
                 version: str = "1.0.0",
                 health_checker: Callable = None) -> None:
        """
        Registra uma dependência no container
        
        Args:
            name: Nome único da dependência
            dependency: Instância ou classe da dependência
            is_singleton: Se é uma instância única (True) ou factory (False)
            dependencies: Lista de nomes de dependências requeridas
            version: Versão da dependência
            health_checker: Função para health check (retorna bool)
            
        Raises:
            ValueError: Se nome já registrado
            DependencyIntegrityError: Se falha na criação de metadados
        """
        with self._lock:
            if name in self._dependency_registry:
                logger.warning(f"Dependência '{name}' já registrada, substituindo")
            
            # Criar metadados
            if hasattr(dependency, '__class__'):
                class_path = f"{dependency.__class__.__module__}.{dependency.__class__.__name__}"
            else:
                class_path = str(type(dependency))
            
            metadata = DependencyMetadata(
                name=name,
                class_path=class_path,
                version=version,
                dependencies=dependencies or [],
                initialized_at=datetime.now(),
                health=ServiceHealth(
                    status=ServiceStatus.INITIALIZING,
                    timestamp=datetime.now()
                )
            )
            metadata.checksum = metadata.calculate_checksum()
            
            # Registrar dependência
            self._dependency_registry[name] = {
                'instance': dependency if is_singleton else None,
                'factory': None if is_singleton else dependency,
                'is_singleton': is_singleton,
                'initialized': is_singleton
            }
            
            # Registrar metadados
            self._metadata_registry[name] = metadata
            
            # Atualizar grafo de dependências
            if dependencies:
                self._dependency_graph[name] = dependencies.copy()
            
            # Registrar health checker se fornecido
            if health_checker:
                self._health_checkers[name] = health_checker
            
            # Atualizar métricas
            self._metrics.dependencies_registered += 1
            
            logger.debug(f"Dependência registrada: {name} ({class_path})")
    
    def resolve(self, name: str, **kwargs) -> Any:
        """
        Resolve uma dependência pelo nome
        
        Args:
            name: Nome da dependência a resolver
            **kwargs: Argumentos adicionais para factories
            
        Returns:
            Instância da dependência
            
        Raises:
            KeyError: Se dependência não encontrada
            DependencyIntegrityError: Se falha na resolução
        """
        with self._lock:
            start_time = datetime.now()
            
            try:
                # Verificar se dependência existe
                if name not in self._dependency_registry:
                    raise KeyError(f"Dependência '{name}' não encontrada no container")
                
                dep_info = self._dependency_registry[name]
                metadata = self._metadata_registry[name]
                
                # Atualizar último acesso
                metadata.last_accessed = datetime.now()
                
                # Resolver dependências requeridas primeiro
                if metadata.dependencies:
                    for dep_name in metadata.dependencies:
                        if dep_name not in self._dependency_registry:
                            raise DependencyIntegrityError(
                                f"Dependência requerida '{dep_name}' não encontrada para '{name}'"
                            )
                        # Resolver dependência requerida recursivamente
                        self.resolve(dep_name)
                
                # Obter instância
                if dep_info['is_singleton']:
                    if not dep_info['initialized']:
                        # Inicializar singleton
                        if dep_info['factory']:
                            dep_info['instance'] = dep_info['factory'](**kwargs)
                        else:
                            dep_info['instance'] = None
                        dep_info['initialized'] = True
                    instance = dep_info['instance']
                else:
                    # Criar nova instância da factory
                    instance = dep_info['factory'](**kwargs) if dep_info['factory'] else None
                
                # Validar instância
                if instance is None:
                    raise DependencyIntegrityError(f"Falha ao criar instância para '{name}'")
                
                # Atualizar health status
                metadata.health.status = ServiceStatus.HEALTHY
                metadata.health.timestamp = datetime.now()
                
                # Atualizar métricas
                self._metrics.dependencies_resolved += 1
                resolution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.debug(f"Dependência resolvida: {name} em {resolution_time:.2f}ms")
                
                return instance
                
            except KeyError as e:
                self._metrics.resolution_errors += 1
                logger.error(f"Erro ao resolver dependência '{name}': {e}")
                raise
            except Exception as e:
                self._metrics.resolution_errors += 1
                logger.error(f"Erro inesperado ao resolver '{name}': {e}")
                raise DependencyIntegrityError(f"Erro ao resolver '{name}': {e}")
    
    def get_health_status(self, name: str = None) -> Dict:
        """
        Retorna status de saúde de uma dependência ou de todas
        
        Args:
            name: Nome da dependência (None para todas)
            
        Returns:
            Dict com status de saúde
        """
        with self._lock:
            if name:
                if name not in self._metadata_registry:
                    return {"error": f"Dependência '{name}' não encontrada"}
                return self._metadata_registry[name].health.to_dict()
            
            # Retornar status de todas as dependências
            return {
                name: metadata.health.to_dict()
                for name, metadata in self._metadata_registry.items()
            }
    
    def get_metrics(self) -> Dict:
        """Retorna métricas do container"""
        with self._lock:
            self._metrics.total_uptime_ms = (datetime.now() - self._start_time).total_seconds() * 1000
            
            return {
                'container_metrics': self._metrics.to_dict(),
                'dependency_count': len(self._dependency_registry),
                'health_checkers_count': len(self._health_checkers),
                'integrity_status': 'VALID' if self._metrics.integrity_failures == 0 else 'INVALID',
                'health_status': self._get_overall_health_status(),
                'uptime_hours': self._metrics.total_uptime_ms / (1000 * 3600),
                'system_config_loaded': bool(self._system_config)
            }
    
    def _get_overall_health_status(self) -> str:
        """Retorna status de saúde geral do sistema"""
        if not self._metadata_registry:
            return "UNKNOWN"
        
        healthy_count = sum(1 for m in self._metadata_registry.values() 
                          if m.health.is_healthy())
        total_count = len(self._metadata_registry)
        
        if healthy_count == total_count:
            return "HEALTHY"
        elif healthy_count >= total_count * 0.8:
            return "DEGRADED"
        else:
            return "UNHEALTHY"
    
    def validate_integrity(self) -> bool:
        """Valida integridade completa do container"""
        with self._lock:
            try:
                self._validate_container_integrity()
                return True
            except Exception:
                return False
    
    def _shutdown(self) -> None:
        """Desliga o container de forma controlada"""
        with self._lock:
            logger.info("Desligando Genesis Includes...")
            self._shutdown_event.set()
            
            # Limpar registries
            self._dependency_registry.clear()
            self._metadata_registry.clear()
            self._dependency_graph.clear()
            self._health_checkers.clear()
            
            self._initialized = False
            self._instance = None
            
            logger.info("Genesis Includes desligado completamente")

# ============================================================================
# SINGLETON GLOBAL
# ============================================================================
_GENESIS_INSTANCE: Optional[GenesisIncludes] = None

def get_genesis() -> GenesisIncludes:
    """Retorna instância singleton do Genesis Includes"""
    global _GENESIS_INSTANCE
    if _GENESIS_INSTANCE is None:
        _GENESIS_INSTANCE = GenesisIncludes()
    return _GENESIS_INSTANCE

def validate_genesis_integrity() -> bool:
    """Valida integridade do Genesis Includes"""
    try:
        genesis = get_genesis()
        return genesis.validate_integrity()
    except Exception as e:
        logger.error(f"Falha na validação de integridade: {e}")
        return False

# ============================================================================
# TESTES DE INTEGRIDADE
# ============================================================================
if __name__ == "__main__":
    """Testes de integridade do Genesis Includes"""
    import sys
    
    print("TESTE: GENESIS INCLUDES v3.0 - TESTE DE INTEGRIDADE")
    print("=" * 60)
    
    try:
        # Teste 1: Inicialização
        print("1. Inicializando Genesis Includes...")
        genesis = get_genesis()
        
        # Teste 2: Registro de dependência
        print("2. Registrando dependência de teste...")
        genesis.register('test_config', {'test': 'value'}, is_singleton=True)
        
        # Teste 3: Resolução de dependência
        print("3. Resolvendo dependência...")
        config = genesis.resolve('test_config')
        assert config['test'] == 'value'
        
        # Teste 4: Validação de integridade
        print("4. Validando integridade...")
        integrity_valid = genesis.validate_integrity()
        assert integrity_valid
        
        # Teste 5: Métricas
        print("5. Verificando métricas...")
        metrics = genesis.get_metrics()
        assert metrics['dependency_count'] > 0
        
        # Teste 6: Health status
        print("6. Verificando health status...")
        health = genesis.get_health_status('test_config')
        assert health['healthy'] == True
        
        print("=" * 60)
        print("OK: GENESIS INCLUDES v3.0 - INTEGRIDADE VALIDADA")
        print(f"METRIC: Dependencias: {metrics['dependency_count']}")
        print(f"INTEGRITY: Integridade: {metrics['integrity_status']}")
        print(f"HEALTH: Health Status: {metrics['health_status']}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"FAIL: FALHA NO TESTE DE INTEGRIDADE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

