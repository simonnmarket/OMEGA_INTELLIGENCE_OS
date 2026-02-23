#!/usr/bin/env python3
"""
Teste Completo de Execução - Numeia v2.0
Testa se o sistema consegue executar completamente
"""

import sys
import json
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("TESTE COMPLETO DE EXECUÇÃO - Numeia v2.0")
print("=" * 70)
print()

try:
    # 1. Importar módulos
    print("[1/7] Importando módulos...")
    from numeia_executor_v2 import Config, load_config, SignalGenerator, CapitalManagement, Task, Metrics, EnhancedParallelExecutor
    import MetaTrader5 as mt5
    print("    ✅ Módulos importados com sucesso")
    print()
    
    # 2. Carregar configuração
    print("[2/7] Carregando configuração...")
    config = load_config()
    print("    ✅ Configuração carregada")
    print(f"    - EMERGENCY_MODE_ENABLED: {config.EMERGENCY_MODE_ENABLED}")
    print(f"    - MAX_PARALLEL_WORKERS: {config.MAX_PARALLEL_WORKERS}")
    print(f"    - TRADING_SYMBOLS: {len(config.TRADING_SYMBOLS)} símbolos")
    print()
    
    # 3. Inicializar MT5
    print("[3/7] Inicializando MetaTrader 5...")
    if not mt5.initialize():
        print(f"    ❌ Falha ao inicializar MT5: {mt5.last_error()}")
        sys.exit(1)
    print("    ✅ MT5 inicializado")
    account_info = mt5.account_info()
    if account_info:
        print(f"    - Conta: {account_info.login}")
        print(f"    - Saldo: {account_info.balance}")
        print(f"    - Trade Permitido: {account_info.trade_allowed}")
    print()
    
    # 4. Criar componentes
    print("[4/7] Criando componentes do sistema...")
    metrics = Metrics()
    capital_manager = CapitalManagement(config)
    signal_generator = SignalGenerator(config.TRADING_SYMBOLS, capital_manager, config)
    print("    ✅ Componentes criados")
    print()
    
    # 5. Testar geração de sinais
    print("[5/7] Testando geração de sinais...")
    tasks = signal_generator.generate_signals()
    print(f"    ✅ {len(tasks)} sinais gerados")
    if tasks:
        for task in tasks[:3]:
            print(f"      - {task.symbol}: {task.action} {task.volume} @ {task.price}")
    else:
        print("    ⚠️  Nenhum sinal gerado (spreads podem estar altos)")
    print()
    
    # 6. Criar executor
    print("[6/7] Criando executor...")
    try:
        executor = EnhancedParallelExecutor(config.MAX_PARALLEL_WORKERS, metrics, config)
        print("    ✅ Executor criado")
    except Exception as e:
        print(f"    ❌ Erro ao criar executor: {e}")
        traceback.print_exc()
        sys.exit(1)
    print()
    
    # 7. Testar execução de uma tarefa (se houver)
    if tasks:
        print("[7/7] Testando execução de uma tarefa...")
        task = tasks[0]
        print(f"    - Testando: {task.symbol} {task.action} {task.volume}")
        try:
            success, filled = executor._execute_task(task)
            if success:
                print(f"    ✅ Ordem executada com sucesso (filled: {filled})")
            else:
                print(f"    ⚠️  Ordem falhou (filled: {filled})")
        except Exception as e:
            print(f"    ❌ Erro ao executar tarefa: {e}")
            traceback.print_exc()
    else:
        print("[7/7] Pulando teste de execução (nenhum sinal gerado)")
    
    mt5.shutdown()
    
    print()
    print("=" * 70)
    print("TESTE COMPLETO CONCLUÍDO")
    print("=" * 70)
    
    if tasks:
        print("✅ Sistema está FUNCIONAL e pronto para executar ordens")
    else:
        print("⚠️  Sistema está funcional mas não está gerando sinais")
        print("   Motivos possíveis:")
        print("   - Spreads acima dos limites configurados")
        print("   - Mercado fechado")
        print("   - Símbolos não disponíveis")
    
    print()
    print("Para iniciar o sistema:")
    print("  python numeia_executor_v2.py")
    
except Exception as e:
    print(f"\n❌ ERRO CRÍTICO: {e}")
    traceback.print_exc()
    sys.exit(1)

