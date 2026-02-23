# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 1.3
Preparar Estrutura de Diretórios

FUNÇÃO: _prepare_directory_structure()
OBJETIVO: Criar estrutura de diretórios para integração completa
TESTÁVEL: Sim - verifica diretórios criados e permissões
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _prepare_directory_structure() -> bool:
    """
    Preparar estrutura de diretórios para integração
    
    Cria diretórios necessários:
    - Server/Production/ (servidor final consolidado)
    - Logs/Integration/ (logs do protocolo)
    - Tests/Integration/ (testes de integração)
    - Core/Integration/ (já existe, mas verificar)
    
    Returns:
        bool: True se estrutura criada com sucesso, False se falhou
    
    VALIDAÇÃO:
    - Verifica que todos os diretórios foram criados
    - Testa permissões de escrita
    - Gera mapeamento da estrutura
    """
    try:
        logger.info("="*80)
        logger.info("FASE 1.3: Preparando estrutura de diretórios")
        logger.info("="*80)
        
        # Base do projeto
        project_root = Path(__file__).parent.parent.parent
        
        # Estrutura de diretórios necessária
        required_dirs = {
            'server_production': project_root / 'Server' / 'Production',
            'logs_integration': project_root / 'Logs' / 'Integration',
            'tests_integration': project_root / 'Tests' / 'Integration',
            'core_integration': project_root / 'Core' / 'Integration',
            'backup': project_root / 'Backup'
        }
        
        dirs_created = 0
        dirs_already_existed = 0
        structure_map = {}
        
        # Criar cada diretório
        for name, dir_path in required_dirs.items():
            logger.info(f"Verificando: {name} ({dir_path.name})")
            
            try:
                if dir_path.exists():
                    logger.info(f"  ℹ️ Já existe: {dir_path}")
                    dirs_already_existed += 1
                    status = 'exists'
                else:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"  ✅ Criado: {dir_path}")
                    dirs_created += 1
                    status = 'created'
                
                # Testar permissão de escrita
                test_file = dir_path / '.test_write_permission'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    writable = True
                    logger.info(f"  ✅ Permissão de escrita: OK")
                except Exception as e:
                    writable = False
                    logger.error(f"  ❌ Sem permissão de escrita: {e}")
                
                structure_map[name] = {
                    'path': str(dir_path),
                    'status': status,
                    'writable': writable,
                    'exists': dir_path.exists()
                }
            
            except Exception as e:
                logger.error(f"  ❌ Erro ao criar {name}: {e}")
                structure_map[name] = {
                    'path': str(dir_path),
                    'status': 'error',
                    'error': str(e),
                    'exists': False
                }
        
        # Criar README em cada diretório
        logger.info("\nCriando READMEs explicativos...")
        
        readmes = {
            'server_production': """# Server/Production/
**Finalidade:** Servidor de produção consolidado

Este diretório conterá o servidor final após integração completa.
""",
            'logs_integration': """# Logs/Integration/
**Finalidade:** Logs do protocolo de integração

Logs gerados durante a execução do Protocolo Numeia v3.1.
""",
            'tests_integration': """# Tests/Integration/
**Finalidade:** Testes de integração

Testes automatizados para validar integração completa do sistema.
""",
            'core_integration': """# Core/Integration/
**Finalidade:** Código de integração do protocolo

Funções e utilitários para execução do Protocolo Numeia v3.1.
"""
        }
        
        readmes_created = 0
        for name, content in readmes.items():
            dir_path = required_dirs.get(name)
            if dir_path and dir_path.exists():
                readme_file = dir_path / 'README.md'
                try:
                    with open(readme_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    readmes_created += 1
                    logger.info(f"  ✅ README criado: {name}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Erro ao criar README {name}: {e}")
        
        # Salvar mapeamento da estrutura
        logger.info("\nSalvando mapeamento da estrutura...")
        structure_file = project_root / 'Core' / 'Integration' / 'directory_structure_map.json'
        
        structure_data = {
            'timestamp': datetime.now().isoformat(),
            'dirs_created': dirs_created,
            'dirs_already_existed': dirs_already_existed,
            'readmes_created': readmes_created,
            'structure': structure_map
        }
        
        with open(structure_file, 'w') as f:
            json.dump(structure_data, f, indent=2)
        
        logger.info(f"  ✅ Mapeamento salvo: {structure_file.name}")
        
        # VALIDAÇÃO FINAL
        logger.info("="*80)
        logger.info("VALIDAÇÃO DA ESTRUTURA:")
        logger.info(f"  Diretórios criados: {dirs_created}")
        logger.info(f"  Diretórios já existentes: {dirs_already_existed}")
        logger.info(f"  Total de diretórios: {dirs_created + dirs_already_existed}")
        logger.info(f"  READMEs criados: {readmes_created}")
        
        # Verificar se todos os diretórios têm permissão de escrita
        all_writable = all(d.get('writable', False) for d in structure_map.values())
        
        logger.info(f"  Todos com permissão de escrita: {all_writable}")
        logger.info("="*80)
        
        if all_writable:
            logger.info(f"✅ ESTRUTURA COMPLETA: {len(required_dirs)} diretórios prontos")
            return True
        else:
            logger.error("❌ PROBLEMA: Alguns diretórios sem permissão de escrita")
            return False
    
    except Exception as e:
        logger.error(f"❌ ERRO ao preparar estrutura: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def _validate_directory_structure() -> Dict:
    """
    Validar que estrutura de diretórios foi criada corretamente
    
    Returns:
        dict: Resultado da validação com detalhes
    """
    project_root = Path(__file__).parent.parent.parent
    
    required_dirs = {
        'server_production': project_root / 'Server' / 'Production',
        'logs_integration': project_root / 'Logs' / 'Integration',
        'tests_integration': project_root / 'Tests' / 'Integration',
        'core_integration': project_root / 'Core' / 'Integration',
        'backup': project_root / 'Backup'
    }
    
    validation = {
        'all_exist': True,
        'all_writable': True,
        'dirs_status': {}
    }
    
    for name, dir_path in required_dirs.items():
        exists = dir_path.exists()
        
        # Testar escrita
        writable = False
        if exists:
            test_file = dir_path / '.test_write'
            try:
                test_file.write_text('test')
                test_file.unlink()
                writable = True
            except:
                writable = False
        
        validation['dirs_status'][name] = {
            'path': str(dir_path),
            'exists': exists,
            'writable': writable
        }
        
        if not exists:
            validation['all_exist'] = False
        if not writable:
            validation['all_writable'] = False
    
    validation['valid'] = validation['all_exist'] and validation['all_writable']
    
    return validation

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_prepare_directory_structure():
    """
    Teste para validar que estrutura foi criada corretamente
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _prepare_directory_structure()")
    logger.info("="*80)
    
    # Executar função
    result = _prepare_directory_structure()
    
    # Validar estrutura
    validation = _validate_directory_structure()
    
    # Resultado do teste
    test_result = {
        'function': '_prepare_directory_structure()',
        'passed': result and validation.get('valid', False),
        'timestamp': datetime.now().isoformat(),
        'details': {
            'structure_created': result,
            'validation': validation
        }
    }
    
    if test_result['passed']:
        logger.info("✅ TESTE PASSOU")
        logger.info(f"  Todos os diretórios existem: {validation['all_exist']}")
        logger.info(f"  Todos com permissão de escrita: {validation['all_writable']}")
        for name, status in validation['dirs_status'].items():
            logger.info(f"    {name}: {'✅' if status['exists'] and status['writable'] else '❌'}")
    else:
        logger.error("❌ TESTE FALHOU")
        if not result:
            logger.error("  Função _prepare_directory_structure() retornou False")
        if not validation.get('valid'):
            logger.error("  Validação da estrutura falhou")
            for name, status in validation['dirs_status'].items():
                if not status['exists']:
                    logger.error(f"    {name}: NÃO EXISTE")
                elif not status['writable']:
                    logger.error(f"    {name}: SEM PERMISSÃO DE ESCRITA")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 1.3")
    print("Função: _prepare_directory_structure()")
    print("="*80 + "\n")
    
    # Executar teste
    result = test_prepare_directory_structure()
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Função: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"\nDetalhes:")
    print(f"  Estrutura criada: {result['details']['structure_created']}")
    if result['details']['validation']:
        val = result['details']['validation']
        print(f"  Todos existem: {val['all_exist']}")
        print(f"  Todos com escrita: {val['all_writable']}")
        print(f"  Válido: {val['valid']}")
        print(f"\n  Status dos diretórios:")
        for name, status in val['dirs_status'].items():
            icon = '✅' if status['exists'] and status['writable'] else '❌'
            print(f"    {icon} {name}")
    print("="*80 + "\n")
    
    # Salvar resultado
    with open('test_result_phase_1_3.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_1_3.json\n")

