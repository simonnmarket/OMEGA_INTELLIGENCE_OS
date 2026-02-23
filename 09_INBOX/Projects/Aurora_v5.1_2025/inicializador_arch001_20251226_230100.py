#!/usr/bin/env python3
"""
🚀 SCRIPT DE INICIALIZAÇÃO ARCH-001
Inicializa todos os componentes do sistema integrado
"""

import os
import sys
from datetime import datetime

def inicializar_sistema():
    """Inicializar sistema ARCH-001"""
    print("=" * 80)
    print("🚀 INICIALIZANDO ARCH-001 - SISTEMA INTEGRADO")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().isoformat()}")
    print()
    
    componentes = [
        ("📈 Monitoramento", "monitor_arch001_20251226_230100.py"),
        ("🔥 Executor principal", "ARCH001_EXECUTOR_FINAL_20251226_230100.py"),
        ("🔄 Sistema de recuperação", "sistema_recuperacao_arch001_20251226_230100.py")
    ]
    
    for nome, script in componentes:
        if os.path.exists(script):
            print(f"✅ {nome}: {script}")
        else:
            print(f"⚠️  {nome}: {script} (não encontrado)")
    
    print()
    print("=" * 80)
    print("✅ ARCH-001 INICIALIZADO")
    print("=" * 80)

if __name__ == "__main__":
    inicializar_sistema()
