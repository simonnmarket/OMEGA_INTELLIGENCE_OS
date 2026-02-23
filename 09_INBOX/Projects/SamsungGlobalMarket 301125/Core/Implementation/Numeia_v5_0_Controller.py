# -*- coding: utf-8 -*-
"""
================================================================================
NUMEIA v5.0 - CONTROLADOR PYTHON PARA PORTFOLIO PASSIVO
================================================================================

FUNÇÃO: Controlar o EA Numeia v5.0 via arquivos de comando
FILOSOFIA: "Executar e Monitorar. Não otimizar. Não interferir."
PROTOCOLO: ASC-AQ v1.0.0

ARQUITETURA:
  Python (este script) → Arquivo JSON → EA (MT5) → Broker → Mercado

COMANDOS DISPONÍVEIS:
  - INITIALIZE: Criar portfolio inicial
  - REBALANCE: Forçar rebalanceamento
  - STATUS: Solicitar status atual
  - KILL_SWITCH: Ativar kill-switch manual

BASEADO EM: Diretiva v4.1 (ACWI Sharpe 0.384)

================================================================================
"""

import json
import os
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuração
MT5_COMMON_PATH = os.path.join(
    os.environ.get('APPDATA', ''),
    'MetaQuotes', 'Terminal', 'Common', 'Files'
)

PORTFOLIO_CONFIG = {
    'SPX500': {'weight': 0.80, 'name': 'S&P 500 Index (Proxy Mercado Global)'},
    'XAUUSD': {'weight': 0.15, 'name': 'Gold (Hedge e Diversificação)'},
    'CASH': {'weight': 0.05, 'name': 'Cash Reserve'}
}

class NumeiaV5Controller:
    """
    Controlador Python para Numeia v5.0 Passive Portfolio.
    """
    
    def __init__(self, mt5_path=MT5_COMMON_PATH):
        self.mt5_path = mt5_path
        self.command_file = os.path.join(mt5_path, 'NumeiaCommand.json')
        self.status_file = os.path.join(mt5_path, 'NumeiaStatus.json')
        
        logging.info("="*80)
        logging.info("NUMEIA v5.0 - CONTROLADOR PYTHON (HANTEC EDITION)")
        logging.info("="*80)
        logging.info(f"MT5 Common Path: {self.mt5_path}")
        logging.info(f"Portfolio: 80% SPX500 + 15% XAUUSD (Gold) + 5% CASH")
        logging.info("="*80)
    
    def send_command(self, command_type, params=None):
        """Enviar comando para o EA via arquivo JSON."""
        
        command = {
            'command': command_type,
            'timestamp': datetime.now().isoformat(),
            'params': params or {}
        }
        
        try:
            with open(self.command_file, 'w', encoding='utf-8') as f:
                json.dump(command, f, indent=2)
            
            logging.info(f"✅ Comando enviado: {command_type}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro ao enviar comando: {e}")
            return False
    
    def initialize_portfolio(self):
        """Enviar comando para inicializar portfolio."""
        logging.info("\n[COMMAND] Inicializando portfolio...")
        logging.info("  80% SPX500 (S&P 500)")
        logging.info("  15% XAUUSD (Gold)")
        logging.info("  5% CASH\n")
        
        return self.send_command('INITIALIZE', {
            'portfolio': PORTFOLIO_CONFIG
        })
    
    def force_rebalance(self):
        """Forçar rebalanceamento imediato."""
        logging.info("\n[COMMAND] Forçando rebalanceamento trimestral...\n")
        return self.send_command('REBALANCE')
    
    def request_status(self):
        """Solicitar status atual do portfolio."""
        logging.info("\n[COMMAND] Solicitando status...\n")
        return self.send_command('STATUS')
    
    def activate_kill_switch(self):
        """Ativar kill-switch manualmente."""
        logging.warning("\n🚨 [COMMAND] Ativando KILL-SWITCH manual...\n")
        return self.send_command('KILL_SWITCH')
    
    def read_status(self):
        """Ler status atual do EA."""
        try:
            if not os.path.exists(self.status_file):
                logging.warning("Arquivo de status não encontrado")
                return None
            
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            return status
            
        except Exception as e:
            logging.error(f"❌ Erro ao ler status: {e}")
            return None
    
    def print_status(self):
        """Imprimir status formatado."""
        status = self.read_status()
        
        if not status:
            logging.warning("Status não disponível")
            return
        
        logging.info("="*80)
        logging.info("STATUS DO PORTFOLIO NUMEIA v5.0")
        logging.info("="*80)
        logging.info(f"Timestamp: {status.get('timestamp', 'N/A')}")
        logging.info(f"Balanço: {status.get('balance', 0):.2f}")
        logging.info(f"Equity: {status.get('equity', 0):.2f}")
        logging.info(f"Drawdown: {status.get('drawdown', 0):.2f}%")
        logging.info(f"Kill-Switch: {'❌ ATIVO' if status.get('kill_switch') else '✅ Normal'}")
        
        if 'positions' in status:
            logging.info("\nPosições:")
            for pos in status['positions']:
                logging.info(f"  {pos['symbol']}: {pos['weight']:.1f}% (target: {pos['target_weight']:.1f}%)")
        
        logging.info("="*80)
    
    def monitor_loop(self, interval=300):
        """Loop de monitoramento contínuo."""
        logging.info(f"\n🔍 Iniciando monitoramento (intervalo: {interval}s)")
        logging.info("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                self.request_status()
                time.sleep(5)  # Aguardar EA processar
                self.print_status()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("\n⏸️ Monitoramento interrompido pelo usuário")


def menu_interativo():
    """Menu interativo para controlar o EA."""
    
    controller = NumeiaV5Controller()
    
    while True:
        print("\n" + "="*80)
        print("NUMEIA v5.0 - MENU DE CONTROLE")
        print("="*80)
        print("1. Inicializar Portfolio (primeira vez)")
        print("2. Forçar Rebalanceamento")
        print("3. Ver Status Atual")
        print("4. Monitoramento Contínuo")
        print("5. 🚨 Ativar Kill-Switch")
        print("0. Sair")
        print("="*80)
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == '1':
            controller.initialize_portfolio()
            print("\n✅ Comando enviado ao EA. Aguarde execução no MT5.")
            
        elif escolha == '2':
            controller.force_rebalance()
            print("\n✅ Comando de rebalanceamento enviado.")
            
        elif escolha == '3':
            controller.request_status()
            time.sleep(2)
            controller.print_status()
            
        elif escolha == '4':
            interval = input("Intervalo de atualização (segundos, default=300): ").strip()
            interval = int(interval) if interval else 300
            controller.monitor_loop(interval)
            
        elif escolha == '5':
            confirm = input("🚨 CONFIRMA ativar kill-switch? (sim/não): ").strip().lower()
            if confirm == 'sim':
                controller.activate_kill_switch()
                print("\n🚨 KILL-SWITCH ATIVADO!")
            else:
                print("Cancelado.")
                
        elif escolha == '0':
            print("\n👋 Saindo...")
            break
        
        else:
            print("\n❌ Opção inválida")


if __name__ == '__main__':
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          NUMEIA v5.0 - PASSIVE PORTFOLIO (HANTEC)            ║
    ║                                                               ║
    ║   "Executar e Monitorar. Não otimizar. Não interferir."      ║
    ║                                                               ║
    ║   Baseado em: Diretiva v4.1 (Evidência Empírica)             ║
    ║   Portfolio: 80% SPX500 + 15% XAUUSD + 5% CASH               ║
    ║   Ativos: 120+ disponíveis no Hantec Market Watch            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    menu_interativo()

