#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar production v4.2
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar production
print("="*80)
print("INICIANDO SERVIDOR PRODUCTION v4.2...")
print("="*80)
print("Pressione Ctrl+C para parar o servidor")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_master_control_v4.2.py", "production"], 
                          check=False)
except KeyboardInterrupt:
    print("\n\nServidor interrompido pelo usuário.")
except Exception as e:
    print(f"\nERRO ao executar: {e}")
    import traceback
    traceback.print_exc()

print("\nServidor finalizado.")
print("Pressione ENTER para sair...")
input()

