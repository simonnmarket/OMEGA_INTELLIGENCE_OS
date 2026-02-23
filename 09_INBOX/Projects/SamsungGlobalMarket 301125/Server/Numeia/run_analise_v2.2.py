#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar análise de performance V2.2
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar análise
print("="*80)
print("PROMETHEUS V2.2: ANÁLISE DE PERFORMANCE")
print("="*80)
print("Analisando logs do Prometheus V2.1...")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.2_analise_performance.py"], 
                          check=False)
except KeyboardInterrupt:
    print("\n\nAnálise interrompida pelo usuário.")
except Exception as e:
    print(f"\nERRO ao executar análise: {e}")
    import traceback
    traceback.print_exc()

print("\nAnálise concluída.")
print("Pressione ENTER para sair...")
input()

