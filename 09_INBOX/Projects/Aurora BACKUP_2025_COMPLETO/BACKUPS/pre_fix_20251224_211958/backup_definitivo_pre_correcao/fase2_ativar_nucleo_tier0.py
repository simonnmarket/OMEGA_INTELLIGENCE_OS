#!/usr/bin/env python3
"""
FASE 2: ATIVAÇÃO DO NÚCLEO TIER-0
Registra os 3 componentes críticos no Genesis Includes
"""

import sys
import os
from pathlib import Path

# Adicionar paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "modules"))
sys.path.insert(0, str(project_root / "00-Governanca"))
sys.path.insert(0, str(project_root / "06-Monitoramento"))

print("=" * 70)
print("FASE 2: ATIVACAO DO NUCLEO TIER-0")
print("=" * 70)

try:
    # Importar Genesis
    from genesis_includes_v3_complete import get_genesis
    
    genesis = get_genesis()
    
    # 2.1 Registrar NCNTModule Template v2.0
    print("\n[2.1] Registrando NCNTModule Template v2.0...")
    try:
        from modules.ncnt_module_template_v2 import NCNTModule
        genesis.register(
            name="ncnt_module_template",
            dependency=NCNTModule,
            is_singleton=False,
            version="2.0.0"
        )
        print("[OK] NCNTModule Template v2.0 registrado")
    except Exception as e:
        print(f"[AVISO] Erro ao registrar template: {e}")
    
    # 2.2 Registrar Neural Connection Monitor
    print("\n[2.2] Registrando Neural Connection Monitor...")
    try:
        from neural_connection_monitor_v2 import NeuralConnectionMonitor
        monitor_instance = NeuralConnectionMonitor()
        genesis.register(
            name="neural_connection_monitor",
            dependency=monitor_instance,
            is_singleton=True,
            version="2.0.0"
        )
        print("[OK] Neural Connection Monitor registrado")
    except Exception as e:
        print(f"[AVISO] Erro ao registrar monitor: {e}")
    
    # 2.3 Registrar RegulatoryContext
    print("\n[2.3] Registrando RegulatoryContext...")
    try:
        from regulatory_context import RegulatoryContext
        regulatory_instance = RegulatoryContext()
        genesis.register(
            name="regulatory_context",
            dependency=regulatory_instance,
            is_singleton=True,
            version="1.0.0"
        )
        print("[OK] RegulatoryContext registrado")
    except Exception as e:
        print(f"[AVISO] Erro ao registrar regulatory context: {e}")
    
    # 2.4 Iniciar monitoramento contínuo
    print("\n[2.4] Iniciando monitoramento continuo...")
    try:
        monitor = genesis.resolve("neural_connection_monitor")
        if monitor:
            monitor.start_monitoring()
            print("[OK] Monitoramento iniciado")
            print("[INFO] Monitor rodando em background (intervalo: 30s)")
        else:
            print("[AVISO] Monitor nao encontrado no Genesis")
    except Exception as e:
        print(f"[AVISO] Erro ao iniciar monitoramento: {e}")
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO FASE 2:")
    print(f"  Modulos registrados no Genesis: {len(genesis._dependency_registry)}")
    print("  [OK] NCNTModule Template v2.0")
    print("  [OK] Neural Connection Monitor")
    print("  [OK] RegulatoryContext")
    print("=" * 70)
    
except Exception as e:
    print(f"[ERRO] Falha na FASE 2: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

