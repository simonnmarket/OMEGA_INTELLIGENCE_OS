#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar Prometheus V1.0 MVPO
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar V1.0
print("="*80)
print("INICIANDO PROMETHEUS V1.0 MVPO (MÍNIMO VIÁVEL OPERACIONAL)")
print("="*80)
print("Foco: Conexão, Análise Simples, Execução Garantida")
print("Estratégia: MA5 > MA20 = BUY")
print("="*80)
print("Pressione Ctrl+C para parar o sistema")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v1.0_mvpo.py"], 
                          check=False)
except KeyboardInterrupt:
    print("\n\nSistema interrompido pelo usuário.")
except Exception as e:
    print(f"\nERRO ao executar: {e}")
    import traceback
    traceback.print_exc()

print("\nSistema finalizado.")
print("Pressione ENTER para sair...")
input()

