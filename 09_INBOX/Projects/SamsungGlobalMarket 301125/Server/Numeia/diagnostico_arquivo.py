# -*- coding: utf-8 -*-
"""
Diagnóstico de problemas com prometheus_master_control_v4.1.py
"""

import sys
import os
from pathlib import Path

print("="*80)
print("DIAGNÓSTICO DE PROBLEMAS - prometheus_master_control_v4.1.py")
print("="*80)
print()

# 1. Verificar se arquivo existe
arquivo = "prometheus_master_control_v4.1.py"
print(f"1. Verificando arquivo: {arquivo}")
print("-" * 80)

if not os.path.exists(arquivo):
    print(f"✗ ERRO: Arquivo {arquivo} não encontrado!")
    print(f"   Diretório atual: {os.getcwd()}")
    sys.exit(1)
else:
    tamanho = os.path.getsize(arquivo)
    print(f"✓ Arquivo existe ({tamanho:,} bytes)")
print()

# 2. Verificar encoding
print("2. Verificando encoding...")
print("-" * 80)
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        primeira_linha = f.readline()
        print(f"✓ Encoding UTF-8 OK")
        print(f"  Primeira linha: {primeira_linha.strip()[:50]}")
except UnicodeDecodeError as e:
    print(f"✗ ERRO DE ENCODING: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ ERRO ao ler arquivo: {e}")
    sys.exit(1)
print()

# 3. Verificar sintaxe
print("3. Verificando sintaxe...")
print("-" * 80)
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    compile(codigo, arquivo, "exec")
    print("✓ Sintaxe OK - Sem erros de sintaxe")
except SyntaxError as e:
    print(f"✗ ERRO DE SINTAXE:")
    print(f"  Linha {e.lineno}: {e.text}")
    print(f"  Erro: {e.msg}")
    sys.exit(1)
except Exception as e:
    print(f"✗ ERRO ao compilar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# 4. Verificar imports básicos
print("4. Verificando imports básicos...")
print("-" * 80)
imports_ok = True
try:
    import MetaTrader5
    print("✓ MetaTrader5")
except ImportError as e:
    print(f"✗ MetaTrader5: {e}")
    imports_ok = False

try:
    import pandas
    print("✓ pandas")
except ImportError as e:
    print(f"✗ pandas: {e}")
    imports_ok = False

try:
    import numpy
    print("✓ numpy")
except ImportError as e:
    print(f"✗ numpy: {e}")
    imports_ok = False

if not imports_ok:
    print("\n⚠️ Algumas dependências não estão instaladas")
    print("  Execute: pip install MetaTrader5 pandas numpy")
print()

# 5. Testar execução direta
print("5. Testando execução direta...")
print("-" * 80)
print("Tentando executar: python prometheus_master_control_v4.1.py --help")
print()

try:
    import subprocess
    result = subprocess.run(
        [sys.executable, arquivo, "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print("✓ Execução direta OK")
    else:
        print(f"⚠️ Código de saída: {result.returncode}")
        if result.stderr:
            print(f"  Erro: {result.stderr[:200]}")
except subprocess.TimeoutExpired:
    print("⚠️ Timeout - arquivo pode estar em loop infinito")
except Exception as e:
    print(f"⚠️ Erro ao executar: {e}")
print()

# 6. Verificar shebang
print("6. Verificando shebang...")
print("-" * 80)
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        primeira = f.readline().strip()
        if primeira.startswith('#!'):
            print(f"✓ Shebang encontrado: {primeira}")
            if 'python3' in primeira or 'python' in primeira:
                print("  ✓ Shebang válido")
            else:
                print("  ⚠️ Shebang pode não funcionar no Windows")
        else:
            print("⚠️ Sem shebang (normal no Windows)")
except Exception as e:
    print(f"✗ Erro: {e}")
print()

# RESUMO
print("="*80)
print("RESUMO DO DIAGNÓSTICO")
print("="*80)

if imports_ok:
    print("✅ Arquivo está OK e pode ser executado!")
    print()
    print("Para executar:")
    print(f"  python {arquivo} discovery")
    print(f"  python {arquivo} production")
else:
    print("⚠️ Arquivo OK mas faltam dependências")
    print("  Instale: pip install MetaTrader5 pandas numpy")

print("="*80)
print("\nPressione ENTER para sair...")
input()

