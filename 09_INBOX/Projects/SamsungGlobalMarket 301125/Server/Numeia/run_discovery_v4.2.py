#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar discovery v4.2
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar discovery
print("="*80)
print("EXECUTANDO DISCOVERY v4.2...")
print("="*80)
print()

try:
    result = subprocess.run([sys.executable, "prometheus_master_control_v4.2.py", "discovery"], 
                          check=False, 
                          capture_output=False)
    print("\n" + "="*80)
    if result.returncode == 0:
        print("DISCOVERY CONCLUÍDO COM SUCESSO!")
    else:
        print(f"DISCOVERY TERMINOU COM CÓDIGO: {result.returncode}")
    print("="*80)
except Exception as e:
    print(f"\nERRO ao executar: {e}")
    import traceback
    traceback.print_exc()

print("\nPressione ENTER para sair...")
input()

