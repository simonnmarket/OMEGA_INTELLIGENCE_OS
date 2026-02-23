# -*- coding: utf-8 -*-
"""
SCRIPT DE EXECUÇÃO DE BACKTESTS - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO
DATA: 2025-01-27
FUNÇÃO: Executar backtests de todas as estratégias e gerar relatório consolidado
"""

import asyncio
import logging
from decimal import Decimal
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
    GoldQuantumPerfectionV3,
    CryptoQuantumMeanReversionV3
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def run_all_backtests():
    """Executa backtests de todas as estratégias principais"""
    
    logging.info("\n" + "="*100)
    logging.info("🚀 SAMSUNG GLOBAL MARKET - BATERIA DE BACKTESTS")
    logging.info("="*100 + "\n")
    
    # Inicializar engines compartilhados
    hale_engine = HaleIntentionalityEngine()
    petrov_engine = PetrovEntanglementEngine()
    rossi_engine = RossiDynamicKellyEngine()
    tanaka_engine = TanakaKalmanEngine()
    leblanc_engine = LeblancZKPEngine()
    market_masters = MarketMastersPerfectionEngine()
    
    # Inicializar backtester
    backtester = Backtester()
    
    # Configurações de teste para cada estratégia
    test_configs = [
        {
            'name': 'Oil Strategy Proven V3',
            'strategy': OilStrategyProvenV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'OIL_WTI',
            'days': 252,
            'start_price': 70.0,
            'trend': 0.0005,  # Leve tendência de alta
            'volatility': 0.025
        },
        {
            'name': 'Golden Strategy Futures V3',
            'strategy': GoldenStrategyFuturesV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'ES_FUTURES',
            'days': 252,
            'start_price': 4500.0,
            'trend': 0.0003,
            'volatility': 0.015
        },
        {
            'name': 'Cross Currency Arbitrage V3',
            'strategy': CrossCurrencyArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'EUR_USD',
            'days': 252,
            'start_price': 1.0855,
            'trend': 0.0001,
            'volatility': 0.008
        },
        {
            'name': 'Crypto Triangular Arbitrage V3',
            'strategy': CryptoTriangularArbitrageV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'BTC_ARBITRAGE',
            'days': 252,
            'start_price': 43000.0,
            'trend': 0.002,
            'volatility': 0.04
        },
        {
            'name': 'Gold Quantum Perfection V3',
            'strategy': GoldQuantumPerfectionV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters),
            'symbol': 'XAU_USD',
            'days': 252,
            'start_price': 1950.0,
            'trend': 0.0008,
            'volatility': 0.012
        },
        {
            'name': 'Crypto Mean Reversion BTC V3',
            'strategy': CryptoQuantumMeanReversionV3(hale_engine, rossi_engine, tanaka_engine, leblanc_engine, market_masters, "BTC/USD"),
            'symbol': 'BTC_USD',
            'days': 252,
            'start_price': 43000.0,
            'trend': 0.001,
            'volatility': 0.035
        }
    ]
    
    # Executar backtests sequencialmente
    results = []
    for idx, config in enumerate(test_configs, 1):
        logging.info(f"\n{'='*100}")
        logging.info(f"🎯 TESTE {idx}/{len(test_configs)}: {config['name']}")
        logging.info(f"{'='*100}\n")
        
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
            
            results.append(result)
            
            # Aguardar um pouco entre testes
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logging.error(f"❌ Erro no backtest de {config['name']}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Gerar relatório consolidado
    logging.info("\n" + "="*100)
    logging.info("📊 GERANDO RELATÓRIO CONSOLIDADO")
    logging.info("="*100 + "\n")
    
    backtester.generate_consolidated_report()
    
    # Salvar resultados em arquivo
    save_results_to_file(results)
    
    logging.info("\n✅ BATERIA DE BACKTESTS CONCLUÍDA COM SUCESSO!\n")
    
    return results

def save_results_to_file(results):
    """Salva resultados em arquivo de texto"""
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backtest_results_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("SAMSUNG GLOBAL MARKET - RESULTADOS DE BACKTESTING\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")
        
        for r in results:
            f.write(f"\nEstratégia: {r['strategy_id']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Capital Inicial:    ${r['initial_capital']:,.2f}\n")
            f.write(f"Capital Final:      ${r['final_capital']:,.2f}\n")
            f.write(f"Retorno Total:      {r['total_return_pct']:.2f}%\n")
            f.write(f"Sharpe Ratio:       {r['sharpe_ratio']:.2f}\n")
            f.write(f"Max Drawdown:       {r['max_drawdown_pct']:.2f}%\n")
            f.write(f"Win Rate:           {r['win_rate_pct']:.2f}%\n")
            f.write(f"Total Trades:       {r['total_trades']}\n")
            f.write(f"Profit Factor:      {r['profit_factor']:.2f}\n")
            f.write("\n")
    
    logging.info(f"💾 Resultados salvos em: {filename}")

if __name__ == "__main__":
    asyncio.run(run_all_backtests())

