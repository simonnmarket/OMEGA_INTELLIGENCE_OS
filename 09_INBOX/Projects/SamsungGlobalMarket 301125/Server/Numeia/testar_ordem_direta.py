#!/usr/bin/env python3
"""
Teste Direto de Execução de Ordem
Testa se conseguimos executar uma ordem diretamente no MT5
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import MetaTrader5 as mt5
    from numeia_executor_v2 import Config, load_config, SignalGenerator, CapitalManagement
    
    print("=" * 70)
    print("TESTE DIRETO DE ORDEM - Numeia v2.0")
    print("=" * 70)
    print()
    
    # Carregar config
    config = load_config()
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
        sys.exit(1)
    
    print("✅ MT5 inicializado")
    account_info = mt5.account_info()
    print(f"   Conta: {account_info.login}")
    print(f"   Saldo: {account_info.balance}")
    print(f"   Trade Permitido: {account_info.trade_allowed}")
    print()
    
    # Criar SignalGenerator
    capital_manager = CapitalManagement(config)
    signal_generator = SignalGenerator(config.TRADING_SYMBOLS, capital_manager, config)
    
    # Gerar sinais
    tasks = signal_generator.generate_signals()
    print(f"✅ {len(tasks)} sinais gerados")
    print()
    
    if not tasks:
        print("⚠️  Nenhum sinal gerado (spreads podem estar altos)")
        mt5.shutdown()
        sys.exit(0)
    
    # Testar primeira ordem
    task = tasks[0]
    print(f"Testando ordem: {task.symbol} {task.action} {task.volume} @ {task.price}")
    print(f"   SL: {task.sl}")
    print(f"   TP: {task.tp}")
    print()
    
    # Preparar request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": task.symbol,
        "volume": task.volume,
        "type": mt5.ORDER_TYPE_BUY if task.action == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": task.price,
        "sl": task.sl,
        "tp": task.tp,
        "deviation": task.deviation,
        "magic": task.magic,
        "comment": f"TESTE_NUMEIA_{int(time.time())}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    print("Enviando ordem...")
    result = mt5.order_send(request)
    
    print()
    print("=" * 70)
    print("RESULTADO")
    print("=" * 70)
    
    if result is None:
        error_info = mt5.last_error()
        error_code = error_info[0] if isinstance(error_info, tuple) else error_info
        error_description = error_info[1] if isinstance(error_info, tuple) and len(error_info) > 1 else str(error_info)
        print(f"❌ Ordem falhou: {error_code}")
        print(f"   Descrição: {error_description}")
        print()
        print("Códigos de erro comuns:")
        print("   - 10004: Requisição processada")
        print("   - 10006: Não há dinheiro suficiente")
        print("   - 10007: Preço inválido")
        print("   - 10008: Stop inválido")
        print("   - 10009: Trade desabilitado")
        print("   - 10010: Muitas requisições")
        print("   - 10011: Mudança não permitida")
        print("   - 10012: Requisição rejeitada")
    else:
        print(f"✅ Retcode: {result.retcode}")
        print(f"   Deal: {result.deal}")
        print(f"   Volume: {result.volume}")
        print(f"   Preço: {result.price}")
        print(f"   Comentário: {result.comment}")
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print()
            print("✅ ORDEM EXECUTADA COM SUCESSO!")
        else:
            print()
            print(f"⚠️  Retcode: {result.retcode} - {result.comment}")
    
    mt5.shutdown()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

