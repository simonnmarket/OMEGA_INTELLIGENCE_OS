# -*- coding: utf-8 -*-
"""
NUMEIA TRADING SYSTEM v3.1 - BACKTEST CRYPTO MOMENTUM
DIRETIVA: F2-T2-PARALLEL (TRILHA B)
DATA: 04-11-2025 00:00 CET

FUNCIONALIDADE:
- Backtest da estratégia Crypto Momentum com lógica real
- Retornos 3M/6M/12M + Filtro de Volume
- Período: 2018-2023 (mesmo que Mean Reversion para comparação)
- Análise por regime + Teste estatístico

COMPLIANCE: PROTOCOLO BLINDADO 100%
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Dict
import logging

# Adicionar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core' / 'Backtesting'))
sys.path.insert(0, str(project_root / 'Core' / 'Strategies' / 'Crypto'))

from backtesting_engine import Backtester, PerformanceMetrics
from CryptoMomentumStrategy_Backtest import CryptoMomentumBacktest
import yfinance as yf
import pandas as pd
from scipy.stats import binomtest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_crypto_momentum_backtest():
    """
    Executa backtest completo da estratégia Crypto Momentum
    """
    print("=" * 80)
    print("NUMEIA TRADING SYSTEM v3.1 - BACKTEST CRYPTO MOMENTUM")
    print("=" * 80)
    print()
    
    # Parâmetros - MESMOS QUE MEAN REVERSION PARA COMPARAÇÃO
    START_DATE = '2018-01-01'
    END_DATE = '2023-12-31'
    CAPITAL = Decimal('30000')
    TRANSACTION_COST = 10
    
    # Mesmos 7 símbolos
    CRYPTO_SYMBOLS = [
        'BTC-USD', 'ETH-USD', 'BNB-USD', 'LTC-USD',
        'ADA-USD', 'XRP-USD', 'SOL-USD'
    ]
    
    logging.info(f"Período: {START_DATE} a {END_DATE}")
    logging.info(f"Capital: EUR {float(CAPITAL):,.0f}")
    logging.info(f"Símbolos: {CRYPTO_SYMBOLS}")
    logging.info(f"Custos: {TRANSACTION_COST} bps")
    print()
    
    # Inicializar estratégia
    strategy = CryptoMomentumBacktest(
        momentum_periods=[90, 180, 365],  # 3M, 6M, 12M
        volume_ma_period=20,
        min_momentum_threshold=0.10,  # 10% return
        exit_threshold=0.00
    )
    
    # Inicializar backtester
    backtester = Backtester(
        initial_capital=CAPITAL,
        transaction_cost_bps=TRANSACTION_COST,
        start_date=START_DATE,
        end_date=END_DATE
    )
    
    # Carregar dados e gerar sinais
    all_signals = {}
    
    for symbol in CRYPTO_SYMBOLS:
        logging.info(f"Processando {symbol}...")
        
        try:
            data_df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
            
            if data_df.empty:
                logging.warning(f"  Sem dados para {symbol}")
                continue
            
            signals_df = strategy.generate_signals(data_df, symbol)
            all_signals[symbol] = signals_df
            
            logging.info(f"  OK: {len(signals_df)} dias processados")
        
        except Exception as e:
            logging.warning(f"  Erro ao processar {symbol}: {e}")
            continue
    
    # Executar backtest
    logging.info("\nIniciando simulacao...")
    
    all_dates = set()
    for signals_df in all_signals.values():
        all_dates.update(signals_df.index)
    trading_days = sorted(list(all_dates))
    
    for date in trading_days:
        current_prices = {}
        
        for symbol in CRYPTO_SYMBOLS:
            if symbol in all_signals:
                signals_df = all_signals[symbol]
                if date in signals_df.index:
                    current_prices[symbol] = float(signals_df.loc[date, 'Close'])
        
        backtester.current_prices = current_prices
        
        for symbol in CRYPTO_SYMBOLS:
            if symbol not in all_signals:
                continue
            
            signals_df = all_signals[symbol]
            
            if date not in signals_df.index:
                continue
            
            signal = strategy.get_signal_for_date(signals_df, date, symbol)
            
            if signal['action'] == 'HOLD':
                continue
            
            position_size = Decimal(str(float(CAPITAL) * 0.10 * signal['confidence']))
            
            if signal['action'] == 'BUY':
                if symbol not in [p.symbol for p in backtester.positions.values()]:
                    price = current_prices.get(symbol)
                    if price:
                        backtester.execute_trade(
                            timestamp=date,
                            symbol=symbol,
                            action='BUY',
                            price=price,
                            size=position_size,
                            strategy='Crypto Momentum',
                            module='Crypto',
                            stop_loss=None,
                            take_profit=None
                        )
            
            elif signal['action'] == 'SELL':
                for pos_key, position in list(backtester.positions.items()):
                    if position.symbol == symbol:
                        price = current_prices.get(symbol)
                        if price:
                            backtester.close_position(date, pos_key, price, 'Signal: Momentum ended')
    
    # Calcular métricas
    performance = backtester.calculate_metrics('Crypto Momentum')
    
    metrics = {
        'final_capital': backtester.current_capital,
        'total_return': performance.total_return,
        'annualized_return': performance.annualized_return,
        'total_trades': performance.total_trades,
        'winning_trades': performance.winning_trades,
        'losing_trades': performance.losing_trades,
        'win_rate': performance.win_rate,
        'sharpe_ratio': performance.sharpe_ratio,
        'max_drawdown': performance.max_drawdown,
        'profit_factor': performance.profit_factor,
        'avg_win': performance.avg_win,
        'avg_loss': performance.avg_loss
    }
    
    # Exibir resultados
    print("\n" + "=" * 80)
    print("RESULTADOS DO BACKTEST - MOMENTUM")
    print("=" * 80)
    print(f"\nCapital Inicial: EUR {float(CAPITAL):,.2f}")
    print(f"Capital Final: EUR {float(metrics['final_capital']):,.2f}")
    print(f"Retorno Total: {metrics['total_return']:.2f}%")
    print(f"Retorno Anualizado: {metrics['annualized_return']:.2f}%")
    print(f"\nTotal de Trades: {metrics['total_trades']}")
    print(f"Trades Vencedores: {metrics['winning_trades']}")
    print(f"Trades Perdedores: {metrics['losing_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.2f}%")
    print(f"\nSharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Maximo Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print("=" * 80)
    
    # Análise por regime
    print("\n" + "=" * 80)
    print("ANALISE DE REGIME (ANO A ANO)")
    print("=" * 80)
    
    regime_analysis = analyze_by_regime(backtester, START_DATE, END_DATE)
    
    # Teste estatístico
    print("\n" + "=" * 80)
    print("TESTE DE HIPOTESE ESTATISTICA")
    print("=" * 80)
    
    statistical_test = perform_binomial_test(metrics)
    
    # Gerar relatório
    generate_momentum_report(metrics, regime_analysis, statistical_test, CAPITAL, CRYPTO_SYMBOLS, START_DATE, END_DATE)
    
    return metrics, regime_analysis, statistical_test


def analyze_by_regime(backtester, start_date: str, end_date: str) -> Dict:
    """Analisa performance por regime (ano a ano)"""
    regime_data = {}
    
    for year in range(int(start_date[:4]), int(end_date[:4]) + 1):
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")
        
        year_trades = [t for t in backtester.trades_history 
                      if t.action == 'CLOSE' and year_start <= t.timestamp <= year_end]
        
        if len(year_trades) == 0:
            regime_data[year] = {
                'trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0.0, 'total_pnl': 0.0
            }
            continue
        
        wins = sum(1 for t in year_trades if hasattr(t, 'pnl') and t.pnl > 0.01)
        losses = sum(1 for t in year_trades if hasattr(t, 'pnl') and t.pnl < -0.01)
        total_pnl = sum(t.pnl for t in year_trades if hasattr(t, 'pnl'))
        
        regime_data[year] = {
            'trades': len(year_trades),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0,
            'total_pnl': total_pnl
        }
        
        print(f"\n{year}:")
        print(f"  Trades: {len(year_trades)}")
        print(f"  Wins/Losses: {wins}/{losses}")
        print(f"  Win Rate: {regime_data[year]['win_rate']:.2f}%")
        print(f"  P&L: EUR {total_pnl:,.2f}")
    
    return regime_data


def perform_binomial_test(metrics: Dict) -> Dict:
    """Executa teste binomial"""
    n_trades = metrics['winning_trades'] + metrics['losing_trades']
    n_wins = metrics['winning_trades']
    win_rate = metrics['win_rate'] / 100
    
    result = binomtest(n_wins, n_trades, 0.5, alternative='greater')
    p_value = result.pvalue
    is_significant = p_value < 0.05
    
    print(f"\nTeste Binomial:")
    print(f"  H0: Win Rate = 50% (sem edge)")
    print(f"  H1: Win Rate > 50% (com edge)")
    print(f"  n = {n_trades} trades")
    print(f"  wins = {n_wins}")
    print(f"  Win Rate observado = {win_rate*100:.2f}%")
    print(f"  p-value = {p_value:.6f}")
    print(f"  Significancia (alpha=0.05): {'SIM' if is_significant else 'NAO'}")
    
    if is_significant:
        print(f"\n  [OK] CONCLUSAO: Edge estatisticamente significativo (p < 0.05)")
    else:
        print(f"\n  [FAIL] CONCLUSAO: Edge NAO estatisticamente significativo (p >= 0.05)")
    
    from scipy.stats import binom
    ci_lower = binom.ppf(0.025, n_trades, win_rate) / n_trades if n_trades > 0 else 0
    ci_upper = binom.ppf(0.975, n_trades, win_rate) / n_trades if n_trades > 0 else 0
    
    print(f"  Intervalo de Confianca 95%: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]")
    
    return {
        'n_trades': n_trades,
        'n_wins': n_wins,
        'win_rate': win_rate * 100,
        'p_value': p_value,
        'is_significant': is_significant,
        'alpha': 0.05,
        'ci_95_lower': ci_lower * 100,
        'ci_95_upper': ci_upper * 100
    }


def generate_momentum_report(metrics: Dict, regime_analysis: Dict, statistical_test: Dict,
                             capital: Decimal, symbols: list, start_date: str, end_date: str):
    """Gerar relatório MD para Momentum"""
    report_path = Path(__file__).parent.parent.parent / 'Documentation' / '03_Relatorios_Conselho' / 'RELATORIO_MOMENTUM_STRATEGY_ANALYSIS.md'
    
    years = int(end_date[:4]) - int(start_date[:4]) + 1
    
    regime_section = ""
    for year in sorted(regime_analysis.keys()):
        data = regime_analysis[year]
        regime_section += f"""
