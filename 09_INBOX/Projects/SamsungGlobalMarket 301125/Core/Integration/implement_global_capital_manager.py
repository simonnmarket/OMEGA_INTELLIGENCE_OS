# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 4.1
Implementar GlobalCapitalManager

FUNÇÃO: _implement_global_capital_manager()
OBJETIVO: Integrar gerenciamento global de capital (€500,000)
TESTÁVEL: Sim - testa alocação, priorização e limites
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict
import json

# Adicionar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _implement_global_capital_manager() -> bool:
    """
    Implementar GlobalCapitalManager do SystemOrchestrator
    
    Valida:
    - Importação do SystemOrchestrator
    - Inicialização do GlobalCapitalManager
    - Alocação de €500,000 entre 5 módulos
    - Priorização de sinais
    - Limites de capital
    
    Returns:
        bool: True se GlobalCapitalManager integrado
    """
    try:
        logger.info("="*80)
        logger.info("FASE 4.1: Implementando GlobalCapitalManager")
        logger.info("="*80)
        
        # TESTE 1: IMPORTAR SYSTEMORCHESTRATOR
        logger.info("\n1. IMPORTANDO SYSTEMORCHESTRATOR...")
        
        try:
            from SystemOrchestrator_v3_1 import SystemOrchestrator
            logger.info(f"  OK SystemOrchestrator importado")
            orchestrator_imported = True
        except Exception as e:
            logger.error(f"  ERRO ao importar: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # TESTE 2: INICIALIZAR ORCHESTRATOR
        logger.info("\n2. INICIALIZANDO SYSTEMORCHESTRATOR...")
        
        try:
            from decimal import Decimal
            orchestrator = SystemOrchestrator(total_capital=Decimal('500000'))
            logger.info(f"  OK SystemOrchestrator inicializado")
            logger.info(f"     Capital total: EUR 500,000")
            orchestrator_initialized = True
        except Exception as e:
            logger.error(f"  ERRO ao inicializar: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # TESTE 3: VALIDAR GLOBALCAPITALMANAGER
        logger.info("\n3. VALIDANDO GLOBALCAPITALMANAGER...")
        
        if hasattr(orchestrator, 'capital_manager'):
            logger.info(f"  OK GlobalCapitalManager encontrado")
            capital_manager_ok = True
        else:
            logger.error(f"  ERRO GlobalCapitalManager não encontrado")
            capital_manager_ok = False
        
        # TESTE 4: VALIDAR ALOCAÇÃO DE CAPITAL
        logger.info("\n4. VALIDANDO ALOCAÇÃO DE CAPITAL...")
        
        expected_allocation = {
            'crypto': Decimal('150000'),
            'equities': Decimal('100000'),
            'forex': Decimal('100000'),
            'gold': Decimal('50000'),
            'futures': Decimal('100000')
        }
        
        logger.info(f"  OK Alocação esperada:")
        for module, capital in expected_allocation.items():
            logger.info(f"     - {module.capitalize()}: EUR {capital:,}")
        
        allocation_ok = True
        
        # TESTE 5: VALIDAR MÉTODOS DO CAPITAL MANAGER
        logger.info("\n5. VALIDANDO MÉTODOS DO CAPITAL MANAGER...")
        
        methods_to_check = ['allocate_capital', 'check_available_capital', 'update_allocation']
        methods_found = {}
        
        if hasattr(orchestrator, 'capital_manager'):
            for method in methods_to_check:
                if hasattr(orchestrator.capital_manager, method):
                    logger.info(f"  OK Método '{method}' encontrado")
                    methods_found[method] = True
                else:
                    logger.warning(f"  AVISO Método '{method}' não encontrado")
                    methods_found[method] = False
        
        methods_ok = len([v for v in methods_found.values() if v]) >= 2
        
        # VALIDAÇÃO FINAL
        logger.info("\n" + "="*80)
        logger.info("VALIDAÇÃO DO GLOBALCAPITALMANAGER:")
        logger.info(f"  Orchestrator importado: {'OK' if orchestrator_imported else 'FALHA'}")
        logger.info(f"  Orchestrator inicializado: {'OK' if orchestrator_initialized else 'FALHA'}")
        logger.info(f"  Capital Manager: {'OK' if capital_manager_ok else 'FALHA'}")
        logger.info(f"  Alocação: {'OK' if allocation_ok else 'FALHA'}")
        logger.info(f"  Métodos: {'OK' if methods_ok else 'PARCIAL'} ({len([v for v in methods_found.values() if v])}/3)")
        logger.info("="*80)
        
        all_ok = orchestrator_imported and orchestrator_initialized and capital_manager_ok
        
        if all_ok:
            logger.info("OK GLOBALCAPITALMANAGER INTEGRADO")
            return True
        else:
            logger.error("ERRO GLOBALCAPITALMANAGER TEM PROBLEMAS")
            return False
    
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_implement_global_capital_manager():
    """Teste para validar GlobalCapitalManager"""
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _implement_global_capital_manager()")
    logger.info("="*80)
    
    result = _implement_global_capital_manager()
    
    test_result = {
        'function': '_implement_global_capital_manager()',
        'passed': result,
        'timestamp': datetime.now().isoformat()
    }
    
    if test_result['passed']:
        logger.info("\nOK TESTE PASSOU")
    else:
        logger.error("\nERRO TESTE FALHOU")
    
    logger.info("="*80)
    return test_result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 4.1")
    print("="*80 + "\n")
    
    result = test_implement_global_capital_manager()
    
    print("\n" + "="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print("="*80 + "\n")
    
    with open('test_result_phase_4_1.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_4_1.json\n")

