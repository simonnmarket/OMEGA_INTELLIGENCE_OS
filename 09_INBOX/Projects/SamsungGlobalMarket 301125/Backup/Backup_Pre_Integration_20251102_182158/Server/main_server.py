#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORQUESTRADOR PRINCIPAL - SAMSUNG GLOBAL MARKET
PROJETO: Prometheus v3.0.0
PROTOCOLO: Omega TIER-0
ARQUITETURA: Big Tech - Modelo de Serviços Desacoplados

Este é o ÚNICO ponto de entrada para iniciar todos os serviços do sistema.
Arquitetura profissional seguindo padrões de microserviços.
"""

import threading
import time
import signal
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Adicionar diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Server.trading_engine import TradingEngine
from Server.mt5_socket_service import MT5SocketService

# ============================================================================
# CONFIGURAÇÃO DE LOGGING INSTITUCIONAL (ISO 8601)
# ============================================================================
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_DIR / "main_server.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("MainServer")

# ============================================================================
# ORQUESTRADOR PRINCIPAL
# ============================================================================
class MainServer:
    """
    Orquestrador que gerencia todos os serviços do sistema.
    Arquitetura desacoplada: cada serviço roda em sua própria thread.
    """
    
    def __init__(self):
        self.is_running = False
        self.services: Dict[str, threading.Thread] = {}
        self.trading_engine: Optional[TradingEngine] = None
        self.socket_service: Optional[MT5SocketService] = None
        self.start_time = None
        
    def start_services(self):
        """Inicia todos os serviços do sistema."""
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO SAMSUNG GLOBAL MARKET SERVER")
        logger.info("=" * 70)
        logger.info("Arquitetura: Big Tech - Modelo de Serviços Desacoplados")
        logger.info("Protocolo: Omega TIER-0")
        logger.info("=" * 70)
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # 1. Iniciar o Motor de Trading (Cérebro)
        try:
            logger.info("[1/2] Iniciando TradingEngine (Cérebro do Sistema)...")
            self.trading_engine = TradingEngine()
            
            self.services['trading_engine'] = threading.Thread(
                target=self._run_trading_engine,
                name="TradingEngine",
                daemon=True
            )
            self.services['trading_engine'].start()
            
            # Aguardar inicialização
            time.sleep(2)
            
            if self.trading_engine.is_running:
                logger.info("[OK] Servico 'TradingEngine' iniciado com sucesso")
            else:
                raise Exception("TradingEngine não iniciou corretamente")
                
        except Exception as e:
            logger.error(f"[ERRO] Falha ao iniciar TradingEngine: {e}")
            self.stop_services()
            return False

        # 2. Iniciar o Serviço de Socket para MT5 (Comunicação)
        try:
            logger.info("[2/2] Iniciando MT5SocketService (Comunicação com EA)...")
            self.socket_service = MT5SocketService()
            
            # Conectar TradingEngine ao SocketService para envio de sinais
            self.socket_service.set_trading_engine(self.trading_engine)
            
            # Conectar SocketService ao TradingEngine para receber sinais
            self.trading_engine.set_signal_callback(self.socket_service.send_signal_to_clients)
            
            self.services['socket_service'] = threading.Thread(
                target=self._run_socket_service,
                name="SocketService",
                daemon=True
            )
            self.services['socket_service'].start()
            
            # Aguardar inicialização
            time.sleep(2)
            
            if self.socket_service.is_running:
                logger.info("[OK] Servico 'SocketService' iniciado na porta 5555")
            else:
                raise Exception("SocketService não iniciou corretamente")
                
        except Exception as e:
            logger.error(f"[ERRO] Falha ao iniciar SocketService: {e}")
            self.stop_services()
            return False

        logger.info("=" * 70)
        logger.info("[SUCESSO] TODOS OS SERVICOS INICIADOS COM SUCESSO!")
        logger.info("=" * 70)
        logger.info("[INFO] O EA 'SamsungGlobalMarket_EA' agora pode se conectar")
        logger.info("[INFO] Motor de trading ativo e buscando alphas...")
        logger.info("=" * 70)
        return True
    
    def _run_trading_engine(self):
        """Wrapper para executar TradingEngine em thread"""
        try:
            self.trading_engine.run()
        except Exception as e:
            logger.error(f"Erro crítico no TradingEngine: {e}")
            self.is_running = False
    
    def _run_socket_service(self):
        """Wrapper para executar SocketService em thread"""
        try:
            self.socket_service.start()
        except Exception as e:
            logger.error(f"Erro crítico no SocketService: {e}")
            self.is_running = False
    
    def stop_services(self):
        """Para todos os serviços de forma graciosa."""
        logger.info("=" * 70)
        logger.info("🛑 SINAL DE PARADA RECEBIDO")
        logger.info("=" * 70)
        logger.info("Parando todos os serviços...")
        
        self.is_running = False
        
        # Parar SocketService
        if self.socket_service and self.socket_service.is_running:
            logger.info("Parando SocketService...")
            self.socket_service.stop()
            time.sleep(1)
        
        # Parar TradingEngine
        if self.trading_engine and self.trading_engine.is_running:
            logger.info("Parando TradingEngine...")
            self.trading_engine.stop()
            time.sleep(1)
        
        # Aguardar threads finalizarem
        for name, thread in self.services.items():
            if thread.is_alive():
                logger.info(f"Aguardando thread '{name}' finalizar...")
                thread.join(timeout=5)
        
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Uptime total: {uptime:.0f} segundos")
        
        logger.info("=" * 70)
        logger.info("[OK] TODOS OS SERVICOS FORAM PARADOS")
        logger.info("=" * 70)
    
    def get_status(self) -> Dict:
        """Retorna status atual do servidor"""
        return {
            'is_running': self.is_running,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'trading_engine_running': self.trading_engine.is_running if self.trading_engine else False,
            'socket_service_running': self.socket_service.is_running if self.socket_service else False,
            'active_clients': len(self.socket_service.clients) if self.socket_service else 0
        }
    
    def run(self):
        """Mantém o servidor principal ativo."""
        if not self.start_services():
            logger.error("Falha ao iniciar serviços. Encerrando...")
            return
        
        try:
            # Loop principal
            while self.is_running:
                # Verificar saúde dos serviços
                if self.trading_engine and not self.trading_engine.is_running:
                    logger.error("TradingEngine parou inesperadamente!")
                    self.is_running = False
                    break
                
                if self.socket_service and not self.socket_service.is_running:
                    logger.error("SocketService parou inesperadamente!")
                    self.is_running = False
                    break
                
                time.sleep(5)  # Verificar a cada 5 segundos
                
        except KeyboardInterrupt:
            logger.info("Interrupção recebida (Ctrl+C)")
        except Exception as e:
            logger.critical(f"Erro crítico no loop principal: {e}")
        finally:
            self.stop_services()

# ============================================================================
# GRACEFUL SHUTDOWN HANDLER
# ============================================================================
server_instance = None

def signal_handler(signum, frame):
    """Handler para sinais de shutdown"""
    if server_instance:
        server_instance.stop_services()
    sys.exit(0)

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    server_instance = MainServer()
    
    # Registrar handlers de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Executar servidor
    server_instance.run()

