#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar Prometheus V2.0 Telemetria
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar V2.0
print("="*80)
print("INICIANDO PROMETHEUS V2.0 (TELEMETRIA)")
print("="*80)
print("Foco: Execução + SL/TP + Monitoramento + Logging Estruturado (JSON)")
print("Estratégia: MA20 > MA50 = BUY")
print("Monitoramento: Fecha posições quando sinal BUY é perdido")
print("Telemetria: Logging JSON estruturado para análise futura")
print("="*80)
print("Pressione Ctrl+C para parar o sistema")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.0_telemetria.py"], 
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

