#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar Prometheus V2.1 Gestão de Risco
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar V2.1
print("="*80)
print("INICIANDO PROMETHEUS V2.1 (GESTÃO DE RISCO AVANÇADA)")
print("="*80)
print("Foco: Execução + SL/TP + Monitoramento + Telemetria + BE + Trailing Stop")
print("Estratégia: MA20 > MA50 = BUY")
print("Monitoramento: Fecha posições quando sinal BUY é perdido")
print("Break-Even: Move SL para entrada quando lucro >= 15 pips")
print("Trailing Stop: Move SL seguindo o preço (20 pips de distância)")
print("="*80)
print("Pressione Ctrl+C para parar o sistema")
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.1_gestao_risco.py"], 
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

