#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema Numeia v2.0
Verifica se todos os componentes estão funcionando corretamente
"""

import sys
from pathlib import Path
import MetaTrader5 as mt5
import json

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from numeia_executor_v2 import Config, load_config, SignalGenerator, CapitalManagement, EnhancedParallelExecutor

def test_system():
    print("=" * 80)
    print("TESTE COMPLETO DO SISTEMA NUMEIA v2.0")
    print("=" * 80)
    
    # 1. Verificar MT5
    print("\n[1/5] Verificando MetaTrader 5...")
    if not mt5.initialize():
        print("❌ ERRO: Não foi possível inicializar MetaTrader 5")
        return False
    print("✅ MT5 inicializado")
    
    # 2. Carregar configuração
    print("\n[2/5] Carregando configuração...")
    try:
        config = load_config()
        print(f"✅ Config carregado: {len(config.TRADING_SYMBOLS)} símbolos")
    except Exception as e:
        print(f"❌ ERRO ao carregar config: {e}")
        mt5.shutdown()
        return False
    
    # 3. Testar geração de sinais
    print("\n[3/5] Testando geração de sinais...")
    try:
        cm = CapitalManagement(config)
        sg = SignalGenerator(config.TRADING_SYMBOLS, cm, config)
        tasks = sg.generate_signals()
        print(f"✅ {len(tasks)} sinais gerados")
        if tasks:
            for task in tasks[:3]:
                print(f"  - {task.symbol}: {task.action} @ {task.price} (SL: {task.sl}, TP: {task.tp})")
    except Exception as e:
        print(f"❌ ERRO ao gerar sinais: {e}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        return False
    
    # 4. Testar executor
    print("\n[4/5] Testando executor (sem executar ordens)...")
    try:
        from numeia_executor_v2 import Metrics
        metrics = Metrics()
        executor = EnhancedParallelExecutor(config.MAX_PARALLEL_WORKERS, metrics, config)
        print("✅ Executor criado com sucesso")
        print(f"  - Max workers: {executor.max_workers}")
        print(f"  - Stop event: {executor._stop_event.is_set()}")
    except Exception as e:
        print(f"❌ ERRO ao criar executor: {e}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        return False
    
    # 5. Verificar métricas
    print("\n[5/5] Verificando métricas...")
    try:
        print(f"✅ Métricas OK:")
        print(f"  - Failures: {executor.metrics.failures}")
        print(f"  - Successes: {executor.metrics.successes}")
        print(f"  - Total orders: {executor.metrics.total_orders}")
        print(f"  - Filled orders: {executor.metrics.filled_orders}")
    except Exception as e:
        print(f"❌ ERRO ao verificar métricas: {e}")
        mt5.shutdown()
        return False
    
    mt5.shutdown()
    
    print("\n" + "=" * 80)
    print("✅ TESTE COMPLETO: TODOS OS COMPONENTES FUNCIONANDO")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)

