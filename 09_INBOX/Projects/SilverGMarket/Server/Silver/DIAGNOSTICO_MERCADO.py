# ==============================================================================
# SCRIPT DE DIAGNÓSTICO - VERIFICAR STATUS DO MERCADO XAG
# ==============================================================================
import MetaTrader5 as mt5
from datetime import datetime
import time

SILVER_SYMBOLS = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]

def diagnosticar_mercado():
    """Diagnostica o status do mercado para os símbolos de prata."""
    print("="*70)
    print("🔍 DIAGNÓSTICO DE MERCADO - PRATA (XAG)")
    print("="*70)
    print()
    
    if not mt5.initialize():
        print("❌ Falha ao conectar ao MT5")
        return
    
    for symbol in SILVER_SYMBOLS:
        print(f"\n📊 {symbol}")
        print("-"*70)
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print("  ❌ Símbolo não encontrado")
            continue
        
        # Trade Mode
        trade_mode = symbol_info.trade_mode
        trade_mode_desc = {
            0: "Não negociável",
            1: "Apenas fechamento",
            2: "Apenas abertura",
            4: "Negociação completa"
        }
        print(f"  Trade Mode: {trade_mode} ({trade_mode_desc.get(trade_mode, 'Desconhecido')})")
        
        # Tick
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print("  ❌ Sem dados de tick")
            continue
        
        print(f"  Bid: {tick.bid:.5f}")
        print(f"  Ask: {tick.ask:.5f}")
        
        if tick.ask > 0 and tick.bid > 0:
            spread = tick.ask - tick.bid
            spread_percent = (spread / tick.bid) * 100
            print(f"  Spread: {spread:.5f} ({spread_percent:.2f}%)")
        
        # Idade do tick
        current_time = time.time()
        tick_age = abs(current_time - tick.time)
        tick_age_minutes = tick_age / 60
        print(f"  Idade do Tick: {tick_age_minutes:.1f} minutos ({tick_age:.0f} segundos)")
        
        # Status
        if trade_mode == 0:
            status = "❌ NÃO NEGOCIÁVEL"
        elif tick_age > 900:
            status = "⚠️ TICK MUITO ANTIGO (>15 min)"
        elif tick.ask > 0 and tick.bid > 0:
            spread_percent = ((tick.ask - tick.bid) / tick.bid) * 100
            if spread_percent > 2.0:
                status = f"⚠️ SPREAD ALTO ({spread_percent:.2f}%)"
            else:
                status = "✅ MERCADO ABERTO"
        else:
            status = "⚠️ DADOS INVÁLIDOS"
        
        print(f"  Status: {status}")
        
        # Tentar executar uma ordem de teste (sem enviar)
        if status == "✅ MERCADO ABERTO":
            print(f"  ✅ Sistema pode tentar executar ordens")
        else:
            print(f"  ⚠️ Sistema pode bloquear ordens (mas tentará mesmo assim)")
    
    print()
    print("="*70)
    print("💡 NOTA: O sistema V3.0 melhorado agora tenta executar mesmo")
    print("   se a verificação prévia falhar, deixando o MT5 decidir.")
    print("="*70)
    
    mt5.shutdown()

if __name__ == "__main__":
    diagnosticar_mercado()

