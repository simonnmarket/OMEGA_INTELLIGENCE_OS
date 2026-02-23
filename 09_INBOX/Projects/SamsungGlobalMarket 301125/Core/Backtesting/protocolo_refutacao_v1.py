# -*- coding: utf-8 -*-
"""
SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0
PROTOCOLO DE REFUTAÇÃO v1.0 - BASELINE CIENTÍFICO
ESTRATÉGIA: Mean Reversion com Bollinger Bands (EURUSD H1)
METODOLOGIA: Walking Forward Analysis

DIRETIVA: CEO UNIVERSAL v1.0 | Prometheus v3.0.0 | TIER-0
DATA: 16 de Novembro de 2025 (CET/Berlin)
AUTOR: Sistema Prometheus
STATUS: ✅ BASELINE EXPERIMENTAL

OBJETIVO:
Este script é nossa linha de base experimental, nosso controle científico.
Ele deve ser robusto, auto-contido e irrefutável em sua lógica.

COMPLIANCE:
- Validação empírica e científica inquestionável (CEO UNIVERSAL)
- Decisões baseadas em métricas quantitativas sólidas
- Governança corporativa e compliance estritas
- Logs estruturados ISO 8601

FUNCIONALIDADE:
- Coleta de dados históricos via MT5 (10 anos)
- Cálculo de indicadores técnicos (SMA 50, Bollinger Bands ± 2σ)
- Simulação de backtest com custos realistas
- Walking Forward Analysis para validação robusta
- Análise de resultados com métricas institucionais
- Geração de relatório de baseline científico
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import json
import csv

# Configuração de logging estruturado (ISO 8601)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
logger = logging.getLogger(__name__)

# =====================================================
# PARÂMETROS FIXOS DA ESTRATÉGIA (NÃO ALTERAR)
# =====================================================

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1
YEARS_OF_DATA = 10
SMA_PERIOD = 50
STD_DEV_MULTIPLIER = 2.0
STOP_LOSS_PIPS = 150
TAKE_PROFIT_PIPS = 300
COMMISSION_PER_LOT = 7.0
LOT_SIZE = 1

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
    logger.info(f"COLETA: {symbol}, {timeframe}, {years} anos")
    
    if not mt5.initialize():
        error = mt5.last_error()
        logger.error(f"ERRO MT5: {error}")
        mt5.shutdown()
        raise RuntimeError(f"Falha ao inicializar MT5: {error}")
    
    try:
        utc_from = datetime.now() - timedelta(days=years * 365)
        utc_to = datetime.now()
        
        logger.info(f"PERÍODO: {utc_from.date()} até {utc_to.date()}")
        data = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
        
        if data is None or len(data) == 0:
            error = mt5.last_error()
            logger.error(f"ERRO DADOS: {error}")
            raise RuntimeError(f"Dados não retornaram: {error}")
        
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        logger.info(f"DADOS COLETADOS: {len(df)} registros")
        return df
        
    finally:
        mt5.shutdown()


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores técnicos (SMA e Bollinger Bands)
    
    Args:
        df: DataFrame com dados OHLCV
    
    Returns:
        DataFrame com indicadores calculados
    """
    logger.info(f"INDICADORES: SMA={SMA_PERIOD}, StdDev={STD_DEV_MULTIPLIER}")
    
    df = df.copy()
    df['sma'] = df['close'].rolling(window=SMA_PERIOD, min_periods=SMA_PERIOD).mean()
    df['std_dev'] = df['close'].rolling(window=SMA_PERIOD, min_periods=SMA_PERIOD).std()
    df['upper_band'] = df['sma'] + STD_DEV_MULTIPLIER * df['std_dev']
    df['lower_band'] = df['sma'] - STD_DEV_MULTIPLIER * df['std_dev']
    
    df = df.dropna()
    logger.info(f"INDICADORES CALCULADOS: {len(df)} registros válidos")
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
    logger.info("BACKTEST: Iniciando simulação")
    
    trades = []
    position = None
    entry_price = 0.0
    entry_time = None
    
    for i in range(len(df)):
        row = df.iloc[i]
        close = row['close']
        time = row.name
        sma = row['sma']
        lower_band = row['lower_band']
        upper_band = row['upper_band']
        
        spread = row['spread'] if 'spread' in row.index else 1.5
        spread_cost = spread * 0.0001 * 100000
        
        # Lógica de entrada
        if position is None:
            if close <= lower_band:
                position = 'long'
                entry_price = close
                entry_time = time
            elif close >= upper_band:
                position = 'short'
                entry_price = close
                entry_time = time
        
        # Lógica de saída
        else:
            exit = False
            exit_reason = None
            
            if position == 'long' and close >= sma:
                exit = True
                exit_reason = 'SMA_cross'
            elif position == 'short' and close <= sma:
                exit = True
                exit_reason = 'SMA_cross'
            
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
            
            if exit:
                exit_price = close
                exit_time = time
                
                if position == 'long':
                    pnl = (exit_price - entry_price) * 100000
                else:
                    pnl = (entry_price - exit_price) * 100000
                
                pnl -= spread_cost + COMMISSION_PER_LOT
                
                trades.append({
                    'entry_time': entry_time,
                    'entry_price': entry_price,
                    'exit_time': exit_time,
                    'exit_price': exit_price,
                    'direction': position,
                    'profit_loss': pnl,
                    'exit_reason': exit_reason
                })
                
                position = None
                entry_price = 0.0
                entry_time = None
    
    logger.info(f"BACKTEST CONCLUÍDO: {len(trades)} trades")
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
    
    Args:
        df: DataFrame completo com dados históricos
        in_sample_years: Anos de dados in-sample
        out_of_sample_months: Meses de dados out-of-sample
    
    Returns:
        Lista de resultados por período out-of-sample
    """
    logger.info(f"WALK-FORWARD: In-Sample={in_sample_years}a, Out-Sample={out_of_sample_months}m")
    
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
            logger.warning(f"PERÍODO {period_num}: Dados insuficientes")
            break
        
        logger.info(f"PERÍODO {period_num}: Out-Sample {in_sample_end.date()} até {out_sample_end.date()}")
        
        in_sample_df = calculate_indicators(in_sample_df)
        out_sample_df = calculate_indicators(out_sample_df)
        
        trades = run_backtest(out_sample_df)
        
        if len(trades) > 0:
            analysis = analyze_results(trades)
            analysis['period_num'] = period_num
            analysis['period_start'] = in_sample_end
            analysis['period_end'] = out_sample_end
            analysis['total_trades'] = len(trades)
            
            results.append(analysis)
            
            logger.info(
                f"PERÍODO {period_num}: {len(trades)} trades, "
                f"Win Rate: {analysis['win_rate']:.2%}, "
                f"Return: ${analysis['total_return']:.2f}, "
                f"Sharpe: {analysis['sharpe_ratio']:.2f}"
            )
        
        current_start += timedelta(days=out_of_sample_months * 30)
        period_num += 1
    
    logger.info(f"WALK-FORWARD CONCLUÍDO: {len(results)} períodos validados")
    return results


# =====================================================
# ANÁLISE DE RESULTADOS
# =====================================================

def analyze_results(trades: List[Dict]) -> Dict:
    """
    Analisa resultados do backtest com métricas institucionais
    
    Args:
        trades: Lista de trades executados
    
    Returns:
        Dicionário com métricas de performance
    """
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'expected_value': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'max_drawdown_pct': 0.0
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
    
    # Sharpe Ratio
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
        'avg_loss': avg_win,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_dd_pct,
        'total_profit': total_profit,
        'total_loss': total_loss
    }
    
    return results


# =====================================================
# GERAÇÃO DE RELATÓRIO DE BASELINE
# =====================================================

def generate_baseline_report(
    results: List[Dict],
    all_trades: List[Dict],
    output_path: Optional[Path] = None
) -> Path:
    """
    Gera relatório de baseline científico em formato CSV e JSON
    
    Args:
        results: Resultados do Walking Forward Analysis
        all_trades: Todos os trades do backtest completo
        output_path: Caminho para salvar relatório (opcional)
    
    Returns:
        Caminho do arquivo gerado
    """
    output_dir = Path(__file__).parent.parent.parent / "Output" / "Backtests" / "Baseline"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_path is None:
        output_path = output_dir / f"baseline_report_{timestamp}.csv"
    
    # Análise agregada
    aggregate_analysis = analyze_results(all_trades)
    
    # Calcula médias do Walk-Forward
    if results:
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_total_return = np.mean([r['total_return'] for r in results])
        avg_max_dd = np.mean([r['max_drawdown'] for r in results])
        total_trades_all = sum([r['total_trades'] for r in results])
    else:
        avg_win_rate = aggregate_analysis['win_rate']
        avg_sharpe = aggregate_analysis['sharpe_ratio']
        avg_total_return = aggregate_analysis['total_return']
        avg_max_dd = aggregate_analysis['max_drawdown']
        total_trades_all = aggregate_analysis['total_trades']
    
    # Gera CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'METRIC', 'VALUE', 'UNIT', 'DESCRIPTION'
        ])
        
        # Baseline Summary
        writer.writerow(['BASELINE_SUMMARY', '', '', ''])
        writer.writerow(['strategy', 'Mean_Reversion_Bollinger_Bands', '', 'Estratégia de baseline'])
        writer.writerow(['symbol', SYMBOL, '', 'Símbolo testado'])
        writer.writerow(['timeframe', 'H1', '', 'Timeframe usado'])
        writer.writerow(['years_of_data', YEARS_OF_DATA, 'anos', 'Período de dados históricos'])
        writer.writerow(['walk_forward_periods', len(results), 'períodos', 'Número de períodos validados'])
        writer.writerow(['', '', '', ''])
        
        # Aggregate Metrics
        writer.writerow(['AGGREGATE_METRICS', '', '', ''])
        writer.writerow(['total_trades', aggregate_analysis['total_trades'], 'trades', 'Total de trades executados'])
        writer.writerow(['win_rate', f"{aggregate_analysis['win_rate']:.4f}", 'ratio', 'Taxa de acerto'])
        writer.writerow(['profit_factor', f"{aggregate_analysis['profit_factor']:.2f}", 'ratio', 'Lucro total / Perda total'])
        writer.writerow(['total_return', f"{aggregate_analysis['total_return']:.2f}", 'USD', 'Retorno total acumulado'])
        writer.writerow(['sharpe_ratio', f"{aggregate_analysis['sharpe_ratio']:.2f}", 'ratio', 'Sharpe ratio anualizado'])
        writer.writerow(['max_drawdown', f"{aggregate_analysis['max_drawdown']:.2f}", 'USD', 'Maior queda do equity'])
        writer.writerow(['max_drawdown_pct', f"{aggregate_analysis['max_drawdown_pct']:.2f}", '%', 'Max drawdown percentual'])
        writer.writerow(['expected_value', f"{aggregate_analysis['expected_value']:.2f}", 'USD', 'Valor esperado por trade'])
        writer.writerow(['', '', '', ''])
        
        # Walk-Forward Averages
        writer.writerow(['WALK_FORWARD_AVERAGES', '', '', ''])
        writer.writerow(['avg_win_rate', f"{avg_win_rate:.4f}", 'ratio', 'Win rate médio (Walk-Forward)'])
        writer.writerow(['avg_sharpe_ratio', f"{avg_sharpe:.2f}", 'ratio', 'Sharpe ratio médio (Walk-Forward)'])
        writer.writerow(['avg_total_return', f"{avg_total_return:.2f}", 'USD', 'Retorno total médio (Walk-Forward)'])
        writer.writerow(['avg_max_drawdown', f"{avg_max_dd:.2f}", 'USD', 'Max drawdown médio (Walk-Forward)'])
        writer.writerow(['', '', '', ''])
        
        # Walk-Forward Periods
        writer.writerow(['WALK_FORWARD_PERIODS', '', '', ''])
        writer.writerow([
            'period', 'start_date', 'end_date', 'trades', 'win_rate', 
            'total_return', 'sharpe_ratio', 'max_drawdown'
        ])
        
        for r in results:
            writer.writerow([
                r['period_num'],
                r['period_start'].strftime('%Y-%m-%d'),
                r['period_end'].strftime('%Y-%m-%d'),
                r['total_trades'],
                f"{r['win_rate']:.4f}",
                f"{r['total_return']:.2f}",
                f"{r['sharpe_ratio']:.2f}",
                f"{r['max_drawdown']:.2f}"
            ])
    
    # Gera JSON para análise programática
    json_path = output_path.with_suffix('.json')
    json_data = {
        'baseline_summary': {
            'strategy': 'Mean_Reversion_Bollinger_Bands',
            'symbol': SYMBOL,
            'timeframe': 'H1',
            'years_of_data': YEARS_OF_DATA,
            'walk_forward_periods': len(results),
            'timestamp': timestamp
        },
        'aggregate_metrics': aggregate_analysis,
        'walk_forward_averages': {
            'avg_win_rate': float(avg_win_rate),
            'avg_sharpe_ratio': float(avg_sharpe),
            'avg_total_return': float(avg_total_return),
            'avg_max_drawdown': float(avg_max_dd)
        },
        'walk_forward_periods': [
            {
                'period_num': r['period_num'],
                'start_date': r['period_start'].strftime('%Y-%m-%d'),
                'end_date': r['period_end'].strftime('%Y-%m-%d'),
                'total_trades': r['total_trades'],
                'win_rate': float(r['win_rate']),
                'total_return': float(r['total_return']),
                'sharpe_ratio': float(r['sharpe_ratio']),
                'max_drawdown': float(r['max_drawdown'])
            }
            for r in results
        ]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"RELATÓRIO GERADO: {output_path}")
    logger.info(f"JSON GERADO: {json_path}")
    
    return output_path


# =====================================================
# BLOCO PRINCIPAL DE EXECUÇÃO
# =====================================================

def main():
    """
    Função principal de execução do protocolo de refutação
    """
    logger.info("=" * 80)
    logger.info("PROTOCOLO DE REFUTAÇÃO v1.0 - BASELINE CIENTÍFICO")
    logger.info("Estratégia: Mean Reversion com Bollinger Bands - EURUSD H1")
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
        
        # 4. Backtest completo para análise agregada
        logger.info("ETAPA 4: Backtest completo para análise agregada")
        all_trades = run_backtest(df)
        aggregate_analysis = analyze_results(all_trades)
        
        # 5. Geração de relatório de baseline
        logger.info("ETAPA 5: Geração de relatório de baseline")
        report_path = generate_baseline_report(results, all_trades)
        
        # 6. Resumo final
        logger.info("=" * 80)
        logger.info("RESULTADOS DO BASELINE CIENTÍFICO")
        logger.info("=" * 80)
        logger.info(f"Total de Trades: {aggregate_analysis['total_trades']}")
        logger.info(f"Win Rate: {aggregate_analysis['win_rate']:.2%}")
        logger.info(f"Profit Factor: {aggregate_analysis['profit_factor']:.2f}")
        logger.info(f"Retorno Total: ${aggregate_analysis['total_return']:.2f}")
        logger.info(f"Sharpe Ratio: {aggregate_analysis['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: ${aggregate_analysis['max_drawdown']:.2f} ({aggregate_analysis['max_drawdown_pct']:.2f}%)")
        logger.info("=" * 80)
        
        if results:
            logger.info("WALK-FORWARD AVERAGES:")
            avg_win_rate = np.mean([r['win_rate'] for r in results])
            avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
            avg_return = np.mean([r['total_return'] for r in results])
            logger.info(f"  Win Rate Médio: {avg_win_rate:.2%}")
            logger.info(f"  Sharpe Ratio Médio: {avg_sharpe:.2f}")
            logger.info(f"  Retorno Total Médio: ${avg_return:.2f}")
            logger.info("=" * 80)
        
        logger.info(f"RELATÓRIO SALVO EM: {report_path}")
        logger.info("BASELINE CIENTÍFICO CONCLUÍDO COM SUCESSO!")
        
        return {
            'success': True,
            'report_path': str(report_path),
            'aggregate_analysis': aggregate_analysis,
            'walk_forward_results': results
        }
        
    except Exception as e:
        logger.exception(f"ERRO durante execução do protocolo de refutação: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    result = main()
    if result['success']:
        print(f"\n✅ Baseline científico concluído!")
        print(f"📊 Relatório: {result['report_path']}")
    else:
        print(f"\n❌ Erro: {result.get('error', 'Desconhecido')}")
        exit(1)

