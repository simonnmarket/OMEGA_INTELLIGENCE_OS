#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar Prometheus V2.3 Gerenciamento Escalonado
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar V2.3
print("="*80)
print("INICIANDO PROMETHEUS V2.3 (GERENCIAMENTO ESCALONADO)")
print("="*80)
print("Foco: Execução + SL/TP + Monitoramento + Telemetria + BE + TS + TP Parcial")
print("Estratégia: MA20 > MA50 = BUY")
print("Volume Inicial: 0.02 lotes (permite fechamento parcial de 0.01)")
print("TP Parcial: Fecha 50% em 40 pips de lucro")
print("TP Final: 80 pips (para o volume restante)")
print("Break-Even: Move SL para entrada quando lucro >= 15 pips")
print("Trailing Stop: Move SL seguindo o preço (20 pips de distância)")
print("="*80)
print("Pressione Ctrl+C para parar o sistema")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.3_gerenciamento_escalonado.py"], 
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

