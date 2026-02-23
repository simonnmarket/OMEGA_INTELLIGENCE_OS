# -*- coding: utf-8 -*-
"""
SAMSUNG GLOBAL MARKET - PROMETHEUS v3.0
TESTE DE CAMPO - FASE 1.5: Validação de Campo
EXECUÇÃO DE CICLO ÚNICO PARA VALIDAÇÃO

Este script executa APENAS UM CICLO do prometheus_brain_v1.1.py
para validação de campo antes da execução completa.

Uso: python test_brain_single_cycle.py
"""

import sys
from pathlib import Path

# Adicionar o diretório Server ao path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

# Importar módulo com ponto no nome
import importlib.util
spec = importlib.util.spec_from_file_location("prometheus_brain_v1_1", server_dir / "prometheus_brain_v1.1.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SystemConfig = module.SystemConfig
AIC_Controller = module.AIC_Controller

def main():
    """Executa um único ciclo de teste."""
    print("="*80)
    print("TESTE DE CAMPO - FASE 1.5: Validação de Campo")
    print("EXECUÇÃO DE CICLO ÚNICO PARA VALIDAÇÃO")
    print("="*80)
    
    config = SystemConfig()
    controller = AIC_Controller(config)
    
    try:
        print("\n[TESTE] Executando ciclo único de validação...")
        controller.run_cycle()
        print("\n[TESTE] Ciclo único concluído com sucesso!")
        print("\n[VALIDACAO] Verifique no terminal MT5 se a ordem foi executada:")
        print("  - Símbolo: XAUUSD")
        print("  - Volume: 0.01")
        print("  - Magic Number: 1000")
        print("  - Ação: BUY")
        print("  - Stop Loss: 150 pontos")
        print("  - Take Profit: 300 pontos")
        print("\n[PROXIMO PASSO] Se a ordem apareceu no MT5, Fase 1.5 foi concluída com sucesso!")
    except Exception as e:
        print(f"\n[ERRO] Falha durante o teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        controller.brain.executor._shutdown_mt5()

if __name__ == "__main__":
    main()

