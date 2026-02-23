# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 1.4
Verificar Dependências Necessárias

FUNÇÃO: _verify_dependencies()
OBJETIVO: Verificar que todas as bibliotecas necessárias estão instaladas
TESTÁVEL: Sim - tenta importar cada biblioteca e reporta status
"""

import logging
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _verify_dependencies() -> bool:
    """
    Verificar dependências necessárias para o sistema Numeia v3.1
    
    Bibliotecas verificadas:
    - ccxt (exchange connectivity)
    - pandas (data manipulation)
    - numpy (numerical computing)
    - psutil (process management)
    - yfinance (market data - Yahoo Finance)
    - scipy (scientific computing)
    - requests (HTTP requests)
    - asyncio (async operations - built-in)
    
    Returns:
        bool: True se TODAS as dependências OK, False se alguma faltando
    
    VALIDAÇÃO:
    - Tenta importar cada biblioteca
    - Registra versão de cada uma
    - Lista dependências faltantes (se houver)
    - Gera relatório detalhado
    """
    try:
        logger.info("="*80)
        logger.info("FASE 1.4: Verificando dependências")
        logger.info("="*80)
        
        # Lista de dependências obrigatórias
        dependencies = {
            'ccxt': {
                'description': 'Exchange connectivity (Binance, etc)',
                'critical': True,
                'import_test': 'import ccxt'
            },
            'pandas': {
                'description': 'Data manipulation and analysis',
                'critical': True,
                'import_test': 'import pandas'
            },
            'numpy': {
                'description': 'Numerical computing',
                'critical': True,
                'import_test': 'import numpy'
            },
            'psutil': {
                'description': 'Process and system utilities',
                'critical': True,
                'import_test': 'import psutil'
            },
            'yfinance': {
                'description': 'Yahoo Finance market data',
                'critical': False,  # Opcional - ccxt é suficiente
                'import_test': 'import yfinance'
            },
            'scipy': {
                'description': 'Scientific computing',
                'critical': False,  # Opcional - para análises avançadas
                'import_test': 'import scipy'
            },
            'requests': {
                'description': 'HTTP requests',
                'critical': True,
                'import_test': 'import requests'
            },
            'asyncio': {
                'description': 'Async operations',
                'critical': True,
                'import_test': 'import asyncio'
            }
        }
        
        results = {}
        all_ok = True
        critical_missing = []
        optional_missing = []
        
        # Verificar cada dependência
        for lib_name, lib_info in dependencies.items():
            logger.info(f"\nVerificando: {lib_name}")
            logger.info(f"  Descrição: {lib_info['description']}")
            logger.info(f"  Crítica: {'SIM' if lib_info['critical'] else 'NÃO'}")
            
            try:
                # Tentar importar
                exec(lib_info['import_test'])
                
                # Se importou, tentar pegar versão
                try:
                    module = __import__(lib_name)
                    version = getattr(module, '__version__', 'unknown')
                except:
                    version = 'unknown'
                
                logger.info(f"  ✅ OK - Versão: {version}")
                
                results[lib_name] = {
                    'status': 'ok',
                    'version': version,
                    'description': lib_info['description'],
                    'critical': lib_info['critical']
                }
            
            except ImportError as e:
                logger.warning(f"  ❌ NÃO INSTALADA")
                
                if lib_info['critical']:
                    critical_missing.append(lib_name)
                    all_ok = False
                else:
                    optional_missing.append(lib_name)
                
                results[lib_name] = {
                    'status': 'missing',
                    'error': str(e),
                    'description': lib_info['description'],
                    'critical': lib_info['critical']
                }
        
        # Relatório final
        logger.info("\n" + "="*80)
        logger.info("RELATÓRIO DE DEPENDÊNCIAS:")
        logger.info("="*80)
        
        ok_count = sum(1 for r in results.values() if r['status'] == 'ok')
        missing_count = sum(1 for r in results.values() if r['status'] == 'missing')
        
        logger.info(f"  Total verificadas: {len(results)}")
        logger.info(f"  OK: {ok_count}")
        logger.info(f"  Faltando: {missing_count}")
        
        if critical_missing:
            logger.error(f"  ❌ Críticas faltando: {', '.join(critical_missing)}")
        else:
            logger.info(f"  ✅ Todas as críticas OK")
        
        if optional_missing:
            logger.warning(f"  ⚠️ Opcionais faltando: {', '.join(optional_missing)}")
        
        logger.info("="*80)
        
        # Salvar relatório de dependências
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        deps_report_file = project_root / 'Core' / 'Integration' / 'dependencies_report.json'
        
        deps_report = {
            'timestamp': datetime.now().isoformat(),
            'all_ok': all_ok,
            'total': len(results),
            'ok': ok_count,
            'missing': missing_count,
            'critical_missing': critical_missing,
            'optional_missing': optional_missing,
            'details': results
        }
        
        with open(deps_report_file, 'w') as f:
            json.dump(deps_report, f, indent=2)
        
        logger.info(f"Relatório salvo: {deps_report_file.name}")
        
        if all_ok:
            logger.info("\n✅ TODAS AS DEPENDÊNCIAS CRÍTICAS OK")
            return True
        else:
            logger.error(f"\n❌ DEPENDÊNCIAS CRÍTICAS FALTANDO: {critical_missing}")
            logger.info("Execute: pip install " + " ".join(critical_missing))
            return False
    
    except Exception as e:
        logger.error(f"❌ ERRO ao verificar dependências: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def _get_python_version() -> str:
    """Obter versão do Python"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_verify_dependencies():
    """
    Teste para validar que dependências foram verificadas
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _verify_dependencies()")
    logger.info("="*80)
    
    # Informar versão do Python
    python_version = _get_python_version()
    logger.info(f"Python: {python_version}")
    
    # Executar função
    result = _verify_dependencies()
    
    # Ler relatório gerado
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    deps_report_file = project_root / 'Core' / 'Integration' / 'dependencies_report.json'
    
    deps_report = {}
    if deps_report_file.exists():
        with open(deps_report_file, 'r') as f:
            deps_report = json.load(f)
    
    # Resultado do teste
    test_result = {
        'function': '_verify_dependencies()',
        'passed': result,
        'timestamp': datetime.now().isoformat(),
        'python_version': python_version,
        'details': {
            'all_dependencies_ok': result,
            'report': deps_report
        }
    }
    
    if test_result['passed']:
        logger.info("✅ TESTE PASSOU")
        logger.info(f"  Todas as dependências críticas: OK")
        logger.info(f"  Total OK: {deps_report.get('ok', 0)}/{deps_report.get('total', 0)}")
    else:
        logger.error("❌ TESTE FALHOU")
        logger.error(f"  Dependências críticas faltando: {deps_report.get('critical_missing', [])}")
        logger.info("  Execute para instalar:")
        missing = deps_report.get('critical_missing', [])
        if missing:
            logger.info(f"    pip install {' '.join(missing)}")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 1.4")
    print("Funcao: _verify_dependencies()")
    print("="*80 + "\n")
    
    # Executar teste
    result = test_verify_dependencies()
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Python: {result['python_version']}")
    print(f"Timestamp: {result['timestamp']}")
    
    if result['details']['report']:
        rep = result['details']['report']
        print(f"\nDependencias:")
        print(f"  Total: {rep.get('total', 0)}")
        print(f"  OK: {rep.get('ok', 0)}")
        print(f"  Faltando: {rep.get('missing', 0)}")
        
        if rep.get('critical_missing'):
            print(f"\n  CRITICAS FALTANDO:")
            for lib in rep['critical_missing']:
                print(f"    - {lib}")
        
        if rep.get('optional_missing'):
            print(f"\n  OPCIONAIS FALTANDO:")
            for lib in rep['optional_missing']:
                print(f"    - {lib}")
    
    print("="*80 + "\n")
    
    # Salvar resultado
    with open('test_result_phase_1_4.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_1_4.json\n")

