#!/usr/bin/env python3
"""
AURORA NCNT System - Entry Point
Sistema de Trading Modular Completo
"""

import asyncio
import sys
from pathlib import Path

# Adicionar raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from system_core.ncnt_orchestrator_complete import NCNTOrchestrator


async def main():
    """Função principal"""
    print("=" * 80)
    print("AURORA NCNT SYSTEM - v2.0")
    print("=" * 80)
    print()
    
    orchestrator = NCNTOrchestrator()
    
    try:
        # Inicializar sistema completo
        await orchestrator.initialize()
        
        # Mostrar status
        print("\nSistema inicializado com sucesso!")
        print(f"Modulos ativos: {len(orchestrator.modules)}")
        print(f"Status: {orchestrator.system_status}")
        
        # Executar demo workflow
        print("\nExecutando workflow de demonstracao...")
        await orchestrator.run_demo_workflow()
        
        # Manter sistema rodando
        print("\nSistema rodando. Pressione Ctrl+C para parar...")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\n\nRecebido sinal de parada...")
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nSistema encerrado.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuario.")
