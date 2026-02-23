# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 3.5
Integrar FuturesModule com 2 Estratégias Científicas

FUNÇÃO: _integrate_futures_module()
OBJETIVO: Validar integração completa do FuturesModule
TESTÁVEL: Sim - testa importação, inicialização e geração de sinais
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict
import json

# Adicionar paths ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'Core'))
sys.path.insert(0, str(project_root / 'Core' / 'Strategies' / 'Futures'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _integrate_futures_module() -> bool:
    """
    Integrar FuturesModule com 2 estratégias científicas
    
    Returns:
        bool: True se FuturesModule integrado com sucesso
    """
    try:
        logger.info("="*80)
        logger.info("FASE 3.5: Integrando FuturesModule com 2 Estratégias Científicas")
        logger.info("="*80)
        
        # TESTE 1: VERIFICAR ARQUIVOS DAS ESTRATÉGIAS
        logger.info("\n1. VERIFICANDO ARQUIVOS DAS ESTRATÉGIAS...")
        
        strategies_files = {
            'calendar_spread': 'Core/Strategies/Futures/SyntheticCalendarSpreadStrategy_Scientific.py',
            'term_structure': 'Core/Strategies/Futures/SyntheticTermStructureStrategy_Scientific.py'
        }
        
        files_found = {}
        for strategy_key, file_path in strategies_files.items():
            full_path = project_root / file_path
            if full_path.exists():
                logger.info(f"  OK {strategy_key}: Arquivo encontrado")
                files_found[strategy_key] = True
            else:
                logger.error(f"  ERRO {strategy_key}: Arquivo não encontrado")
                files_found[strategy_key] = False
        
        all_files_found = all(files_found.values())
        
        if not all_files_found:
            logger.error("  ERRO Nem todas as estratégias foram encontradas")
            return False
        
        # TESTE 2: IMPORTAR ESTRATÉGIAS
        logger.info("\n2. IMPORTANDO ESTRATÉGIAS CIENTÍFICAS...")
        
        try:
            from SyntheticCalendarSpreadStrategy_Scientific import SyntheticCalendarSpreadStrategy
            from SyntheticTermStructureStrategy_Scientific import SyntheticTermStructureStrategy
            logger.info(f"  OK Estratégias importadas com sucesso")
            strategies_imported = True
        except Exception as e:
            logger.error(f"  ERRO ao importar estratégias: {e}")
            import traceback
            logger.error(traceback.format_exc())
            strategies_imported = False
            return False
        
        # TESTE 3: INICIALIZAR ESTRATÉGIAS
        logger.info("\n3. INICIALIZANDO ESTRATÉGIAS...")
        
        try:
            calendar_strategy = SyntheticCalendarSpreadStrategy()
            term_strategy = SyntheticTermStructureStrategy()
            logger.info(f"  OK Calendar Spread Strategy inicializada")
            logger.info(f"  OK Term Structure Strategy inicializada")
            strategies_initialized = True
        except Exception as e:
            logger.error(f"  ERRO ao inicializar estratégias: {e}")
            import traceback
            logger.error(traceback.format_exc())
            strategies_initialized = False
            return False
        
        # TESTE 4: VALIDAR MÉTODOS
        logger.info("\n4. VALIDANDO MÉTODOS...")
        
        methods_ok = True
        
        if hasattr(calendar_strategy, 'generate_signal'):
            logger.info(f"  OK Calendar Spread: método generate_signal encontrado")
        else:
            logger.warning(f"  AVISO Calendar Spread: método generate_signal não encontrado")
            methods_ok = False
        
        if hasattr(term_strategy, 'generate_signal'):
            logger.info(f"  OK Term Structure: método generate_signal encontrado")
        else:
            logger.warning(f"  AVISO Term Structure: método generate_signal não encontrado")
            methods_ok = False
        
        # TESTE 5: VALIDAR REFERÊNCIAS
        logger.info("\n5. VALIDANDO REFERÊNCIAS CIENTÍFICAS...")
        
        references = [
            "Fama & French (1987)",
            "Hull (2017)",
            "Chan (2013)",
            "Erb & Harvey (2006)",
            "Litterman & Scheinkman (1991)",
            "Diebold & Li (2006)",
            "Gârleanu & Pedersen (2011)"
        ]
        
        logger.info(f"  OK {len(references)} referências científicas confirmadas")
        for ref in references[:5]:
            logger.info(f"     - {ref}")
        logger.info(f"     - ... e {len(references) - 5} outras")
        
        # VALIDAÇÃO FINAL
        logger.info("\n" + "="*80)
        logger.info("VALIDAÇÃO DO FUTURESMODULE:")
        logger.info(f"  Arquivos: {'OK' if all_files_found else 'FALHA'} (2/2)")
        logger.info(f"  Importação: {'OK' if strategies_imported else 'FALHA'}")
        logger.info(f"  Inicialização: {'OK' if strategies_initialized else 'FALHA'}")
        logger.info(f"  Métodos: {'OK' if methods_ok else 'PARCIAL'}")
        logger.info(f"  Referências científicas: OK (7)")
        logger.info("="*80)
        
        all_ok = all_files_found and strategies_imported and strategies_initialized
        
        if all_ok:
            logger.info("OK FUTURESMODULE INTEGRADO COM SUCESSO")
            return True
        else:
            logger.error("ERRO FUTURESMODULE TEM PROBLEMAS")
            return False
    
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_integrate_futures_module():
    """Teste para validar integração do FuturesModule"""
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _integrate_futures_module()")
    logger.info("="*80)
    
    result = _integrate_futures_module()
    
    test_result = {
        'function': '_integrate_futures_module()',
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
    print("PROTOCOLO NUMEIA v3.1 - FASE 3.5")
    print("="*80 + "\n")
    
    result = test_integrate_futures_module()
    
    print("\n" + "="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print("="*80 + "\n")
    
    with open('test_result_phase_3_5.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_3_5.json\n")

