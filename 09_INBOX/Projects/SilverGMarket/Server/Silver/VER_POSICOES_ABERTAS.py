# ==============================================================================
# SCRIPT PARA VER POSIÇÕES ABERTAS E ÚLTIMAS ENTRADAS
# ==============================================================================
import json
import MetaTrader5 as mt5
from datetime import datetime

LOG_FILE = "silver_telemetry_v3.0.log"
MAGIC_NUMBER = 99992

def ver_posicoes_abertas():
    """Mostra posições abertas no MT5 e últimas entradas do log."""
    print("="*70)
    print("🥈 SILVER SYSTEM V3.0 - POSIÇÕES ABERTAS")
    print("="*70)
    print()
    
    # 1. Verificar posições abertas no MT5
    print("💼 POSIÇÕES ABERTAS NO MOMENTO:")
    print("-"*70)
    
    if not mt5.initialize():
        print("❌ Falha ao conectar ao MT5")
        return
    
    positions = mt5.positions_get()
    if positions:
        silver_positions = [p for p in positions if p.magic == MAGIC_NUMBER]
        
        if silver_positions:
            print(f"Total: {len(silver_positions)} posição(ões) aberta(s)\n")
            
            total_pnl = 0.0
            for pos in silver_positions:
                pnl = pos.profit
                total_pnl += pnl
                
                # Calcular lucro em pips
                symbol_info = mt5.symbol_info(pos.symbol)
                if symbol_info:
                    point = symbol_info.point
                    digits = symbol_info.digits
                    if digits == 3 or digits == 5:
                        pip_value = 10 * point
                    else:
                        pip_value = point
                    
                    profit_pips = (pos.price_current - pos.price_open) / pip_value
                else:
                    profit_pips = 0
                
                print(f"  📊 {pos.symbol}")
                print(f"     Ticket: {pos.ticket}")
                print(f"     Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
                print(f"     Volume: {pos.volume:.2f} lotes")
                print(f"     Entrada: {pos.price_open:.5f}")
                print(f"     Atual: {pos.price_current:.5f}")
                print(f"     SL: {pos.sl:.5f} | TP: {pos.tp:.5f}")
                print(f"     PnL: ${pnl:.2f} ({profit_pips:+.1f} pips)")
                print()
            
            print(f"💰 PnL Total: ${total_pnl:.2f}")
        else:
            print("Nenhuma posição aberta no momento.")
    else:
        print("Nenhuma posição aberta no momento.")
    
    print()
    print("-"*70)
    print("📝 ÚLTIMAS 10 ENTRADAS DO LOG:")
    print("-"*70)
    
    # 2. Ler últimas entradas do log
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        entries = []
        for line in lines:
            try:
                entry = json.loads(line.strip())
                if entry.get('event') == 'position_opened':
                    entries.append(entry)
            except:
                continue
        
        if entries:
            # Mostrar últimas 10
            for entry in entries[-10:]:
                data = entry.get('data', {})
                timestamp = entry.get('timestamp', '')
                time_str = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp
                
                print(f"  🕐 {time_str}")
                print(f"     {data.get('symbol')} | Ticket: {data.get('ticket')}")
                print(f"     Entrada: {data.get('entry_price')} | Volume: {data.get('volume')}")
                print(f"     SL: {data.get('sl_price')} | TP: {data.get('tp_price')}")
                print()
        else:
            print("Nenhuma entrada encontrada no log.")
            
    except FileNotFoundError:
        print(f"❌ Arquivo de log não encontrado: {LOG_FILE}")
    except Exception as e:
        print(f"❌ Erro ao ler log: {e}")
    
    print("="*70)
    mt5.shutdown()

if __name__ == "__main__":
    ver_posicoes_abertas()