### {year}
```
Trades: {data['trades']}
Wins/Losses: {data['wins']}/{data['losses']}
Win Rate: {data['win_rate']:.2f}%
P&L: EUR {data['total_pnl']:,.2f}
```
"""
    
    content = f"""# RELATÓRIO MOMENTUM STRATEGY ANALYSIS
## DIRETIVA F2-T2-PARALLEL (TRILHA B): ESTRATÉGIA #2

**Data do Relatório:** {datetime.now().strftime('%d-%m-%Y %H:%M CET')}  
**Período Testado:** {start_date} a {end_date} ({years} anos)  
**Capital Inicial:** EUR {float(capital):,.2f}  
**Estratégia:** Crypto Momentum (Jegadeesh & Titman 1993)

---

## 📊 RESULTADOS FINANCEIROS

### Performance Geral
```
Capital Inicial:      EUR {float(capital):>12,.2f}
Capital Final:        EUR {float(metrics['final_capital']):>12,.2f}
P&L Líquido:          EUR {float(metrics['final_capital'] - capital):>12,.2f}
Retorno Total:        {metrics['total_return']:>15.2f}%
Retorno Anualizado:   {metrics['annualized_return']:>15.2f}%
```

### Métricas de Trading
```
Total de Trades:      {metrics['total_trades']:>15}
Trades Vencedores:    {metrics['winning_trades']:>15}
Trades Perdedores:    {metrics['losing_trades']:>15}
Win Rate:             {metrics['win_rate']:>15.2f}%
Average Win:          EUR {metrics['avg_win']:>12.2f}
Average Loss:         EUR {metrics['avg_loss']:>12.2f}
```

