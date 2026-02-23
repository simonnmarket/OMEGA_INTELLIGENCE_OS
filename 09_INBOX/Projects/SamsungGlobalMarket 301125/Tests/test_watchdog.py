#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DO WATCHDOG - VALIDAÇÃO DO SISTEMA
PROJETO: Samsung Global Market
"""

import sys
from pathlib import Path
import socket
import time

def test_health_check():
    """Testa o health checker"""
    print("[TEST] Testando Health Checker...")
    
    sys.path.insert(0, str(Path.cwd()))
    from server_watchdog import HealthChecker
    
    checker = HealthChecker('127.0.0.1', 5555)
    result = checker.check_health()
    
    if result:
        print("[OK] Health check passou (servidor está online)")
    else:
        print("[INFO] Health check falhou (servidor está offline - normal se não estiver rodando)")
    
    return True

def test_state_manager():
    """Testa o gerenciador de estado"""
    print("[TEST] Testando State Manager...")
    
    sys.path.insert(0, str(Path.cwd()))
    from server_watchdog import StateManager
    
    state_mgr = StateManager('test_state.json')
    
    # Salvar estado
    state = {
        'test': 'value',
        'timestamp': time.time()
    }
    state_mgr.save_state(state)
    print("[OK] Estado salvo")
    
    # Carregar estado
    loaded = state_mgr.load_state()
    if loaded.get('test') == 'value':
        print("[OK] Estado carregado corretamente")
    else:
        print("[ERRO] Estado não carregou corretamente")
        return False
    
    # Limpar arquivo de teste
    Path('test_state.json').unlink(missing_ok=True)
    print("[OK] Arquivo de teste removido")
    
    return True

def test_server_manager():
    """Testa o gerenciador de servidor"""
    print("[TEST] Testando Server Manager...")
    
    sys.path.insert(0, str(Path.cwd()))
    from server_watchdog import ServerManager
    
    if not Path('simple_mt5_server.py').exists():
        print("[SKIP] simple_mt5_server.py não encontrado - pulando teste")
        return True
    
    manager = ServerManager('simple_mt5_server.py')
    
    print(f"[INFO] Python encontrado: {manager.venv_python}")
    print(f"[INFO] Script path: {manager.script_path}")
    print("[OK] Server Manager inicializado")
    
    return True

def main():
    """Executa todos os testes"""
    print("=" * 70)
    print("TESTE DO WATCHDOG - VALIDAÇÃO DO SISTEMA")
    print("=" * 70)
    print("")
    
    tests = [
        ("Health Checker", test_health_check),
        ("State Manager", test_state_manager),
        ("Server Manager", test_server_manager)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            print("")
        except Exception as e:
            print(f"[ERRO] Teste '{name}' falhou: {e}")
            results.append((name, False))
            print("")
    
    # Relatório final
    print("=" * 70)
    print("RELATÓRIO DE TESTES")
    print("=" * 70)
    
    for name, result in results:
        status = "PASSOU" if result else "FALHOU"
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}: {status}")
    
    print("=" * 70)
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("[OK] Todos os testes passaram!")
        return 0
    else:
        print("[ERRO] Alguns testes falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())

