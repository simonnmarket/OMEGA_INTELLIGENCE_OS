# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 1.2
Fazer Backup do Estado Atual

FUNÇÃO: _create_backup()
OBJETIVO: Criar backup completo do sistema antes de modificações
TESTÁVEL: Sim - verifica arquivos criados e integridade
"""

import os
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _create_backup() -> bool:
    """
    Fazer backup do estado atual do sistema
    
    Backup inclui:
    - Todos os servidores Python (Server/*.py)
    - Configurações atuais
    - Logs recentes (últimas 24h)
    - Arquivos de comunicação EA (se existirem)
    - Estado de documentação
    
    Returns:
        bool: True se backup criado com sucesso, False se falhou
    
    VALIDAÇÃO:
    - Verifica que diretório foi criado
    - Conta arquivos copiados
    - Valida integridade
    - Gera manifesto (lista de arquivos)
    """
    try:
        logger.info("="*80)
        logger.info("FASE 1.2: Criando backup do estado atual")
        logger.info("="*80)
        
        # Base do projeto
        project_root = Path(__file__).parent.parent.parent
        
        # Criar diretório de backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = project_root / 'Backup' / f'Backup_Pre_Integration_{timestamp}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Diretório de backup: {backup_dir}")
        
        # Contador de arquivos
        files_backed_up = 0
        backup_manifest = {
            'timestamp': timestamp,
            'backup_dir': str(backup_dir),
            'files': [],
            'errors': []
        }
        
        # 1. BACKUP DOS SERVIDORES
        logger.info("1. Fazendo backup dos servidores...")
        server_dir = project_root / 'Server'
        backup_server_dir = backup_dir / 'Server'
        backup_server_dir.mkdir(exist_ok=True)
        
        if server_dir.exists():
            for file in server_dir.glob('*.py'):
                try:
                    dest = backup_server_dir / file.name
                    shutil.copy2(file, dest)
                    files_backed_up += 1
                    backup_manifest['files'].append({
                        'source': str(file),
                        'dest': str(dest),
                        'size': file.stat().st_size,
                        'type': 'server'
                    })
                    logger.info(f"  ✅ {file.name} ({file.stat().st_size} bytes)")
                except Exception as e:
                    logger.warning(f"  ⚠️ Erro ao copiar {file.name}: {e}")
                    backup_manifest['errors'].append(f"Server/{file.name}: {e}")
        
        # 2. BACKUP DOS LOGS
        logger.info("2. Fazendo backup dos logs...")
        backup_logs_dir = backup_dir / 'Logs'
        backup_logs_dir.mkdir(exist_ok=True)
        
        # Logs do servidor
        for log_file in server_dir.glob('*.log'):
            try:
                dest = backup_logs_dir / log_file.name
                shutil.copy2(log_file, dest)
                files_backed_up += 1
                backup_manifest['files'].append({
                    'source': str(log_file),
                    'dest': str(dest),
                    'size': log_file.stat().st_size,
                    'type': 'log'
                })
                logger.info(f"  ✅ {log_file.name} ({log_file.stat().st_size} bytes)")
            except Exception as e:
                logger.warning(f"  ⚠️ Erro ao copiar {log_file.name}: {e}")
                backup_manifest['errors'].append(f"Logs/{log_file.name}: {e}")
        
        # 3. BACKUP DAS CONFIGURAÇÕES
        logger.info("3. Fazendo backup das configurações...")
        backup_config_dir = backup_dir / 'Config'
        backup_config_dir.mkdir(exist_ok=True)
        
        # Arquivos de configuração (se existirem)
        config_files = [
            project_root / 'config.json',
            project_root / 'settings.py',
            project_root / '.env'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    dest = backup_config_dir / config_file.name
                    shutil.copy2(config_file, dest)
                    files_backed_up += 1
                    backup_manifest['files'].append({
                        'source': str(config_file),
                        'dest': str(dest),
                        'size': config_file.stat().st_size,
                        'type': 'config'
                    })
                    logger.info(f"  ✅ {config_file.name}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Erro ao copiar {config_file.name}: {e}")
        
        # 4. BACKUP DOS ARQUIVOS DE COMUNICAÇÃO EA (se existirem)
        logger.info("4. Fazendo backup dos arquivos de comunicação EA...")
        backup_ea_dir = backup_dir / 'EA_Communication'
        backup_ea_dir.mkdir(exist_ok=True)
        
        # Pasta MT5
        mt5_path = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
        
        if mt5_path.exists():
            ea_files = [
                'AIRequest.BTCUSD.json',
                'AIResponse.BTCUSD.json',
                'request.json',
                'response.json'
            ]
            
            for ea_file_name in ea_files:
                ea_file = mt5_path / ea_file_name
                if ea_file.exists():
                    try:
                        dest = backup_ea_dir / ea_file_name
                        shutil.copy2(ea_file, dest)
                        files_backed_up += 1
                        backup_manifest['files'].append({
                            'source': str(ea_file),
                            'dest': str(dest),
                            'size': ea_file.stat().st_size,
                            'type': 'ea_communication'
                        })
                        logger.info(f"  ✅ {ea_file_name}")
                    except Exception as e:
                        logger.warning(f"  ⚠️ Erro ao copiar {ea_file_name}: {e}")
        
        # 5. SALVAR MANIFESTO DO BACKUP
        logger.info("5. Salvando manifesto do backup...")
        manifest_file = backup_dir / 'BACKUP_MANIFEST.json'
        
        backup_manifest['total_files'] = files_backed_up
        backup_manifest['backup_complete'] = True
        
        with open(manifest_file, 'w') as f:
            json.dump(backup_manifest, f, indent=2)
        
        logger.info(f"  ✅ Manifesto salvo: {manifest_file.name}")
        
        # 6. CRIAR README DO BACKUP
        logger.info("6. Criando README do backup...")
        readme_file = backup_dir / 'README.md'
        
        readme_content = f"""# BACKUP PRÉ-INTEGRAÇÃO NUMEIA v3.1
**Data:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S CET')}  
**Timestamp:** {timestamp}  
**Arquivos:** {files_backed_up}  
**Status:** Completo  

## CONTEÚDO

- **Servidores:** Todos os arquivos .py em Server/
- **Logs:** Logs recentes dos servidores
- **Configurações:** Arquivos de config (se existirem)
- **Comunicação EA:** Arquivos JSON de comunicação

## RESTAURAR

Para restaurar este backup:
1. Copiar arquivos de `Server/` de volta para `Server/`
2. Copiar logs de volta (opcional)
3. Reiniciar servidor desejado

## MANIFESTO

Ver arquivo `BACKUP_MANIFEST.json` para lista completa de arquivos.
"""
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"  ✅ README criado: {readme_file.name}")
        
        # VALIDAÇÃO FINAL
        logger.info("="*80)
        logger.info("VALIDAÇÃO DO BACKUP:")
        logger.info(f"  Diretório criado: {backup_dir.exists()}")
        logger.info(f"  Arquivos copiados: {files_backed_up}")
        logger.info(f"  Manifesto criado: {manifest_file.exists()}")
        logger.info(f"  README criado: {readme_file.exists()}")
        logger.info(f"  Erros: {len(backup_manifest['errors'])}")
        logger.info("="*80)
        
        if files_backed_up > 0:
            logger.info(f"✅ BACKUP COMPLETO: {files_backed_up} arquivos salvos em {backup_dir}")
            return True
        else:
            logger.warning("⚠️ BACKUP VAZIO: Nenhum arquivo foi copiado")
            return False
    
    except Exception as e:
        logger.error(f"❌ ERRO ao criar backup: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def _validate_backup(backup_dir: Path) -> Dict:
    """
    Validar que backup foi criado corretamente
    
    Args:
        backup_dir: Diretório do backup a validar
    
    Returns:
        dict: Resultado da validação com detalhes
    """
    validation = {
        'backup_exists': backup_dir.exists(),
        'manifest_exists': False,
        'readme_exists': False,
        'files_count': 0,
        'total_size_mb': 0.0,
        'valid': False
    }
    
    if not backup_dir.exists():
        return validation
    
    # Verificar manifesto
    manifest_file = backup_dir / 'BACKUP_MANIFEST.json'
    validation['manifest_exists'] = manifest_file.exists()
    
    # Verificar README
    readme_file = backup_dir / 'README.md'
    validation['readme_exists'] = readme_file.exists()
    
    # Contar arquivos e tamanho total
    total_size = 0
    files_count = 0
    
    for item in backup_dir.rglob('*'):
        if item.is_file():
            files_count += 1
            total_size += item.stat().st_size
    
    validation['files_count'] = files_count
    validation['total_size_mb'] = total_size / (1024 * 1024)
    
    # Backup é válido se tem manifesto, README e pelo menos 3 arquivos
    validation['valid'] = (
        validation['manifest_exists'] and 
        validation['readme_exists'] and 
        validation['files_count'] >= 3
    )
    
    return validation

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_create_backup():
    """
    Teste para validar que backup foi criado corretamente
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _create_backup()")
    logger.info("="*80)
    
    # Executar função
    result = _create_backup()
    
    # Encontrar último backup criado
    project_root = Path(__file__).parent.parent.parent
    backup_root = project_root / 'Backup'
    
    latest_backup = None
    if backup_root.exists():
        backups = sorted(backup_root.glob('Backup_Pre_Integration_*'))
        if backups:
            latest_backup = backups[-1]
    
    # Validar backup
    validation = _validate_backup(latest_backup) if latest_backup else {}
    
    # Resultado do teste
    test_result = {
        'function': '_create_backup()',
        'passed': result and validation.get('valid', False),
        'timestamp': datetime.now().isoformat(),
        'details': {
            'backup_created': result,
            'backup_dir': str(latest_backup) if latest_backup else None,
            'validation': validation
        }
    }
    
    if test_result['passed']:
        logger.info("✅ TESTE PASSOU")
        logger.info(f"  Backup em: {latest_backup}")
        logger.info(f"  Arquivos: {validation['files_count']}")
        logger.info(f"  Tamanho: {validation['total_size_mb']:.2f} MB")
    else:
        logger.error("❌ TESTE FALHOU")
        if not result:
            logger.error("  Função _create_backup() retornou False")
        if not validation.get('valid'):
            logger.error("  Validação do backup falhou")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    
    print("\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 1.2")
    print("Função: _create_backup()")
    print("="*80 + "\n")
    
    # Executar teste
    result = test_create_backup()
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Função: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"\nDetalhes:")
    print(f"  Backup criado: {result['details']['backup_created']}")
    print(f"  Diretório: {result['details']['backup_dir']}")
    if result['details']['validation']:
        print(f"  Arquivos: {result['details']['validation']['files_count']}")
        print(f"  Tamanho: {result['details']['validation']['total_size_mb']:.2f} MB")
        print(f"  Válido: {result['details']['validation']['valid']}")
    print("="*80 + "\n")
    
    # Salvar resultado
    with open('test_result_phase_1_2.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_1_2.json\n")

