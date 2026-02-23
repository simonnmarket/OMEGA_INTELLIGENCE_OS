#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST DE VALIDAÇÃO DE INTELIGÊNCIA PROMETHEUS v3.6
Protocolo de Validação Comparativa - Baseline vs Inteligência de Mercado

Objetivo: Comprovar estatisticamente se o filtro de inteligência melhora a lucratividade
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

# --- HELPER FUNCTIONS ---

def calculate_ma(data: pd.DataFrame, period: int) -> float:
    """Calcula média móvel simples"""
    return data['close'].rolling(window=period).mean().iloc[-1]

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
    """Calcula RSI (Relative Strength Index)"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_volume_average(data: pd.DataFrame, period: int = 20) -> float:
    """Calcula média de volume"""
    return data['tick_volume'].rolling(window=period).mean().iloc[-1]

def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """Calcula Profit Factor"""
    if trades.empty:
        return 0.0
    
    profits = trades['profit'].values
    winning = profits[profits > 0]
    losing = abs(profits[profits < 0])
    
    total_profit = winning.sum() if len(winning) > 0 else 0
    total_loss = losing.sum() if len(losing) > 0 else 0
    
    if total_loss == 0:
        return float('inf') if total_profit > 0 else 0.0
    
    return total_profit / total_loss

def calculate_win_rate(trades: pd.DataFrame) -> float:
    """Calcula Win Rate (%)"""
    if trades.empty:
        return 0.0
    winning = (trades['profit'] > 0).sum()
    return (winning / len(trades)) * 100

def calculate_expectancy(trades: pd.DataFrame) -> float:
    """Calcula Expectancy"""
    if trades.empty:
        return 0.0
    return trades['profit'].mean()

# --- INTELIGÊNCIA DE MERCADO ---

def is_optimal_trading_window(timestamp: int) -> bool:
    """
    Verifica se estamos na janela ideal de trading (Londres/NY).
    Londres: 08:00-12:00 GMT
    NY: 13:00-17:00 GMT
    Sobreposição: 13:00-17:00 GMT (melhor liquidez)
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        hour = dt.hour  # GMT
        
        # Janela de Londres (08:00-12:00 GMT)
        london_window = 8 <= hour < 12
        
        # Janela de NY (13:00-17:00 GMT)
        ny_window = 13 <= hour < 17
        
        # Sobreposição (13:00-17:00 GMT) - melhor janela
        overlap_window = 13 <= hour < 17
        
        # Retornar True se estiver em qualquer janela ideal
        return london_window or ny_window or overlap_window
    except:
        return True  # Se erro, permitir trading (não bloquear)

# --- LÓGICA DE BACKTEST COMPARATIVO ---

