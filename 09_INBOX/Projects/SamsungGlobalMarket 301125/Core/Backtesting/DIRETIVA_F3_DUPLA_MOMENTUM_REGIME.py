# -*- coding: utf-8 -*-
"""
DIRETIVA OFICIAL F3-DUPLA - MOMENTUM + REGIME CLASSIFIER
EXECUTOR: Agente AIC
DATA: 04-11-2025 00:25 CET
STATUS: EXECUTANDO IMEDIATAMENTE

PROTOCOLO BLINDADO - SEGUIR EXCLUSIVAMENTE ESTAS INSTRUÇÕES
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
import warnings
warnings.filterwarnings('ignore')

# CONSTANTES DEFINIDAS PELO CEO
SYMBOLS = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD', 'MATIC-USD', 'ATOM-USD']
START_DATE = "2018-01-01"
END_DATE = "2023-12-31"
INITIAL_CAPITAL = 30000
TRANSACTION_COST = 0.0010  # 10 bps

# =============================================================================
# COMPONENTE 1: REGIME CLASSIFIER (DXY + VIX)
# =============================================================================

class CryptoRegimeClassifier:
    """
    CLASSIFICADOR DE REGIME CRYPTO BASEADO EM INDICADORES MACRO
    REGRAS DEFINIDAS PELO CEO:
    - DXY > 105 → Risk-off (BEAR crypto)
    - VIX > 20 → High fear (BEAR crypto)  
    - Combinação → Sinal dinâmico de alocação
    """
    
    def __init__(self):
        self.regime_history = {}
        # Pre-carregar dados macro para evitar downloads repetidos
        print("  [RegimeClassifier] Carregando dados macro (DXY, VIX)...")
        try:
            self.dxy_data = yf.download('DX-Y.NYB', start=START_DATE, end=END_DATE, progress=False)['Close']
            self.vix_data = yf.download('^VIX', start=START_DATE, end=END_DATE, progress=False)['Close']
            print(f"  [RegimeClassifier] OK - DXY: {len(self.dxy_data)} dias, VIX: {len(self.vix_data)} dias")
        except Exception as e:
            print(f"  [RegimeClassifier] ERRO ao carregar macro: {e}")
            self.dxy_data = pd.Series()
            self.vix_data = pd.Series()
        
    def get_macro_data(self, date):
        """Busca dados DXY e VIX para data específica"""
        try:
            # Usar dados pre-carregados
            if date in self.dxy_data.index:
                dxy_value = float(self.dxy_data.loc[date])
            else:
                # Buscar valor mais próximo
                nearest_date = self.dxy_data.index[self.dxy_data.index.get_indexer([date], method='nearest')[0]]
                dxy_value = float(self.dxy_data.loc[nearest_date])
            
            if date in self.vix_data.index:
                vix_value = float(self.vix_data.loc[date])
            else:
                nearest_date = self.vix_data.index[self.vix_data.index.get_indexer([date], method='nearest')[0]]
                vix_value = float(self.vix_data.loc[nearest_date])
            
            return dxy_value, vix_value
        except:
            return 100, 15  # Valores default
    
    def classify_regime(self, date):
        """Classifica regime com base nas regras definidas"""
        dxy, vix = self.get_macro_data(date)
        
        # REGRAS DEFINIDAS PELO CEO
        bear_conditions = [
            dxy > 105,    # USD forte = risk-off crypto
            vix > 20      # Medo alto = risk-off
        ]
        
        bull_conditions = [
            dxy < 95,     # USD fraco = risk-on crypto  
            vix < 15      # Medo baixo = risk-on
        ]
        
        # CLASSIFICAÇÃO
        if any(bear_conditions):
            regime = "BEAR"
            allocation = 0.0  # 0% alocação
        elif all(bull_conditions):
            regime = "BULL"
            allocation = 0.8  # 80% alocação
        else:
            regime = "NEUTRAL"
            allocation = 0.4  # 40% alocação
        
        # Cache do regime
        if date not in self.regime_history:
            self.regime_history[date] = (regime, allocation, dxy, vix)
        
        return regime, allocation

# =============================================================================
# COMPONENTE 2: MOMENTUM STRATEGY COM ALOCAÇÃO DINÂMICA
# =============================================================================

class DynamicMomentumStrategy:
    """
    ESTRATÉGIA MOMENTUM COM REGIME SWITCHING
    BASE CIENTÍFICA: Jegadeesh & Titman (1993) + Regime Adaptation
    """
    
    def __init__(self, regime_classifier):
        self.regime_classifier = regime_classifier
        
    def calculate_momentum_score(self, prices_dict):
        """
        Calcula momentum score para múltiplos símbolos
        Retorna dict de {symbol: momentum_signals_df}
        """
        all_signals = {}
        
        for symbol in SYMBOLS:
            if symbol not in prices_dict:
                continue
            
            prices = prices_dict[symbol]
            signals = pd.DataFrame(index=prices.index)
            
            # Retornos multi-período (base científica)
            returns_3m = prices.pct_change(63)   # ~3 meses
            returns_6m = prices.pct_change(126)  # ~6 meses  
            returns_12m = prices.pct_change(252) # ~12 meses
            
            # Sinal composto (equal weight)
            momentum_score = (returns_3m + returns_6m + returns_12m) / 3
            
            signals['price'] = prices
            signals['momentum_score'] = momentum_score
            signals['signal'] = 'HOLD'
            
            # Condições de entrada/saída
            buy_condition = (momentum_score > 0.10)  # Momentum positivo forte
            sell_condition = (momentum_score < 0.00)  # Momentum virou negativo
            
            signals.loc[buy_condition, 'signal'] = 'BUY'
            signals.loc[sell_condition, 'signal'] = 'SELL'
            
            all_signals[symbol] = signals
        
        return all_signals
    
    def execute_backtest_with_regime(self, prices_dict):
        """Executa backtest completo com regime switching"""
        
        # Calcular sinais de momentum para todos os símbolos
        all_signals = self.calculate_momentum_score(prices_dict)
        
        # State tracking
        cash = Decimal(str(INITIAL_CAPITAL))
        positions = {}  # {symbol: (size, entry_price, entry_date)}
        trades_history = []
        equity_curve = []
        equity_dates = []
        
        # Pegar todas as datas únicas
        all_dates = set()
        for signals in all_signals.values():
            all_dates.update(signals.index)
        trading_days = sorted(list(all_dates))
        
        print(f"  [Backtest] Simulando {len(trading_days)} dias...")
        
        for date in trading_days:
            # CONSULTA REGIME CLASSIFIER
            regime, allocation_pct = self.regime_classifier.classify_regime(date)
            
            # Preços atuais
            current_prices = {}
            for symbol in SYMBOLS:
                if symbol in all_signals and date in all_signals[symbol].index:
                    current_prices[symbol] = float(all_signals[symbol].loc[date, 'price'])
            
            # REGIME-BASED ALLOCATION
            if regime == 'BEAR':
                # FECHAR TODAS AS POSIÇÕES em bear market
                for symbol in list(positions.keys()):
                    if symbol in current_prices:
                        size, entry_price, entry_date = positions[symbol]
                        exit_price = current_prices[symbol]
                        
                        pnl_pct = (exit_price - entry_price) / entry_price
                        pnl_amount = pnl_pct * float(size)
                        
                        # Transaction costs
                        costs = float(size) * TRANSACTION_COST * 2  # Entry + exit
                        net_pnl = pnl_amount - costs
                        
                        cash += Decimal(str(float(size) + net_pnl))
                        
                        trades_history.append({
                            'date': date,
                            'symbol': symbol,
                            'action': 'CLOSE',
                            'price': exit_price,
                            'size': float(size),
                            'pnl': net_pnl,
                            'regime': regime,
                            'reason': 'BEAR regime - exit all'
                        })
                        
                        del positions[symbol]
            
            else:
                # BULL ou NEUTRAL: processar sinais
                for symbol in SYMBOLS:
                    if symbol not in all_signals or date not in all_signals[symbol].index:
                        continue
                    
                    signal = all_signals[symbol].loc[date, 'signal']
                    
                    if signal == 'BUY' and symbol not in positions:
                        # Calcular tamanho da posição baseado em alocação de regime
                        position_value = float(cash) * allocation_pct / len(SYMBOLS)
                        price = current_prices.get(symbol)
                        
                        if price and position_value > 100:  # Mínimo EUR 100 por posição
                            size = Decimal(str(position_value))
                            
                            # Deduzir do cash
                            cost = size * Decimal(str(1 + TRANSACTION_COST))
                            
                            if cost <= cash:
                                cash -= cost
                                positions[symbol] = (size, price, date)
                                
                                trades_history.append({
                                    'date': date,
                                    'symbol': symbol,
                                    'action': 'BUY',
                                    'price': price,
                                    'size': float(size),
                                    'pnl': 0.0,
                                    'regime': regime,
                                    'reason': f'{regime} regime - allocation {allocation_pct*100:.0f}%'
                                })
                    
                    elif signal == 'SELL' and symbol in positions:
                        # Fechar posição
                        size, entry_price, entry_date = positions[symbol]
                        exit_price = current_prices.get(symbol)
                        
                        if exit_price:
                            pnl_pct = (exit_price - entry_price) / entry_price
                            pnl_amount = pnl_pct * float(size)
                            costs = float(size) * TRANSACTION_COST * 2
                            net_pnl = pnl_amount - costs
                            
                            cash += Decimal(str(float(size) + net_pnl))
                            
                            trades_history.append({
                                'date': date,
                                'symbol': symbol,
                                'action': 'CLOSE',
                                'price': exit_price,
                                'size': float(size),
                                'pnl': net_pnl,
                                'regime': regime,
                                'reason': 'Momentum signal SELL'
                            })
                            
                            del positions[symbol]
            
            # Calcular equity atual
            positions_value = sum(float(size) * current_prices.get(symbol, 0) 
                                 for symbol, (size, _, _) in positions.items() 
                                 if symbol in current_prices)
            current_equity = float(cash) + positions_value
            
            equity_curve.append(current_equity)
            equity_dates.append(date)
        
        return trades_history, equity_curve, equity_dates


# =============================================================================
# COMPONENTE 3: SISTEMA DE VALIDAÇÃO ESTATÍSTICA
# =============================================================================

class StatisticalValidator:
    """
    SISTEMA DE VALIDAÇÃO ESTATÍSTICA RIGOROSA
    MÉTRICAS DEFINIDAS PELO CEO
    """
    
    @staticmethod
    def calculate_all_metrics(trades_history, equity_curve, equity_dates):
        """Calcula todas as métricas estatísticas"""
        from scipy import stats
        from scipy.stats import binomtest
        
        # Filtrar apenas trades fechados
        closed_trades = [t for t in trades_history if t['action'] == 'CLOSE']
        
        if len(closed_trades) == 0:
            return {'error': 'No trades executed'}
        
        # Basic metrics
        total_trades = len(closed_trades)
        wins = sum(1 for t in closed_trades if t['pnl'] > 0.01)
        losses = sum(1 for t in closed_trades if t['pnl'] < -0.01)
        
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in closed_trades)
        final_capital = INITIAL_CAPITAL + total_pnl
        
        # Returns
        total_return = (final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        years = (datetime.strptime(END_DATE, '%Y-%m-%d') - datetime.strptime(START_DATE, '%Y-%m-%d')).days / 365.25
        annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100
        
        # Equity curve analysis
        equity_series = pd.Series(equity_curve, index=equity_dates)
        equity_returns = equity_series.pct_change().dropna()
        
        # Volatility
        if len(equity_returns) > 1:
            daily_vol = equity_returns.std()
            annualized_vol = daily_vol * np.sqrt(252)
        else:
            annualized_vol = 0
        
        # Sharpe Ratio (standard)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return/100 - risk_free_rate) / annualized_vol if annualized_vol > 0 else 0
        
        # Sharpe ajustado para skewness (Pezier)
        if len(equity_returns) > 2:
            skewness = stats.skew(equity_returns)
            adjusted_sharpe = sharpe_ratio * (1 + skewness/6 * sharpe_ratio - (skewness**2)/24 * (sharpe_ratio**2 - 1))
        else:
            adjusted_sharpe = sharpe_ratio
        
        # Max Drawdown
        peak = INITIAL_CAPITAL
        max_dd = 0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # Profit Factor
        total_wins = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
        total_losses = abs(sum(t['pnl'] for t in closed_trades if t['pnl'] < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # TESTE BINOMIAL (p-value para win rate)
        if wins + losses > 0:
            result = binomtest(wins, wins + losses, 0.5, alternative='greater')
            p_value_binomial = result.pvalue
        else:
            p_value_binomial = 1.0
        
        # TESTE t de Student (retorno esperado)
        if len(equity_returns) > 1:
            t_stat, p_value_ttest = stats.ttest_1samp(equity_returns, 0)
        else:
            t_stat, p_value_ttest = 0, 1.0
        
        # TESTE ADF (estacionaridade)
        from statsmodels.tsa.stattools import adfuller
        if len(equity_returns) > 10:
            adf_result = adfuller(equity_returns.dropna())
            adf_pvalue = adf_result[1]
            is_stationary = adf_pvalue < 0.05
        else:
            adf_pvalue = 1.0
            is_stationary = False
        
        # Análise por regime (2022 - bear market crítico)
        trades_2022 = [t for t in closed_trades if t['date'].year == 2022]
        pnl_2022 = sum(t['pnl'] for t in trades_2022)
        bear_2022_return = (pnl_2022 / INITIAL_CAPITAL) * 100 if trades_2022 else -100
        
        return {
            'total_trades': total_trades,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'sharpe_adjusted_pezier': adjusted_sharpe,
            'max_drawdown': max_dd,
            'profit_factor': profit_factor,
            'final_capital': final_capital,
            'p_value_binomial': p_value_binomial,
            'p_value_ttest': p_value_ttest,
            'adf_pvalue': adf_pvalue,
            'is_stationary': is_stationary,
            'bear_2022_return': bear_2022_return,
            'skewness': skewness if len(equity_returns) > 2 else 0,
            'volatility': annualized_vol * 100
        }

# =============================================================================
# EXECUÇÃO PRINCIPAL - PROTOCOLO OBRIGATÓRIO
# =============================================================================

def main():
    print("=" * 80)
    print("EXECUTANDO DIRETIVA F3-DUPLA - MOMENTUM + REGIME CLASSIFIER")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%d-%m-%Y %H:%M CET')}")
    print(f"Periodo: {START_DATE} a {END_DATE}")
    print(f"Simbolos: {len(SYMBOLS)} ativos")
    print(f"Capital: EUR {INITIAL_CAPITAL:,}")
    print()
    
    # 1. INICIALIZAR COMPONENTES
    print("[1/5] Inicializando componentes...")
    regime_classifier = CryptoRegimeClassifier()
    strategy = DynamicMomentumStrategy(regime_classifier)
    validator = StatisticalValidator()
    print("  OK")
    
    # 2. CARREGAR DADOS
    print("\n[2/5] Carregando dados de crypto...")
    prices_dict = {}
    for symbol in SYMBOLS:
        try:
            data = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
            if not data.empty:
                # Handle MultiIndex
                if isinstance(data.columns, pd.MultiIndex):
                    prices_dict[symbol] = data['Close'].iloc[:, 0]
                else:
                    prices_dict[symbol] = data['Close']
                print(f"  {symbol}: {len(prices_dict[symbol])} dias")
        except Exception as e:
            print(f"  {symbol}: ERRO - {e}")
    
    print(f"  OK - {len(prices_dict)}/{len(SYMBOLS)} simbolos carregados")
    
    # 3. EXECUTAR BACKTEST
    print("\n[3/5] Executando backtest com regime switching...")
    trades, equity_curve, equity_dates = strategy.execute_backtest_with_regime(prices_dict)
    print(f"  OK - {len(trades)} trades executados")
    
    # 4. VALIDAÇÃO ESTATÍSTICA
    print("\n[4/5] Executando testes estatisticos...")
    metrics = validator.calculate_all_metrics(trades, equity_curve, equity_dates)
    print("  OK - Metricas calculadas")
    
    # 5. RELATÓRIO FINAL
    print("\n[5/5] Gerando relatorio decisorio...")
    generate_final_report(metrics, trades, regime_classifier)
    
    return metrics, trades


def generate_final_report(metrics, trades, regime_classifier):
    """Gera relatório final decisório"""
    print("\n" + "="*80)
    print("RELATORIO FINAL - DIRETIVA F3-DUPLA")
    print("="*80)
    
    # Exibir métricas principais
    print(f"\nCAPITAL:")
    print(f"  Inicial: EUR {INITIAL_CAPITAL:,.2f}")
    print(f"  Final: EUR {metrics.get('final_capital', 0):,.2f}")
    print(f"  P&L: EUR {metrics.get('final_capital', INITIAL_CAPITAL) - INITIAL_CAPITAL:,.2f}")
    
    print(f"\nPERFORMANCE:")
    print(f"  Retorno Total: {metrics.get('total_return', 0):.2f}%")
    print(f"  Retorno Anualizado: {metrics.get('annualized_return', 0):.2f}%")
    print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  Sharpe Ajustado (Pezier): {metrics.get('sharpe_adjusted_pezier', 0):.2f}")
    
    print(f"\nRISCO:")
    print(f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    print(f"  Volatilidade: {metrics.get('volatility', 0):.2f}%")
    print(f"  Bear 2022 Return: {metrics.get('bear_2022_return', 0):.2f}%")
    
    print(f"\nTRADING:")
    print(f"  Total Trades: {metrics.get('total_trades', 0)}")
    print(f"  Wins/Losses: {metrics.get('winning_trades', 0)}/{metrics.get('losing_trades', 0)}")
    print(f"  Win Rate: {metrics.get('win_rate', 0):.2f}%")
    print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
    
    print(f"\nTESTES ESTATISTICOS:")
    print(f"  p-value (Binomial): {metrics.get('p_value_binomial', 1):.6f}")
    print(f"  p-value (t-test): {metrics.get('p_value_ttest', 1):.6f}")
    print(f"  ADF p-value (Estacionaridade): {metrics.get('adf_pvalue', 1):.6f}")
    print(f"  Estacionario: {'SIM' if metrics.get('is_stationary', False) else 'NAO'}")
    
    # CRITÉRIOS DE APROVAÇÃO DEFINIDOS PELO CEO
    print("\n" + "="*80)
    print("CRITERIOS DE APROVACAO")
    print("="*80)
    
    approval_criteria = {
        'p_value': metrics.get('p_value_binomial', 1.0) < 0.05,
        'sharpe_adjusted': metrics.get('sharpe_adjusted_pezier', 0) > 0.43,
        'max_drawdown': metrics.get('max_drawdown', 100) < 15,
        'bear_protection': metrics.get('bear_2022_return', -100) > -5
    }
    
    print(f"[{'OK' if approval_criteria['p_value'] else 'FAIL'}] p-value < 0.05: {metrics.get('p_value_binomial', 1):.4f}")
    print(f"[{'OK' if approval_criteria['sharpe_adjusted'] else 'FAIL'}] Sharpe Ajustado > 0.43: {metrics.get('sharpe_adjusted_pezier', 0):.2f}")
    print(f"[{'OK' if approval_criteria['max_drawdown'] else 'FAIL'}] Max DD < 15%: {metrics.get('max_drawdown', 100):.2f}%")
    print(f"[{'OK' if approval_criteria['bear_protection'] else 'FAIL'}] Bear 2022 > -5%: {metrics.get('bear_2022_return', -100):.2f}%")
    
    approved = all(approval_criteria.values())
    criteria_met = sum(approval_criteria.values())
    
    print(f"\nSCORE: {criteria_met}/4 criterios atendidos")
    
    print("\n" + "="*80)
    if approved:
        print("DECISAO FINAL: GO - ESTRATEGIA APROVADA")
        print("="*80)
        print("\nPROXIMA FASE: PAPER TRADING")
    else:
        print("DECISAO FINAL: NO-GO - ESTRATEGIA REPROVADA")
        print("="*80)
        print("\nACÃO: Retornar para desenvolvimento ou descartar")
    
    # Salvar relatório
    save_final_report(metrics, trades, regime_classifier, approved)
    
    return approved


def save_final_report(metrics, trades, regime_classifier, approved):
    """Salva relatório final em MD"""
    from pathlib import Path
    
    report_path = Path(__file__).parent.parent.parent / 'Documentation' / '03_Relatorios_Conselho' / 'RELATORIO_FINAL_F3_DUPLA_MOMENTUM_REGIME.md'
    
    # Análise de regime
    regime_counts = {}
    for date, (regime, allocation, dxy, vix) in regime_classifier.regime_history.items():
        if regime not in regime_counts:
            regime_counts[regime] = 0
        regime_counts[regime] += 1
    
    content = f"""# RELATÓRIO FINAL - DIRETIVA F3-DUPLA
