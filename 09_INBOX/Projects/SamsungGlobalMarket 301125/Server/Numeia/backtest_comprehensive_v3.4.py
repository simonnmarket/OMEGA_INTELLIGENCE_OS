#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST ABRANGENTE PROMETHEUS v3.4
Protocolo de Validação Abrangente - Varredura Sistemática de Todo o Market Watch

Objetivo: Descobrir o ativo com maior edge estatístico através de varredura completa
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

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

def get_symbols_by_category() -> Dict[str, List[str]]:
    """Obtém dinamicamente os símbolos do Market Watch por categoria."""
    if not mt5.initialize():
        print("Falha ao inicializar MT5")
        return {}
    
    all_symbols_info = mt5.symbols_get()
    symbols = {
        "forex_majors": [],
        "silver": [],
        "crypto": [],
        "crypto_btc": [],
        "cfd_stocks": []
    }
    
    major_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
    
    for s_info in all_symbols_info:
        symbol = s_info.name
        path = s_info.path
        description = s_info.description.lower()
        
        # Habilitar o símbolo no Market Watch para obter dados
        if not mt5.symbol_select(symbol, True):
            continue
        
        # Forex Majors
        if "Forex" in path or "FX" in path:
            if len(symbol) >= 6:
                base, quote = symbol[:3], symbol[3:6]
                if base in major_currencies and quote in major_currencies:
                    symbols["forex_majors"].append(symbol)
        
        # Silver
        if "XAGUSD" in symbol or "XAG" in symbol:
            symbols["silver"].append(symbol)
        
        # Crypto
        if "Crypto" in path or "crypto" in description:
            symbols["crypto"].append(symbol)
            if "BTCUSD" in symbol or "BTC" in symbol:
                symbols["crypto_btc"].append(symbol)
        
        # CFD Stocks/Indices (Foco em EUA)
        if ("Stocks" in path or "Indices" in path or "Stock" in path) and ("US" in symbol or ".us" in symbol.lower()):
            symbols["cfd_stocks"].append(symbol)
    
    # Limitar para não sobrecarregar (pegar os 10 primeiros por categoria)
    for key in symbols:
        if len(symbols[key]) > 10:
            symbols[key] = symbols[key][:10]
    
    return symbols

def is_market_open(symbol: str) -> bool:
    """Verifica se o mercado está aberto para o símbolo"""
    try:
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
        
        # Verificar se o tick é recente (últimos 15 minutos)
        tick_age = datetime.now().timestamp() - tick.time
        if tick_age > 900:  # 15 minutos
            return False
        
        # Verificar se há sessão de trading
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return False
        
        # Crypto é sempre aberto (24/7)
        if "Crypto" in symbol_info.path or "crypto" in symbol_info.description.lower():
            return True
        
        # Para outros ativos, verificar horário de sessão
        return True  # Assumir aberto se tick é recente
    except:
        return False

