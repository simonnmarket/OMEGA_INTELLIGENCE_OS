#!/usr/bin/env python3
"""
GENESIS INCLUDES v3.0 - Container IoC para NCNT
Implementação baseada na Análise Crítica #1
Adaptado para estrutura Aurora
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("NCNT.GenesisIncludes")

@dataclass
class DependencyConfig:
    """Configuração de uma dependência"""
    name: str
    interface: Any
    implementation: Any
    is_singleton: bool = True
    initialization_params: Dict = None

class DependencyError(Exception):
    """Erro de dependência"""
    pass

class GenesisIncludes:
    """
    Container de Injeção de Dependências para NCNT v3.0
    Baseado nos princípios de Inversão de Controle (IoC)
    """
    
    _instance = None
    _dependencies: Dict[str, Any] = {}
    _initialized = False
    _checksum = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_secrets()
            self._initialize_core_dependencies()
            self._calculate_checksum()
            self._initialized = True
            logger.info("Genesis Includes v3.0 inicializado")
    
    def _load_secrets(self):
        """Carrega segredos do arquivo .env.secrets"""
        secrets_path = os.path.join(os.path.dirname(__file__), '.env.secrets')
        # Se não existir, tenta carregar do template
        if not os.path.exists(secrets_path):
            template_path = os.path.join(os.path.dirname(__file__), '.env.secrets.template')
            if os.path.exists(template_path):
                logger.warning(f"Arquivo de segredos não encontrado, usando template: {template_path}")
                secrets_path = template_path
            else:
                logger.warning(f"Arquivo de segredos não encontrado: {secrets_path}. Usando valores padrão.")
                self.secrets = {}
                return
        
        self.secrets = {}
        with open(secrets_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.secrets[key.strip()] = value.strip()
        
        logger.info(f"Carregados {len(self.secrets)} segredos")
    
    def _initialize_core_dependencies(self):
        """Inicializa dependências core do sistema"""
        # Configurações do sistema
        self.register('config', self.secrets)
        
        # Interfaces serão resolvidas dinamicamente
        self.register('interfaces_registry', {})
        
        # Metrics
        self.register('metrics_collector', MetricsCollector())
        
        logger.info("Dependências core inicializadas")
    
    def register(self, name: str, dependency: Any, is_interface: bool = False):
        """
        Registra uma dependência no container
        
        Args:
            name: Nome da dependência
            dependency: Instância ou classe
            is_interface: Se é uma interface (sem implementação)
        """
        if name in self._dependencies:
            logger.warning(f"Dependência '{name}' já registrada, substituindo")
        
        self._dependencies[name] = {
            'instance': dependency,
            'is_interface': is_interface,
            'timestamp': os.path.getmtime(__file__) if os.path.exists(__file__) else 0
        }
        
        if is_interface:
            interfaces = self.resolve('interfaces_registry')
            interfaces[name] = dependency
        
        logger.debug(f"Dependência registrada: {name}")
    
    def resolve(self, name: str) -> Any:
        """
        Resolve uma dependência pelo nome
        
        Args:
            name: Nome da dependência
            
        Returns:
            Instância da dependência
            
        Raises:
            DependencyError: Se dependência não encontrada
        """
        if name not in self._dependencies:
            # Tenta carregar dinamicamente
            if name.endswith('_interface'):
                return self._load_interface(name)
            raise DependencyError(f"Dependência não encontrada: {name}")
        
        dep_info = self._dependencies[name]
        
        if dep_info['is_interface']:
            # Para interfaces, retorna a definição
            return dep_info['instance']
        
        # Para implementações, verifica se precisa instanciar
        instance = dep_info['instance']
        if isinstance(instance, type):
            # É uma classe, precisa instanciar
            instance = instance()
            self._dependencies[name]['instance'] = instance
        
        return instance
    
    def _load_interface(self, interface_name: str) -> Any:
        """Carrega interface dinamicamente"""
        # Remove sufixo _interface
        module_name = interface_name.replace('_interface', '')
        
        # Tenta importar do módulo correspondente
        try:
            if module_name.startswith('risk'):
                # Adaptado para estrutura Aurora
                import sys
                from pathlib import Path
                base_path = Path(__file__).parent.parent
                sys.path.insert(0, str(base_path))
                
                from importlib import import_module
                risk_module = import_module('01-Departamentos.Risk-Controls.interfaces')
                interface_class = getattr(risk_module, module_name.title().replace('_', ''))
                self.register(interface_name, interface_class, is_interface=True)
                return interface_class
        except (ImportError, AttributeError) as e:
            raise DependencyError(f"Interface {interface_name} não encontrada: {e}")
    
    def _calculate_checksum(self):
        """Calcula checksum do container para integridade"""
        deps_data = {
            name: {
                'type': str(type(info['instance'])),
                'is_interface': info['is_interface'],
                'timestamp': info['timestamp']
            }
            for name, info in self._dependencies.items()
        }
        
        deps_str = json.dumps(deps_data, sort_keys=True, default=str)
        self._checksum = hashlib.sha3_256(deps_str.encode()).hexdigest()[:32]
        logger.debug(f"Checksum container: {self._checksum}")
    
    def validate_integrity(self) -> bool:
        """Valida integridade do container"""
        current_checksum = self._checksum
        self._calculate_checksum()
        return current_checksum == self._checksum
    
    def get_all_dependencies(self) -> Dict:
        """Retorna todas as dependências registradas"""
        return {
            name: {
                'type': type(info['instance']).__name__,
                'is_interface': info['is_interface']
            }
            for name, info in self._dependencies.items()
        }

class MetricsCollector:
    """Coletor de métricas para o container"""
    
    def __init__(self):
        self.metrics = {
            'dependency_resolutions': 0,
            'interface_loads': 0,
            'errors': 0
        }
    
    def increment(self, metric: str):
        """Incrementa uma métrica"""
        if metric in self.metrics:
            self.metrics[metric] += 1
    
    def get_metrics(self) -> Dict:
        """Retorna todas as métricas"""
        return self.metrics.copy()

# Singleton global (lazy initialization)
GENESIS = None

def get_genesis() -> GenesisIncludes:
    """Retorna instância singleton do Genesis Includes"""
    global GENESIS
    if GENESIS is None:
        GENESIS = GenesisIncludes()
    return GENESIS

# Testes unitários
if __name__ == "__main__":
    print("🧪 Testando Genesis Includes v3.0")
    
    genesis = get_genesis()
    
    # Teste 1: Carregamento de segredos
    config = genesis.resolve('config')
    print("✅ Segredos carregados")
    
    # Teste 2: Registro e resolução
    test_obj = {"test": "object"}
    genesis.register('test_dependency', test_obj)
    resolved = genesis.resolve('test_dependency')
    assert resolved == test_obj
    print("✅ Registro e resolução funcionando")
    
    # Teste 3: Integridade
    assert genesis.validate_integrity()
    print("✅ Integridade validada")
    
    print("🎯 Genesis Includes v3.0 testado com sucesso")

