#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WATCHDOG DO SERVIDOR MT5 - SISTEMA DE MONITORAMENTO 24/7
PROJETO: Samsung Global Market
PROTOCOLO: Omega TIER-0
VERSÃO: 1.0.0

CARACTERÍSTICAS:
- Monitoramento contínuo 24/7 (sem interrupções)
- Auto-restart automático em caso de falha
- Preservação de estado e progresso
- Health checks via socket
- Logging institucional ISO 8601
- Sistema de failover robusto
"""

import subprocess
import socket
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Optional

# ============================================================================
# CONFIGURAÇÃO DE LOGGING INSTITUCIONAL (ISO 8601)
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/watchdog.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================
WATCHDOG_CONFIG = {
    'server_script': 'simple_mt5_server.py',
    'host': '127.0.0.1',
    'port': 5555,
    'health_check_interval': 10,  # Verificar saúde a cada 10 segundos
    'restart_delay': 5,  # Aguardar 5 segundos antes de reiniciar
    'max_restart_attempts': 5,  # Máximo de tentativas consecutivas
    'state_file': 'watchdog_state.json',
    'logs_dir': 'logs',
    'server_process': None
}

# ============================================================================
# SISTEMA DE PERSISTÊNCIA DE ESTADO
# ============================================================================
class StateManager:
    """Gerencia persistência de estado do sistema"""
    
    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_state(self) -> Dict:
        """Carrega estado salvo do disco"""
        if not self.state_file.exists():
            return {
                'start_time': None,
                'restart_count': 0,
                'last_restart': None,
                'uptime_seconds': 0,
                'total_uptime_seconds': 0,
                'health_checks_passed': 0,
                'health_checks_failed': 0,
                'last_health_check': None,
                'server_version': '1.0.0'
            }
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            logger.info(f"[STATE] Estado carregado: {state.get('restart_count', 0)} restarts")
            return state
        except Exception as e:
            logger.error(f"[STATE] Erro ao carregar estado: {e}")
            return self.load_state()  # Retorna estado padrão
    
    def save_state(self, state: Dict):
        """Salva estado atual no disco"""
        try:
            state['last_save'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[STATE] Erro ao salvar estado: {e}")
    
    def update_uptime(self, state: Dict):
        """Atualiza tempo de atividade total"""
        if state.get('start_time'):
            try:
                start_dt = datetime.fromisoformat(state['start_time'])
                uptime = (datetime.now() - start_dt).total_seconds()
                state['uptime_seconds'] = int(uptime)
                state['total_uptime_seconds'] = state.get('total_uptime_seconds', 0) + int(uptime)
            except Exception as e:
                logger.warning(f"[STATE] Erro ao calcular uptime: {e}")

# ============================================================================
# SISTEMA DE HEALTH CHECK
# ============================================================================
class HealthChecker:
    """Verifica saúde do servidor via socket"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.timeout = 5
    
    def check_health(self) -> bool:
        """Verifica se o servidor está respondendo"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                logger.debug(f"[HEALTH] Servidor respondendo em {self.host}:{self.port}")
                return True
            else:
                logger.warning(f"[HEALTH] Servidor não responde em {self.host}:{self.port}")
                return False
        except Exception as e:
            logger.warning(f"[HEALTH] Erro no health check: {e}")
            return False

# ============================================================================
# GERENCIADOR DE PROCESSO DO SERVIDOR
# ============================================================================
class ServerManager:
    """Gerencia o processo do servidor Python"""
    
    def __init__(self, script_path: str):
        self.script_path = Path(script_path)
        self.process: Optional[subprocess.Popen] = None
        self.venv_python = self._find_python()
    
    def _find_python(self) -> str:
        """Encontra o interpretador Python do ambiente virtual"""
        # Tenta encontrar venv
        venv_python = Path('venv/Scripts/python.exe')
        if venv_python.exists():
            return str(venv_python)
        
        # Fallback para Python do sistema
        return sys.executable
    
    def is_running(self) -> bool:
        """Verifica se o processo está rodando"""
        if self.process is None:
            return False
        
        if self.process.poll() is None:
            return True
        
        return False
    
    def start(self):
        """Inicia o servidor"""
        if self.is_running():
            logger.warning("[SERVER] Servidor já está rodando")
            return True
        
        try:
            logger.info(f"[SERVER] Iniciando servidor: {self.script_path}")
            logger.info(f"[SERVER] Python: {self.venv_python}")
            
            self.process = subprocess.Popen(
                [self.venv_python, str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd(),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Aguardar um pouco para verificar se iniciou corretamente
            time.sleep(2)
            
            if self.is_running():
                logger.info(f"[SERVER] Servidor iniciado com PID: {self.process.pid}")
                return True
            else:
                logger.error("[SERVER] Servidor não iniciou corretamente")
                return False
                
        except Exception as e:
            logger.error(f"[SERVER] Erro ao iniciar servidor: {e}")
            return False
    
    def stop(self):
        """Para o servidor"""
        if not self.is_running():
            return True
        
        try:
            logger.info(f"[SERVER] Parando servidor (PID: {self.process.pid})")
            self.process.terminate()
            
            # Aguardar terminação graciosa (5 segundos)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("[SERVER] Forçando término do processo")
                self.process.kill()
                self.process.wait()
            
            self.process = None
            logger.info("[SERVER] Servidor parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"[SERVER] Erro ao parar servidor: {e}")
            return False
    
    def restart(self):
        """Reinicia o servidor"""
        logger.info("[SERVER] Reiniciando servidor...")
        self.stop()
        time.sleep(WATCHDOG_CONFIG['restart_delay'])
        return self.start()

# ============================================================================
# WATCHDOG PRINCIPAL
# ============================================================================
class Watchdog:
    """Sistema de monitoramento e auto-restart 24/7"""
    
    def __init__(self):
        self.state_manager = StateManager(WATCHDOG_CONFIG['state_file'])
        self.health_checker = HealthChecker(
            WATCHDOG_CONFIG['host'],
            WATCHDOG_CONFIG['port']
        )
        self.server_manager = ServerManager(WATCHDOG_CONFIG['server_script'])
        self.state = self.state_manager.load_state()
        self.running = True
        self.consecutive_failures = 0
        self._initialize_state()
    
    def _initialize_state(self):
        """Inicializa estado na primeira execução"""
        if not self.state.get('start_time'):
            self.state['start_time'] = datetime.now().isoformat()
            logger.info("[WATCHDOG] Estado inicializado")
        else:
            logger.info(f"[WATCHDOG] Continuando de estado anterior (Restarts: {self.state.get('restart_count', 0)})")
    
    def _update_statistics(self, health_ok: bool):
        """Atualiza estatísticas de monitoramento"""
        self.state['last_health_check'] = datetime.now().isoformat()
        
        if health_ok:
            self.state['health_checks_passed'] = self.state.get('health_checks_passed', 0) + 1
            self.consecutive_failures = 0
        else:
            self.state['health_checks_failed'] = self.state.get('health_checks_failed', 0) + 1
            self.consecutive_failures += 1
        
        self.state_manager.update_uptime(self.state)
    
    def _handle_server_failure(self):
        """Trata falha do servidor"""
        logger.error("[WATCHDOG] FALHA DETECTADA: Servidor não está respondendo")
        
        # Verificar se o processo ainda está rodando
        if not self.server_manager.is_running():
            logger.warning("[WATCHDOG] Processo do servidor não está rodando")
        else:
            logger.warning("[WATCHDOG] Processo existe mas não está respondendo")
        
        # Verificar limite de tentativas
        if self.state.get('restart_count', 0) >= WATCHDOG_CONFIG['max_restart_attempts']:
            logger.critical(f"[WATCHDOG] LIMITE DE RESTARTS ATINGIDO ({WATCHDOG_CONFIG['max_restart_attempts']})")
            logger.critical("[WATCHDOG] Parando watchdog para evitar loop infinito")
            self.running = False
            return False
        
        # Reiniciar servidor
        logger.info("[WATCHDOG] Iniciando auto-restart...")
        self.state['restart_count'] = self.state.get('restart_count', 0) + 1
        self.state['last_restart'] = datetime.now().isoformat()
        
        success = self.server_manager.restart()
        
        if success:
            logger.info("[WATCHDOG] Servidor reiniciado com sucesso")
            self.state['start_time'] = datetime.now().isoformat()  # Resetar start_time
            self.consecutive_failures = 0
            return True
        else:
            logger.error("[WATCHDOG] Falha ao reiniciar servidor")
            return False
    
    def _print_status(self):
        """Imprime status do sistema"""
        uptime = self.state.get('uptime_seconds', 0)
        total_uptime = self.state.get('total_uptime_seconds', 0)
        restarts = self.state.get('restart_count', 0)
        health_passed = self.state.get('health_checks_passed', 0)
        health_failed = self.state.get('health_checks_failed', 0)
        
        # Calcular taxa de sucesso
        total_checks = health_passed + health_failed
        success_rate = (health_passed / total_checks * 100) if total_checks > 0 else 100
        
        logger.info("=" * 70)
        logger.info(f"[STATUS] Uptime: {uptime}s | Total: {total_uptime}s")
        logger.info(f"[STATUS] Restarts: {restarts} | Health: {health_passed} OK / {health_failed} FAIL")
        logger.info(f"[STATUS] Taxa de Sucesso: {success_rate:.2f}%")
        logger.info(f"[STATUS] Servidor: {'RUNNING' if self.server_manager.is_running() else 'STOPPED'}")
        logger.info("=" * 70)
    
    def run(self):
        """Loop principal de monitoramento"""
        logger.info("=" * 70)
        logger.info("[WATCHDOG] SISTEMA DE MONITORAMENTO 24/7 INICIADO")
        logger.info("=" * 70)
        logger.info(f"[CONFIG] Health Check: {WATCHDOG_CONFIG['health_check_interval']}s")
        logger.info(f"[CONFIG] Restart Delay: {WATCHDOG_CONFIG['restart_delay']}s")
        logger.info(f"[CONFIG] Max Restarts: {WATCHDOG_CONFIG['max_restart_attempts']}")
        logger.info("=" * 70)
        
        # Iniciar servidor na primeira execução
        if not self.server_manager.is_running():
            logger.info("[WATCHDOG] Iniciando servidor pela primeira vez...")
            if not self.server_manager.start():
                logger.critical("[WATCHDOG] FALHA ao iniciar servidor na inicialização")
                return
        
        # Aguardar alguns segundos para o servidor inicializar
        time.sleep(5)
        
        # Loop principal
        last_status_print = 0
        status_interval = 60  # Imprimir status a cada 60 segundos
        
        try:
            while self.running:
                # Health check
                health_ok = self.health_checker.check_health()
                self._update_statistics(health_ok)
                
                # Verificar se servidor está rodando
                if not self.server_manager.is_running():
                    logger.warning("[WATCHDOG] Processo do servidor parou")
                    health_ok = False
                
                # Tratar falha se necessário
                if not health_ok:
                    if self.consecutive_failures >= 3:  # 3 checks consecutivos falharam
                        self._handle_server_failure()
                
                # Salvar estado periodicamente
                if int(time.time()) % 30 == 0:  # A cada 30 segundos
                    self.state_manager.save_state(self.state)
                
                # Imprimir status periodicamente
                current_time = time.time()
                if current_time - last_status_print >= status_interval:
                    self._print_status()
                    last_status_print = current_time
                
                # Aguardar próximo check
                time.sleep(WATCHDOG_CONFIG['health_check_interval'])
                
        except KeyboardInterrupt:
            logger.info("[WATCHDOG] Interrupção recebida (Ctrl+C)")
            self.shutdown()
        except Exception as e:
            logger.critical(f"[WATCHDOG] ERRO CRÍTICO: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown gracioso do watchdog"""
        logger.info("[WATCHDOG] Encerrando watchdog...")
        self.running = False
        
        # Salvar estado final
        self.state_manager.update_uptime(self.state)
        self.state_manager.save_state(self.state)
        
        logger.info("[WATCHDOG] Estado salvo")
        logger.info("[WATCHDOG] Watchdog encerrado")

# ============================================================================
# ENTRY POINT
# ============================================================================
def main():
    """Função principal"""
    # Criar diretório de logs
    Path('logs').mkdir(exist_ok=True)
    
    # Iniciar watchdog
    watchdog = Watchdog()
    watchdog.run()

if __name__ == "__main__":
    main()

