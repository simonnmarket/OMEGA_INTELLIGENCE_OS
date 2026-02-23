# -*- coding: utf-8 -*-
"""
SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0
BACKTESTING: MEAN REVERSION COM BOLLINGER BANDS - EURUSD
ESTRATÉGIA: Mean Reversion usando Bollinger Bands
FONTE DE DADOS: MetaTrader 5 Python API

DIRETIVA: CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0
DATA: 16 de Novembro de 2025 (CET/Berlin)
AUTOR: Sistema Prometheus
STATUS: ✅ PRODUÇÃO

COMPLIANCE:
- Validação empírica e científica (CEO UNIVERSAL)
- Decisões baseadas em métricas quantitativas
- Governança corporativa e compliance estritas
- Logs estruturados ISO 8601

FUNCIONALIDADE:
- Coleta de dados históricos via MT5 (10 anos)
- Cálculo de indicadores técnicos (SMA, Bollinger Bands)
- Simulação de backtest com custos realistas
- Walking Forward Analysis para validação robusta
- Análise de resultados com métricas institucionais
- Visualização de equity curve e performance
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import json

# Configuração de logging estruturado (ISO 8601)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
logger = logging.getLogger(__name__)

# =====================================================
# PARÂMETROS FIXOS DA ESTRATÉGIA
# =====================================================

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1
YEARS_OF_DATA = 10
SMA_PERIOD = 50
STD_DEV_MULTIPLIER = 2.0
STOP_LOSS_PIPS = 150
TAKE_PROFIT_PIPS = 300
COMMISSION_PER_LOT = 7.0
LOT_SIZE = 1  # lote padrão

# =====================================================
# FUNÇÕES DE COLETA E PROCESSAMENTO DE DADOS
# =====================================================

def fetch_data(symbol: str, timeframe: int, years: int) -> pd.DataFrame:
    """
    Coleta dados históricos do MetaTrader 5
    
    Args:
        symbol: Símbolo do ativo (ex: "EURUSD")
        timeframe: Timeframe MT5 (ex: mt5.TIMEFRAME_H1)
        years: Número de anos de dados históricos
    
    Returns:
        DataFrame com dados OHLCV
    
    Raises:
        RuntimeError: Se MT5 não inicializar ou dados não retornarem
    """
    logger.info(f"Iniciando coleta de dados: {symbol}, {timeframe}, {years} anos")
    
    if not mt5.initialize():
        error = mt5.last_error()
        logger.error(f"Falha ao inicializar MT5: {error}")
        mt5.shutdown()
        raise RuntimeError(f"Erro ao inicializar MT5: {error}")
    
    try:
        utc_from = datetime.now() - timedelta(days=years * 365)
        utc_to = datetime.now()
        
        logger.info(f"Buscando dados de {utc_from} até {utc_to}")
        data = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
        
        if data is None or len(data) == 0:
            error = mt5.last_error()
            logger.error(f"Dados não retornaram: {error}")
            raise RuntimeError(f"Dados não retornaram: {error}")
        
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        logger.info(f"Dados coletados: {len(df)} registros de {df.index[0]} até {df.index[-1]}")
        return df
        
    finally:
        mt5.shutdown()
        logger.info("Conexão MT5 encerrada")


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores técnicos (SMA e Bollinger Bands)
    
    Args:
        df: DataFrame com dados OHLCV
    
    Returns:
        DataFrame com indicadores calculados
    """
    logger.info(f"Calculando indicadores técnicos (SMA={SMA_PERIOD}, StdDev={STD_DEV_MULTIPLIER})")
    
    df = df.copy()
    df['sma'] = df['close'].rolling(window=SMA_PERIOD, min_periods=SMA_PERIOD).mean()
    df['std_dev'] = df['close'].rolling(window=SMA_PERIOD, min_periods=SMA_PERIOD).std()
    df['upper_band'] = df['sma'] + STD_DEV_MULTIPLIER * df['std_dev']
    df['lower_band'] = df['sma'] - STD_DEV_MULTIPLIER * df['std_dev']
    
    # Remover NaN dos períodos iniciais
    df = df.dropna()
    
    logger.info(f"Indicadores calculados: {len(df)} registros válidos")
    return df


# =====================================================
# SIMULADOR DE BACKTEST
# =====================================================

