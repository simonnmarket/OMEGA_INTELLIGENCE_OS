# ==============================================================================
# SILVER SYSTEM: ANÁLISE DE PERFORMANCE ESPECIALIZADA
# Projeto: SilverGMarket (Independente)
# Objetivo: Analisar logs do Sistema Silver (apenas XAG)
# Data: 26/11/2025
# ==============================================================================

import json
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
import re
import sys
import os

# Tentar importar MetaTrader5 para acesso direto ao histórico
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# Configurações específicas para Silver
LOG_FILE_NAME = "silver_telemetry.log"
MAGIC_NUMBER = 99992  # Magic Number do Sistema Silver
PERIODO_ANALISE_HORAS = 24

# ==============================================================================
# FUNÇÕES DE CÁLCULO
# ==============================================================================

def calcular_drawdown(pnl_history):
    """Calcula o Maximum Drawdown (MDD)."""
    if not pnl_history or len(pnl_history) == 0:
        return 0.0
    equity_curve = np.cumsum(np.array(pnl_history, dtype=float))
    max_peak = equity_curve[0]
    max_drawdown = 0.0
    for equity in equity_curve:
        max_peak = max(max_peak, equity)
        drawdown_atual = max_peak - equity
        max_drawdown = max(max_drawdown, drawdown_atual)
    return float(max_drawdown)

def calcular_sharpe_ratio(pnl_history, risk_free_rate=0.0001):
    """Calcula o Sharpe Ratio."""
    if len(pnl_history) < 2:
        return 0.0
    pnl_array = np.array(pnl_history, dtype=float)
    std_dev = np.std(pnl_array, ddof=1)
    if std_dev == 0:
        return 0.0
    avg_return = np.mean(pnl_array)
    return float((avg_return - risk_free_rate) / std_dev)

def formatar_valor_monetario(valor):
    """Formata valor monetário."""
    if valor >= 0:
        return f"${valor:,.2f}"
    else:
        return f"-${abs(valor):,.2f}"

def obter_status_sharpe(sharpe):
    """Retorna status do Sharpe Ratio."""
    if sharpe is None:
        return "N/A"
    if sharpe >= 1.0:
        return "✅ EXCELENTE"
    elif sharpe >= 0.5:
        return "✅ BOM"
    elif sharpe >= 0:
        return "⚠️ BAIXO"
    else:
        return "❌ NEGATIVO"

# ==============================================================================
# COLETA DE DADOS
# ==============================================================================