## MOMENTUM COM REGIME CLASSIFIER - VALIDAÇÃO DEFINITIVA

**Data:** {datetime.now().strftime('%d-%m-%Y %H:%M CET')}  
**Executor:** Agente IA Cursor (AIC)  
**Status:** {'✅ APROVADO' if approved else '❌ REPROVADO'}

---

## 📊 RESULTADOS FINANCEIROS

```
Capital Inicial:      EUR {INITIAL_CAPITAL:>12,.2f}
Capital Final:        EUR {metrics.get('final_capital', 0):>12,.2f}
P&L Líquido:          EUR {metrics.get('final_capital', INITIAL_CAPITAL) - INITIAL_CAPITAL:>12,.2f}
Retorno Total:        {metrics.get('total_return', 0):>15.2f}%
Retorno Anualizado:   {metrics.get('annualized_return', 0):>15.2f}%
```

## 📈 MÉTRICAS DE RISCO-RETORNO

```
Sharpe Ratio (Standard):      {metrics.get('sharpe_ratio', 0):>10.2f}
Sharpe Ajustado (Pezier):     {metrics.get('sharpe_adjusted_pezier', 0):>10.2f}
Volatilidade Anualizada:      {metrics.get('volatility', 0):>10.2f}%
Máximo Drawdown:              {metrics.get('max_drawdown', 0):>10.2f}%
Skewness:                     {metrics.get('skewness', 0):>10.2f}
```