def run_backtest_for_symbol(symbol: str, lookback_days: int = 30) -> Optional[Dict]:
    """
    Executa o backtest para um único símbolo usando a estratégia multi-timeframe.
    Retorna métricas ou None se falhar.
    """
    try:
        # Verificar se símbolo está disponível
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"symbol": symbol, "error": "Symbol not found", "decision": "REJECT"}
        
        # Verificar se mercado está aberto (para análise realtime)
        market_open = is_market_open(symbol)
        
        # Tentar obter dados históricos (últimos 30 dias)
        from_date = datetime.now() - timedelta(days=lookback_days)
        to_date = datetime.now()
        
        # Dados multi-timeframe - tentar copy_rates_range primeiro
        h4_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H4, from_date, to_date)
        h1_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, from_date, to_date)
        m5_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, from_date, to_date)
        
        # Fallback: usar copy_rates_from_pos se copy_rates_range falhar
        if h4_data is None or len(h4_data) < 50:
            h4_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 200)
        if h1_data is None or len(h1_data) < 50:
            h1_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 200)
        if m5_data is None or len(m5_data) < 50:
            m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 200)
        
        if h4_data is None or h1_data is None or m5_data is None:
            return {"symbol": symbol, "error": "No historical data", "market_open": market_open, "decision": "REJECT"}
        
        if len(h4_data) < 50 or len(h1_data) < 50 or len(m5_data) < 50:
            return {"symbol": symbol, "error": "Insufficient data", "market_open": market_open, "decision": "REJECT"}
        
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
                    
                    # Simular fechamento (buscar próximo candle que atinge SL ou TP)
                    for j in range(i + 1, min(i + 100, len(m5_df))):
                        high = m5_df.iloc[j]['high']
                        low = m5_df.iloc[j]['low']
                        
                        if high >= tp:
                            # TP atingido
                            exit_price = tp
                            profit = (exit_price - entry_price) / point * point * 0.02  # Volume 0.02
                            trades.append({
                                "entry": entry_price,
                                "exit": exit_price,
                                "profit": profit,
                                "reason": "TP"
                            })
                            break
                        elif low <= sl:
                            # SL atingido
                            exit_price = sl
                            profit = (exit_price - entry_price) / point * point * 0.02
                            trades.append({
                                "entry": entry_price,
                                "exit": exit_price,
                                "profit": profit,
                                "reason": "SL"
                            })
                            break
            except Exception as e:
                continue
        
        if len(trades) == 0:
            return None
        
        # Calcular métricas
        profits = [t['profit'] for t in trades]
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [abs(p) for p in profits if p < 0]
        
        total_profit = sum(winning_trades) if winning_trades else 0
        total_loss = sum(losing_trades) if losing_trades else 0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0)
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        expectancy = sum(profits) / len(trades) if trades else 0
        
        # Calcular drawdown
        cumulative = 0
        peak = 0
        max_drawdown = 0
        for profit in profits:
            cumulative += profit
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "symbol": symbol,
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
            "win_rate": round(win_rate, 2),
            "expectancy": round(expectancy, 4),
            "max_drawdown": round(max_drawdown, 4),
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "total_profit": round(total_profit, 2),
            "total_loss": round(total_loss, 2),
            "market_open": market_open,
            "decision": "APPROVE" if (profit_factor > 1.3 and win_rate > 55 and len(trades) > 30) else "REJECT"
        }
    
    except Exception as e:
        print(f"Erro ao processar {symbol}: {e}")
        return None

def analyze_crypto_realtime(crypto_symbols: List[str]) -> Dict:
    """Analisa performance das crypto em tempo real"""
    results = {}
    print("\n" + "=" * 80)
    print("ANÁLISE REALTIME - CRIPTOMOEDAS (MERCADO ABERTO 24/7)")
    print("=" * 80)
    
    for symbol in crypto_symbols:
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                continue
            
            # Obter dados recentes para análise
            m5_data = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
            if m5_data is None or len(m5_data) < 20:
                continue
            
            df = pd.DataFrame(m5_data)
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['rsi'] = df['close'].diff()
            df['rsi_gain'] = (df['rsi'].where(df['rsi'] > 0, 0)).rolling(window=14).mean()
            df['rsi_loss'] = (-df['rsi'].where(df['rsi'] < 0, 0)).rolling(window=14).mean()
            df['rsi'] = 100 - (100 / (1 + (df['rsi_gain'] / df['rsi_loss'])))
            
            current_price = tick.ask
            ma20 = df['ma20'].iloc[-1] if not pd.isna(df['ma20'].iloc[-1]) else None
            rsi = df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else None
            
            # Verificar condições de sinal
            signal = None
            if ma20 and rsi:
                if current_price > ma20 and 40 < rsi < 60:
                    signal = "🟢 COMPRA POTENCIAL"
                elif current_price < ma20:
                    signal = "🔴 AGUARDAR"
            
            results[symbol] = {
                "price": current_price,
                "ma20": round(ma20, 2) if ma20 else None,
                "rsi": round(rsi, 2) if rsi else None,
                "signal": signal,
                "spread": round((tick.ask - tick.bid) / tick.ask * 10000, 2) if tick.ask > 0 else None
            }
            
            print(f"{symbol}: Preço={current_price:.2f} | MA20={ma20:.2f if ma20 else 'N/A'} | RSI={rsi:.1f if rsi else 'N/A'} | {signal if signal else 'N/A'}")
        except Exception as e:
            continue
    
    return results

