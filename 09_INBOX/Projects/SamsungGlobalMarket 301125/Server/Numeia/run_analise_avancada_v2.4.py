#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar análise avançada de performance V2.4
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar análise avançada
print("="*80)
print("PROMETHEUS V2.4: ANÁLISE AVANÇADA DE PERFORMANCE")
print("="*80)
print("Analisando logs do Prometheus V2.3 com métricas avançadas...")
print()
print("Métricas Calculadas:")
print("  - Win Rate (Taxa de Acerto)")
print("  - Profit Factor (Fator de Lucro)")
print("  - Expectancy (Expectativa)")
print("  - Maximum Drawdown (MDD)")
print("  - Sharpe Ratio (Risco/Retorno)")
print("  - Win/Loss Ratio")
print("  - Análise de TP Parcial")
print("  - Análise por Símbolo")
print("="*80)
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.4_analise_avancada.py"], 
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

