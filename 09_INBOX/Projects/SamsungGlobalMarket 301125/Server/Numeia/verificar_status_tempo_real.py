#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO DE STATUS EM TEMPO REAL
Verifica se há servidores ou processos rodando AGORA
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

print("="*80)
print("VERIFICAÇÃO DE STATUS EM TEMPO REAL")
print("="*80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. Verificar executor_emergency_v3.1.py (servidor antigo)
print("1. SERVIDOR ANTIGO (executor_emergency_v3.1.py):")
print("-" * 80)
heartbeat_old = Path("executor_heartbeat.tmp")
if heartbeat_old.exists():
    last_mod = os.path.getmtime(heartbeat_old)
    age_seconds = time.time() - last_mod
    age_minutes = age_seconds / 60
    age_hours = age_seconds / 3600
    
    if age_seconds < 120:  # Atualizado nos últimos 2 minutos
        print(f"✓ RODANDO - Heartbeat atualizado há {int(age_seconds)}s")
        print(f"  Última atualização: {datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"✗ PARADO - Heartbeat desatualizado há {int(age_minutes)} minutos ({int(age_hours)} horas)")
        print(f"  Última atualização: {datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("✗ NÃO RODANDO - Heartbeat não encontrado")
print()

# 2. Verificar prometheus_master_control_v4.1.py (servidor novo)
print("2. SERVIDOR NOVO (prometheus_master_control_v4.1.py):")
print("-" * 80)
heartbeat_new = Path("prometheus_heartbeat.tmp")
if heartbeat_new.exists():
    last_mod = os.path.getmtime(heartbeat_new)
    age_seconds = time.time() - last_mod
    age_minutes = age_seconds / 60
    
    if age_seconds < 120:
        print(f"✓ RODANDO - Heartbeat atualizado há {int(age_seconds)}s")
        print(f"  Última atualização: {datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"✗ PARADO - Heartbeat desatualizado há {int(age_minutes)} minutos")
        print(f"  Última atualização: {datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("✗ NÃO RODANDO - Heartbeat não encontrado")
print()

# 3. Verificar logs recentes
print("3. LOGS RECENTES:")
print("-" * 80)

# Log do servidor antigo
log_old = Path("numeia_execution.jsonl")
if log_old.exists():
    last_mod = os.path.getmtime(log_old)
    age_seconds = time.time() - last_mod
    age_minutes = age_seconds / 60
    print(f"  numeia_execution.jsonl: Última atualização há {int(age_minutes)} minutos")
    if age_minutes < 5:
        print("  ✓ Log recente (servidor antigo pode estar rodando)")
    else:
        print("  ✗ Log antigo (servidor antigo parado)")
else:
    print("  numeia_execution.jsonl: Não encontrado")

# Log do servidor novo
log_new = Path("prometheus_master_log.jsonl")
if log_new.exists():
    last_mod = os.path.getmtime(log_new)
    age_seconds = time.time() - last_mod
    age_minutes = age_seconds / 60
    print(f"  prometheus_master_log.jsonl: Última atualização há {int(age_minutes)} minutos")
    if age_minutes < 5:
        print("  ✓ Log recente (servidor novo pode estar rodando)")
    else:
        print("  ✗ Log antigo (servidor novo parado)")
else:
    print("  prometheus_master_log.jsonl: Não encontrado")
print()

# 4. Verificar correções aplicadas
print("4. CORREÇÕES APLICADAS:")
print("-" * 80)
try:
    with open("prometheus_master_control_v4.1.py", 'r', encoding='utf-8') as f:
        content = f.read()
        if '"max_spread_points": 200' in content:
            print("✓ Filtros ajustados (max_spread: 200)")
        else:
            print("✗ Filtros NÃO ajustados")
        
        if "FALLBACK" in content or "fallback" in content:
            print("✓ Fallback implementado (usa config.json se discovery falhar)")
        else:
            print("✗ Fallback NÃO implementado")
except:
    print("✗ Erro ao verificar correções")
print()

# 5. Resumo final
print("="*80)
print("RESUMO:")
print("="*80)

servidores_rodando = 0
if heartbeat_old.exists() and (time.time() - os.path.getmtime(heartbeat_old)) < 120:
    servidores_rodando += 1
    print("✓ Servidor ANTIGO (v3.1) está RODANDO")
if heartbeat_new.exists() and (time.time() - os.path.getmtime(heartbeat_new)) < 120:
    servidores_rodando += 1
    print("✓ Servidor NOVO (v4.1) está RODANDO")

if servidores_rodando == 0:
    print("✗ NENHUM servidor está rodando no momento")
    print()
    print("Para iniciar:")
    print("  - Servidor novo: python run_production.py")
    print("  - Servidor antigo: python executor_emergency_v3.1.py")
else:
    print(f"✓ {servidores_rodando} servidor(es) rodando")

print("="*80)
print("\nPressione ENTER para sair...")
input()