## 🎯 MÉTRICAS DE TRADING

```
Total de Trades:              {metrics.get('total_trades', 0):>10}
Trades Vencedores:            {metrics.get('winning_trades', 0):>10}
Trades Perdedores:            {metrics.get('losing_trades', 0):>10}
Win Rate:                     {metrics.get('win_rate', 0):>10.2f}%
Profit Factor:                {metrics.get('profit_factor', 0):>10.2f}
```

## 🔬 TESTES ESTATÍSTICOS

### Teste Binomial (Win Rate)
```
H0: Win Rate = 50%
H1: Win Rate > 50%
p-value: {metrics.get('p_value_binomial', 1):.6f}
Significativo (α=0.05): {'SIM' if metrics.get('p_value_binomial', 1) < 0.05 else 'NAO'}
```

### Teste t de Student (Retorno Esperado)
```
H0: Retorno = 0
H1: Retorno ≠ 0
p-value: {metrics.get('p_value_ttest', 1):.6f}
Significativo: {'SIM' if metrics.get('p_value_ttest', 1) < 0.05 else 'NAO'}
```

### Teste ADF (Estacionaridade)
```
H0: Série tem raiz unitária (não estacionária)
H1: Série é estacionária
p-value: {metrics.get('adf_pvalue', 1):.6f}
Estacionária: {'SIM' if metrics.get('is_stationary', False) else 'NAO'}
```

