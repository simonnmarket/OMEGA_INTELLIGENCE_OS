# ==============================================================================
# SCRIPT DE ANÁLISE RÁPIDA - RESULTADOS DA NOITE
# Execute este script amanhã para ver os resultados do Silver System V3.0
# ==============================================================================
import json
from datetime import datetime
from collections import defaultdict
import MetaTrader5 as mt5

LOG_FILE = "silver_telemetry_v3.0.log"

def analisar_logs():
    """Analisa os logs da noite e mostra resumo dos resultados."""
    print("="*70)
    print("🥈 SILVER SYSTEM V3.0 - ANÁLISE DE RESULTADOS")
    print("="*70)
    print()
    
    # Estatísticas
    stats = {
        'total_ciclos': 0,
        'total_sinais_buy': 0,
        'total_ordens_executadas': 0,
        'total_posicoes_abertas': 0,
        'total_posicoes_fechadas': 0,
        'total_pnl': 0.0,
        'trades_por_symbol': defaultdict(int),
        'ordens_por_hora': defaultdict(int),
        'primeira_ordem': None,
        'ultima_ordem': None
    }
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    event = entry.get('event')
                    data = entry.get('data', {})
                    timestamp = entry.get('timestamp', '')
                    
                    # Contar ciclos
                    if event == 'cycle_start':
                        stats['total_ciclos'] += 1
                        if timestamp:
                            hora = timestamp.split('T')[1].split(':')[0] if 'T' in timestamp else '00'
                            stats['ordens_por_hora'][hora] += 0  # Placeholder
                    
                    # Contar sinais BUY
                    if event == 'signal_detected' and data.get('signal') == 'BUY':
                        stats['total_sinais_buy'] += 1
                        symbol = data.get('symbol', 'UNKNOWN')
                        stats['trades_por_symbol'][symbol] += 1
                    
                    # Contar ordens executadas
                    if event == 'position_opened':
                        stats['total_ordens_executadas'] += 1
                        symbol = data.get('symbol', 'UNKNOWN')
                        stats['trades_por_symbol'][symbol] += 1
                        
                        if not stats['primeira_ordem']:
                            stats['primeira_ordem'] = timestamp
                        stats['ultima_ordem'] = timestamp
                        
                        if timestamp:
                            hora = timestamp.split('T')[1].split(':')[0] if 'T' in timestamp else '00'
                            stats['ordens_por_hora'][hora] += 1
                    
                    # Contar posições fechadas
                    if event == 'position_closed' or event == 'position_partially_closed':
                        stats['total_posicoes_fechadas'] += 1
                        pnl = data.get('pnl', 0) or data.get('pnl_realized', 0)
                        stats['total_pnl'] += float(pnl)
                    
                    # Gestão de risco
                    if event == 'risk_management':
                        action = data.get('action', '')
                        if 'BREAK_EVEN' in action:
                            stats['total_posicoes_abertas'] += 0  # Placeholder
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    continue
        
    except FileNotFoundError:
        print(f"❌ Arquivo de log não encontrado: {LOG_FILE}")
        return
    
    # Exibir resultados
    print(f"📊 PERÍODO ANALISADO: {stats['primeira_ordem'] or 'N/A'} até {stats['ultima_ordem'] or 'N/A'}")
    print()
    print("-"*70)
    print("📈 ESTATÍSTICAS GERAIS")
    print("-"*70)
    print(f"Total de Ciclos Executados: {stats['total_ciclos']}")
    print(f"Sinais BUY Detectados: {stats['total_sinais_buy']}")
    print(f"Ordens Executadas: {stats['total_ordens_executadas']}")
    print(f"Posições Fechadas (Total/Parcial): {stats['total_posicoes_fechadas']}")
    print(f"PnL Total Realizado: ${stats['total_pnl']:.2f}")
    print()
    
    if stats['trades_por_symbol']:
        print("-"*70)
        print("📊 ORDENS POR SÍMBOLO")
        print("-"*70)
        for symbol, count in sorted(stats['trades_por_symbol'].items()):
            print(f"{symbol}: {count} ordem(ns)")
        print()
    
    if stats['ordens_por_hora']:
        print("-"*70)
        print("⏰ DISTRIBUIÇÃO POR HORA")
        print("-"*70)
        for hora in sorted(stats['ordens_por_hora'].keys()):
            if stats['ordens_por_hora'][hora] > 0:
                print(f"{hora}:00 - {stats['ordens_por_hora'][hora]} ordem(ns)")
        print()
    
    # Verificar posições abertas no MT5
    print("-"*70)
    print("💼 POSIÇÕES ABERTAS NO MOMENTO")
    print("-"*70)
    
    if mt5.initialize():
        positions = mt5.positions_get()
        if positions:
            silver_positions = [p for p in positions if p.magic == 99992]
            if silver_positions:
                print(f"Total de Posições Abertas: {len(silver_positions)}")
                print()
                for pos in silver_positions:
                    pnl = pos.profit
                    print(f"  {pos.symbol} | Ticket: {pos.ticket} | Volume: {pos.volume:.2f} | PnL: ${pnl:.2f}")
            else:
                print("Nenhuma posição aberta no momento.")
        else:
            print("Nenhuma posição aberta no momento.")
        mt5.shutdown()
    else:
        print("Não foi possível conectar ao MT5 para verificar posições.")
    
    print()
    print("="*70)
    print("✅ Análise concluída!")
    print("="*70)

if __name__ == "__main__":
    analisar_logs()