def run_backtest(df: pd.DataFrame) -> List[Dict]:
    """
    Executa simulação de backtest da estratégia Mean Reversion
    
    Estratégia:
    - LONG: Quando preço toca banda inferior
    - SHORT: Quando preço toca banda superior
    - Saída: Quando preço cruza SMA ou atinge SL/TP
    
    Args:
        df: DataFrame com dados e indicadores calculados
    
    Returns:
        Lista de trades executados
    """
    logger.info("Iniciando simulação de backtest")
    
    trades = []
    position = None
    entry_price = 0.0
    entry_time = None
    
    for i in range(len(df)):
        row = df.iloc[i]
        close = row['close']
        time = row.name  # índice é datetime
        sma = row['sma']
        lower_band = row['lower_band']
        upper_band = row['upper_band']
        
        # Spread estimado (em pontos para EURUSD)
        spread = row['spread'] if 'spread' in row.index else 1.5
        spread_cost = spread * 0.0001 * 100000  # spread em dólares por lote
        
        # Lógica de entrada
        if position is None:
            # LONG: Preço toca banda inferior (oversold)
            if close <= lower_band:
                position = 'long'
                entry_price = close
                entry_time = time
                logger.debug(f"LONG entry: {entry_time}, price: {entry_price:.5f}")
            
            # SHORT: Preço toca banda superior (overbought)
            elif close >= upper_band:
                position = 'short'
                entry_price = close
                entry_time = time
                logger.debug(f"SHORT entry: {entry_time}, price: {entry_price:.5f}")
        
        # Lógica de saída
        else:
            exit = False
            exit_reason = None
            
            # Saída por cruzar SMA (mean reversion completa)
            if position == 'long' and close >= sma:
                exit = True
                exit_reason = 'SMA_cross'
            elif position == 'short' and close <= sma:
                exit = True
                exit_reason = 'SMA_cross'
            
            # Saída por Stop Loss ou Take Profit
            if position == 'long':
                sl_price = entry_price - STOP_LOSS_PIPS * 0.0001
                tp_price = entry_price + TAKE_PROFIT_PIPS * 0.0001
                
                if close <= sl_price:
                    exit = True
                    exit_reason = 'stop_loss'
                elif close >= tp_price:
                    exit = True
                    exit_reason = 'take_profit'
            
            elif position == 'short':
                sl_price = entry_price + STOP_LOSS_PIPS * 0.0001
                tp_price = entry_price - TAKE_PROFIT_PIPS * 0.0001
                
                if close >= sl_price:
                    exit = True
                    exit_reason = 'stop_loss'
                elif close <= tp_price:
                    exit = True
                    exit_reason = 'take_profit'
            
            # Executa saída
            if exit:
                exit_price = close
                exit_time = time
                
                # Calcula P&L
                if position == 'long':
                    pnl = (exit_price - entry_price) * 100000  # 1 lote = 100k unidades
                else:  # short
                    pnl = (entry_price - exit_price) * 100000
                
                # Subtrai custos (spread + comissão)
                pnl -= spread_cost + COMMISSION_PER_LOT
                
                trades.append({
                    'entry_time': entry_time,
                    'entry_price': entry_price,
                    'exit_time': exit_time,
                    'exit_price': exit_price,
                    'direction': position,
                    'profit_loss': pnl,
                    'exit_reason': exit_reason,
                    'duration_hours': (exit_time - entry_time).total_seconds() / 3600
                })
                
                logger.debug(
                    f"{position.upper()} exit: {exit_time}, price: {exit_price:.5f}, "
                    f"P&L: {pnl:.2f}, reason: {exit_reason}"
                )
                
                position = None
                entry_price = 0.0
                entry_time = None
    
    logger.info(f"Backtest concluído: {len(trades)} trades executados")
    return trades


# =====================================================
# WALKING FORWARD ANALYSIS
# =====================================================

