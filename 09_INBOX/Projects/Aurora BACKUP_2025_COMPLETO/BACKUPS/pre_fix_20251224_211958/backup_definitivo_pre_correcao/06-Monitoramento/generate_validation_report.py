#!/usr/bin/env python3
"""
Script para gerar relatório de validação Tier-0
"""

import sys
import os
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "06-Monitoramento"))

from neural_connection_monitor_v2 import NeuralConnectionMonitor

monitor = NeuralConnectionMonitor()
report_path = project_root / "AURORA_TIER0_VALIDATION_20251216.json"
report = monitor.generate_report(str(report_path))

print(f"[OK] Relatorio gerado: {report_path}")
print("[OK] Verifique os campos-chave:")
print("   • \"system_summary\" -> status geral")
print("   • \"detailed_reports\" -> saude por modulo")
print("   • \"recent_alerts\" -> historico de alertas (vazio = tudo OK)")

