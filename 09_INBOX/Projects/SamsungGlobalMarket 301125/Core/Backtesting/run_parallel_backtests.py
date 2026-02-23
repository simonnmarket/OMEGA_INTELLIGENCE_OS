# -*- coding: utf-8 -*-
"""
BACKTESTING HOLÍSTICO DO PORTFÓLIO COMPLETO - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO TIER-0
DATA: 2025-01-27
FUNÇÃO: Validação paralela de todas as 12 estratégias + análise de correlação
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime
from backtesting_engine import Backtester
from NumeiaTradingSystem_v3_0_FINAL import (
    HaleIntentionalityEngine,
    PetrovEntanglementEngine,
    RossiDynamicKellyEngine,
    TanakaKalmanEngine,
    LeblancZKPEngine,
    MarketMastersPerfectionEngine,
    OilStrategyProvenV3,
    GoldenStrategyFuturesV3,
    CrossCurrencyArbitrageV3,
    CryptoTriangularArbitrageV3,
    EquitiesDefenseTechPairsV3,
    EquitiesSectorRotationV3,
    EquitiesVolatilityArbitrageV3,
    ForexCentralBankSentimentV3,
    ForexLiquidityMiningV3,
    TermStructureArbitrageV3,
    GoldQuantumPerfectionV3,
    CryptoQuantumMeanReversionV3
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PortfolioAnalyzer:
    """Analisador holístico de portfólio de estratégias"""
    
    def __init__(self):
        self.results = []
        self.equity_curves = {}
        
    def calculate_portfolio_metrics(self, results_dict):
        """Calcula métricas agregadas do portfólio"""
        
        # Criar matriz de retornos
        returns_matrix = []
        strategy_names = []
        
        for strategy_id, result in results_dict.items():
            if result['total_trades'] > 0:
                equity_curve = result['equity_curve']
                returns = pd.Series(equity_curve).pct_change().dropna()
                returns_matrix.append(returns.values)
                strategy_names.append(strategy_id)
        
        if len(returns_matrix) == 0:
            logging.warning("⚠️ Nenhuma estratégia gerou trades - impossível calcular correlações")
            return None
        
        # Calcular correlação entre estratégias
        returns_df = pd.DataFrame(returns_matrix).T
        returns_df.columns = strategy_names
        correlation_matrix = returns_df.corr()
        
        # Simular portfólio igualmente ponderado
        portfolio_returns = returns_df.mean(axis=1)
        
        # Métricas do portfólio
        portfolio_sharpe = (portfolio_returns.mean() * 252 - 0.02) / (portfolio_returns.std() * np.sqrt(252))
        portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Drawdown do portfólio
        portfolio_equity = (1 + portfolio_returns).cumprod()
        portfolio_dd = (portfolio_equity / portfolio_equity.expanding().max() - 1).min()
        
        return {
            'correlation_matrix': correlation_matrix,
            'portfolio_sharpe': portfolio_sharpe,
            'portfolio_volatility': portfolio_volatility,
            'portfolio_max_dd': portfolio_dd,
            'diversification_benefit': self._calculate_diversification_benefit(returns_df)
        }
    
    def _calculate_diversification_benefit(self, returns_df):
        """Calcula o benefício da diversificação"""
        # Volatilidade média das estratégias individuais
        individual_vols = returns_df.std() * np.sqrt(252)
        avg_individual_vol = individual_vols.mean()
        
        # Volatilidade do portfólio
        portfolio_vol = returns_df.mean(axis=1).std() * np.sqrt(252)
        
        # Benefício (redução de volatilidade em %)
        benefit = (1 - portfolio_vol / avg_individual_vol) * 100
        
        return benefit

async def run_comprehensive_backtest():
    """Executa backtest holístico de todas as 12 estratégias"""
    
    logging.info("\n" + "="*120)
    logging.info("🌐 SAMSUNG GLOBAL MARKET - BACKTESTING HOLÍSTICO DO PORTFÓLIO COMPLETO")
    logging.info("="*120 + "\n")
    
    # Inicializar engines compartilhados
    hale_engine = HaleIntentionalityEngine()
    petrov_engine = PetrovEntanglementEngine()
    rossi_engine = RossiDynamicKellyEngine()
    tanaka_engine = TanakaKalmanEngine()
    leblanc_engine = LeblancZKPEngine()
    market_masters = MarketMastersPerfectionEngine()
    
    # Inicializar backtester
    backtester = Backtester()
    analyzer = PortfolioAnalyzer()
    
    # Configurações completas das 12 estratégias
    test_configs = [
        # Commodities
        {
            'name': 'Oil Strategy Proven V3',
            'category': 'Commodities',
            'strategy': OilStrategyProvenV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'OIL_WTI',
            'days': 252,
            'start_price': 70.0,
            'trend': 0.0005,
            'volatility': 0.025
        },
        {
            'name': 'Gold Quantum Perfection V3',
            'category': 'Commodities',
            'strategy': GoldQuantumPerfectionV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'XAU_USD',
            'days': 252,
            'start_price': 1950.0,
            'trend': 0.0008,
            'volatility': 0.012
        },
        
        # Futuros
        {
            'name': 'Golden Strategy Futures V3',
            'category': 'Futuros',
            'strategy': GoldenStrategyFuturesV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'ES_FUTURES',
            'days': 252,
            'start_price': 4500.0,
            'trend': 0.0003,
            'volatility': 0.015
        },
        {
            'name': 'Term Structure Arbitrage V3',
            'category': 'Futuros',
            'strategy': TermStructureArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'CL_CALENDAR',
            'days': 252,
            'start_price': 75.0,
            'trend': 0.0002,
            'volatility': 0.02
        },
        
        # Forex
        {
            'name': 'Cross Currency Arbitrage V3',
            'category': 'Forex',
            'strategy': CrossCurrencyArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'EUR_USD',
            'days': 252,
            'start_price': 1.0855,
            'trend': 0.0001,
            'volatility': 0.008
        },
        {
            'name': 'Forex Central Bank Sentiment V3',
            'category': 'Forex',
            'strategy': ForexCentralBankSentimentV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'USD_JPY',
            'days': 252,
            'start_price': 145.0,
            'trend': -0.0001,
            'volatility': 0.009
        },
        {
            'name': 'Forex Liquidity Mining V3',
            'category': 'Forex',
            'strategy': ForexLiquidityMiningV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'GBP_USD',
            'days': 252,
            'start_price': 1.2655,
            'trend': 0.0002,
            'volatility': 0.01
        },
        
        # Crypto
        {
            'name': 'Crypto Triangular Arbitrage V3',
            'category': 'Crypto',
            'strategy': CryptoTriangularArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'BTC_ARBITRAGE',
            'days': 252,
            'start_price': 43000.0,
            'trend': 0.002,
            'volatility': 0.04
        },
        {
            'name': 'Crypto Mean Reversion BTC V3',
            'category': 'Crypto',
            'strategy': CryptoQuantumMeanReversionV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters, "BTC/USD"),
            'symbol': 'BTC_USD',
            'days': 252,
            'start_price': 43000.0,
            'trend': 0.001,
            'volatility': 0.035
        },
        
        # Equities
        {
            'name': 'Equities Defense Tech Pairs V3',
            'category': 'Equities',
            'strategy': EquitiesDefenseTechPairsV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'PAIR_LMT_AAPL',
            'days': 252,
            'start_price': 2.5,
            'trend': 0.0001,
            'volatility': 0.015
        },
        {
            'name': 'Equities Sector Rotation V3',
            'category': 'Equities',
            'strategy': EquitiesSectorRotationV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'SECTOR_XLK',
            'days': 252,
            'start_price': 195.50,
            'trend': 0.0004,
            'volatility': 0.018
        },
        {
            'name': 'Equities Volatility Arbitrage V3',
            'category': 'Equities',
            'strategy': EquitiesVolatilityArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'VOL_AAPL',
            'days': 252,
            'start_price': 35.0,
            'trend': -0.0002,
            'volatility': 0.25
        }
    ]
    
    # Executar backtests
    results_dict = {}
    
    for idx, config in enumerate(test_configs, 1):
        logging.info(f"\n{'='*120}")
        logging.info(f"🎯 TESTE {idx}/12: {config['name']} ({config['category']})")
        logging.info(f"{'='*120}\n")
        
        try:
            # Gerar dados históricos
            data = backtester.generate_historical_data(
                symbol=config['symbol'],
                days=config['days'],
                start_price=config['start_price'],
                trend=config['trend'],
                volatility=config['volatility']
            )
            
            # Executar backtest
            result = await backtester.run_backtest(
                strategy=config['strategy'],
                data=data,
                initial_capital=100000.0
            )
            
            result['category'] = config['category']
            result['name'] = config['name']
            results_dict[result['strategy_id']] = result
            
            # Aguardar um pouco entre testes
            await asyncio.sleep(0.3)
            
        except Exception as e:
            logging.error(f"❌ Erro no backtest de {config['name']}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Gerar análise holística
    logging.info("\n" + "="*120)
    logging.info("📊 ANÁLISE HOLÍSTICA DO PORTFÓLIO COMPLETO")
    logging.info("="*120 + "\n")
    
    generate_comprehensive_report(results_dict, analyzer)
    
    # Salvar resultados
    save_comprehensive_results(results_dict, analyzer)
    
    logging.info("\n✅ BACKTESTING HOLÍSTICO CONCLUÍDO COM SUCESSO!\n")
    
    return results_dict

def generate_comprehensive_report(results_dict, analyzer):
    """Gera relatório holístico completo"""
    
    # Ordenar por Sharpe Ratio
    sorted_results = sorted(
        results_dict.items(),
        key=lambda x: x[1]['sharpe_ratio'],
        reverse=True
    )
    
    # SEÇÃO 1: RANKING GERAL
    logging.info("=" * 120)
    logging.info("🏆 RANKING GERAL POR SHARPE RATIO")
    logging.info("=" * 120 + "\n")
    
    print(f"{'Pos':<5} {'Estratégia':<40} {'Categoria':<15} {'Sharpe':<10} {'Retorno':<12} {'Max DD':<12} {'Trades':<8}")
    print("-" * 120)
    
    for idx, (strategy_id, result) in enumerate(sorted_results, 1):
        pos_marker = "[1]" if idx == 1 else "[2]" if idx == 2 else "[3]" if idx == 3 else f"[{idx}]"
        print(f"{pos_marker:<5} {result['name']:<40} {result['category']:<15} "
              f"{result['sharpe_ratio']:<10.2f} {result['total_return_pct']:<12.2f}% "
              f"{result['max_drawdown_pct']:<12.2f}% {result['total_trades']:<8}")
    
    print("\n")
    
    # SEÇÃO 2: ANÁLISE POR CATEGORIA
    logging.info("=" * 120)
    logging.info("📊 ANÁLISE POR CATEGORIA DE ATIVOS")
    logging.info("=" * 120 + "\n")
    
    categories = {}
    for strategy_id, result in results_dict.items():
        category = result['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(result)
    
    for category, results in categories.items():
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_return = np.mean([r['total_return_pct'] for r in results])
        total_trades = sum([r['total_trades'] for r in results])
        
        logging.info(f"📁 {category}:")
        logging.info(f"   - Estratégias: {len(results)}")
        logging.info(f"   - Sharpe Médio: {avg_sharpe:.2f}")
        logging.info(f"   - Retorno Médio: {avg_return:.2f}%")
        logging.info(f"   - Total de Trades: {total_trades}\n")
    
    # SEÇÃO 3: ESTATÍSTICAS AGREGADAS
    logging.info("=" * 120)
    logging.info("📈 ESTATÍSTICAS AGREGADAS DO PORTFÓLIO")
    logging.info("=" * 120 + "\n")
    
    total_strategies = len(results_dict)
    active_strategies = sum(1 for r in results_dict.values() if r['total_trades'] > 0)
    total_trades = sum(r['total_trades'] for r in results_dict.values())
    avg_sharpe = np.mean([r['sharpe_ratio'] for r in results_dict.values()])
    avg_return = np.mean([r['total_return_pct'] for r in results_dict.values()])
    
    logging.info(f"Total de Estratégias Testadas:     {total_strategies}")
    logging.info(f"Estratégias que Geraram Trades:    {active_strategies} ({active_strategies/total_strategies*100:.1f}%)")
    logging.info(f"Total de Trades Executados:        {total_trades}")
    logging.info(f"Sharpe Ratio Médio:                {avg_sharpe:.2f}")
    logging.info(f"Retorno Médio:                     {avg_return:.2f}%\n")
    
    # SEÇÃO 4: ANÁLISE DE CORRELAÇÃO
    portfolio_metrics = analyzer.calculate_portfolio_metrics(results_dict)
    
    if portfolio_metrics:
        logging.info("=" * 120)
        logging.info("🔗 ANÁLISE DE CORRELAÇÃO ENTRE ESTRATÉGIAS")
        logging.info("=" * 120 + "\n")
        
        corr_matrix = portfolio_metrics['correlation_matrix']
        
        logging.info("Matriz de Correlação (estratégias ativas):")
        print(corr_matrix.to_string())
        
        logging.info(f"\n📊 MÉTRICAS DO PORTFÓLIO IGUALMENTE PONDERADO:")
        logging.info(f"   - Sharpe do Portfólio:          {portfolio_metrics['portfolio_sharpe']:.2f}")
        logging.info(f"   - Volatilidade do Portfólio:    {portfolio_metrics['portfolio_volatility']*100:.2f}%")
        logging.info(f"   - Max Drawdown do Portfólio:    {portfolio_metrics['portfolio_max_dd']*100:.2f}%")
        logging.info(f"   - Benefício da Diversificação:  {portfolio_metrics['diversification_benefit']:.2f}%\n")
    
    # SEÇÃO 5: RECOMENDAÇÕES ESTRATÉGICAS
    logging.info("=" * 120)
    logging.info("🎯 RECOMENDAÇÕES ESTRATÉGICAS DE ALOCAÇÃO")
    logging.info("=" * 120 + "\n")
    
    # Identificar as 3 melhores
    top_3 = sorted_results[:3]
    
    logging.info("Com base na análise holística, recomendamos a seguinte alocação de capital:\n")
    
    for idx, (strategy_id, result) in enumerate(top_3, 1):
        allocation = [40, 30, 20][idx-1] if idx <= 3 else 0
        logging.info(f"{idx}. {result['name']}")
        logging.info(f"   - Alocação Recomendada: {allocation}%")
        logging.info(f"   - Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        logging.info(f"   - Retorno: {result['total_return_pct']:.2f}%")
        logging.info(f"   - Max Drawdown: {result['max_drawdown_pct']:.2f}%")
        logging.info(f"   - Justificativa: {'Melhor perfil risco/retorno' if idx==1 else 'Diversificação'}\n")
    
    logging.info("   - 10% restantes: Manter em reserva/liquidez\n")
    
    # SEÇÃO 6: CONCLUSÃO ESTRATÉGICA
    best_strategy = sorted_results[0][1]
    
    logging.info("=" * 120)
    logging.info("🏁 CONCLUSÃO ESTRATÉGICA")
    logging.info("=" * 120 + "\n")
    
    logging.info(f"✅ A estratégia **{best_strategy['name']}** apresenta o melhor perfil de risco ajustado.")
    logging.info(f"✅ Sharpe Ratio: {best_strategy['sharpe_ratio']:.2f}")
    logging.info(f"✅ Retorno: {best_strategy['total_return_pct']:.2f}%")
    logging.info(f"✅ Max Drawdown: {best_strategy['max_drawdown_pct']:.2f}%\n")
    
    if active_strategies >= 3:
        logging.info("✅ O portfólio demonstra diversificação adequada com múltiplas estratégias ativas.")
    else:
        logging.info("⚠️ ALERTA: Baixa diversificação. Apenas {active_strategies} estratégias geraram trades.")
        logging.info("⚠️ RECOMENDAÇÃO: Ajustar parâmetros para aumentar frequência de sinais.\n")
    
    if portfolio_metrics and portfolio_metrics['diversification_benefit'] > 20:
        logging.info(f"✅ Benefício significativo da diversificação: {portfolio_metrics['diversification_benefit']:.1f}% de redução de volatilidade.")
    
    logging.info("\n" + "=" * 120 + "\n")

def save_comprehensive_results(results_dict, analyzer):
    """Salva resultados em arquivo detalhado"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"portfolio_analysis_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("SAMSUNG GLOBAL MARKET - ANÁLISE HOLÍSTICA DE PORTFÓLIO\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 120 + "\n\n")
        
        # Ranking
        sorted_results = sorted(
            results_dict.items(),
            key=lambda x: x[1]['sharpe_ratio'],
            reverse=True
        )
        
        f.write("RANKING COMPLETO (12 ESTRATÉGIAS):\n")
        f.write("-" * 120 + "\n")
        
        for idx, (strategy_id, result) in enumerate(sorted_results, 1):
            f.write(f"\n{idx}. {result['name']} ({result['category']})\n")
            f.write(f"   Capital Final:     ${result['final_capital']:,.2f}\n")
            f.write(f"   Retorno:           {result['total_return_pct']:.2f}%\n")
            f.write(f"   Sharpe Ratio:      {result['sharpe_ratio']:.2f}\n")
            f.write(f"   Sortino Ratio:     {result['sortino_ratio']:.2f}\n")
            f.write(f"   Max Drawdown:      {result['max_drawdown_pct']:.2f}%\n")
            f.write(f"   Win Rate:          {result['win_rate_pct']:.2f}%\n")
            f.write(f"   Total Trades:      {result['total_trades']}\n")
            f.write(f"   Profit Factor:     {result['profit_factor']:.2f}\n")
    
    logging.info(f"💾 Análise completa salva em: {filename}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_backtest())

