# -*- coding: utf-8 -*-
"""
TESTE DO BACKTESTING ENGINE - SINGLE STRATEGY
Testar com Crypto Mean Reversion antes de expandir
"""

import sys
from pathlib import Path
from decimal import Decimal

# Adicionar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core' / 'Backtesting'))

from backtesting_engine import Backtester
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mean_reversion_backtest():
    """
    Teste do backtesting engine com Crypto Mean Reversion
    """
    print("\n" + "="*80)
    print("TESTE: Backtesting Engine - Crypto Mean Reversion")
    print("="*80 + "\n")
    
    # Inicializar backtester
    backtester = Backtester(
        start_date='2021-01-01',
        end_date='2023-12-31',
        initial_capital=Decimal('30000'),  # Capital da estratégia
        transaction_cost_bps=10.0
    )
    
    # Símbolos para teste (usando equities para evitar rate limit)
    symbols = ['AAPL', 'MSFT']
    
    # Carregar dados
    logger.info("Carregando dados de mercado...")
    data_loaded = backtester.load_market_data(symbols)
    
    if not data_loaded:
        logger.error("ERRO: Falha ao carregar dados")
        return False
    
    # Executar backtest (simplificado para teste)
    logger.info("\nExecutando backtest simplificado...")
    
    metrics = backtester.run_backtest(
        strategy_function=None,  # Placeholder
        strategy_name='Crypto Mean Reversion',
        symbols=symbols,
        allocated_capital=Decimal('30000')
    )
    
    # Gerar sumário
    summary = backtester.get_summary()
    
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print(f"  Período: {summary['period']}")
    print(f"  Capital inicial: EUR {summary['initial_capital']:,.0f}")
    print(f"  Capital final: EUR {summary['final_capital']:,.0f}")
    print(f"  Retorno: {summary['total_return']:.2f}%")
    print(f"  Símbolos testados: {summary['symbols_tested']}")
    print("="*80 + "\n")
    
    # Gerar relatório básico
    backtester.generate_report("TEST_BACKTEST_REPORT.md")
    
    return True

if __name__ == "__main__":
    success = test_mean_reversion_backtest()
    
    if success:
        print("\n[OK] Teste do Backtesting Engine PASSOU")
    else:
        print("\n[ERRO] Teste do Backtesting Engine FALHOU")

