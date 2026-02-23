#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO RÁPIDA DE RESULTADOS DA VALIDAÇÃO v3.6
"""

import os
import pandas as pd
from pathlib import Path

print("=" * 80)
print("VERIFICAÇÃO DE RESULTADOS - VALIDAÇÃO v3.6")
print("=" * 80)
print()

results_file = "backtest_validation_results_v3.6.csv"
comparison_file = "validation_comparison_v3.6.csv"

# Verificar arquivo de resultados
if os.path.exists(results_file):
    print(f"✅ {results_file} ENCONTRADO")
    print()
    try:
        df = pd.read_csv(results_file)
        print(f"Total de resultados: {len(df)}")
        print()
        print("RESULTADOS:")
        print(df.to_string())
        print()
        
        # Verificar decisão
        if 'decision' in df.columns:
            decisions = df['decision'].unique()
            print(f"Decisões encontradas: {list(decisions)}")
        
        # Separar baseline e filtro
        if 'filter_used' in df.columns:
            baseline = df[df['filter_used'] == False]
            with_filter = df[df['filter_used'] == True]
            print()
            print(f"Baseline (sem filtro): {len(baseline)} resultados")
            print(f"Com filtro: {len(with_filter)} resultados")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
else:
    print(f"❌ {results_file} NÃO ENCONTRADO")
    print(f"   Caminho verificado: {os.path.abspath(results_file)}")

print()

# Verificar arquivo de comparação
if os.path.exists(comparison_file):
    print(f"✅ {comparison_file} ENCONTRADO")
    print()
    try:
        df = pd.read_csv(comparison_file)
        print("COMPARAÇÃO:")
        print(df.to_string())
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
else:
    print(f"❌ {comparison_file} NÃO ENCONTRADO")

print()
print("=" * 80)

