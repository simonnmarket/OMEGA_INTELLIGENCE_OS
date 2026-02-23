#!/usr/bin/env python3
"""
Teste Rápido da Correção de Spread
Valida que o sistema agora aceita spreads configuráveis
"""

import sys
import json
from pathlib import Path

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from numeia_executor_v2 import Config, SignalGenerator, CapitalManagement, load_config
    import MetaTrader5 as mt5
    
    print("=" * 70)
    print("TESTE DE VALIDAÇÃO - Correção de Spread")
    print("=" * 70)
    print()
    
    # Carregar config
    print("[1/4] Carregando configuração...")
    config = load_config()
    print(f"    ✅ Config carregado")
    print(f"    ✅ MAX_SPREAD_PIPS: {config.MAX_SPREAD_PIPS}")
    print()
    
    # Inicializar MT5
    print("[2/4] Conectando ao MetaTrader 5...")
    if not mt5.initialize():
        print(f"    ❌ Falha ao conectar MT5: {mt5.last_error()}")
        sys.exit(1)
    print(f"    ✅ MT5 conectado")
    print()
    
    # Criar SignalGenerator
    print("[3/4] Criando SignalGenerator...")
    capital_manager = CapitalManagement(config)
    signal_generator = SignalGenerator(config.TRADING_SYMBOLS, capital_manager, config)
    print(f"    ✅ SignalGenerator criado")
    print()
    
    # Testar geração de sinais
    print("[4/4] Testando geração de sinais...")
    tasks = signal_generator.generate_signals()
    
    print(f"    ✅ {len(tasks)} tarefas geradas")
    
    if tasks:
        print("\n" + "=" * 70)
        print("✅ SUCESSO! Sinais sendo gerados!")
        print("=" * 70)
        for task in tasks[:5]:  # Mostrar primeiros 5
            print(f"  - {task.symbol}: {task.action} {task.volume} @ {task.price}")
    else:
        print("\n" + "=" * 70)
        print("⚠️  Nenhum sinal gerado ainda")
        print("=" * 70)
        print("Motivos possíveis:")
        print("  - Spreads ainda acima dos limites configurados")
        print("  - Mercado fechado")
        print("  - Símbolos não disponíveis")
        print()
        print("Limites configurados:")
        for symbol in config.TRADING_SYMBOLS:
            max_spread = signal_generator._get_max_spread_for_symbol(symbol)
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    spread = (tick.ask - tick.bid) / symbol_info.point
                    status = "✅" if spread <= max_spread else "❌"
                    print(f"  {status} {symbol}: spread={spread:.2f} pips (limite={max_spread})")
    
    mt5.shutdown()
    print("\n✅ Teste concluído")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

