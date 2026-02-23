# ==============================================================================
# ANÁLISE DE ENTRADAS PREMATURAS - VALIDAÇÃO DA ESTRATÉGIA
# Objetivo: Descobrir se estamos entrando muito cedo nas operações
# ==============================================================================
import json
import MetaTrader5 as mt5
from datetime import datetime
from collections import defaultdict

LOG_FILE = "silver_telemetry_v3.0.log"
MAGIC_NUMBER = 99992

def analisar_entradas_prematuras():
    """
    Analisa se as entradas estão ocorrendo muito cedo.
    Métricas:
    - Quantas vezes o SL foi atingido antes do TP
    - Tempo médio até SL vs TP
    - Distância média do preço de entrada até SL/TP
    - Taxa de entradas que viraram lucro vs prejuízo
    """
    print("="*70)
    print("🔍 ANÁLISE DE ENTRADAS PREMATURAS - VALIDAÇÃO DA ESTRATÉGIA")
    print("="*70)
    print()
    
    # Dados coletados
    trades = []
    entradas_por_symbol = defaultdict(list)
    
    # Ler log
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    event = entry.get('event')
                    data = entry.get('data', {})
                    
                    if event == 'position_opened':
                        entradas_por_symbol[data.get('symbol')].append({
                            'ticket': data.get('ticket'),
                            'timestamp': entry.get('timestamp'),
                            'entry_price': data.get('entry_price'),
                            'sl_price': data.get('sl_price'),
                            'tp_price': data.get('tp_price'),
                            'volume': data.get('volume'),
                            'symbol': data.get('symbol')
                        })
                    elif event == 'position_closed':
                        ticket = data.get('ticket')
                        # Encontrar entrada correspondente
                        for symbol, entries in entradas_por_symbol.items():
                            for entry in entries:
                                if entry['ticket'] == ticket:
                                    entry['closed'] = True
                                    entry['close_price'] = data.get('close_price')
                                    entry['pnl'] = data.get('pnl', 0)
                                    entry['close_reason'] = data.get('reason', 'UNKNOWN')
                                    entry['close_timestamp'] = entry.get('timestamp')
                                    trades.append(entry)
                                    break
                except:
                    continue
    except FileNotFoundError:
        print(f"❌ Arquivo de log não encontrado: {LOG_FILE}")
        return
    
    # Verificar posições abertas no MT5
    if mt5.initialize():
        positions = mt5.positions_get()
        if positions:
            silver_positions = [p for p in positions if p.magic == MAGIC_NUMBER]
            
            for pos in silver_positions:
                symbol_info = mt5.symbol_info(pos.symbol)
                if symbol_info:
                    point = symbol_info.point
                    digits = symbol_info.digits
                    if digits == 3 or digits == 5:
                        pip_value = 10 * point
                    else:
                        pip_value = point
                    
                    current_price = pos.price_current
                    profit_pips = (current_price - pos.price_open) / pip_value
                    
                    # Adicionar posição aberta à análise
                    trades.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'entry_price': pos.price_open,
                        'sl_price': pos.sl,
                        'tp_price': pos.tp,
                        'current_price': current_price,
                        'profit_pips': profit_pips,
                        'pnl': pos.profit,
                        'closed': False,
                        'volume': pos.volume
                    })
        mt5.shutdown()
    
    if not trades:
        print("⚠️ Nenhum trade encontrado para análise.")
        print("   Execute o sistema por mais tempo para coletar dados.")
        return
    
    # Análise
    print("📊 ESTATÍSTICAS GERAIS:")
    print("-"*70)
    total_trades = len(trades)
    trades_fechados = [t for t in trades if t.get('closed', False)]
    trades_abertos = [t for t in trades if not t.get('closed', False)]
    
    print(f"Total de Trades: {total_trades}")
    print(f"  - Fechados: {len(trades_fechados)}")
    print(f"  - Abertos: {len(trades_abertos)}")
    print()
    
    # Análise de entradas prematuras
    if trades_fechados:
        print("🔍 ANÁLISE DE ENTRADAS PREMATURAS:")
        print("-"*70)
        
        sl_hits = [t for t in trades_fechados if t.get('close_reason') == 'SL' or (t.get('pnl', 0) < 0 and t.get('close_reason') != 'TP')]
        tp_hits = [t for t in trades_fechados if t.get('close_reason') == 'TP' or (t.get('pnl', 0) > 0 and t.get('close_reason') != 'SL')]
        
        print(f"Trades que atingiram SL: {len(sl_hits)} ({len(sl_hits)/len(trades_fechados)*100:.1f}%)")
        print(f"Trades que atingiram TP: {len(tp_hits)} ({len(tp_hits)/len(trades_fechados)*100:.1f}%)")
        print()
        
        # Análise por símbolo
        print("📊 ANÁLISE POR SÍMBOLO:")
        print("-"*70)
        
        for symbol in ['XAGUSD', 'XAGAUD', 'XAGEUR', 'XAGGBP']:
            symbol_trades = [t for t in trades_fechados if t.get('symbol') == symbol]
            if symbol_trades:
                symbol_sl = [t for t in symbol_trades if t.get('pnl', 0) < 0]
                symbol_tp = [t for t in symbol_trades if t.get('pnl', 0) > 0]
                
                print(f"  {symbol}:")
                print(f"    Total: {len(symbol_trades)}")
                print(f"    SL: {len(symbol_sl)} ({len(symbol_sl)/len(symbol_trades)*100:.1f}%)")
                print(f"    TP: {len(symbol_tp)} ({len(symbol_tp)/len(symbol_trades)*100:.1f}%)")
                print()
        
        # Análise de distância até SL/TP
        print("📏 DISTÂNCIA MÉDIA ATÉ SL/TP:")
        print("-"*70)
        
        for trade in trades_fechados:
            if 'entry_price' in trade and 'sl_price' in trade:
                sl_distance = abs(trade['entry_price'] - trade['sl_price'])
                tp_distance = abs(trade['tp_price'] - trade['entry_price'])
                trade['sl_distance'] = sl_distance
                trade['tp_distance'] = tp_distance
        
        if trades_fechados:
            avg_sl_distance = sum(t.get('sl_distance', 0) for t in trades_fechados) / len(trades_fechados)
            avg_tp_distance = sum(t.get('tp_distance', 0) for t in trades_fechados) / len(trades_fechados)
            
            print(f"Distância média até SL: {avg_sl_distance:.5f}")
            print(f"Distância média até TP: {avg_tp_distance:.5f}")
            print(f"Razão TP/SL: {avg_tp_distance/avg_sl_distance:.2f}:1")
            print()
    
    # Análise de posições abertas
    if trades_abertos:
        print("💼 ANÁLISE DE POSIÇÕES ABERTAS:")
        print("-"*70)
        
        for trade in trades_abertos:
            symbol = trade.get('symbol', 'UNKNOWN')
            ticket = trade.get('ticket', 'N/A')
            profit_pips = trade.get('profit_pips', 0)
            pnl = trade.get('pnl', 0)
            
            status = "✅ LUCRO" if profit_pips > 0 else "❌ PREJUÍZO"
            print(f"  {symbol} (Ticket: {ticket}): {status} | {profit_pips:+.1f} pips | ${pnl:.2f}")
        print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES:")
    print("-"*70)
    
    if trades_fechados:
        sl_rate = len(sl_hits) / len(trades_fechados) if trades_fechados else 0
        
        if sl_rate > 0.6:
            print("⚠️ ALTA TAXA DE SL (>60%):")
            print("   -> Possível entrada muito cedo")
            print("   -> Considere aguardar confirmação adicional (ex: 2-3 barras)")
            print("   -> Ou ajustar MA para períodos maiores (ex: MA30/MA60)")
        elif sl_rate > 0.4:
            print("⚠️ TAXA MODERADA DE SL (40-60%):")
            print("   -> Estratégia pode estar entrando um pouco cedo")
            print("   -> Considere filtro adicional (ex: volume, RSI)")
        else:
            print("✅ TAXA BAIXA DE SL (<40%):")
            print("   -> Estratégia parece estar entrando no momento adequado")
            print("   -> Continue monitorando")
    
    print()
    print("="*70)
    print("✅ Análise concluída!")
    print("="*70)

if __name__ == "__main__":
    analisar_entradas_prematuras()