def run_walk_forward(
    df: pd.DataFrame,
    in_sample_years: int = 2,
    out_of_sample_months: int = 6
) -> List[Dict]:
    """
    Executa análise Walking Forward para validação robusta
    
    Metodologia:
    - In-Sample: Dados para treinar/ajustar parâmetros
    - Out-of-Sample: Dados para validar desempenho
    
    Args:
        df: DataFrame completo com dados históricos
        in_sample_years: Anos de dados in-sample
        out_of_sample_months: Meses de dados out-of-sample
    
    Returns:
        Lista de resultados por período out-of-sample
    """
    logger.info(
        f"Iniciando Walking Forward Analysis: "
        f"In-Sample={in_sample_years} anos, Out-Sample={out_of_sample_months} meses"
    )
    
    results = []
    start_date = df.index.min()
    end_date = df.index.max()
    current_start = start_date
    
    period_num = 1
    
    while current_start + timedelta(days=in_sample_years * 365 + out_of_sample_months * 30) <= end_date:
        in_sample_end = current_start + timedelta(days=in_sample_years * 365)
        out_sample_end = in_sample_end + timedelta(days=out_of_sample_months * 30)
        
        in_sample_df = df[(df.index >= current_start) & (df.index < in_sample_end)].copy()
        out_sample_df = df[(df.index >= in_sample_end) & (df.index < out_sample_end)].copy()
        
        if len(in_sample_df) < SMA_PERIOD or len(out_sample_df) < SMA_PERIOD:
            logger.warning(
                f"Período {period_num}: Dados insuficientes "
                f"(In-Sample: {len(in_sample_df)}, Out-Sample: {len(out_sample_df)})"
            )
            break
        
        logger.info(
            f"Período {period_num}: "
            f"In-Sample {current_start.date()} até {in_sample_end.date()}, "
            f"Out-Sample {in_sample_end.date()} até {out_sample_end.date()}"
        )
        
        # Calcula indicadores no in-sample (para ajuste de parâmetros futuro)
        in_sample_df = calculate_indicators(in_sample_df)
        
        # Calcula indicadores no out-sample
        out_sample_df = calculate_indicators(out_sample_df)
        
        # Executa backtest no out-sample
        trades = run_backtest(out_sample_df)
        
        # Analisa resultados
        if len(trades) > 0:
            analysis = analyze_results(trades)
            analysis['period_num'] = period_num
            analysis['period_start'] = in_sample_end
            analysis['period_end'] = out_sample_end
            analysis['in_sample_start'] = current_start
            analysis['in_sample_end'] = in_sample_end
            analysis['out_sample_start'] = in_sample_end
            analysis['out_sample_end'] = out_sample_end
            analysis['total_trades'] = len(trades)
            
            results.append(analysis)
            
            logger.info(
                f"Período {period_num} concluído: "
                f"{len(trades)} trades, Win Rate: {analysis['win_rate']:.2%}, "
                f"Total Return: {analysis['total_return']:.2f}, "
                f"Sharpe: {analysis['sharpe_ratio']:.2f}"
            )
        else:
            logger.warning(f"Período {period_num}: Nenhum trade executado")
        
        # Avança para próximo período (rolling window)
        current_start += timedelta(days=out_of_sample_months * 30)
        period_num += 1
    
    logger.info(f"Walking Forward Analysis concluída: {len(results)} períodos validados")
    return results


# =====================================================
# ANÁLISE DE RESULTADOS
# =====================================================

def analyze_results(trades: List[Dict]) -> Dict:
    """
    Analisa resultados do backtest com métricas institucionais
    
    Métricas calculadas:
    - Win Rate, Profit Factor, Total Return
    - Sharpe Ratio, Max Drawdown
    - Expected Value, Avg Win/Loss
    
    Args:
        trades: Lista de trades executados
    
    Returns:
        Dicionário com métricas de performance
    """
    if not trades:
        logger.warning("Nenhum trade para analisar")
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'expected_value': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0
        }
    
    total_trades = len(trades)
    profits = np.array([t['profit_loss'] for t in trades])
    
    wins = profits[profits > 0]
    losses = profits[profits <= 0]
    
    win_rate = len(wins) / total_trades if total_trades > 0 else 0.0
    
    total_profit = wins.sum() if len(wins) > 0 else 0.0
    total_loss = abs(losses.sum()) if len(losses) > 0 else 0.0
    profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0.0)
    
    total_return = profits.sum()
    expected_value = profits.mean()
    
    avg_win = wins.mean() if len(wins) > 0 else 0.0
    avg_loss = losses.mean() if len(losses) > 0 else 0.0
    
    # Sharpe Ratio (assumindo 252 períodos/ano e risco livre = 0)
    if len(profits) > 1:
        mean_return = profits.mean()
        std_return = profits.std()
        sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0.0
    else:
        sharpe_ratio = 0.0
    
    # Max Drawdown
    equity_curve = np.cumsum(profits)
    peak = np.maximum.accumulate(equity_curve)
    drawdown = equity_curve - peak
    max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0.0
    
    # Calcule drawdown percentual se equity inicial > 0
    if len(equity_curve) > 0 and equity_curve[0] != 0:
        max_dd_pct = (max_drawdown / abs(equity_curve[0])) * 100
    else:
        max_dd_pct = 0.0
    
    results = {
        'total_trades': total_trades,
        'winning_trades': len(wins),
        'losing_trades': len(losses),
        'win_rate': win_rate,
        'profit_factor': profit_factor if profit_factor != float('inf') else 999.0,
        'total_return': total_return,
        'expected_value': expected_value,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_dd_pct,
        'total_profit': total_profit,
        'total_loss': total_loss
    }
    
    logger.info(
        f"Análise concluída: {total_trades} trades, Win Rate: {win_rate:.2%}, "
        f"Total Return: {total_return:.2f}, Sharpe: {sharpe_ratio:.2f}, "
        f"Max DD: {max_drawdown:.2f} ({max_dd_pct:.2f}%)"
    )
    
    return results