def ler_logs_silver():
    """Lê e processa logs JSON do Sistema Silver."""
    trades = {}
    sinais_gerados = defaultdict(int)
    ordens_tentadas = 0
    ordens_executadas = 0
    ordens_falhas = 0
    risk_metrics = defaultdict(int)
    pnl_history = []
    timeline_execucao = []
    
    if not os.path.exists(LOG_FILE_NAME):
        return trades, sinais_gerados, ordens_tentadas, ordens_executadas, ordens_falhas, risk_metrics, pnl_history, timeline_execucao
    
    try:
        with open(LOG_FILE_NAME, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    match = re.search(r'\{.*\}', line)
                    if not match:
                        continue
                    
                    entry = json.loads(match.group(0))
                    
                    if 'timestamp' in entry and 'data' in entry:
                        event = entry.get('event')
                        data = entry.get('data', {})
                        timestamp = entry.get('timestamp', '')
                    else:
                        event = entry.get('event')
                        data = entry
                        timestamp = datetime.now().isoformat()
                    
                    ticket = data.get('ticket') or data.get('trade_id')
                    symbol = data.get('symbol', 'UNKNOWN')
                    
                    if event == 'signal_detected':
                        sinais_gerados[symbol] += 1
                    
                    if event == 'position_opened':
                        ordens_executadas += 1
                        if ticket:
                            trades[ticket] = {
                                'symbol': symbol,
                                'entry_price': data.get('entry_price'),
                                'pnl': 0.0,
                                'closed': False,
                                'is_parcial': False,
                                'parcial_pnl': 0.0,
                                'volume': data.get('volume'),
                                'timestamp': timestamp
                            }
                            timeline_execucao.append({
                                'timestamp': timestamp,
                                'symbol': symbol,
                                'ticket': ticket,
                                'resultado': 'EXECUTADA'
                            })
                    
                    elif event == 'error_opening':
                        ordens_falhas += 1
                        timeline_execucao.append({
                            'timestamp': timestamp,
                            'symbol': symbol,
                            'ticket': None,
                            'resultado': 'FALHA'
                        })
                    
                    elif event == 'position_partially_closed':
                        if ticket in trades:
                            trades[ticket]['is_parcial'] = True
                            parcial_pnl = data.get('pnl_realized', data.get('pnl', 0.0))
                            trades[ticket]['parcial_pnl'] += float(parcial_pnl)
                            pnl_history.append(float(parcial_pnl))
                            risk_metrics['parcial_closed_count'] += 1
                    
                    elif event == 'position_closed':
                        if ticket in trades:
                            trades[ticket]['closed'] = True
                            final_pnl = data.get('pnl', data.get('final_pnl', 0.0))
                            total_pnl = trades[ticket]['parcial_pnl'] + float(final_pnl)
                            trades[ticket]['pnl'] = total_pnl
                            
                            if not trades[ticket]['is_parcial']:
                                pnl_history.append(float(total_pnl))
                            else:
                                pnl_history.append(float(final_pnl))
                    
                    elif event == 'risk_management':
                        action = data.get('action', '')
                        if 'BREAK_EVEN' in action.upper():
                            risk_metrics['break_even_hit'] += 1
                        elif 'TRAILING_STOP' in action.upper():
                            risk_metrics['trailing_stop_moves'] += 1
                            
                except:
                    continue
                    
        ordens_tentadas = ordens_executadas + ordens_falhas
        
    except Exception as e:
        print(f"⚠️ Erro ao ler logs: {e}")
    
    return trades, sinais_gerados, ordens_tentadas, ordens_executadas, ordens_falhas, risk_metrics, pnl_history, timeline_execucao

def ler_historico_mt5_silver(days_back=1):
    """Lê histórico de deals do MT5 apenas do Sistema Silver (Magic 99992)."""
    if not MT5_AVAILABLE:
        return {}, []
    
    mt5_trades = {}
    mt5_pnl_history = []
    
    try:
        if not mt5.initialize():
            return mt5_trades, mt5_pnl_history
        
        date_from = datetime.now() - timedelta(days=days_back)
        date_to = datetime.now()
        
        deals = mt5.history_deals_get(date_from, date_to)
        if not deals:
            mt5.shutdown()
            return mt5_trades, mt5_pnl_history
        
        # Filtrar deals do Sistema Silver (Magic 99992)
        silver_deals = [d for d in deals if getattr(d, 'magic', 0) == MAGIC_NUMBER]
        
        deals_por_posicao = defaultdict(list)
        for deal in silver_deals:
            pos_id = getattr(deal, 'position_id', getattr(deal, 'ticket', 0))
            deals_por_posicao[pos_id].append(deal)
        
        for pos_id, deal_list in deals_por_posicao.items():
            deal_list.sort(key=lambda d: getattr(d, 'time', 0))
            total_pnl = sum(getattr(d, 'profit', 0) for d in deal_list)
            
            if deal_list:
                first_deal = deal_list[0]
                symbol = getattr(first_deal, 'symbol', 'UNKNOWN')
                
                is_parcial = len(deal_list) > 2
                parcial_pnl = sum(getattr(d, 'profit', 0) for d in deal_list[:-1]) if is_parcial else 0.0
                final_pnl = getattr(deal_list[-1], 'profit', 0) if deal_list else 0.0
                
                mt5_trades[pos_id] = {
                    'symbol': symbol,
                    'pnl': total_pnl,
                    'closed': True,
                    'is_parcial': is_parcial,
                    'parcial_pnl': parcial_pnl
                }
                
                if is_parcial:
                    mt5_pnl_history.append(parcial_pnl)
                    mt5_pnl_history.append(final_pnl)
                else:
                    mt5_pnl_history.append(total_pnl)
        
        mt5.shutdown()
        
    except Exception as e:
        print(f"⚠️ Erro ao ler histórico MT5: {e}")
        if MT5_AVAILABLE:
            try:
                mt5.shutdown()
            except:
                pass
    
    return mt5_trades, mt5_pnl_history

# ==============================================================================
# GERAÇÃO DE RELATÓRIO
# ==============================================================================

def gerar_relatorio_silver():
    """Gera relatório de performance do Sistema Silver."""
    
    print("🥈 SILVER SYSTEM: Análise de Performance")
    print("   Projeto: SilverGMarket (Independente)")
    print("   Sistema especializado em Prata (XAG)")
    print()
    
    # Coletar dados
    trades_log, sinais_gerados, ordens_tentadas, ordens_executadas, ordens_falhas, risk_metrics, pnl_history, timeline = ler_logs_silver()
    trades_mt5, pnl_history_mt5 = ler_historico_mt5_silver(days_back=1)
    
    # Combinar dados
    trades = trades_log.copy()
    for ticket, trade_mt5 in trades_mt5.items():
        if ticket not in trades:
            trades[ticket] = trade_mt5
        elif not trades[ticket].get('closed', False) and trade_mt5.get('closed', False):
            trades[ticket].update(trade_mt5)
    
    pnl_history.extend(pnl_history_mt5)
    
    # Calcular métricas
    closed_trades = [t for t in trades.values() if t.get('closed', False)]
    
    if not closed_trades:
        print("⚠️ Nenhum trade fechado encontrado.")
        print("   O sistema pode estar rodando, mas ainda não fechou nenhuma posição.")
        return
    
    total_trades = len(closed_trades)
    total_pnl = sum(t['pnl'] for t in closed_trades)
    winning_trades = sum(1 for t in closed_trades if t['pnl'] > 0)
    losing_trades = total_trades - winning_trades
    
    gross_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
    gross_loss = sum(abs(t['pnl']) for t in closed_trades if t['pnl'] < 0)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    sharpe = calcular_sharpe_ratio(pnl_history)
    mdd = calcular_drawdown(pnl_history)
    
    # Relatório
    print("="*80)
    print(f"{'SILVER SYSTEM - RELATÓRIO DE PERFORMANCE':^80}")
    print("="*80)
    print(f"Data da Análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Fonte: {LOG_FILE_NAME}")
    print(f"Magic Number: {MAGIC_NUMBER} (Sistema Silver)")
    print(f"Projeto: SilverGMarket (Independente)")
    print("-" * 80)
    print()
    
    print(f"{'📊 MÉTRICAS DE PERFORMANCE':^80}")
    print("-" * 80)
    print(f"Total de Trades Fechados: {total_trades}")
    print(f"Lucro/Prejuízo Total:     {formatar_valor_monetario(total_pnl):>40}")
    print(f"Taxa de Acerto (Win Rate): {win_rate:>6.2f}% ({winning_trades} Ganhos / {losing_trades} Perdas)")
    
    pf_display = f"{profit_factor:,.2f}" if profit_factor != float('inf') else "INF (Sem perdas)"
    print(f"Fator de Lucro:            {pf_display:>40}")
    print(f"Sharpe Ratio:              {sharpe:.4f} {obter_status_sharpe(sharpe):>30}")
    print(f"Maximum Drawdown:          {formatar_valor_monetario(mdd):>40}")
    print()
    
    print(f"{'🛡️ GESTÃO DE RISCO':^80}")
    print("-" * 80)
    print(f"Trades com TP Parcial:     {risk_metrics.get('parcial_closed_count', 0):>40}")
    print(f"Trades com Break-Even:      {risk_metrics.get('break_even_hit', 0):>40}")
    print(f"Movimentos Trailing Stop:  {risk_metrics.get('trailing_stop_moves', 0):>40}")
    print()
    
    # Análise por símbolo
    symbol_analysis = defaultdict(lambda: {'trades': 0, 'pnl': 0.0, 'wins': 0, 'losses': 0})
    for t in closed_trades:
        symbol = t.get('symbol', 'UNKNOWN')
        symbol_analysis[symbol]['trades'] += 1
        symbol_analysis[symbol]['pnl'] += t['pnl']
        if t['pnl'] > 0:
            symbol_analysis[symbol]['wins'] += 1
        else:
            symbol_analysis[symbol]['losses'] += 1
    
    if symbol_analysis:
        print(f"{'📈 PERFORMANCE POR SÍMBOLO':^80}")
        print("-" * 80)
        print(f"{'Símbolo':<12} {'Trades':<8} {'PnL':<15} {'Win Rate':<12} {'W/L':<10}")
        print("-" * 80)
        
        for symbol in sorted(symbol_analysis.keys()):
            data = symbol_analysis[symbol]
            win_rate_sym = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            wl_ratio = f"{data['wins']}/{data['losses']}"
            print(f"{symbol:<12} {data['trades']:<8} {formatar_valor_monetario(data['pnl']):<15} {win_rate_sym:>10.2f}% {wl_ratio:<10}")
    
    print()
    print("="*80)

# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    try:
        import numpy as np
    except ImportError:
        print("❌ ERRO: A biblioteca 'numpy' é necessária.")
        print("   Instale-a com: pip install numpy")
        sys.exit(1)
    
    gerar_relatorio_silver()

