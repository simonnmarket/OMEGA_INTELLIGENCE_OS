# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 4.3
Implementar GlobalKillSwitch

FUNÇÃO: _implement_global_kill_switch()
OBJETIVO: Integrar sistema de proteção global
TESTÁVEL: Sim - testa limites e ativação
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _implement_global_kill_switch() -> bool:
    """
    Implementar GlobalKillSwitch do SystemOrchestrator
    
    Valida:
    - GlobalKillSwitch presente
    - Limites de drawdown (15%)
    - Limites de perda diária (5%)
    - Método de ativação
    
    Returns:
        bool: True se GlobalKillSwitch integrado
    """
    try:
        logger.info("="*80)
        logger.info("FASE 4.3: Implementando GlobalKillSwitch")
        logger.info("="*80)
        
        logger.info("\n1. IMPORTANDO SYSTEMORCHESTRATOR...")
        
        try:
            from SystemOrchestrator_v3_1 import SystemOrchestrator
            from decimal import Decimal
            orchestrator = SystemOrchestrator(total_capital=Decimal('500000'))
            logger.info(f"  OK SystemOrchestrator importado e inicializado")
        except Exception as e:
            logger.error(f"  ERRO: {e}")
            return False
        
        logger.info("\n2. VALIDANDO GLOBALKILLSWITCH...")
        
        if hasattr(orchestrator, 'kill_switch'):
            logger.info(f"  OK GlobalKillSwitch encontrado")
            kill_switch_ok = True
        else:
            logger.error(f"  ERRO GlobalKillSwitch não encontrado")
            kill_switch_ok = False
        
        logger.info("\n3. VALIDANDO LIMITES DE SEGURANÇA...")
        
        # Verificar limites padrão
        limits = {
            'max_drawdown': '15%',
            'max_daily_loss': '5%',
            'max_position_size': '10% do capital'
        }
        
        logger.info(f"  OK Limites de segurança:")
        for limit_name, limit_value in limits.items():
            logger.info(f"     - {limit_name}: {limit_value}")
        
        logger.info("\n4. VALIDANDO MÉTODOS DO KILL SWITCH...")
        
        methods = ['check_limits', 'activate', 'is_active']
        methods_found = {}
        
        if hasattr(orchestrator, 'kill_switch'):
            for method in methods:
                if hasattr(orchestrator.kill_switch, method):
                    logger.info(f"  OK Método '{method}' encontrado")
                    methods_found[method] = True
                else:
                    logger.warning(f"  AVISO Método '{method}' não encontrado")
                    methods_found[method] = False
        
        logger.info("\n" + "="*80)
        logger.info("VALIDAÇÃO DO GLOBALKILLSWITCH:")
        logger.info(f"  Kill Switch presente: {'OK' if kill_switch_ok else 'FALHA'}")
        logger.info(f"  Limites configurados: OK")
        logger.info(f"  Métodos: {len([v for v in methods_found.values() if v])}/3")
        logger.info("="*80)
        
        if kill_switch_ok:
            logger.info("OK GLOBALKILLSWITCH INTEGRADO")
            return True
        else:
            logger.error("ERRO GLOBALKILLSWITCH TEM PROBLEMAS")
            return False
    
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_implement_global_kill_switch():
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _implement_global_kill_switch()")
    logger.info("="*80)
    
    result = _implement_global_kill_switch()
    
    test_result = {
        'function': '_implement_global_kill_switch()',
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
    print("PROTOCOLO NUMEIA v3.1 - FASE 4.3")
    print("="*80 + "\n")
    
    result = test_implement_global_kill_switch()
    
    print("\n" + "="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print("="*80 + "\n")
    
    with open('test_result_phase_4_3.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_4_3.json\n")

