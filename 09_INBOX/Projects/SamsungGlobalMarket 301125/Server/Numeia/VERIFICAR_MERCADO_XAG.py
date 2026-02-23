# ==============================================================================
# SCRIPT PARA VERIFICAR STATUS DO MERCADO XAG
# ==============================================================================
import MetaTrader5 as mt5
from datetime import datetime

print("🔍 VERIFICANDO STATUS DO MERCADO XAG")
print("="*60)

# Conectar ao MT5
if not mt5.initialize():
    print(f"❌ Erro ao conectar ao MT5: {mt5.last_error()}")
    exit()

account_info = mt5.account_info()
if account_info:
    print(f"✅ Conectado à conta: {account_info.login}")
    print()

# Símbolos para verificar
symbols = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]

print("📊 STATUS DOS SÍMBOLOS XAG:")
print("-"*60)

for symbol in symbols:
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        print(f"❌ {symbol}: Símbolo não encontrado no MT5")
        continue
    
    tick = mt5.symbol_info_tick(symbol)
    
    print(f"\n{symbol}:")
    print(f"  Visível: {symbol_info.visible}")
    print(f"  Trade Mode: {symbol_info.trade_mode} ({'Negociável' if symbol_info.trade_mode > 0 else 'NÃO Negociável'})")
    
    if tick:
        tick_time = datetime.fromtimestamp(tick.time)
        current_time = datetime.now()
        age_seconds = (current_time - tick_time).total_seconds()
        
        print(f"  Último Tick: {tick_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Idade do Tick: {age_seconds:.0f} segundos")
        print(f"  Bid: {tick.bid:.5f}")
        print(f"  Ask: {tick.ask:.5f}")
        print(f"  Spread: {(tick.ask - tick.bid):.5f}")
        
        if age_seconds > 60:
            print(f"  ⚠️ ATENÇÃO: Tick muito antigo (mercado pode estar fechado)")
        elif symbol_info.trade_mode == 0:
            print(f"  ⚠️ ATENÇÃO: Trade mode = 0 (trading desabilitado)")
        else:
            print(f"  ✅ Mercado parece estar aberto")
    else:
        print(f"  ❌ Sem dados de tick disponíveis")

print()
print("="*60)
print("💡 DICA: Se todos os símbolos mostrarem 'Tick muito antigo' ou")
print("   'Trade Mode = 0', o mercado XAG pode estar fechado.")
print("   Verifique os horários de trading da sua corretora.")
print("="*60)

mt5.shutdown()

