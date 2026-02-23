# ==============================================================================
# SCRIPT DE VERIFICAÇÃO - DIAGNOSTICAR PROBLEMAS DE TRADING NO MT5
# ==============================================================================
import MetaTrader5 as mt5

def verificar_mt5_trading():
    """Verifica se o MT5 está configurado corretamente para trading."""
    print("="*70)
    print("🔍 DIAGNÓSTICO MT5 - VERIFICAÇÃO DE TRADING")
    print("="*70)
    print()
    
    if not mt5.initialize():
        print("❌ Falha ao conectar ao MT5")
        print(f"   Erro: {mt5.last_error()}")
        return
    
    print("✅ MT5 Conectado")
    print()
    
    # Verificar informações da conta
    account_info = mt5.account_info()
    if account_info is None:
        print("❌ Não foi possível obter informações da conta")
        mt5.shutdown()
        return
    
    print("📊 INFORMAÇÕES DA CONTA:")
    print(f"   Login: {account_info.login}")
    print(f"   Balance: ${account_info.balance:.2f}")
    print(f"   Equity: ${account_info.equity:.2f}")
    print(f"   Trading Permitido: {'✅ SIM' if account_info.trade_allowed else '❌ NÃO'}")
    print(f"   Trading Expert: {'✅ SIM' if account_info.trade_expert else '❌ NÃO'}")
    print()
    
    if not account_info.trade_allowed:
        print("⚠️ ATENÇÃO: Trading NÃO está permitido na conta!")
        print("   -> Verifique as configurações da conta no MT5")
        print("   -> Vá em: Ferramentas > Opções > Expert Advisors")
        print("   -> Marque: 'Permitir negociação automatizada'")
        print()
    
    # Verificar símbolos de prata
    symbols = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]
    print("📊 VERIFICAÇÃO DOS SÍMBOLOS DE PRATA:")
    print()
    
    for symbol in symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"   {symbol}: ❌ Símbolo não encontrado")
            continue
        
        print(f"   {symbol}:")
        print(f"      Trade Mode: {symbol_info.trade_mode} ({'Negociável' if symbol_info.trade_mode > 0 else 'Não Negociável'})")
        print(f"      Visible: {'✅' if symbol_info.visible else '❌'}")
        print(f"      Volume Min: {symbol_info.volume_min}")
        print(f"      Volume Max: {symbol_info.volume_max}")
        print(f"      Volume Step: {symbol_info.volume_step}")
        
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(f"      Bid: {tick.bid:.5f}")
            print(f"      Ask: {tick.ask:.5f}")
            if tick.ask > 0 and tick.bid > 0:
                spread = tick.ask - tick.bid
                print(f"      Spread: {spread:.5f}")
        else:
            print(f"      ❌ Sem dados de tick")
        print()
    
    # Teste de ordem (simulação)
    print("🧪 TESTE DE ORDEM (SIMULAÇÃO):")
    print()
    
    test_symbol = "XAGUSD"
    symbol_info = mt5.symbol_info(test_symbol)
    if symbol_info and account_info.trade_allowed:
        tick = mt5.symbol_info_tick(test_symbol)
        if tick and tick.ask > 0:
            # Criar request de teste (não enviar)
            test_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": test_symbol,
                "volume": 0.10,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "sl": tick.ask - 0.10,
                "tp": tick.ask + 0.10,
                "deviation": 20,
                "magic": 99992,
                "comment": "TESTE_SILVER",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            print(f"   Request criado para {test_symbol}:")
            print(f"      Volume: {test_request['volume']}")
            print(f"      Price: {test_request['price']:.5f}")
            print(f"      SL: {test_request['sl']:.5f}")
            print(f"      TP: {test_request['tp']:.5f}")
            print()
            print("   ⚠️ NOTA: Request não foi enviado (apenas simulação)")
            print("   -> Se todos os parâmetros acima estão OK, o sistema deve funcionar")
        else:
            print(f"   ❌ Não foi possível criar request (sem tick válido)")
    else:
        print(f"   ❌ Não foi possível criar request")
        if not account_info.trade_allowed:
            print(f"      Motivo: Trading não permitido na conta")
        if not symbol_info:
            print(f"      Motivo: Símbolo {test_symbol} não encontrado")
    
    print()
    print("="*70)
    print("✅ Diagnóstico concluído!")
    print("="*70)
    
    mt5.shutdown()

if __name__ == "__main__":
    verificar_mt5_trading()