# =====================================================
# VISUALIZAÇÃO E RELATÓRIOS
# =====================================================

def plot_equity_curve(trades: List[Dict], save_path: Optional[Path] = None) -> None:
    """
    Plota equity curve e métricas de performance
    
    Args:
        trades: Lista de trades executados
        save_path: Caminho para salvar gráfico (opcional)
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        logger.warning("Matplotlib não disponível. Gráficos não serão gerados.")
        return
    
    if not trades:
        logger.warning("Nenhum trade para plotar")
        return
    
    # Calcula equity curve
    profits = np.array([t['profit_loss'] for t in trades])
    equity = np.cumsum(profits)
    timestamps = [t['entry_time'] for t in trades]
    
    # Cria figura com subplots
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(f'Backtest Mean Reversion - {SYMBOL} (Bollinger Bands)', fontsize=16, fontweight='bold')
    
    # Plot 1: Equity Curve
    axes[0].plot(timestamps, equity, linewidth=2, color='#2E86AB', label='Equity')
    axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[0].fill_between(timestamps, 0, equity, where=(equity >= 0), alpha=0.3, color='green', label='Profit')
    axes[0].fill_between(timestamps, 0, equity, where=(equity < 0), alpha=0.3, color='red', label='Loss')
    axes[0].set_ylabel('Equity (USD)', fontsize=12)
    axes[0].set_title('Equity Curve', fontsize=14, fontweight='bold')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    axes[0].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    
    # Plot 2: Drawdown
    peak = np.maximum.accumulate(equity)
    drawdown = (equity - peak) / peak * 100
    drawdown[np.isnan(drawdown)] = 0
    
    axes[1].fill_between(timestamps, 0, drawdown, color='red', alpha=0.5, label='Drawdown %')
    axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1].set_ylabel('Drawdown (%)', fontsize=12)
    axes[1].set_xlabel('Data', fontsize=12)
    axes[1].set_title('Drawdown Curve', fontsize=14, fontweight='bold')
    axes[1].legend(loc='best')
    axes[1].grid(True, alpha=0.3)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    axes[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Gráfico salvo em: {save_path}")
    else:
        plt.savefig(f'equity_curve_{SYMBOL}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        logger.info("Gráfico salvo no diretório atual")
    
    plt.close()


def generate_report(results: List[Dict], output_path: Optional[Path] = None) -> str:
    """
    Gera relatório completo em formato markdown
    
    Args:
        results: Lista de resultados do walking forward
        output_path: Caminho para salvar relatório (opcional)
    
    Returns:
        String com relatório formatado
    """
    output_dir = Path(__file__).parent.parent.parent / "Output" / "Backtests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_path is None:
        output_path = output_dir / f"backtest_report_{SYMBOL}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report = f"""# RELATÓRIO DE BACKTEST - MEAN REVERSION BOLLINGER BANDS
# Símbolo: {SYMBOL} | Timeframe: H1 | Período: {YEARS_OF_DATA} anos

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (CET/Berlin)  
**Estratégia:** Mean Reversion usando Bollinger Bands  
**Protocolo:** CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0

---

## PARÂMETROS DA ESTRATÉGIA

| Parâmetro | Valor |
|-----------|-------|
| Símbolo | {SYMBOL} |
| Timeframe | H1 (1 hora) |
| SMA Period | {SMA_PERIOD} |
| Std Dev Multiplier | {STD_DEV_MULTIPLIER} |
| Stop Loss | {STOP_LOSS_PIPS} pips |
| Take Profit | {TAKE_PROFIT_PIPS} pips |
| Commission per Lot | ${COMMISSION_PER_LOT} |
| Lot Size | {LOT_SIZE} |

---

## RESULTADOS WALKING FORWARD ANALYSIS

"""
    
    if results:
        # Médias agregadas
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_total_return = np.mean([r['total_return'] for r in results])
        avg_max_dd = np.mean([r['max_drawdown'] for r in results])
        total_trades_all = sum([r['total_trades'] for r in results])
        
        report += f"""### RESUMO GERAL

| Métrica | Valor |
|---------|-------|
| **Períodos Analisados** | {len(results)} |
| **Total de Trades** | {total_trades_all} |
| **Win Rate Médio** | {avg_win_rate:.2%} |
| **Sharpe Ratio Médio** | {avg_sharpe:.2f} |
| **Retorno Total Médio** | ${avg_total_return:.2f} |
| **Max Drawdown Médio** | ${avg_max_dd:.2f} |