## 🎯 REGIME CLASSIFIER ANALYSIS

### Distribuição de Regimes
```
{chr(10).join([f'{regime}: {count} dias ({count/sum(regime_counts.values())*100:.1f}%)' for regime, count in sorted(regime_counts.items())])}
```

### Performance em Bear Market 2022
```
Retorno 2022: {metrics.get('bear_2022_return', 0):.2f}%
Proteção: {'OK' if metrics.get('bear_2022_return', -100) > -5 else 'FALHOU'}
```

## 🏆 DECISÃO FINAL

### Critérios de Aprovação (CEO)

| Critério | Threshold | Obtido | Status |
|----------|-----------|--------|--------|
| p-value (Binomial) | < 0.05 | {metrics.get('p_value_binomial', 1):.4f} | {'✅' if metrics.get('p_value_binomial', 1) < 0.05 else '❌'} |
| Sharpe Ajustado | > 0.43 | {metrics.get('sharpe_adjusted_pezier', 0):.2f} | {'✅' if metrics.get('sharpe_adjusted_pezier', 0) > 0.43 else '❌'} |
| Max Drawdown | < 15% | {metrics.get('max_drawdown', 100):.2f}% | {'✅' if metrics.get('max_drawdown', 100) < 15 else '❌'} |
| Bear 2022 Protection | > -5% | {metrics.get('bear_2022_return', -100):.2f}% | {'✅' if metrics.get('bear_2022_return', -100) > -5 else '❌'} |

**SCORE: {sum([metrics.get('p_value_binomial', 1) < 0.05, metrics.get('sharpe_adjusted_pezier', 0) > 0.43, metrics.get('max_drawdown', 100) < 15, metrics.get('bear_2022_return', -100) > -5])}/4**

### VEREDITO EXECUTIVO

{'✅ **ESTRATÉGIA APROVADA PARA PAPER TRADING**' if approved else '❌ **ESTRATÉGIA REPROVADA - DESCARTAR OU OTIMIZAR**'}

---

**Assinatura:**  
Agente IA Cursor (AIC)  
Data: {datetime.now().strftime('%d-%m-%Y %H:%M CET')}  
Diretiva: F3-DUPLA COMPLETA
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[OK] Relatorio salvo: {report_path}")


if __name__ == "__main__":
    print("=" * 80)
    print("DIRETIVA F3-DUPLA - PROTOCOLO BLINDADO")
    print("=" * 80)
    print()
    
    try:
        metrics, trades = main()
        print("\n[OK] DIRETIVA F3-DUPLA COMPLETA")
    except Exception as e:
        print(f"\n[ERROR] Execucao falhou: {e}")
        import traceback
        traceback.print_exc()

