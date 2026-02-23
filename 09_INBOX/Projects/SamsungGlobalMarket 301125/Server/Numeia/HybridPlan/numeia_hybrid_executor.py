# -*- coding: utf-8 -*-
"""
Projeto Numeia - Plano Híbrido ΩΔ - Executor Principal
Execução Segura e Escalável

Versão: 2025-11-20 23:50 UTC
Autor: CEO-Cientista-Chefe - Implementação para Agent IA Cursor (AIC)
"""

import os
import json
import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Adicionar path para imports
server_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(server_dir))

# Importar componentes do Plano Híbrido
from Numeia.HybridPlan.execution_controller import ExecutionController
from Numeia.HybridPlan.monitoring import ExecutionMonitor
from Numeia.HybridPlan.capital_manager import CapitalManager

# Importar componentes do sistema existente
EXISTING_SYSTEM_AVAILABLE = False
SystemConfig = None
SignalGenerator = None
CircuitBreaker = None
AIC_Controller = None

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("prometheus_brain_v1_1", server_dir / "prometheus_brain_v1.1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    SystemConfig = module.SystemConfig
    SignalGenerator = module.SignalGenerator
    CircuitBreaker = module.CircuitBreaker
    AIC_Controller = module.AIC_Controller
    EXISTING_SYSTEM_AVAILABLE = True
except Exception as e:
    logger.warning(f"Sistema existente não disponível: {e}. Usando apenas Plano Híbrido.")

# Configuração do logger estruturado com JSON
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler("numeia_execution.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """Formatter para logs JSON estruturados."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar campos extras se existirem
        if hasattr(record, 'order_id'):
            log_entry['order_id'] = record.order_id
        if hasattr(record, 'latency_ms'):
            log_entry['latency_ms'] = record.latency_ms
        if hasattr(record, 'symbol'):
            log_entry['symbol'] = record.symbol
        
        return json.dumps(log_entry)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Carrega configuração do arquivo config.json.
    
    Args:
        config_path: Caminho para arquivo de configuração
    
    Returns:
        Dict com configurações
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Arquivo config não encontrado: {config_path}. Usando valores padrão.")
        return {
            'EXECUTION_CYCLE_SECONDS': 300,
            'EMERGENCY_MODE_ENABLED': False,
            'MAX_PARALLEL_WORKERS': 10,
            'LATENCY_THRESHOLD_MS': 500,
            'FAILURE_RATE_THRESHOLD': 0.05,
            'ROLLBACK_ENABLED': True,
            'MONITORING_WINDOW_SECONDS': 300,
            'FAILURE_WINDOW_SECONDS': 600
        }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Configuração carregada de {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}. Usando valores padrão.")
        return {
            'EXECUTION_CYCLE_SECONDS': 300,
            'EMERGENCY_MODE_ENABLED': False,
            'MAX_PARALLEL_WORKERS': 10
        }


class NumeiaHybridExecutor:
    """
    Executor principal do Plano Híbrido ΩΔ.
    Integra modo paralelo/serial com sistema existente.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        
        # Inicializar sistema existente se disponível
        self.circuit_breaker: Optional[CircuitBreaker] = None
        self.signal_generator: Optional[SignalGenerator] = None
        
        if EXISTING_SYSTEM_AVAILABLE:
            sys_config = SystemConfig()
            self.circuit_breaker = CircuitBreaker(sys_config)
            self.signal_generator = SignalGenerator(sys_config)
            logger.info("Sistema existente integrado (CircuitBreaker, SignalGenerator)")
        
        # Inicializar Execution Controller
        self.controller = ExecutionController(
            config=config,
            circuit_breaker=self.circuit_breaker
        )
        
        logger.info(
            f"NumeiaHybridExecutor inicializado: "
            f"Modo: {self.controller.current_mode}, "
            f"Ciclo: {config.get('EXECUTION_CYCLE_SECONDS', 300)}s"
        )
    
    def generate_signal(self) -> Optional[Dict[str, Any]]:
        """Gera sinal de trading."""
        if self.signal_generator:
            return self.signal_generator.generate_test_signal()
        else:
            # Sinal simples se gerador não disponível
            return {
                'action': 'BUY',
                'symbol': 'XAUUSD',
                'volume': 0.01,
                'magic_number': 1000,
                'order_id': str(uuid.uuid4()),
                'timestamp': time.time()
            }
    
    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Valida sinal antes de executar."""
        if not signal:
            return False
        
        # Validar com circuit breaker se disponível
        if self.circuit_breaker:
            if not self.circuit_breaker.check_signal_approval(signal):
                logger.warning("Sinal rejeitado pelo Circuit Breaker")
                return False
        
        # Validar com signal generator se disponível
        if self.signal_generator:
            if not self.signal_generator.validate_signal(signal):
                logger.warning("Sinal inválido segundo SignalGenerator")
                return False
        
        return True
    
    def run_cycle(self):
        """Executa um ciclo completo: Geração -> Validação -> Execução."""
        logger.info("--- Iniciando Ciclo de Execução (Plano Híbrido ΩΔ) ---")
        
        # Gerar sinal
        signal = self.generate_signal()
        if not signal:
            logger.warning("Falha ao gerar sinal")
            return
        
        # Validar sinal
        if not self.validate_signal(signal):
            logger.warning("Sinal rejeitado na validação")
            return
        
        # Executar ordem
        result = self.controller.execute_order(signal)
        
        # Log estruturado
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle': 'execution',
            'order_id': result.get('order_id'),
            'status': result.get('status'),
            'mode': self.controller.current_mode,
            'signal': {
                'symbol': signal.get('symbol'),
                'action': signal.get('action'),
                'volume': signal.get('volume')
            }
        }
        
        logger.info(f"Execution cycle: {json.dumps(log_entry)}")
        
        # Atualizar circuit breaker se disponível
        if self.circuit_breaker and result.get('status') == 'SUCCESS':
            self.circuit_breaker.update_performance({'pnl': 0.0})
        
        logger.info("--- Ciclo de Execução Finalizado ---")
    
    def run(self):
        """Loop principal de execução."""
        cycle_seconds = self.config.get('EXECUTION_CYCLE_SECONDS', 300)
        
        logger.info("Sistema NumeiaHybridExecutor iniciado. Entrando no loop principal.")
        logger.info(f"Modo: {self.controller.current_mode}, Ciclo: {cycle_seconds}s")
        
        self.running = True
        
        try:
            while self.running:
                # Executar ciclo
                self.run_cycle()
                
                # Status periódico
                status = self.controller.get_status()
                logger.info(f"Status: {json.dumps(status, default=str)}")
                
                # Aguardar próximo ciclo
                logger.info(f"Aguardando próximo ciclo em {cycle_seconds} segundos...")
                time.sleep(cycle_seconds)
                
        except KeyboardInterrupt:
            logger.info("Sistema interrompido pelo usuário.")
        except Exception as e:
            logger.critical(f"Erro crítico no loop principal: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Encerra sistema."""
        self.running = False
        self.controller.shutdown()
        logger.info("Sistema NumeiaHybridExecutor encerrado.")


def main():
    """Ponto de entrada principal."""
    print("="*80)
    print("PROJETO NUMEIA - PLANO HÍBRIDO ΩΔ")
    print("Execução Segura e Escalável")
    print("="*80)
    print(f"Data: {datetime.now().isoformat()}")
    print("="*80)
    
    # Carregar configuração
    config = load_config()
    
    # Mostrar configuração
    print("\n📋 Configuração:")
    print(f"  Modo Emergência: {'✅ Ativado' if config.get('EMERGENCY_MODE_ENABLED') else '❌ Desativado'}")
    print(f"  Max Workers Paralelo: {config.get('MAX_PARALLEL_WORKERS', 10)}")
    print(f"  Ciclo de Execução: {config.get('EXECUTION_CYCLE_SECONDS', 300)}s")
    print(f"  Rollback Automático: {'✅ Habilitado' if config.get('ROLLBACK_ENABLED') else '❌ Desabilitado'}")
    print("="*80)
    
    # Inicializar e executar
    executor = NumeiaHybridExecutor(config)
    executor.run()


if __name__ == "__main__":
    main()