---

### DETALHES POR PERÍODO

"""
        
        for i, r in enumerate(results, 1):
            report += f"""#### Período {i}

**Out-of-Sample:** {r['out_sample_start'].strftime('%Y-%m-%d')} até {r['out_sample_end'].strftime('%Y-%m-%d')}

| Métrica | Valor |
|---------|-------|
| Total de Trades | {r['total_trades']} |
| Trades Vencedores | {r['winning_trades']} |
| Trades Perdedores | {r['losing_trades']} |
| Win Rate | {r['win_rate']:.2%} |
| Profit Factor | {r['profit_factor']:.2f} |
| Retorno Total | ${r['total_return']:.2f} |
| Sharpe Ratio | {r['sharpe_ratio']:.2f} |
| Max Drawdown | ${r['max_drawdown']:.2f} ({r['max_drawdown_pct']:.2f}%) |
| Expected Value | ${r['expected_value']:.2f} |
| Avg Win | ${r['avg_win']:.2f} |
| Avg Loss | ${r['avg_loss']:.2f} |

---

"""
    else:
        report += "*Nenhum resultado disponível*\n\n"
    
    report += f"""
---

## CONCLUSÕES

**Status da Estratégia:** {'✅ VIÁVEL' if results and avg_sharpe > 0.5 and avg_win_rate > 0.5 else '⚠️ REQUER AJUSTES'}

**Recomendações:**
- Análise de robustez dos parâmetros
- Validação em múltiplos timeframes
- Teste em diferentes regimes de mercado
- Otimização de SL/TP para diferentes condições

---

**Relatório gerado por:** Sistema Prometheus v3.0  
**Protocolo:** CEO UNIVERSAL v1.0 | Excelência Goldman Sachs/BlackRock
"""
    
    output_path.write_text(report, encoding='utf-8')
    logger.info(f"Relatório salvo em: {output_path}")
    
    return report


# =====================================================
# BLOCO PRINCIPAL DE EXECUÇÃO
# =====================================================

def main():
    """
    Função principal de execução do backtest
    """
    logger.info("=" * 80)
    logger.info("BACKTEST MEAN REVERSION BOLLINGER BANDS - EURUSD")
    logger.info("Protocolo: CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0")
    logger.info("=" * 80)
    
    try:
        # 1. Coleta de dados
        logger.info("ETAPA 1: Coleta de dados históricos")
        df = fetch_data(SYMBOL, TIMEFRAME, YEARS_OF_DATA)
        
        # 2. Cálculo de indicadores
        logger.info("ETAPA 2: Cálculo de indicadores técnicos")
        df = calculate_indicators(df)
        
        # 3. Walking Forward Analysis
        logger.info("ETAPA 3: Walking Forward Analysis")
        results = run_walk_forward(df, in_sample_years=2, out_of_sample_months=6)
        
        # 4. Análise e relatório
        logger.info("ETAPA 4: Geração de relatório")
        report = generate_report(results)
        print(report)
        
        # 5. Backtest completo para equity curve
        logger.info("ETAPA 5: Backtest completo para visualização")
        all_trades = run_backtest(df)
        
        if all_trades:
            # Plota equity curve
            output_dir = Path(__file__).parent.parent.parent / "Output" / "Backtests"
            output_dir.mkdir(parents=True, exist_ok=True)
            plot_path = output_dir / f"equity_curve_{SYMBOL}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plot_equity_curve(all_trades, save_path=plot_path)
            
            # Análise agregada
            aggregate_analysis = analyze_results(all_trades)
            logger.info("=" * 80)
            logger.info("RESULTADOS AGREGADOS (TODO O PERÍODO)")
            logger.info(f"Total de Trades: {aggregate_analysis['total_trades']}")
            logger.info(f"Win Rate: {aggregate_analysis['win_rate']:.2%}")
            logger.info(f"Profit Factor: {aggregate_analysis['profit_factor']:.2f}")
            logger.info(f"Retorno Total: ${aggregate_analysis['total_return']:.2f}")
            logger.info(f"Sharpe Ratio: {aggregate_analysis['sharpe_ratio']:.2f}")
            logger.info(f"Max Drawdown: ${aggregate_analysis['max_drawdown']:.2f} ({aggregate_analysis['max_drawdown_pct']:.2f}%)")
            logger.info("=" * 80)
        
        logger.info("Backtest concluído com sucesso!")
        
    except Exception as e:
        logger.exception(f"Erro durante execução do backtest: {e}")
        raise


if __name__ == "__main__":
    main()