def run_backtest_for_symbol(symbol: str, use_intelligence_filter: bool = False, lookback_days: int = 30) -> Optional[Dict]:
    """
    Executa o backtest para um símbolo, com ou sem o filtro de inteligência.
    """
    try:
        # Obter dados históricos
        from_date = datetime.now() - timedelta(days=lookback_days)
        to_date = datetime.now()
        
        # Dados multi-timeframe
        h4_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H4, from_date, to_date)
        h1_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, from_date, to_date)
        m5_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, from_date, to_date)
        
        # Fallback
        if h4_data is None or len(h4_data) < 50:
            h4_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 200)
        if h1_data is None or len(h1_data) < 50:
            h1_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 200)
        if m5_data is None or len(m5_data) < 50:
            m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 200)
        
        if h4_data is None or h1_data is None or m5_data is None:
            return None
        
        if len(h4_data) < 50 or len(h1_data) < 50 or len(m5_data) < 50:
            return None
        
        h4_df = pd.DataFrame(h4_data)
        h1_df = pd.DataFrame(h1_data)
        m5_df = pd.DataFrame(m5_data)
        
        # Calcular indicadores
        h4_df['ma20'] = h4_df['close'].rolling(window=20).mean()
        h4_df['ma50'] = h4_df['close'].rolling(window=50).mean()
        h1_df['ma20'] = h1_df['close'].rolling(window=20).mean()
        h1_df['ma50'] = h1_df['close'].rolling(window=50).mean()
        m5_df['ma20'] = m5_df['close'].rolling(window=20).mean()
        m5_df['rsi'] = m5_df['close'].diff()
        m5_df['rsi_gain'] = (m5_df['rsi'].where(m5_df['rsi'] > 0, 0)).rolling(window=14).mean()
        m5_df['rsi_loss'] = (-m5_df['rsi'].where(m5_df['rsi'] < 0, 0)).rolling(window=14).mean()
        m5_df['rsi'] = 100 - (100 / (1 + (m5_df['rsi_gain'] / m5_df['rsi_loss'])))
        m5_df['volume_avg'] = m5_df['tick_volume'].rolling(window=20).mean()
        
        # Simular trades
        trades = []
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return None
        
        point = symbol_info.point
        if point <= 0:
            return None
        
        # Iterar sobre os dados M5 para encontrar sinais
        for i in range(50, len(m5_df)):
            try:
                # FILTRO DE INTELIGÊNCIA (NOVO)
                if use_intelligence_filter:
                    m5_time = m5_df.iloc[i]['time']
                    if not is_optimal_trading_window(m5_time):
                        continue  # Pula o candle se não estiver na janela ideal
                
                # Obter índices correspondentes em H4 e H1
                m5_time = m5_df.iloc[i]['time']
                
                # Encontrar candle H4 correspondente
                h4_idx = h4_df[h4_df['time'] <= m5_time].index
                if len(h4_idx) < 2:
                    continue
                h4_idx = h4_idx[-1]
                
                # Encontrar candle H1 correspondente
                h1_idx = h1_df[h1_df['time'] <= m5_time].index
                if len(h1_idx) < 2:
                    continue
                h1_idx = h1_idx[-1]
                
                # Verificar condições
                if pd.isna(h4_df.iloc[h4_idx]['ma20']) or pd.isna(h4_df.iloc[h4_idx]['ma50']):
                    continue
                if pd.isna(h1_df.iloc[h1_idx]['ma20']) or pd.isna(h1_df.iloc[h1_idx]['ma50']):
                    continue
                if pd.isna(m5_df.iloc[i]['ma20']) or pd.isna(m5_df.iloc[i]['rsi']):
                    continue
                
                h4_trend_up = h4_df.iloc[h4_idx]['ma20'] > h4_df.iloc[h4_idx]['ma50']
                h1_confirmation_up = h1_df.iloc[h1_idx]['ma20'] > h1_df.iloc[h1_idx]['ma50']
                m5_entry_up = m5_df.iloc[i]['close'] > m5_df.iloc[i]['ma20']
                rsi_ok = 40 < m5_df.iloc[i]['rsi'] < 60
                volume_spike = m5_df.iloc[i]['tick_volume'] > m5_df.iloc[i]['volume_avg']
                
                # Sinal de COMPRA
                if h4_trend_up and h1_confirmation_up and m5_entry_up and rsi_ok and volume_spike:
                    entry_price = m5_df.iloc[i]['close']
                    sl = entry_price - 50 * point
                    tp = entry_price + 100 * point
                    
                    # Simular fechamento
                    for j in range(i + 1, min(i + 100, len(m5_df))):
                        high = m5_df.iloc[j]['high']
                        low = m5_df.iloc[j]['low']
                        
                        if high >= tp:
                            exit_price = tp
                            profit = (exit_price - entry_price) / point * point * 0.02
                            trades.append({
                                "entry_time": m5_time,
                                "entry_price": entry_price,
                                "exit_time": m5_df.iloc[j]['time'],
                                "exit_price": exit_price,
                                "profit": profit
                            })
                            break
                        elif low <= sl:
                            exit_price = sl
                            profit = (exit_price - entry_price) / point * point * 0.02
                            trades.append({
                                "entry_time": m5_time,
                                "entry_price": entry_price,
                                "exit_time": m5_df.iloc[j]['time'],
                                "exit_price": exit_price,
                                "profit": profit
                            })
                            break
            except Exception as e:
                continue
        
        if len(trades) == 0:
            return {
                "symbol": symbol,
                "filter_used": use_intelligence_filter,
                "decision": "REJECT",
                "reason": "Nenhum trade gerado"
            }
        
        # Calcular métricas
        trades_df = pd.DataFrame(trades)
        
        profit_factor = calculate_profit_factor(trades_df)
        win_rate = calculate_win_rate(trades_df)
        expectancy = calculate_expectancy(trades_df)
        
        # Calcular drawdown
        cumulative = trades_df['profit'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = running_max - cumulative
        max_drawdown = drawdown.max()
        
        return {
            "symbol": symbol,
            "filter_used": use_intelligence_filter,
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
            "win_rate": round(win_rate, 2),
            "expectancy": round(expectancy, 4),
            "max_drawdown": round(max_drawdown, 4),
            "total_trades": len(trades)
        }
    
    except Exception as e:
        return {
            "symbol": symbol,
            "filter_used": use_intelligence_filter,
            "error": str(e),
            "decision": "REJECT"
        }

def analyze_and_decide(results: pd.DataFrame) -> Dict:
    """
    Analisa os resultados comparativos e toma a decisão final.
    """
    # Separar baseline e com filtro
    baseline = results[results['filter_used'] == False].set_index('symbol')
    with_filter = results[results['filter_used'] == True].set_index('symbol')
    
    # Pegar apenas símbolos que têm ambos os resultados
    common_symbols = baseline.index.intersection(with_filter.index)
    
    if len(common_symbols) == 0:
        return {
            'decision': 'REJECT',
            'reason': 'Nenhum símbolo comum entre baseline e filtro'
        }
    
    baseline = baseline.loc[common_symbols]
    with_filter = with_filter.loc[common_symbols]
    
    # Calcular melhorias
    comparison = pd.DataFrame({
        'pf_improvement': with_filter['profit_factor'] - baseline['profit_factor'],
        'wr_improvement': with_filter['win_rate'] - baseline['win_rate'],
        'exp_improvement': with_filter['expectancy'] - baseline['expectancy'],
        'trade_reduction_pct': ((baseline['total_trades'] - with_filter['total_trades']) / baseline['total_trades'] * 100).fillna(0)
    })
    
    # Critérios de Aprovação do Conselho
    pf_improvement_mean = comparison['pf_improvement'].mean()
    exp_improvement_mean = comparison['exp_improvement'].mean()
    trade_reduction_mean = comparison['trade_reduction_pct'].mean()
    
    approval = (
        (pf_improvement_mean > 0.1) and  # Melhora > 10% no Profit Factor
        (exp_improvement_mean > 0) and   # Melhora na Expectancy
        (trade_reduction_mean < 60)      # Não elimina mais de 60% dos trades
    )
    
    return {
        'comparison_metrics': comparison,
        'pf_improvement_mean': pf_improvement_mean,
        'exp_improvement_mean': exp_improvement_mean,
        'trade_reduction_mean': trade_reduction_mean,
        'approval_recommendation': approval,
        'decision': "APPROVE" if approval else "REJECT",
        'common_symbols': list(common_symbols)
    }

if __name__ == "__main__":
    print("=" * 80)
    print("BACKTEST DE VALIDAÇÃO DE INTELIGÊNCIA PROMETHEUS v3.6")
    print("Protocolo de Validação Comparativa")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not mt5.initialize():
        print("Falha ao inicializar MT5")
        exit(1)
    
    # Cesta de ativos do plano v3.4 - Foco em ativos disponíveis agora
    asset_basket = ["XAUUSD", "BTCUSD", "ETHUSD"]  # Foco em ativos 24/7 primeiro
    
    # Verificar quais símbolos estão disponíveis
    available_symbols = []
    for symbol in asset_basket:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            available_symbols.append(symbol)
        else:
            print(f"⚠️ {symbol} não disponível, pulando...")
    
    if not available_symbols:
        print("❌ Nenhum símbolo disponível para teste")
        mt5.shutdown()
        exit(1)
    
    print(f"Símbolos para validação: {available_symbols}")
    print()
    
    all_results = []
    
    for asset in available_symbols:
        print(f"--- Validando {asset} ---")
        
        # Rodar baseline (sem filtro)
        print(f"  [BASELINE] Testando sem filtro...", end=" ")
        baseline_res = run_backtest_for_symbol(asset, use_intelligence_filter=False)
        if baseline_res and 'error' not in baseline_res:
            print(f"✅ PF: {baseline_res.get('profit_factor', 'N/A')} | Trades: {baseline_res.get('total_trades', 0)}")
            all_results.append(baseline_res)
        else:
            print(f"❌ Falhou")
            if baseline_res:
                all_results.append(baseline_res)
        
        # Rodar com filtro
        print(f"  [FILTRO] Testando com inteligência...", end=" ")
        filter_res = run_backtest_for_symbol(asset, use_intelligence_filter=True)
        if filter_res and 'error' not in filter_res:
            print(f"✅ PF: {filter_res.get('profit_factor', 'N/A')} | Trades: {filter_res.get('total_trades', 0)}")
            all_results.append(filter_res)
        else:
            print(f"❌ Falhou")
            if filter_res:
                all_results.append(filter_res)
        
        print()
    
    mt5.shutdown()
    
    if not all_results:
        print("❌ Nenhum resultado obtido")
        exit(1)
    
    # Criar DataFrame e analisar
    try:
        df_results = pd.DataFrame(all_results)
        final_decision = analyze_and_decide(df_results)
        
        print("=" * 80)
        print("RESULTADO FINAL DA VALIDAÇÃO")
        print("=" * 80)
        print(f"DECISÃO: {final_decision.get('decision', 'UNKNOWN')}")
        print()
        
        if final_decision.get('decision') == 'APPROVE':
            print("✅ FILTRO DE INTELIGÊNCIA APROVADO")
            print()
            print("MÉTRICAS DE MELHORIA:")
            pf_imp = final_decision.get('pf_improvement_mean', 0)
            exp_imp = final_decision.get('exp_improvement_mean', 0)
            trade_red = final_decision.get('trade_reduction_mean', 0)
            print(f"  Melhoria média no Profit Factor: {pf_imp:.2f} ({pf_imp*100:.1f}%)")
            print(f"  Melhoria média na Expectancy: {exp_imp:.4f}")
            print(f"  Redução média no Nº de Trades: {trade_red:.1f}%")
            print()
            if 'comparison_metrics' in final_decision:
                print("DETALHES POR SÍMBOLO:")
                print(final_decision['comparison_metrics'].to_string())
        else:
            print("❌ FILTRO DE INTELIGÊNCIA REJEITADO")
            print()
            if 'reason' in final_decision:
                print(f"RAZÃO: {final_decision['reason']}")
            else:
                print("RAZÃO:")
                pf_imp = final_decision.get('pf_improvement_mean', 0)
                exp_imp = final_decision.get('exp_improvement_mean', 0)
                trade_red = final_decision.get('trade_reduction_mean', 0)
                if pf_imp <= 0.1:
                    print(f"  - Melhoria no Profit Factor insuficiente: {pf_imp:.2f} (mínimo: 0.1)")
                if exp_imp <= 0:
                    print(f"  - Expectancy não melhorou: {exp_imp:.4f}")
                if trade_red >= 60:
                    print(f"  - Redução de trades excessiva: {trade_red:.1f}% (máximo: 60%)")
        
        # Salvar resultados (SEMPRE salvar, mesmo se decisão for REJECT)
        output_dir = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(output_dir, "backtest_validation_results_v3.6.csv")
        df_results.to_csv(results_file, index=False)
        print()
        print(f"✅ Resultados salvos em: {results_file}")
        
        if 'comparison_metrics' in final_decision and final_decision['comparison_metrics'] is not None:
            comparison_file = os.path.join(output_dir, "validation_comparison_v3.6.csv")
            final_decision['comparison_metrics'].to_csv(comparison_file)
            print(f"✅ Comparação salva em: {comparison_file}")
        
    except Exception as e:
        print(f"❌ ERRO ao processar resultados: {e}")
        import traceback
        traceback.print_exc()
        # Salvar resultados mesmo com erro
        try:
            output_dir = os.path.dirname(os.path.abspath(__file__))
            results_file = os.path.join(output_dir, "backtest_validation_results_v3.6.csv")
            df_results.to_csv(results_file, index=False)
            print(f"✅ Resultados parciais salvos em: {results_file}")
        except:
            pass
    
    print()
    print(f"Resultados salvos em:")
    print(f"  - backtest_validation_results_v3.6.csv")
    if 'comparison_metrics' in final_decision:
        print(f"  - validation_comparison_v3.6.csv")
    print()
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

