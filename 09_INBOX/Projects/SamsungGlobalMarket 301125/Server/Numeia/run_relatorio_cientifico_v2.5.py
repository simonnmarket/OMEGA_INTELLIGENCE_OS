#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar relatório científico V2.5
"""
import subprocess
import sys
import os

# Mudar para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Executar relatório científico
print("="*80)
print("PROMETHEUS V2.5: RELATÓRIO CIENTÍFICO DE PERFORMANCE")
print("="*80)
print("Gerando relatório JSON estruturado com:")
print("  - Relatório de Ordens Executadas")
print("  - Métricas de Performance")
print("  - Análise de Eficácia da Estratégia (MA5/MA20)")
print("  - Contexto de Mercado")
print("  - Métricas de Validação de Hipóteses (H1-H4)")
print("  - Saúde do Sistema")
print("  - Análise CEO Científica")
print("="*80)
print()

try:
    result = subprocess.run([sys.executable, "prometheus_v2.5_relatorio_cientifico.py"], 
                          check=False)
except KeyboardInterrupt:
    print("\n\nRelatório interrompido pelo usuário.")
except Exception as e:
    print(f"\nERRO ao executar relatório: {e}")
    import traceback
    traceback.print_exc()

print("\nRelatório concluído.")
print("Pressione ENTER para sair...")
input()

