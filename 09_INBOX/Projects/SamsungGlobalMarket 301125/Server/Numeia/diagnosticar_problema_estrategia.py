#!/usr/bin/env python3
"""
Diagnóstico: Por que apenas EURUSD gera ordens e todas estão no prejuízo
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

try:
    import MetaTrader5 as mt5
    from numeia_executor_v2 import Config, load_config, SignalGenerator, CapitalManagement
    
    print("=" * 70)
    print("DIAGNÓSTICO: Problema de Estratégia e Geração de Sinais")
    print("=" * 70)
    print()
    
    # Carregar config
    config = load_config()
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
        sys.exit(1)
    
    print("✅ MT5 inicializado")
    print()
    
    # Criar SignalGenerator
    capital_manager = CapitalManagement(config)
    signal_generator = SignalGenerator(config.TRADING_SYMBOLS, capital_manager, config)
    
    # Gerar sinais
    print("Gerando sinais...")
    tasks = signal_generator.generate_signals()
    print(f"✅ {len(tasks)} sinais gerados")
    print()
    
    if not tasks:
        print("⚠️  Nenhum sinal gerado (spreads podem estar altos)")
        mt5.shutdown()
        sys.exit(0)
    
    # Analisar cada símbolo
    print("=" * 70)
    print("ANÁLISE DE CADA SÍMBOLO")
    print("=" * 70)
    print()
    
    for symbol in config.TRADING_SYMBOLS:
        print(f"[{symbol}] Verificando...")
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"    ❌ Símbolo não encontrado")
            continue
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"    ❌ Sem dados de tick")
            continue
        
        spread = (tick.ask - tick.bid) / symbol_info.point
        max_spread = signal_generator._get_max_spread_for_symbol(symbol)
        
        print(f"    - Bid: {tick.bid}")
        print(f"    - Ask: {tick.ask}")
        print(f"    - Spread: {spread:.2f} pips (limite: {max_spread} pips)")
        
        if spread > max_spread:
            print(f"    ⚠️  Spread muito alto - NÃO gera sinal")
        else:
            print(f"    ✅ Spread OK - DEVE gerar sinal")
        
        # Verificar se há task para este símbolo
        symbol_tasks = [t for t in tasks if t.symbol == symbol]
        if symbol_tasks:
            task = symbol_tasks[0]
            print(f"    ✅ Sinal gerado: {task.action} {task.volume} @ {task.price}")
            print(f"    - SL: {task.sl}")
            print(f"    - TP: {task.tp}")
            
            # Calcular distância SL/TP
            sl_distance = abs(task.price - task.sl) / symbol_info.point
            tp_distance = abs(task.tp - task.price) / symbol_info.point
            print(f"    - SL Distance: {sl_distance:.0f} pontos")
            print(f"    - TP Distance: {tp_distance:.0f} pontos")
        else:
            print(f"    ❌ Nenhum sinal gerado para este símbolo")
        
        print()
    
    # Analisar estratégia (direção das ordens)
    print("=" * 70)
    print("ANÁLISE DA ESTRATÉGIA")
    print("=" * 70)
    print()
    
    buy_count = sum(1 for t in tasks if t.action == 'buy')
    sell_count = sum(1 for t in tasks if t.action == 'sell')
    
    print(f"Total de sinais: {len(tasks)}")
    print(f"Buy: {buy_count}")
    print(f"Sell: {sell_count}")
    print()
    
    # Verificar padrão de geração (i % 2)
    print("⚠️  PROBLEMA IDENTIFICADO:")
    print("   O código usa 'i % 2' para determinar ação:")
    print("   - Se índice par (0, 2, 4...) → buy")
    print("   - Se índice ímpar (1, 3, 5...) → sell")
    print()
    print("   Isso significa:")
    print("   - Símbolo 0 (EURUSD): sempre buy")
    print("   - Símbolo 1 (GBPUSD): sempre sell")
    print("   - Símbolo 2 (USDJPY): sempre buy")
    print("   - Símbolo 3 (XAUUSD): sempre sell")
    print("   - Símbolo 4 (US500): sempre buy")
    print()
    print("   ❌ PROBLEMA: Ação não é baseada em análise de mercado!")
    print("   ❌ PROBLEMA: Sempre a mesma direção para cada símbolo!")
    print("   ❌ PROBLEMA: Não há estratégia real, apenas padrão fixo!")
    print()
    
    # Verificar posições abertas
    print("=" * 70)
    print("POSIÇÕES ABERTAS NO MT5")
    print("=" * 70)
    print()
    
    positions = mt5.positions_get()
    if positions:
        print(f"✅ {len(positions)} posição(ões) aberta(s):")
        total_profit = 0
        for pos in positions:
            profit = pos.profit
            total_profit += profit
            status = "✅" if profit >= 0 else "❌"
            pos_type = "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL"
            print(f"    {status} {pos.symbol} {pos_type} {pos.volume} @ {pos.price_open}")
            print(f"      Profit: {profit:.2f} ({profit/pos.volume:.2f} por lote)")
            print(f"      SL: {pos.sl}")
            print(f"      TP: {pos.tp}")
            print()
        
        print(f"Profit Total: {total_profit:.2f}")
        if total_profit < 0:
            print("    ❌ Prejuízo total detectado")
    else:
        print("⚠️  Nenhuma posição aberta no momento")
    
    mt5.shutdown()
    
    print()
    print("=" * 70)
    print("DIAGNÓSTICO COMPLETO")
    print("=" * 70)
    print()
    print("PROBLEMAS IDENTIFICADOS:")
    print("1. ❌ Estratégia não baseada em análise de mercado")
    print("2. ❌ Ação determinada apenas por índice (i % 2)")
    print("3. ❌ Sempre mesma direção para cada símbolo")
    print("4. ❌ Não há lógica de entrada real")
    print()
    print("SOLUÇÃO NECESSÁRIA:")
    print("   Implementar estratégia real baseada em:")
    print("   - Análise técnica (indicadores)")
    print("   - Análise de momentum")
    print("   - Análise de tendência")
    print("   - Análise de força relativa")
    print()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

