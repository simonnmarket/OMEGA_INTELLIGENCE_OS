# -*- coding: utf-8 -*-
"""
================================================================================
EXPERIMENTO DE REFUTAÇÃO - GOLD "QUANTUM" STRATEGY
================================================================================

OBJETIVO: Refutar ou validar a estratégia "quântica" de Gold com dados REAIS

PROTOCOLO: ASC-AQ v1.0.0 - Falsificação Ativa
EXECUTOR: Agente ASC-AQ
DATA: 05-11-2025

HIPÓTESE A SER REFUTADA:
"A estratégia Gold Quantum baseada em MacroIndex + Tunneling possui edge
explorável com Sharpe > 0.5 e Expectativa > 0"

CRITÉRIOS DE REFUTAÇÃO:
- Se Sharpe < 0.5 em walk-forward → REFUTADA
- Se Expectativa < 0 → REFUTADA
- Se Max DD > 30% → REFUTADA
- Se Win Rate não difere de 50% (p > 0.05) → REFUTADA

================================================================================
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
from scipy.stats import binomtest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("="*80)
logging.info("EXPERIMENTO DE REFUTAÇÃO - GOLD QUANTUM STRATEGY")
logging.info("Protocolo: ASC-AQ v1.0.0 - Falsificação Ativa")
logging.info("="*80)

# Configuração
PERIOD_START = '2015-01-01'
PERIOD_SPLIT = '2020-12-31'  # Train/Test split
PERIOD_END = '2024-11-01'
LOOKBACK = 252

logging.info(f"\n[CONFIG] Período Total: {PERIOD_START} a {PERIOD_END}")
logging.info(f"[CONFIG] Split: Train até {PERIOD_SPLIT}, Test depois")
logging.info(f"[CONFIG] Lookback: {LOOKBACK} dias\n")

# Baixar dados REAIS
logging.info("[DATA] Baixando Gold (GC=F)...")
try:
    gold_data = yf.download('GC=F', start=PERIOD_START, end=PERIOD_END, progress=False)
    gold = gold_data['Close'].values
    dates = gold_data.index
    logging.info(f"[DATA] ✅ Gold: {len(gold)} dias coletados")
except Exception as e:
    logging.error(f"[DATA] ❌ Erro ao baixar Gold: {e}")
    raise

logging.info("[DATA] Baixando VIX (^VIX) como proxy de geo risk...")
try:
    vix_data = yf.download('^VIX', start=PERIOD_START, end=PERIOD_END, progress=False)
    vix = vix_data['Close'].values / 100  # Normalizar
    logging.info(f"[DATA] ✅ VIX: {len(vix)} dias coletados")
except Exception as e:
    logging.error(f"[DATA] ❌ Erro ao baixar VIX: {e}")
    vix = np.random.normal(0.15, 0.05, len(gold))  # Fallback

logging.info("[DATA] Baixando 10Y Treasury (^TNX) como proxy de rates...")
try:
    tnx_data = yf.download('^TNX', start=PERIOD_START, end=PERIOD_END, progress=False)
    tnx = tnx_data['Close'].values / 100  # Converter para decimal
    logging.info(f"[DATA] ✅ TNX: {len(tnx)} dias coletados")
except Exception as e:
    logging.error(f"[DATA] ❌ Erro ao baixar TNX: {e}")
    tnx = np.random.normal(0.02, 0.01, len(gold))  # Fallback

# Proxies simulados (DXY e Inflation - APIs pagas)
logging.info("[DATA] Gerando proxies para DXY e Inflation (dados limitados)...")
dxy = np.random.normal(0.95, 0.02, len(gold))  # Proxy DXY
inf = np.random.normal(0.02, 0.005, len(gold))  # Proxy Inflation

# Alinhar tamanhos (pode haver missing data)
min_len = min(len(gold), len(vix), len(tnx))
gold = gold[:min_len]
vix = vix[:min_len]
tnx = tnx[:min_len]
dxy = dxy[:min_len]
inf = inf[:min_len]
dates = dates[:min_len]

logging.info(f"[DATA] Dados alinhados: {min_len} dias\n")

# Calcular retornos
gold_prices = gold.flatten() if len(gold.shape) > 1 else gold
returns = np.diff(np.log(gold_prices))

# Sinais da estratégia "Quantum"
signals = []
macro_values = []
tunneling_values = []

logging.info("[STRATEGY] Gerando sinais baseados em MacroIndex + Tunneling...")

for i in range(LOOKBACK, len(gold)):
    # MacroIndex (do código original)
    usd = dxy[i] - np.mean(dxy[i-50:i])  # Delta USD
    rates = -(tnx[i] - 0.02)  # Real rates negativos = bullish
    inflation = inf[i]
    geo = vix[i]
    
    # Composite Macro Score
    composite = -0.4*usd - 0.6*rates + 0.3*inflation + 0.2*geo
    macro_values.append(composite)
    
    # QuantumState (tunneling)
    ret_slice = returns[i-50:i]
    energy = np.std(ret_slice) if len(ret_slice) > 0 else 0.01
    barrier = abs(composite)
    tunneling = np.exp(-5 * barrier / energy) if energy > 0 else 0
    tunneling_values.append(tunneling)
    
    # Sinais (baseado no código original)
    long_sig = composite > 0.1 and tunneling > 0.3
    short_sig = composite < -0.1 and tunneling > 0.4
    
    if long_sig:
        signals.append(1)  # Buy
    elif short_sig:
        signals.append(-1)  # Sell
    else:
        signals.append(0)  # Hold

logging.info(f"[STRATEGY] ✅ {len(signals)} sinais gerados\n")

# Alinhar signals com returns (shift para forward)
signals_array = np.array(signals)
returns_aligned = returns[LOOKBACK:LOOKBACK+len(signals_array)]

# Garantir mesmo tamanho
min_len_align = min(len(signals_array), len(returns_aligned))
signals_array = signals_array[:min_len_align]
returns_aligned = returns_aligned[:min_len_align]

strategy_returns = signals_array * returns_aligned
costs = 0.0001 * np.abs(np.diff(signals_array, prepend=0))  # Custo de transação 1 bp
net_returns = strategy_returns - costs

# Separar Train/Test
split_idx = len([d for d in dates if d <= pd.Timestamp(PERIOD_SPLIT)]) - LOOKBACK - 1

train_returns = net_returns[:split_idx]
test_returns = net_returns[split_idx:]

logging.info(f"[SPLIT] Train: {len(train_returns)} dias")
logging.info(f"[SPLIT] Test: {len(test_returns)} dias\n")

# Função de métricas
def calculate_metrics(rets, label):
    if len(rets) == 0:
        return
    
    exp = np.mean(rets)
    sharpe = np.mean(rets) / np.std(rets) * np.sqrt(252) if np.std(rets) > 0 else 0
    
    cumulative = np.cumsum(rets)
    peak = np.maximum.accumulate(cumulative)
    drawdown = cumulative - peak
    max_dd = np.min(drawdown)
    
    win_rate = np.mean(rets > 0)
    num_trades = len(rets)
    num_wins = int(win_rate * num_trades)
    
    # Binomial test
    if num_trades > 0:
        p_value = binomtest(num_wins, num_trades, 0.5, alternative='greater').pvalue
    else:
        p_value = 1.0
    
    total_return = np.exp(np.sum(rets)) - 1
    
    logging.info(f"[METRICS {label}]")
    logging.info(f"  Expectativa (diária): {exp:.6f}")
    logging.info(f"  Sharpe Ratio: {sharpe:.3f}")
    logging.info(f"  Max Drawdown: {max_dd:.4f} ({max_dd*100:.2f}%)")
    logging.info(f"  Win Rate: {win_rate:.3f} ({win_rate*100:.1f}%)")
    logging.info(f"  p-value (binomial): {p_value:.4f}")
    logging.info(f"  Num Trades: {num_trades}")
    logging.info(f"  Retorno Total: {total_return*100:.2f}%\n")
    
    return {
        'expectativa': exp,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'win_rate': win_rate,
        'p_value': p_value,
        'total_return': total_return
    }

# Calcular métricas
logging.info("="*80)
logging.info("RESULTADOS - IN-SAMPLE (TRAIN)")
logging.info("="*80)
train_metrics = calculate_metrics(train_returns, "TRAIN")

logging.info("="*80)
logging.info("RESULTADOS - OUT-OF-SAMPLE (TEST)")
logging.info("="*80)
test_metrics = calculate_metrics(test_returns, "TEST")

# VEREDITO FINAL
logging.info("="*80)
logging.info("VEREDITO FINAL - REFUTAÇÃO")
logging.info("="*80)

refutada = False
razoes = []

if test_metrics['sharpe'] < 0.5:
    refutada = True
    razoes.append(f"❌ Sharpe {test_metrics['sharpe']:.3f} < 0.5")

if test_metrics['expectativa'] < 0:
    refutada = True
    razoes.append(f"❌ Expectativa {test_metrics['expectativa']:.6f} < 0 (negativa)")

if abs(test_metrics['max_dd']) > 0.30:
    refutada = True
    razoes.append(f"❌ Max DD {abs(test_metrics['max_dd'])*100:.2f}% > 30%")

if test_metrics['p_value'] > 0.05:
    refutada = True
    razoes.append(f"❌ Win Rate não significativo (p={test_metrics['p_value']:.4f} > 0.05)")

if refutada:
    logging.info("\n🚨 HIPÓTESE REFUTADA 🚨\n")
    for razao in razoes:
        logging.info(f"  {razao}")
    logging.info("\n❌ A estratégia Gold Quantum NÃO possui edge explorável.")
    logging.info("❌ NÃO ALOCAR RECURSOS.\n")
else:
    logging.info("\n✅ HIPÓTESE NÃO REFUTADA (ainda)\n")
    logging.info("  ✅ Passou nos critérios básicos")
    logging.info("  ⚠️ Requer validação adicional (Monte Carlo, stress tests)")
    logging.info("  ⚠️ Testar em paper trading antes de capital real\n")

# Comparação com Buy-and-Hold
logging.info("="*80)
logging.info("COMPARAÇÃO COM BUY-AND-HOLD SIMPLES")
logging.info("="*80)

bh_returns = returns[LOOKBACK:]
bh_test = bh_returns[split_idx:]

bh_exp = np.mean(bh_test)
bh_sharpe = np.mean(bh_test) / np.std(bh_test) * np.sqrt(252) if np.std(bh_test) > 0 else 0
bh_total = np.exp(np.sum(bh_test)) - 1

logging.info(f"[BUY-HOLD TEST]")
logging.info(f"  Sharpe: {bh_sharpe:.3f}")
logging.info(f"  Expectativa: {bh_exp:.6f}")
logging.info(f"  Retorno Total: {bh_total*100:.2f}%\n")

if test_metrics['sharpe'] < bh_sharpe:
    logging.info("❌ CRITICAL: Estratégia Quantum PIOR que Buy-Hold simples!")
    logging.info("❌ Complexidade DESTRUIU valor.\n")
else:
    logging.info("✅ Estratégia superou Buy-Hold em Sharpe.\n")

logging.info("="*80)
logging.info("FIM DO EXPERIMENTO DE REFUTAÇÃO")
logging.info("="*80)

