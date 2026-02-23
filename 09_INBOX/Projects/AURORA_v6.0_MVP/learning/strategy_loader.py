"""
Strategy Loader - AURORA v6.0 MVP
Carregador dinâmico de estratégias
"""

import importlib
import importlib.util
import os
import sys
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("STRATEGY_LOADER")


class StrategyLoader:
    """
    Carregador Dinâmico de Estratégias
    
    Responsabilidades:
    - Recarga a quente de estratégias (sem restart)
    - Carregar modelos treinados (.pkl)
    - A/B testing entre estratégias
    - Secretário de versões
    
    API:
        load_strategy(path: str, name: str)
        reload_strategy(name: str)
        list_strategies() -> List[dict]
        get_active_strategy(symbol: str) -> Strategy
        
    Formato de Modelo (template):
        class MyStrategy:
            def __init__(self, config):
                pass
            
            def generate_signal(self, state) -> dict:
                # Retorna {action, confidence}
                pass
    """
    
    def __init__(self, strategies_path: str = "strategies/"):
        self.strategies_path = strategies_path
        self.loaded_strategies: Dict[str, Any] = {}
        self.active_strategies: Dict[str, str] = {}  # symbol -> strategy_name
        self.strategy_versions: Dict[str, int] = {}
        
    def load_strategy(self, path: str, name: str, config: Dict = None) -> bool:
        """
        Carrega estratégia de um arquivo
        
        Args:
            path: Caminho para o arquivo .py
            name: Nome identificador da estratégia
            config: Configuração para passar ao __init__
            
        Returns:
            bool: True se carregou com sucesso
        """
        try:
            # Carregar módulo dinamicamente
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # Procurar classe de estratégia
            strategy_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'generate_signal'):
                    strategy_class = attr
                    break
            
            if strategy_class is None:
                logger.error(f"No strategy class found in {path}")
                return False
            
            # Instanciar
            instance = strategy_class(config or {})
            
            # Armazenar
            self.loaded_strategies[name] = {
                "instance": instance,
                "class": strategy_class,
                "path": path,
                "config": config,
                "loaded_at": __import__('datetime').datetime.now().isoformat()
            }
            
            self.strategy_versions[name] = self.strategy_versions.get(name, 0) + 1
            
            logger.info(f"Strategy loaded: {name} (v{self.strategy_versions[name]})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load strategy {name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reload_strategy(self, name: str) -> bool:
        """
        Recarrega estratégia (hot reload)
        
        Args:
            name: Nome da estratégia
            
        Returns:
            bool: True se recarregou com sucesso
        """
        if name not in self.loaded_strategies:
            logger.error(f"Strategy {name} not loaded")
            return False
        
        strategy_info = self.loaded_strategies[name]
        path = strategy_info["path"]
        config = strategy_info["config"]
        
        # Remover do cache de módulos
        if name in sys.modules:
            del sys.modules[name]
        
        # Recarregar
        return self.load_strategy(path, name, config)
    
    def unload_strategy(self, name: str) -> bool:
        """Remove estratégia"""
        if name in self.loaded_strategies:
            del self.loaded_strategies[name]
            if name in sys.modules:
                del sys.modules[name]
            logger.info(f"Strategy unloaded: {name}")
            return True
        return False
    
    def list_strategies(self) -> List[Dict]:
        """Lista todas as estratégias carregadas"""
        return [
            {
                "name": name,
                "path": info["path"],
                "version": self.strategy_versions.get(name, 1),
                "loaded_at": info["loaded_at"],
                "has_generate_signal": hasattr(info["instance"], "generate_signal")
            }
            for name, info in self.loaded_strategies.items()
        ]
    
    def get_strategy(self, name: str) -> Optional[Any]:
        """Retorna instância da estratégia"""
        if name in self.loaded_strategies:
            return self.loaded_strategies[name]["instance"]
        return None
    
    def get_active_strategy(self, symbol: str) -> Optional[Any]:
        """
        Retorna estratégia ativa para um símbolo
        
        Args:
            symbol: Símbolo do ativo (ex: "XAUUSD")
            
        Returns:
            Strategy instance ou None
        """
        strategy_name = self.active_strategies.get(symbol)
        if strategy_name:
            return self.get_strategy(strategy_name)
        
        # Se não tem estratégia específica, retornar primeira disponível
        if self.loaded_strategies:
            return list(self.loaded_strategies.values())[0]["instance"]
        
        return None
    
    def set_active_strategy(self, symbol: str, strategy_name: str) -> bool:
        """Define estratégia ativa para um símbolo"""
        if strategy_name not in self.loaded_strategies:
            logger.error(f"Strategy {strategy_name} not loaded")
            return False
        
        self.active_strategies[symbol] = strategy_name
        logger.info(f"Active strategy for {symbol}: {strategy_name}")
        return True
    
    def generate_signal(self, symbol: str, state: Dict) -> Optional[Dict]:
        """
        Gera sinal usando estratégia ativa
        
        Args:
            symbol: Símbolo do ativo
            state: Estado atual do mercado
            
        Returns:
            dict: {action, confidence} ou None
        """
        strategy = self.get_active_strategy(symbol)
        
        if strategy is None:
            logger.warning(f"No strategy available for {symbol}")
            return None
        
        try:
            signal = strategy.generate_signal(state)
            signal["symbol"] = symbol
            signal["strategy"] = self.active_strategies.get(symbol, "default")
            return signal
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
    
    def load_all_from_directory(self, config: Dict = None) -> int:
        """
        Carrega todas as estratégias do diretório
        
        Returns:
            int: Número de estratégias carregadas
        """
        loaded = 0
        
        if not os.path.exists(self.strategies_path):
            logger.warning(f"Strategies path not found: {self.strategies_path}")
            return 0
        
        for filename in os.listdir(self.strategies_path):
            if filename.endswith('.py') and not filename.startswith('_'):
                name = filename[:-3]  # Remove .py
                path = os.path.join(self.strategies_path, filename)
                
                if self.load_strategy(path, name, config):
                    loaded += 1
        
        logger.info(f"Loaded {loaded} strategies from {self.strategies_path}")
        return loaded
    
    def get_status(self) -> Dict:
        """Retorna status do loader"""
        return {
            "loaded_count": len(self.loaded_strategies),
            "strategies": list(self.loaded_strategies.keys()),
            "active_mappings": self.active_strategies,
            "versions": self.strategy_versions
        }