### Métricas de Risco
```
Sharpe Ratio:         {metrics['sharpe_ratio']:>15.2f}
Máximo Drawdown:      {metrics['max_drawdown']:>15.2f}%
Profit Factor:        {metrics['profit_factor']:>15.2f}
```

---

## 📈 ANÁLISE DE REGIME (ANO A ANO)

{regime_section}

---

## 🔬 TESTE DE HIPÓTESE ESTATÍSTICA

### Teste Binomial
```
Sample Size (n):           {statistical_test['n_trades']}
Trades Vencedores (k):     {statistical_test['n_wins']}
Win Rate Observado:        {statistical_test['win_rate']:.2f}%
p-value:                   {statistical_test['p_value']:.6f}
Intervalo Confiança 95%:   [{statistical_test['ci_95_lower']:.2f}%, {statistical_test['ci_95_upper']:.2f}%]
```

### Conclusão Estatística
{'**A estratégia mostra um edge estatisticamente significativo (p < 0.05)**' if statistical_test['is_significant'] else '**A estratégia NÃO mostra um edge estatisticamente significativo (p >= 0.05)**'}

---

## 🎯 LÓGICA DA ESTRATÉGIA

### Entry (BUY)
- Retorno 3M > 10%
- AND Volume > MA 20 dias
- = Tendência forte confirmada

### Exit (SELL)
- Retorno 3M < 0%
- = Momentum acabou

### Diferença vs Mean Reversion
- **Mean Reversion:** Compra quedas, vende recuperações
- **Momentum:** Compra tendências, vende quando acabam
- **Perfis OPOSTOS:** Hedge natural

---

**Assinatura:**  
Agente IA Cursor (AIC)  
Data: {datetime.now().strftime('%d-%m-%Y %H:%M CET')}  
Status: Trilha B - Momentum Analysis Completa
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"\n[OK] Relatório Momentum salvo: {report_path}")


if __name__ == "__main__":
    try:
        metrics, regime_analysis, statistical_test = run_crypto_momentum_backtest()
        
        print("\n" + "=" * 80)
        print("BACKTEST MOMENTUM COMPLETO")
        print("=" * 80)
        print(f"\nTotal de Trades: {statistical_test['n_trades']}")
        print(f"p-value: {statistical_test['p_value']:.6f}")
        print(f"Significancia: {'[OK] SIM (p < 0.05)' if statistical_test['is_significant'] else '[FAIL] NAO (p >= 0.05)'}")
        print("\n[OK] Relatorio gerado")
        
    except Exception as e:
        print(f"\n[ERROR] Backtest falhou: {e}")
        logging.error(f"Error: {e}", exc_info=True)

