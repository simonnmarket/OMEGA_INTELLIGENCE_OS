# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 5.5 (CORREÇÃO CRÍTICA)
Corrigir Integração do EquitiesModule

FUNÇÃO: _fix_equities_module_integration()
OBJETIVO: Resolver pendência crítica do EquitiesModule
TESTÁVEL: Sim - testa integração completa
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Core'))
sys.path.insert(0, str(project_root / 'Core' / 'Modules'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _fix_equities_module_integration() -> bool:
    """
    Corrige integração do EquitiesModule ao SystemOrchestrator
    
    Valida:
    - EquitiesModule_Numeia_v3_0.py criado
    - EquitiesStrategiesAdapter_Numeia.py criado
    - Integração no SystemOrchestrator
    - 3 estratégias científicas funcionando
    
    Returns:
        bool: True se correção bem-sucedida
    """
    try:
        logger.info("="*80)
        logger.info("FASE 5.5: Corrigindo Integração do EquitiesModule")
        logger.info("="*80)
        
        # TESTE 1: VERIFICAR ARQUIVOS CRIADOS
        logger.info("\n1. VERIFICANDO ARQUIVOS CRIADOS...")
        
        files_to_check = {
            'EquitiesModule': project_root / 'Core' / 'Modules' / 'EquitiesModule_Numeia_v3_0.py',
            'EquitiesAdapter': project_root / 'Core' / 'Strategies' / 'Equities' / 'EquitiesStrategiesAdapter_Numeia.py'
        }
        
        files_status = {}
        for name, filepath in files_to_check.items():
            exists = filepath.exists()
            files_status[name] = exists
            symbol = "✅" if exists else "❌"
            logger.info(f"  {symbol} {name}: {'ENCONTRADO' if exists else 'FALTANDO'}")
        
        if not all(files_status.values()):
            logger.error("  ❌ ERRO: Arquivos necessários não encontrados")
            return False
        
        # TESTE 2: IMPORTAR EQUITIESMODULE
        logger.info("\n2. IMPORTANDO EQUITIESMODULE...")
        
        try:
            from decimal import Decimal
            from EquitiesModule_Numeia_v3_0 import EquitiesModule
            logger.info(f"  ✅ EquitiesModule importado com sucesso")
            module_imported = True
        except Exception as e:
            logger.error(f"  ❌ ERRO ao importar: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # TESTE 3: INICIALIZAR EQUITIESMODULE
        logger.info("\n3. INICIALIZANDO EQUITIESMODULE...")
        
        try:
            equities = EquitiesModule(allocated_capital=Decimal('100000'))
            logger.info(f"  ✅ EquitiesModule inicializado")
            logger.info(f"     Capital: EUR 100,000")
            logger.info(f"     Max Positions: 5")
            logger.info(f"     Max Daily Trades: 10")
            module_initialized = True
        except Exception as e:
            logger.error(f"  ❌ ERRO ao inicializar: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # TESTE 4: VALIDAR 3 ESTRATÉGIAS
        logger.info("\n4. VALIDANDO 3 ESTRATÉGIAS CIENTÍFICAS...")
        
        try:
            status = equities.adapter.get_strategies_status()
            total_strategies = status['total_strategies']
            
            if total_strategies == 3:
                logger.info(f"  ✅ {total_strategies}/3 estratégias encontradas")
                logger.info(f"     - Pairs Trading: EUR {status['strategies']['pairs_trading']['capital']:,.0f}")
                logger.info(f"     - Volatility Arb: EUR {status['strategies']['volatility_arbitrage']['capital']:,.0f}")
                logger.info(f"     - Sector Rotation: EUR {status['strategies']['sector_rotation']['capital']:,.0f}")
                strategies_ok = True
            else:
                logger.error(f"  ❌ ERRO: Apenas {total_strategies}/3 estratégias")
                strategies_ok = False
        except Exception as e:
            logger.error(f"  ❌ ERRO ao validar estratégias: {e}")
            strategies_ok = False
        
        # TESTE 5: VALIDAR INTEGRAÇÃO NO SYSTEMORCHESTRATOR
        logger.info("\n5. VALIDANDO INTEGRAÇÃO NO SYSTEMORCHESTRATOR...")
        
        try:
            from SystemOrchestrator_v3_1 import SystemOrchestrator
            orchestrator = SystemOrchestrator(total_capital=Decimal('500000'))
            
            if 'Equities' in orchestrator.modules:
                logger.info(f"  ✅ EquitiesModule integrado no SystemOrchestrator")
                logger.info(f"     Total de módulos: {len(orchestrator.modules)}/5")
                orchestrator_ok = True
            else:
                logger.error(f"  ❌ ERRO: EquitiesModule NÃO encontrado no SystemOrchestrator")
                logger.error(f"     Módulos presentes: {list(orchestrator.modules.keys())}")
                orchestrator_ok = False
        except Exception as e:
            logger.error(f"  ❌ ERRO ao validar SystemOrchestrator: {e}")
            import traceback
            logger.error(traceback.format_exc())
            orchestrator_ok = False
        
        # TESTE 6: VALIDAÇÃO COMPLETA DO MÓDULO
        logger.info("\n6. EXECUTANDO VALIDAÇÃO COMPLETA...")
        
        try:
            validation_passed = equities.validate_integration()
            symbol = "✅" if validation_passed else "❌"
            logger.info(f"  {symbol} Validação interna: {'PASSOU' if validation_passed else 'FALHOU'}")
        except Exception as e:
            logger.error(f"  ❌ ERRO na validação: {e}")
            validation_passed = False
        
        # RESULTADO FINAL
        logger.info("\n" + "="*80)
        logger.info("RESULTADO DA CORREÇÃO:")
        logger.info(f"  Arquivos criados: {'✅ OK' if all(files_status.values()) else '❌ FALHA'}")
        logger.info(f"  Módulo importado: {'✅ OK' if module_imported else '❌ FALHA'}")
        logger.info(f"  Módulo inicializado: {'✅ OK' if module_initialized else '❌ FALHA'}")
        logger.info(f"  Estratégias: {'✅ OK (3/3)' if strategies_ok else '❌ FALHA'}")
        logger.info(f"  Integração SystemOrchestrator: {'✅ OK' if orchestrator_ok else '❌ FALHA'}")
        logger.info(f"  Validação interna: {'✅ OK' if validation_passed else '❌ FALHA'}")
        logger.info("="*80)
        
        all_ok = (
            all(files_status.values()) and
            module_imported and
            module_initialized and
            strategies_ok and
            orchestrator_ok and
            validation_passed
        )
        
        if all_ok:
            logger.info("✅ CORREÇÃO BEM-SUCEDIDA - EQUITIESMODULE 100% INTEGRADO")
            return True
        else:
            logger.error("❌ CORREÇÃO FALHOU - PROBLEMAS IDENTIFICADOS")
            return False
    
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_fix_equities_module_integration():
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _fix_equities_module_integration()")
    logger.info("="*80)
    
    result = _fix_equities_module_integration()
    
    test_result = {
        'function': '_fix_equities_module_integration()',
        'passed': result,
        'timestamp': datetime.now().isoformat()
    }
    
    if test_result['passed']:
        logger.info("\n✅ TESTE PASSOU - EQUITIESMODULE INTEGRADO")
    else:
        logger.error("\n❌ TESTE FALHOU")
    
    logger.info("="*80)
    return test_result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 5.5 (CORREÇÃO CRÍTICA)")
    print("="*80 + "\n")
    
    result = test_fix_equities_module_integration()
    
    print("\n" + "="*80)
    print(f"Função: {result['function']}")
    print(f"Passou: {result['passed']}")
    print("="*80 + "\n")
    
    with open('test_result_phase_5_5_CRITICAL_FIX.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_5_5_CRITICAL_FIX.json\n")

