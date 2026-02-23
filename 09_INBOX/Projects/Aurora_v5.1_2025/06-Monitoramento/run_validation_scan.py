#!/usr/bin/env python3
"""
Script de validação - Scan completo do sistema
"""

import sys
import os
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "06-Monitoramento"))

from neural_connection_monitor_v2 import NeuralConnectionMonitor
import time

print("[OK] Iniciando scan completo...")
monitor = NeuralConnectionMonitor(scan_interval_seconds=5)
monitor.start_monitoring()

time.sleep(12)  # Aguarda 2 ciclos completos

print("[OK] Coletando resultados...")
summary = monitor.get_health_summary()
monitor.stop_monitoring()

print(f"[OK] Scan concluido | Modulos monitorados: {summary.get('total_modules', 0)}")
print(f"   • Saudaveis: {summary.get('healthy_modules', 0)}")
print(f"   • Degradados: {summary.get('degraded_modules', 0)}")
print(f"   • Criticos: {summary.get('critical_modules', 0)}")
print(f"   • Score do sistema: {summary.get('system_score', 0):.1f}/100")
print(f"   • Status: {summary.get('system_status', 'UNKNOWN')}")