if __name__ == "__main__":
    print("=" * 80)
    print("BACKTEST ABRANGENTE PROMETHEUS v3.4")
    print("Protocolo de Validação Abrangente - Varredura Sistemática")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not mt5.initialize():
        print("Falha ao inicializar MT5")
        exit(1)
    
    # Obter símbolos por categoria
    print("Obtendo símbolos do Market Watch...")
    asset_categories = get_symbols_by_category()
    
    print("\nCategorias e Símbolos encontrados para teste:")
    total_symbols = 0
    for cat, syms in asset_categories.items():
        print(f"- {cat}: {len(syms)} símbolos - {syms[:5]}{'...' if len(syms) > 5 else ''}")
        total_symbols += len(syms)
    
    print(f"\nTotal de símbolos para testar: {total_symbols}")
    
    # ANÁLISE REALTIME DAS CRYPTO (enquanto mercado está aberto)
    if asset_categories.get("crypto"):
        analyze_crypto_realtime(asset_categories["crypto"])
    
    print("\n" + "=" * 80)
    
    all_results = []
    
    for category, symbol_list in asset_categories.items():
        if not symbol_list:
            continue
        
        print(f"\n--- Iniciando Backtest para a categoria: {category} ---")
        print(f"Total de símbolos na categoria: {len(symbol_list)}")
        
        for idx, symbol in enumerate(symbol_list, 1):
            print(f"  [{idx}/{len(symbol_list)}] Testando {symbol}...", end=" ")
            result = run_backtest_for_symbol(symbol)
            
            if result:
                all_results.append(result)
                if 'error' in result:
                    market_status = "🟢 ABERTO" if result.get('market_open', False) else "🔴 FECHADO"
                    print(f"⚠️ {result['error']} | {market_status}")
                else:
                    status = "✅ APROVADO" if result['decision'] == 'APPROVE' else "❌ REJEITADO"
                    market_status = "🟢 ABERTO" if result.get('market_open', False) else "🔴 FECHADO"
                    print(f"{status} | {market_status} | PF: {result['profit_factor']:.2f} | WR: {result['win_rate']:.1f}% | Trades: {result['total_trades']}")
            else:
                print("❌ FALHOU (erro desconhecido)")
    
    mt5.shutdown()
    
    if not all_results:
        print("\n" + "=" * 80)
        print("NENHUM RESULTADO OBTIDO")
        print("Verificar conexão MT5 e disponibilidade de dados históricos.")
        print("=" * 80)
        exit(1)
    
    # Criar o Ranking de Performance Global
    df_results = pd.DataFrame(all_results)
    
    # Separar resultados com erro dos resultados válidos
    valid_results = df_results[~df_results.get('profit_factor', pd.Series()).isna()]
    error_results = df_results[df_results.get('profit_factor', pd.Series()).isna()]
    
    if not valid_results.empty:
        valid_results = valid_results.sort_values(by=['profit_factor', 'win_rate'], ascending=False)
        
        print("\n" + "=" * 80)
        print("RANKING GLOBAL DE PERFORMANCE (RESULTADOS VÁLIDOS)")
        print("=" * 80)
        display_cols = ['symbol', 'profit_factor', 'win_rate', 'total_trades', 'market_open', 'decision']
        available_cols = [col for col in display_cols if col in valid_results.columns]
        print(valid_results[available_cols].to_string())
    
    if not error_results.empty:
        print("\n" + "=" * 80)
        print("SÍMBOLOS COM ERROS (MERCADO FECHADO OU DADOS INSUFICIENTES)")
        print("=" * 80)
        error_display = error_results[['symbol', 'error', 'market_open']].to_string() if 'error' in error_results.columns else error_results[['symbol']].to_string()
        print(error_display)
    
    # Usar valid_results para ranking final
    df_results = valid_results if not valid_results.empty else df_results
    
    # Salvar o ranking para análise
    csv_file = "backtest_global_ranking_v3.4.csv"
    df_results.to_csv(csv_file, index=False)
    print(f"\nRanking salvo em: {csv_file}")
    
    # Identificar o(s) vencedor(es)
    winners = df_results[df_results['decision'] == 'APPROVE']
    
    print("\n" + "=" * 80)
    if not winners.empty:
        print("ATIVOS VENCEDORES (APROVADOS)")
        print("=" * 80)
        print(winners[['symbol', 'profit_factor', 'win_rate', 'total_trades', 'expectancy']].to_string())
        
        # Vencedor global (maior profit_factor)
        global_winner = winners.iloc[0]
        print(f"\n🏆 VENCEDOR GLOBAL: {global_winner['symbol']}")
        print(f"   Profit Factor: {global_winner['profit_factor']:.2f}")
        print(f"   Win Rate: {global_winner['win_rate']:.1f}%")
        print(f"   Total Trades: {global_winner['total_trades']}")
        print(f"   Expectancy: {global_winner['expectancy']:.4f}")
    else:
        print("NENHUM ATIVO APROVADO ENCONTRADO")
        print("=" * 80)
        print("A estratégia não atendeu aos critérios em nenhum ativo testado.")
        print("Recomendação: Revisar estratégia ou critérios de aprovação.")
    
    print(f"\nFim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

