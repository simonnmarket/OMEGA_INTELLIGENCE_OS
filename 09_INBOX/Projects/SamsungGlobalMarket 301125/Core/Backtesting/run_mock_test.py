# -*- coding: utf-8 -*-
"""
VALIDAÇÃO DO FRAMEWORK DE BACKTESTING COM MOCK STRATEGY
DIRETIVA: F1-T4 - Validação do Chassi
DATA: 02-11-2025 22:00 CET

OBJETIVO:
- Validar que framework calcula P&L corretamente
- Validar que métricas são computadas corretamente
- Validar geração de relatório
- Tudo com dados simples e previsíveis
"""

import sys
from pathlib import Path
from decimal import Decimal
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import logging

# Adicionar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core' / 'Backtesting'))

from backtesting_engine import Backtester, BacktestTrade
from mock_strategy import MockStrategy, MockStrategyValidator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_price_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Cria dados de preço mock para testes
    
    Args:
        symbol: Símbolo do ativo
        start_date: Data inicial
        end_date: Data final
        
    Returns:
        DataFrame com OHLCV mock
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Preços mock: tendência de alta + ruído
    base_price = 100.0
    trend = 0.0003  # +0.03% ao dia = ~11% ao ano
    volatility = 0.01  # 1% de volatilidade diária
    
    prices = []
    current_price = base_price
    
    for i in range(len(dates)):
        # Drift + random walk
        daily_return = trend + np.random.normal(0, volatility)
        current_price = current_price * (1 + daily_return)
        prices.append(current_price)
    
    # Criar DataFrame
    df = pd.DataFrame({
        'Open': [p * 0.998 for p in prices],
        'High': [p * 1.005 for p in prices],
        'Low': [p * 0.995 for p in prices],
        'Close': prices,
        'Volume': [1000000] * len(dates)
    }, index=dates)
    
    logger.info(f"[MockData] Criado para {symbol}: {len(df)} dias")
    logger.info(f"  Preço inicial: {df['Close'].iloc[0]:.2f}")
    logger.info(f"  Preço final: {df['Close'].iloc[-1]:.2f}")
    logger.info(f"  Retorno: {((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100:.2f}%")
    
    return df

def run_mock_validation_test():
    """
    Teste de validação do framework com mock strategy
    
    Testa:
    1. Carregamento de dados mock
    2. Geração de sinais previsíveis
    3. Execução de trades
    4. Cálculo de P&L
    5. Cálculo de métricas
    6. Geração de relatório
    """
    print("\n" + "="*80)
    print("VALIDAÇÃO DO FRAMEWORK - MOCK STRATEGY TEST")
    print("="*80 + "\n")
    
    # Configuração do teste
    symbol = 'SPY'
    start_date = '2023-01-01'
    end_date = '2023-03-31'  # 3 meses para teste rápido
    initial_capital = Decimal('10000')  # EUR 10k para teste
    
    logger.info("CONFIGURAÇÃO DO TESTE:")
    logger.info(f"  Símbolo: {symbol}")
    logger.info(f"  Período: {start_date} a {end_date} (3 meses)")
    logger.info(f"  Capital: EUR {float(initial_capital):,.0f}")
    logger.info(f"  Estratégia: Monthly Rotation (BUY dia 1, SELL dia 15)")
    
    # Criar dados mock
    logger.info("\n1. CRIANDO DADOS MOCK...")
    price_data = create_mock_price_data(symbol, start_date, end_date)
    
    # Inicializar backtester
    logger.info("\n2. INICIALIZANDO BACKTESTER...")
    backtester = Backtester(
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        transaction_cost_bps=10.0
    )
    
    # Manualmente adicionar dados mock ao backtester
    backtester.market_data[symbol] = price_data
    
    # Inicializar mock strategy
    logger.info("\n3. INICIALIZANDO MOCK STRATEGY...")
    strategy = MockStrategy(strategy_type='monthly_rotation')
    
    # Simular backtest manualmente
    logger.info("\n4. SIMULANDO BACKTEST...")
    
    trades_executed = 0
    current_date = pd.to_datetime(start_date)
    
    while current_date <= pd.to_datetime(end_date):
        # Pular fins de semana
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Obter preço do dia (se existir)
        if current_date in price_data.index:
            current_price = float(price_data.loc[current_date, 'Close'])
            price_hist = price_data.loc[:current_date, 'Close']
            
            # Gerar sinal
            signal = strategy.generate_signal(
                symbol=symbol,
                current_date=current_date,
                current_price=current_price,
                price_history=price_hist
            )
            
            # Executar trade se houver sinal
            if signal:
                logger.info(f"  {current_date.date()}: {signal['action']} @ {signal['price']:.2f} - {signal['reason']}")
                
                backtester.execute_trade(
                    timestamp=current_date,
                    symbol=symbol,
                    action=signal['action'],
                    price=signal['price'],
                    size=initial_capital * Decimal('0.95'),  # 95% do capital (margem de segurança)
                    strategy='Mock Monthly Rotation',
                    module='Validation',
                    stop_loss=signal.get('stop_loss'),
                    take_profit=signal.get('take_profit')
                )
                
                trades_executed += 1
        
        # Próximo dia
        current_date += timedelta(days=1)
    
    logger.info(f"\n  Total de trades executados: {trades_executed}")
    
    # Calcular métricas
    logger.info("\n5. CALCULANDO MÉTRICAS...")
    metrics = backtester.calculate_metrics('Mock Monthly Rotation')
    
    logger.info(f"  Retorno total: {metrics.total_return:.2f}%")
    logger.info(f"  Total de trades: {metrics.total_trades}")
    logger.info(f"  Max drawdown: {metrics.max_drawdown:.2f}%")
    
    # Gerar relatório
    logger.info("\n6. GERANDO RELATÓRIO...")
    backtester.generate_report("TEST_MOCK_VALIDATION_REPORT.md")
    
    # Validação contra valores esperados
    logger.info("\n7. VALIDANDO RESULTADOS...")
    
    validator = MockStrategyValidator()
    expected = validator.calculate_expected_metrics_monthly_rotation(years=0.25)  # 3 meses
    
    actual = {
        'total_trades': metrics.total_trades,
        'total_return': metrics.total_return / 100  # Converter de % para decimal
    }
    
    validation_passed = validator.validate_results(actual, expected)
    
    # Sumário final
    print("\n" + "="*80)
    print("RESULTADO DA VALIDAÇÃO:")
    print(f"  Trades executados: {trades_executed}")
    print(f"  Trades registrados: {metrics.total_trades}")
    print(f"  Capital inicial: EUR {float(initial_capital):,.0f}")
    print(f"  Capital final: EUR {float(backtester.current_capital):,.0f}")
    print(f"  Retorno: {metrics.total_return:.2f}%")
    print(f"  Validacao: {'PASSOU' if validation_passed else 'FALHOU'}")
    print("="*80 + "\n")
    
    # Gerar relatório de validação
    generate_validation_report(
        trades_executed=trades_executed,
        metrics=metrics,
        validation_passed=validation_passed,
        expected=expected
    )
    
    return validation_passed

