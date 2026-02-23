#!/usr/bin/env python3
"""
Script de validação pós-execução da Fase 1
"""

import os
import json
import hashlib
from datetime import datetime

def validate_directory_structure():
    """Validar estrutura de diretórios criada"""
    required_dirs = ['scripts_fix', 'patches', 'backups', 'logs', 'temp']
    missing = []
    
    for d in required_dirs:
        if not os.path.exists(d):
            missing.append(d)
    
    if missing:
        print(f"❌ Diretórios faltando: {missing}")
        return False
    else:
        print("✅ Estrutura de diretórios OK")
        return True

def validate_core_module_fix():
    """Validar correção do módulo core"""
    core_file = "system_core/ncnt_orchestrator_complete.py"
    
    if not os.path.exists(core_file):
        print(f"❌ Arquivo core não encontrado: {core_file}")
        return False
    
    try:
        with open(core_file, 'rb') as f:
            content = f.read()
        
        # Verificar BOM
        if content.startswith(b'\xef\xbb\xbf'):
            print("❌ UTF-8 BOM ainda presente")
            return False
        if content.startswith(b'\xfe\xff') or content.startswith(b'\xff\xfe'):
            print("❌ UTF-16 BOM ainda presente")
            return False
        
        # Tentar importar
        import sys
        sys.path.insert(0, '.')
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ncnt_orchestrator_complete", 
            core_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✅ Módulo core corrigido e importável")
        return True
        
    except Exception as e:
        print(f"❌ Erro validando core: {e}")
        return False

def validate_backup_exists():
    """Validar existência de backup"""
    if not os.path.exists('backups'):
        print("❌ Diretório backups não existe")
        return False
    
    backup_dirs = [d for d in os.listdir('backups') 
                  if os.path.isdir(os.path.join('backups', d))]
    
    if not backup_dirs:
        print("❌ Nenhum backup encontrado")
        return False
    
    latest_backup = max(backup_dirs)
    backup_path = os.path.join('backups', latest_backup)
    
    # Verificar se backup tem conteúdo
    files_in_backup = []
    for root, dirs, files in os.walk(backup_path):
        files_in_backup.extend(files)
    
    if len(files_in_backup) < 10:  # Número mínimo esperado
        print(f"⚠️ Backup suspeito: apenas {len(files_in_backup)} arquivos")
        return True  # Ainda válido, mas com aviso
    
    print(f"✅ Backup válido encontrado: {latest_backup} ({len(files_in_backup)} arquivos)")
    return True

def validate_logs_generated():
    """Validar logs gerados"""
    if not os.path.exists('logs'):
        print("❌ Diretório logs não existe")
        return False
    
    log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
    
    if not log_files:
        print("❌ Nenhum arquivo de log encontrado")
        return False
    
    latest_log = max(log_files)
    log_path = os.path.join('logs', latest_log)
    
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if len(lines) < 5:
        print(f"⚠️ Log muito curto: {len(lines)} linhas")
        return True  # Ainda válido
    
    print(f"✅ Logs gerados: {latest_log} ({len(lines)} linhas)")
    return True

def generate_validation_report():
    """Gerar relatório de validação completo"""
    tests = [
        ("Estrutura de diretórios", validate_directory_structure),
        ("Correção módulo core", validate_core_module_fix),
        ("Backup criado", validate_backup_exists),
        ("Logs gerados", validate_logs_generated),
    ]
    
    results = []
    all_passed = True
    
    print("=" * 60)
    print("VALIDAÇÃO FASE 1 - AIC EXECUTION")
    print("=" * 60)
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append({
                "test": test_name,
                "status": "PASS" if passed else "FAIL",
                "timestamp": datetime.now().isoformat()
            })
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print(f"❌ Erro executando {test_name}: {e}")
            results.append({
                "test": test_name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            all_passed = False
    
    # Salvar relatório
    report = {
        "phase": 1,
        "timestamp": datetime.now().isoformat(),
        "overall_status": "PASS" if all_passed else "FAIL",
        "tests": results
    }
    
    report_file = f"logs/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"RELATÓRIO SALVO: {report_file}")
    print(f"STATUS FINAL: {'✅ PASS' if all_passed else '❌ FAIL'}")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = generate_validation_report()
    exit(0 if success else 1)

