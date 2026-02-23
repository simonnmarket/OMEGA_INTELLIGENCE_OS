#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de execução de ordem direta para diagnosticar problema
"""

import MetaTrader5 as mt5
import json
from numeia_executor_v2 import load_config, SignalGenerator, CapitalManagement, Task
from datetime import datetime

def test_order_execution():
    print("=" * 80)
    print("TESTE DE EXECUÇÃO DE ORDEM DIRETA")
    print("=" * 80)
    
    # 1. Inicializar MT5
    if not mt5.initialize():
        print("❌ ERRO: Não foi possível inicializar MetaTrader 5")
        return False
    
    print("✅ MT5 inicializado")
    
    # 2. Gerar um sinal de teste
    print("\n[1/4] Gerando sinal de teste...")
    try:
        config = load_config()
        cm = CapitalManagement(config)
        sg = SignalGenerator(config.TRADING_SYMBOLS, cm, config)
        tasks = sg.generate_signals()
        
        if not tasks:
            print("❌ Nenhum sinal gerado")
            mt5.shutdown()
            return False
        
        task = tasks[0]  # Pegar primeiro sinal
        print(f"✅ Sinal gerado: {task.symbol} {task.action} @ {task.price}")
        print(f"   Volume: {task.volume}, SL: {task.sl}, TP: {task.tp}")
    except Exception as e:
        print(f"❌ ERRO ao gerar sinal: {e}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        return False
    
    # 3. Verificar se símbolo está disponível
    print(f"\n[2/4] Verificando símbolo {task.symbol}...")
    symbol_info = mt5.symbol_info(task.symbol)
    if not symbol_info:
        print(f"❌ Símbolo {task.symbol} não encontrado")
        mt5.shutdown()
        return False
    
    if not symbol_info.visible:
        print(f"⚠️  Símbolo {task.symbol} não está visível no Market Watch")
        print("   Tentando selecionar...")
        if not mt5.symbol_select(task.symbol, True):
            print(f"❌ Não foi possível selecionar {task.symbol}")
            mt5.shutdown()
            return False
    
    print(f"✅ Símbolo {task.symbol} disponível")
    
    # 4. Verificar tick atual
    print(f"\n[3/4] Verificando tick atual...")
    tick = mt5.symbol_info_tick(task.symbol)
    if not tick:
        print(f"❌ Não foi possível obter tick para {task.symbol}")
        mt5.shutdown()
        return False
    
    print(f"✅ Tick: Bid={tick.bid}, Ask={tick.ask}, Spread={(tick.ask - tick.bid):.5f}")
    
    # 5. Preparar ordem (NÃO EXECUTAR - apenas simular)
    print(f"\n[4/4] Preparando ordem (SIMULAÇÃO - NÃO EXECUTA)...")
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": task.symbol,
        "volume": task.volume,
        "type": mt5.ORDER_TYPE_BUY if task.action == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": task.price or (tick.ask if task.action == 'buy' else tick.bid),
        "sl": task.sl,
        "tp": task.tp,
        "deviation": task.deviation,
        "magic": task.magic,
        "comment": f"Numeia_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    print("📋 Request de ordem:")
    print(json.dumps(request, indent=2, default=str))
    
    # Verificar se trading está habilitado
    account_info = mt5.account_info()
    if account_info:
        print(f"\n📊 Informações da conta:")
        print(f"   Trade allowed: {account_info.trade_allowed}")
        print(f"   Trade expert: {account_info.trade_expert}")
        print(f"   Balance: {account_info.balance}")
        print(f"   Equity: {account_info.equity}")
        
        if not account_info.trade_allowed:
            print("\n⚠️  AVISO: Trading não está habilitado na conta!")
            print("   Ative o trading automático no MT5: Tools > Options > Expert Advisors")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)
    print("\n⚠️  NOTA: Esta foi uma simulação. A ordem NÃO foi executada.")
    print("   Para testar execução real, descomente a linha abaixo no código.")
    
    # DESCOMENTAR ABAIXO PARA EXECUTAR REALMENTE (PERIGOSO):
    # result = mt5.order_send(request)
    # if result:
    #     print(f"✅ Ordem enviada: {result.retcode}")
    #     print(f"   Deal: {result.deal}, Order: {result.order}")
    # else:
    #     error = mt5.last_error()
    #     print(f"❌ ERRO ao enviar ordem: {error}")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    test_order_execution()
