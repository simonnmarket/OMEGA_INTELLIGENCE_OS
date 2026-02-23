# -*- coding: utf-8 -*-
"""
MONITOR AUTOMÁTICO - DIRETIVA F2-T2-PLUS TRILHA 1
Monitora yfinance rate limit e executa backtest automaticamente

AÇÃO: Verificar a cada 30 minutos até resolver
GATILHO: yfinance funcional → EXECUTAR run_backtest.py
"""

import yfinance as yf
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_yfinance_status():
    """Verifica se yfinance está funcional"""
    try:
        data = yf.download('SPY', start='2023-01-01', end='2023-01-02', progress=False)
        if len(data) > 0:
            return True
    except:
        pass
    return False

def monitor_and_execute():
    """
    Monitora yfinance e executa backtest quando disponível
    """
    print("\n" + "="*80)
    print("MONITOR AUTOMÁTICO - DIRETIVA F2-T2-PLUS TRILHA 1")
    print("="*80)
    print("\nMonitorando yfinance rate limit...")
    print("Verificação a cada 30 minutos")
    print("Pressione Ctrl+C para parar\n")
    print("="*80 + "\n")
    
    check_count = 0
    
    while True:
        check_count += 1
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        logger.info(f"[CHECK #{check_count}] {timestamp} - Verificando yfinance...")
        
        if check_yfinance_status():
            logger.info("✅✅✅ YFINANCE FUNCIONAL - GATILHO ACIONADO!")
            logger.info("="*80)
            logger.info("EXECUTANDO BACKTEST EMPÍRICO AGORA...")
            logger.info("="*80)
            
            # EXECUTAR run_backtest.py
            result = subprocess.run(
                ['python', 'run_backtest.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True
            )
            
            logger.info("BACKTEST CONCLUÍDO!")
            logger.info(f"Exit code: {result.returncode}")
            
            if result.returncode == 0:
                logger.info("✅ TRILHA 1 CONCLUÍDA COM SUCESSO")
                logger.info("✅ RELATÓRIO GERADO: RELATORIO_BACKTESTING_FASE1.md")
                logger.info("\n" + "="*80)
                logger.info("NOTIFICAÇÃO AO CEO:")
                logger.info("TRILHA 1 CONCLUÍDA. RELATÓRIO GERADO. AGUARDANDO ANÁLISE DO CEO PARA ATIVAÇÃO DA TRILHA 2.")
                logger.info("="*80)
            else:
                logger.error("❌ Backtest falhou - verificar logs")
            
            break
        else:
            logger.info("⏸️ Rate limit ainda ativo - aguardando...")
            logger.info(f"   Próxima verificação em 30 minutos\n")
            time.sleep(1800)  # 30 minutos

if __name__ == "__main__":
    try:
        monitor_and_execute()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor interrompido pelo usuário")

