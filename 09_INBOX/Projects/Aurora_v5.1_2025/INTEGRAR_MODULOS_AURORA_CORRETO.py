#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CORRETO para integrar os 252 módulos do sistema Aurora ao sistema de governança
Baseado na distribuição documentada: Core(5) + Departments(40) + Documentation(1) + 
Governance(28) + Infrastructure(17) + Modules(12) + Monitoring(7) + Operations(12) + 
Processes(16) + Root(114) = 252 módulos
"""

import sys
import os
from pathlib import Path
import json

# Adicionar path do módulo de governança
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: Modulo financial_governance_orchestrator nao encontrado")
    sys.exit(1)


def is_system_module(file_path: Path) -> bool:
    """
    Determina se um arquivo Python e um modulo do sistema (252 modulos principais).
    Filtra apenas modulos principais, excluindo:
    - __init__.py
    - Arquivos de teste
    - Scripts utilitarios na raiz
    - Subarquivos de suporte (helpers, utils)
    """
    path_str = str(file_path)
    name = file_path.name
    
    # Excluir arquivos de sistema/cache
    if '__pycache__' in path_str or '.git' in path_str:
        return False
    
    # Excluir __init__.py
    if name == '__init__.py':
        return False
    
    # Excluir arquivos de teste
    if 'test_' in name or '_test.py' in name or 'tests' in path_str.lower():
        return False
    
    # Excluir scripts utilitarios na raiz
    parts = file_path.parts
    if len(parts) == 2 and parts[0] == '.':
        # Scripts utilitarios geralmente comecam com maiuscula ou sao geradores
        if name[0].isupper() or 'GERAR' in name.upper() or 'GENERATE' in name.upper():
            return False
        # Mas incluir se for modulo core importante
        if name.startswith(('ncnt_', 'aurora_', 'main_', 'core_')):
            return True
    
    # Incluir modulos em diretorios hierarquicos (00-*, 01-*, etc.)
    for part in parts:
        if part.startswith(('00-', '01-', '02-', '03-', '04-', '05-', '06-')):
            # Excluir subarquivos de suporte
            if 'helper' in name.lower() or 'util' in name.lower():
                return False
            return True
    
    # Incluir modulos em system_core
    if 'system_core' in parts:
        if 'helper' in name.lower() or 'util' in name.lower():
            return False
        return True
    
    # Incluir modulos em modules/ (estrutura organizada, limitar profundidade)
    if 'modules' in parts and len(parts) <= 4:
        if 'helper' in name.lower() or 'util' in name.lower():
            return False
        return True
    
    # Incluir wrappers_v2
    if 'wrappers_v2' in parts:
        return True
    
    return False


def scan_aurora_system_modules(base_path: str = ".") -> list:
    """Escaneia e identifica os 252 modulos do sistema."""
    base = Path(base_path)
    modules = []
    
    # Escanear todos os arquivos Python
    for py_file in base.rglob('*.py'):
        if is_system_module(py_file):
            # Determinar categoria
            category = "Root"
            parts = py_file.parts
            
            for part in parts:
                if part.startswith('00-'):
                    category = "Governance"
                    break
                elif part.startswith('01-'):
                    category = "Departments"
                    break
                elif part.startswith('02-'):
                    category = "Processes"
                    break
                elif part.startswith('03-'):
                    category = "Operations"
                    break
                elif part.startswith('04-'):
                    category = "Infrastructure"
                    break
                elif part.startswith('05-'):
                    category = "Documentation"
                    break
                elif part.startswith('06-'):
                    category = "Monitoring"
                    break
                elif 'system_core' in part:
                    category = "Core"
                    break
                elif 'modules' in part and len(parts) > 2:
                    category = "Modules"
                    break
            
            rel_path = py_file.relative_to(base)
            module_name = str(rel_path).replace('\\', '/').replace('.py', '').replace('/', '_')
            
            modules.append({
                "name": module_name,
                "path": str(rel_path),
                "category": category,
                "full_path": str(py_file)
            })
    
    return modules


def integrate_aurora_modules_correct(dry_run: bool = False) -> dict:
    """Integra os 252 modulos do sistema ao sistema de governanca."""
    print("\n" + "=" * 80)
    print("INTEGRACAO DE MODULOS AURORA - SISTEMA DE GOVERNANCA")
    print("=" * 80)
    
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    print("\nEscaneando estrutura do Aurora (252 modulos do sistema)...")
    modules_found = scan_aurora_system_modules()
    
    # Agrupar por categoria
    by_category = {}
    for mod in modules_found:
        cat = mod["category"]
        by_category.setdefault(cat, [])
        by_category[cat].append(mod)
    
    print(f"\nTotal identificado: {len(modules_found)} modulos")
    print(f"\nDistribuicao por categoria:")
    for cat, mods in sorted(by_category.items()):
        print(f"   {cat:20s}: {len(mods):3d} modulos")
    
    # Verificar se esta proximo de 252
    if len(modules_found) > 300:
        print(f"\nAVISO: Identificados {len(modules_found)} modulos, mas o sistema tem 252.")
        print("Aplicando filtro adicional para identificar apenas modulos principais...")
        # Aplicar filtro mais restritivo se necessario
        modules_found = [m for m in modules_found if not any(x in m['name'].lower() for x in ['helper', 'util', 'support', 'base', 'common'])]
        print(f"Apos filtro: {len(modules_found)} modulos")
    
    print(f"\nExemplos (primeiros 10):")
    for i, mod in enumerate(modules_found[:10], 1):
        print(f"   {i:2d}. [{mod['category']:12s}] {mod['name'][:50]}")
    
    if dry_run:
        print("\nDRY RUN: Nenhuma alteracao sera feita")
        return {
            "modules_found": len(modules_found),
            "modules_list": modules_found,
            "by_category": {k: len(v) for k, v in by_category.items()},
            "dry_run": True
        }
    
    # Importar modulos
    print("\nImportando modulos para o sistema de governanca...")
    module_names = [mod["name"] for mod in modules_found]
    result = orchestrator.import_from_list(module_names)
    print(f"   {result}")
    
    # Adicionar metadados
    print("\nAdicionando metadados de categoria...")
    modules_dict = orchestrator.state["modules"]
    added = 0
    
    for mod_info in modules_found:
        for mod_id, mod_data in modules_dict.items():
            if mod_data.get("name") == mod_info["name"]:
                if "metadata" not in mod_data:
                    mod_data["metadata"] = {}
                mod_data["metadata"]["category"] = mod_info["category"]
                mod_data["metadata"]["path"] = mod_info["path"]
                added += 1
                break
    
    orchestrator._save()
    print(f"   {added} modulos com metadados adicionados")
    
    # Relatorio
    report = orchestrator.generate_report(detailed=False)
    
    print(f"\nESTADO APOS INTEGRACAO:")
    print(f"   Total de Modulos: {report['TOTAL_MODULES']}")
    print(f"   Distribuicao por Status:")
    for status, count in report["BY_STATUS"].items():
        print(f"     {status}: {count}")
    
    return {
        "modules_found": len(modules_found),
        "modules_imported": report['TOTAL_MODULES'],
        "by_category": {k: len(v) for k, v in by_category.items()},
        "report": report,
        "dry_run": False
    }


def main():
    """Funcao principal"""
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        result = integrate_aurora_modules_correct(dry_run=dry_run)
        
        print("\n" + "=" * 80)
        if dry_run:
            print("DRY RUN CONCLUIDO")
            print(f"\nModulos identificados: {result['modules_found']}")
            print(f"Distribuicao:")
            for cat, count in sorted(result['by_category'].items()):
                print(f"   {cat}: {count}")
        else:
            print("INTEGRACAO CONCLUIDA")
            print(f"\nModulos identificados: {result['modules_found']}")
            print(f"Modulos importados: {result['modules_imported']}")
        print("=" * 80)
        
        if not dry_run:
            report_file = "RELATORIO_INTEGRACAO_GOVERNANCA_CORRETO.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"\nRelatorio salvo em: {report_file}")
        
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