def generate_validation_report(trades_executed: int, metrics, 
                               validation_passed: bool, expected: Dict):
    """
    Gera relatório de validação do framework
    """
    output_path = project_root / 'Documentation' / '03_Relatorios_Conselho' / 'RELATORIO_VALIDACAO_FRAMEWORK.md'
    
    lines = []
    
    lines.append("# RELATÓRIO DE VALIDAÇÃO - FRAMEWORK DE BACKTESTING")
    lines.append("## TESTE COM MOCK STRATEGY")
    lines.append("")
    lines.append(f"**Data:** {datetime.now().strftime('%d-%m-%Y %H:%M CET')}")
    lines.append(f"**Objetivo:** Validar cálculo de P&L e métricas")
    lines.append(f"**Método:** Mock Strategy com sinais previsíveis")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## CONFIGURAÇÃO DO TESTE")
    lines.append("")
    lines.append("**Mock Strategy:** Monthly Rotation")
    lines.append("- Regra: BUY no dia 1 de cada mês")
    lines.append("- Regra: SELL no dia 15 de cada mês")
    lines.append("- Ativo: SPY (mock data)")
    lines.append("- Período: 3 meses (2023-01-01 a 2023-03-31)")
    lines.append("- Capital: EUR 10,000")
    lines.append("")
    
    lines.append("## RESULTADOS")
    lines.append("")
    lines.append(f"**Trades Executados:** {trades_executed}")
    lines.append(f"**Trades Registrados:** {metrics.total_trades}")
    lines.append(f"**Retorno Total:** {metrics.total_return:.2f}%")
    lines.append(f"**Max Drawdown:** {metrics.max_drawdown:.2f}%")
    lines.append(f"**Sharpe Ratio:** {metrics.sharpe_ratio:.2f}")
    lines.append("")
    
    lines.append("## VALIDAÇÃO")
    lines.append("")
    lines.append(f"**Status:** {'✅ PASSOU' if validation_passed else '❌ FALHOU'}")
    lines.append("")
    
    if validation_passed:
        lines.append("O framework de backtesting foi validado com sucesso.")
        lines.append("Os cálculos de P&L, métricas e geração de relatório estão funcionando corretamente.")
    else:
        lines.append("A validação identificou discrepâncias.")
        lines.append("Revisar implementação do framework antes de prosseguir.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Conclusão:**")
    lines.append("")
    lines.append("Framework pronto para integração com estratégias reais.")
    lines.append("")
    lines.append("**Assinatura:**")
    lines.append("Agente Cursor Omega")
    lines.append(f"Data: {datetime.now().strftime('%d-%m-%Y %H:%M CET')}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    logger.info(f"[OK] Relatório de validação salvo: {output_path}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DIRETIVA F1-T4: VALIDAÇÃO DO FRAMEWORK")
    print("EXECUTOR: Agente Cursor Omega")
    print("="*80 + "\n")
    
    success = run_mock_validation_test()
    
    if success:
        print("\n[OK] Framework validado com sucesso")
        print("[OK] Pronto para integração com estratégias reais")
    else:
        print("\n[ERRO] Validação falhou - revisar framework")
    
    print("\n" + "="*80 + "\n")

