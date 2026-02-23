#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO RÁPIDA DO STATUS DO SISTEMA
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("VERIFICAÇÃO DE STATUS DO SISTEMA - PROMETHEUS v3.4")
print("=" * 80)
print()

# 1. Verificar arquivos
print("1. VERIFICANDO ARQUIVOS:")
print("-" * 80)
files_to_check = [
    "backtest_comprehensive_v3.4.py",
    "executor_emergency_v3.1.py",
    "config.json"
]

for file in files_to_check:
    path = Path(file)
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {file} - {size:,} bytes")
    else:
        print(f"❌ {file} - NÃO ENCONTRADO")

print()

# 2. Verificar MT5
print("2. VERIFICANDO METATRADER 5:")
print("-" * 80)
try:
    import MetaTrader5 as mt5
    
    if mt5.initialize():
        account = mt5.account_info()
        terminal = mt5.terminal_info()
        
        print(f"✅ MT5 Conectado")
        print(f"   Conta: {account.login if account else 'N/A'}")
        print(f"   Servidor: {account.server if account else 'N/A'}")
        print(f"   Terminal Conectado: {terminal.connected if terminal else 'N/A'}")
        
        # Verificar alguns símbolos
        print()
        print("3. VERIFICANDO SÍMBOLOS DISPONÍVEIS:")
        print("-" * 80)
        
        test_symbols = ["BTCUSD", "ETHUSD", "XAUUSD", "EURUSD"]
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    status = "🟢 ATIVO" if (datetime.now().timestamp() - tick.time) < 900 else "🔴 INATIVO"
                    print(f"✅ {symbol}: {status} | Preço: {tick.ask:.2f}")
                else:
                    print(f"⚠️ {symbol}: Símbolo existe mas sem tick")
            else:
                print(f"❌ {symbol}: Não encontrado")
        
        mt5.shutdown()
    else:
        error = mt5.last_error()
        print(f"❌ MT5 Falhou ao inicializar")
        print(f"   Erro: {error}")
        
except ImportError:
    print("❌ MetaTrader5 não instalado")
    print("   Execute: pip install MetaTrader5")
except Exception as e:
    print(f"❌ Erro ao verificar MT5: {e}")

print()

# 3. Verificar dependências Python
print("4. VERIFICANDO DEPENDÊNCIAS PYTHON:")
print("-" * 80)
dependencies = ["pandas", "numpy", "pydantic"]
for dep in dependencies:
    try:
        __import__(dep)
        print(f"✅ {dep} instalado")
    except ImportError:
        print(f"❌ {dep} NÃO instalado")

print()

# 4. Verificar processos Python
print("5. VERIFICANDO PROCESSOS PYTHON:")
print("-" * 80)
try:
    import subprocess
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], 
                          capture_output=True, text=True, timeout=5)
    if "python.exe" in result.stdout:
        lines = [l for l in result.stdout.split('\n') if 'python.exe' in l]
        print(f"✅ {len(lines)} processo(s) Python rodando")
        for line in lines[:3]:  # Mostrar até 3
            print(f"   {line.strip()}")
    else:
        print("ℹ️ Nenhum processo Python rodando")
except Exception as e:
    print(f"⚠️ Não foi possível verificar processos: {e}")

print()

# 5. Verificar arquivo de log
print("6. VERIFICANDO LOGS:")
print("-" * 80)
log_file = Path("numeia_execution.jsonl")
if log_file.exists():
    size = log_file.stat().st_size
    lines = sum(1 for _ in open(log_file)) if size > 0 else 0
    print(f"✅ numeia_execution.jsonl existe")
    print(f"   Tamanho: {size:,} bytes")
    print(f"   Linhas: {lines:,}")
    
    # Últimas linhas
    if lines > 0:
        print()
        print("   Últimas 3 linhas:")
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            last_lines = f.readlines()[-3:]
            for i, line in enumerate(last_lines, 1):
                print(f"   {i}. {line.strip()[:80]}...")
else:
    print("ℹ️ Arquivo de log não encontrado (normal se sistema não foi executado)")

print()
print("=" * 80)
print("VERIFICAÇÃO CONCLUÍDA")
print("=" * 80)

