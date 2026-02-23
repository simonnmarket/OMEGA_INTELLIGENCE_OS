# ==============================================================================
# PROMETHEUS V2.2: SCRIPT DE ANÁLISE DE PERFORMANCE
# Objetivo: Analisar o arquivo de log JSON (V2.1) para calcular métricas de trading.
# Data: 26/11/2025
# ==============================================================================

import json
from collections import defaultdict
from datetime import datetime

# Nome do arquivo de log gerado pelo Prometheus V2.1
LOG_FILE_NAME = "prometheus_telemetry_v2.1.log"

def ler_log_e_extrair_dados(filename):
    """
    Lê o arquivo JSON Lines e extrai os dados relevantes de trades e gestão de risco.
    """
    trades = {}
    
    # Dicionário para contar a eficácia das ações de gestão de risco
    risk_metrics = defaultdict(int) 
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    event = entry.get('event')
                    data = entry.get('data', {})
                    ticket = data.get('ticket')

                    if event == 'position_opened':
                        # Armazena dados de abertura (Ticket é a chave principal)
                        if ticket:
                            trades[ticket] = {
                                'symbol': data.get('symbol'),
                                'entry_price': data.get('entry_price'),
                                'sl_original': data.get('sl_price'),
                                'closed': False,
                                'pnl': 0.0,
                                'close_reason': 'N/A',
                                'close_price': None,
                                'break_even_hit': False,
                                'trailing_stop_moves': 0
                            }
                    
                    elif event == 'position_closed':
                        # Atualiza dados de fechamento
                        if ticket in trades:
                            trades[ticket]['closed'] = True
                            # O PnL pode estar negativo, então usamos o valor bruto
                            trades[ticket]['pnl'] = data.get('pnl', 0.0) 
                            trades[ticket]['close_reason'] = data.get('reason', 'UNKNOWN')
                            trades[ticket]['close_price'] = data.get('close_price')
                            
                            # Contagem de razão de fechamento
                            if trades[ticket]['pnl'] > 0:
                                risk_metrics['closed_win'] += 1
                            else:
                                risk_metrics['closed_loss'] += 1
                                
                            if data.get('reason') == 'SIGNAL_REVERSAL':
                                risk_metrics['closed_by_reversal'] += 1

                    elif event == 'risk_management':
                        # Contagem das ações de gestão de risco
                        action = data.get('action')
                        ticket_risk = data.get('ticket')
                        
                        if action == 'BREAK_EVEN_SET':
                            risk_metrics['break_even_hit'] += 1
                            if ticket_risk in trades:
                                trades[ticket_risk]['break_even_hit'] = True
                        elif action == 'TRAILING_STOP_MOVE':
                            risk_metrics['trailing_stop_moves'] += 1
                            if ticket_risk in trades:
                                trades[ticket_risk]['trailing_stop_moves'] += 1
                            
                except json.JSONDecodeError:
                    print(f"⚠️ Aviso: Linha inválida no log (não é JSON válido): {line.strip()[:100]}")
                    continue
                
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de log '{filename}' não encontrado.")
        print(f"   Execute o Prometheus V2.1 primeiro para gerar dados.")
        return None, None
    except Exception as e:
        print(f"❌ ERRO ao processar o log: {e}")
        import traceback
        traceback.print_exc()
        return None, None

    return trades, risk_metrics


