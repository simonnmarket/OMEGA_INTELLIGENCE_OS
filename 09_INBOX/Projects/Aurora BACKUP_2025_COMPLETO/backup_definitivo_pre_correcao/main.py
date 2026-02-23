#!/usr/bin/env python3
"""
🏦 AURORA NCNT System - Entry Point
Sistema de Trading Modular
"""

import asyncio
import sys
from system_core import NCNTOrchestrator


async def main():
    """Função principal"""
    print("=" * 60)
    print("🏦 AURORA NCNT SYSTEM")
    print("=" * 60)
    print()
    
    orchestrator = NCNTOrchestrator()
    
    try:
        # Iniciar sistema
        await orchestrator.start()
        
        # Mostrar status
        status = orchestrator.get_system_status()
        print("\n📊 Status do Sistema:")
        print(f"   Sistema: {status['system']}")
        print(f"   Versão: {status['version']}")
        print(f"   Status: {'🟢 Rodando' if status['running'] else '🔴 Parado'}")
        print(f"   Módulos registrados: {status['registry_stats']['total_modules']}")
        
        # Manter sistema rodando
        print("\n✅ Sistema iniciado. Pressione Ctrl+C para parar...")
        await asyncio.Event().wait()  # Aguardar indefinidamente
        
    except KeyboardInterrupt:
        print("\n\n🛑 Recebido sinal de parada...")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await orchestrator.stop()
        print("\n👋 Sistema encerrado.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Encerrado pelo usuário.")