def gerar_relatorio_performance(trades, risk_metrics):
    """
    Calcula as métricas de trading e imprime o relatório final.
    """
    
    if not trades:
        print("❌ Nenhum trade para analisar.")
        return

    # Filtra apenas os trades que foram fechados (realizados)
    closed_trades = [t for t in trades.values() if t['closed']]

    if not closed_trades:
        print("⚠️ Nenhum trade fechado encontrado no log.")
        print("   O sistema pode estar rodando, mas ainda não fechou nenhuma posição.")
        print("   Aguarde alguns ciclos e execute a análise novamente.")
        return

    total_trades_closed = len(closed_trades)
    
    # 1. Métricas Financeiras
    total_pnl = sum(t['pnl'] for t in closed_trades)
    winning_trades = sum(1 for t in closed_trades if t['pnl'] > 0)
    losing_trades = total_trades_closed - winning_trades
    
    gross_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
    gross_loss = sum(abs(t['pnl']) for t in closed_trades if t['pnl'] < 0)
    
    # 2. Cálculos de Performance
    win_rate = (winning_trades / total_trades_closed) * 100 if total_trades_closed > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # 3. Métricas de Gestão de Risco (Extraídas do risk_metrics)
    be_hit_rate = (risk_metrics['break_even_hit'] / total_trades_closed) * 100 if total_trades_closed > 0 else 0
    
    # 4. Análise de Trades com Break-Even
    trades_with_be = sum(1 for t in closed_trades if t.get('break_even_hit', False))
    be_win_rate = 0
    if trades_with_be > 0:
        be_wins = sum(1 for t in closed_trades if t.get('break_even_hit', False) and t['pnl'] > 0)
        be_win_rate = (be_wins / trades_with_be) * 100
    
    # 5. Análise de Trades com Trailing Stop
    trades_with_ts = sum(1 for t in closed_trades if t.get('trailing_stop_moves', 0) > 0)
    avg_ts_moves = sum(t.get('trailing_stop_moves', 0) for t in closed_trades) / total_trades_closed if total_trades_closed > 0 else 0
    
    # 6. Análise por Símbolo
    symbol_stats = defaultdict(lambda: {'trades': 0, 'pnl': 0.0, 'wins': 0, 'losses': 0})
    for t in closed_trades:
        symbol = t.get('symbol', 'UNKNOWN')
        symbol_stats[symbol]['trades'] += 1
        symbol_stats[symbol]['pnl'] += t['pnl']
        if t['pnl'] > 0:
            symbol_stats[symbol]['wins'] += 1
        else:
            symbol_stats[symbol]['losses'] += 1

    # --- IMPRESSÃO DO RELATÓRIO ---
    
    print("\n" + "="*80)
    print("      PROMETHEUS V2.2: RELATÓRIO DE ANÁLISE DE PERFORMANCE")
    print("="*80)
    print(f"Data da Análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Fonte de Dados: {LOG_FILE_NAME}")
    print("-" * 80)
    
    print("               📊 MÉTRICAS DE PERFORMANCE GERAL")
    print("-" * 80)
    print(f"Total de Trades Analisados (Fechados): {total_trades_closed}")
    print(f"Lucro/Prejuízo Líquido (PnL):        ${total_pnl:,.2f}")
    print(f"Taxa de Acerto (Win Rate):           {win_rate:,.2f}% ({winning_trades} Ganhos / {losing_trades} Perdas)")
    
    # Fator de lucro (Profit Factor)
    pf_display = f"{profit_factor:,.2f}"
    if profit_factor == float('inf'):
        pf_display = "INF (Sem perdas)"
    print(f"Fator de Lucro (Profit Factor):      {pf_display} (Lucro Bruto / Prejuízo Bruto)")
    
    if gross_profit > 0:
        print(f"Lucro Bruto Total:                  ${gross_profit:,.2f}")
    if gross_loss > 0:
        print(f"Prejuízo Bruto Total:               ${gross_loss:,.2f}")
    
    print("-" * 80)
    
    print("           🛡️ EFICÁCIA DA GESTÃO DE RISCO (V2.1)")
    print("-" * 80)
    print(f"Trades que Atingiram Break-Even (BE): {risk_metrics['break_even_hit']} ({be_hit_rate:,.2f}% dos trades)")
    
    if trades_with_be > 0:
        print(f"  └─ Trades com BE que foram Ganhadores: {trades_with_be} ({be_win_rate:,.2f}% win rate)")
    
    print(f"Movimentos de Trailing Stop (TS):     {risk_metrics['trailing_stop_moves']} movimentos")
    if trades_with_ts > 0:
        print(f"  └─ Trades que usaram TS: {trades_with_ts} (Média: {avg_ts_moves:.1f} movimentos por trade)")
    
    print(f"Fechamentos por Reversão (V1.2):     {risk_metrics['closed_by_reversal']} trades")
    print("-" * 80)
    
    if losing_trades > 0:
        loss_reason = f"{risk_metrics['closed_loss']} trades ({risk_metrics['closed_by_reversal']} por Reversão)"
    else:
        loss_reason = "0 perdas (Parabéns!)"
        
    print(f"Total de Trades Vencedores: {risk_metrics['closed_win']}")
    print(f"Total de Trades Perdedores: {loss_reason}")
    
    # Análise por Símbolo
    if len(symbol_stats) > 0:
        print("-" * 80)
        print("           📈 ANÁLISE DE PERFORMANCE POR SÍMBOLO")
        print("-" * 80)
        print(f"{'Símbolo':<12} {'Trades':<8} {'PnL':<15} {'Win Rate':<12} {'W/L':<10}")
        print("-" * 80)
        
        # Ordenar por PnL (maior primeiro)
        sorted_symbols = sorted(symbol_stats.items(), key=lambda x: x[1]['pnl'], reverse=True)
        
        for symbol, stats in sorted_symbols:
            symbol_win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
            wl_ratio = f"{stats['wins']}/{stats['losses']}"
            print(f"{symbol:<12} {stats['trades']:<8} ${stats['pnl']:>12,.2f} {symbol_win_rate:>10.2f}% {wl_ratio:<10}")
    
    print("="*80 + "\n")


# --- EXECUÇÃO PRINCIPAL ---
def main():
    print("🔍 PROMETHEUS V2.2: Iniciando análise de performance...")
    print(f"📂 Procurando arquivo: {LOG_FILE_NAME}")
    print()
    
    trades, risk_metrics = ler_log_e_extrair_dados(LOG_FILE_NAME)
    
    if trades is not None and risk_metrics is not None:
        gerar_relatorio_performance(trades, risk_metrics)
    else:
        print("\n❌ Não foi possível gerar o relatório. Verifique se o arquivo de log existe.")

if __name__ == "__main__":
    main()

