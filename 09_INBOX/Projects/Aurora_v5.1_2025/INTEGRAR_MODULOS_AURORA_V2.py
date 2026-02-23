#!/usr/bin/env python3
"""
Script V2 para integrar módulos existentes do Aurora ao sistema de governança
Identifica os 252 módulos do sistema (excluindo scripts utilitários)
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
    print("❌ Erro: Módulo financial_governance_orchestrator não encontrado")
    sys.exit(1)


def is_system_module(file_path: Path) -> bool:
    """
    Determina se um arquivo Python é um módulo do sistema (252 módulos principais).
    
    Critérios (baseado na documentação):
    - Está dentro de diretórios de sistema (system_core, modules, 00-*, 01-*, etc.)
    - NÃO é __init__.py (arquivos de inicialização)
    - NÃO é arquivo de teste (test_*, *_test.py)
    - NÃO é script utilitário na raiz (scripts que começam com maiúscula ou são geradores)
    - NÃO está em __pycache__ ou .git
    - É um módulo principal (não subarquivo de suporte)
    """
    path_str = str(file_path)
    name = file_path.name
    
    # Excluir arquivos de sistema/cache
    if '__pycache__' in path_str or '.git' in path_str or '.pytest_cache' in path_str:
        return False
    
    # Excluir __init__.py (arquivos de inicialização de pacotes)
    if name == '__init__.py':
        return False
    
    # Excluir arquivos de teste
    if 'test_' in name or '_test.py' in name or 'tests' in path_str.lower():
        return False
    
    # Excluir scripts utilitários na raiz (scripts que começam com maiúscula ou são geradores)
    parts = file_path.parts
    if len(parts) == 2 and parts[0] == '.':
        # Scripts utilitários geralmente começam com maiúscula ou são geradores
        if name[0].isupper() or 'GERAR' in name.upper() or 'GENERATE' in name.upper() or 'CREATE' in name.upper():
            return False
        # Mas incluir se for módulo core importante
        if name.startswith(('ncnt_', 'aurora_', 'main_', 'core_')):
            return True
    
    # Incluir módulos em diretórios hierárquicos (00-*, 01-*, etc.)
    for part in parts:
        if part.startswith(('00-', '01-', '02-', '03-', '04-', '05-', '06-')):
            # Dentro de diretórios hierárquicos, incluir apenas módulos principais
            # Excluir subarquivos de suporte (helpers, utils, etc.)
            if 'helper' in name.lower() or 'util' in name.lower() or 'support' in name.lower():
                return False
            return True
    
    # Incluir módulos em system_core (apenas principais, não subarquivos)
    if 'system_core' in parts:
        # Excluir subarquivos de suporte
        if 'helper' in name.lower() or 'util' in name.lower() or 'support' in name.lower():
            return False
        return True
    
    # Incluir módulos em modules/ (estrutura organizada)
    if 'modules' in parts and len(parts) <= 4:  # Limitar profundidade
        # Excluir subarquivos de suporte
        if 'helper' in name.lower() or 'util' in name.lower() or 'support' in name.lower():
            return False
        return True
    
    # Incluir wrappers_v2 (módulos principais)
    if 'wrappers_v2' in parts:
        return True
    
    return False


def scan_aurora_system_modules(base_path: str = ".") -> list:
    """
    Escaneia estrutura do Aurora e identifica os 252 módulos do sistema.
    
    Returns:
        Lista de tuplas (module_name, module_path, category)
    """
    base = Path(base_path)
    modules = []
    
    # Padrões de diretórios do sistema
    system_patterns = [
        '00-*', '01-*', '02-*', '03-*', '04-*', '05-*', '06-*',
        'system_core', 'modules', 'wrappers_v2'
    ]
    
    # Escanear todos os arquivos Python
    for py_file in base.rglob('*.py'):
        if is_system_module(py_file):
            # Determinar categoria
            category = "Unknown"
            parts = py_file.parts
            
            # Categorizar por diretório hierárquico
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
                elif 'modules' in part:
                    category = "Modules"
                    break
            
            # Nome do módulo baseado no caminho
            rel_path = py_file.relative_to(base)
            module_name = str(rel_path).replace('\\', '/').replace('.py', '').replace('/', '_')
            
            modules.append({
                "name": module_name,
                "path": str(rel_path),
                "category": category,
                "full_path": str(py_file)
            })
    
    return modules


def integrate_aurora_modules_v2(dry_run: bool = False) -> dict:
    """
    Integra módulos do Aurora ao sistema de governança (versão melhorada).
    
    Args:
        dry_run: Se True, apenas mostra o que seria feito sem executar
    
    Returns:
        Relatório da integração
    """
    print("\n" + "=" * 80)
    print("🔄 INTEGRAÇÃO DE MÓDULOS AURORA V2 - SISTEMA DE GOVERNANÇA")
    print("=" * 80)
    
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    # Escanear módulos do sistema
    print("\n📦 Escaneando estrutura do Aurora (módulos do sistema)...")
    modules_found = scan_aurora_system_modules()
    
    # Agrupar por categoria
    by_category = {}
    for mod in modules_found:
        cat = mod["category"]
        by_category.setdefault(cat, [])
        by_category[cat].append(mod)
    
    print(f"\n✅ {len(modules_found)} módulos do sistema identificados:")
    print(f"\n📊 Distribuição por categoria:")
    for cat, mods in sorted(by_category.items()):
        print(f"   {cat:20s}: {len(mods):3d} módulos")
    
    # Mostrar alguns exemplos
    print(f"\n📋 Exemplos de módulos identificados (primeiros 10):")
    for i, mod in enumerate(modules_found[:10], 1):
        print(f"   {i:2d}. [{mod['category']:12s}] {mod['name'][:50]}")
    
    if len(modules_found) > 10:
        print(f"   ... e mais {len(modules_found) - 10} módulos")
    
    if dry_run:
        print("\n🔍 DRY RUN: Nenhuma alteração será feita")
        return {
            "modules_found": len(modules_found),
            "modules_list": modules_found,
            "by_category": {k: len(v) for k, v in by_category.items()},
            "dry_run": True
        }
    
    # Preparar lista de nomes para importação
    module_names = [mod["name"] for mod in modules_found]
    
    # Importar módulos
    print("\n📥 Importando módulos para o sistema de governança...")
    result = orchestrator.import_from_list(module_names)
    print(f"   {result}")
    
    # Adicionar metadados de categoria aos módulos importados
    print("\n🏷️  Adicionando metadados de categoria...")
    modules_dict = orchestrator.state["modules"]
    added_categories = 0
    
    for mod_info in modules_found:
        # Encontrar módulo correspondente (pode ter ID diferente após importação)
        # Vamos adicionar categoria ao primeiro módulo que corresponder ao nome
        for mod_id, mod_data in modules_dict.items():
            if mod_data.get("name") == mod_info["name"]:
                if "metadata" not in mod_data:
                    mod_data["metadata"] = {}
                mod_data["metadata"]["category"] = mod_info["category"]
                mod_data["metadata"]["path"] = mod_info["path"]
                added_categories += 1
                break
    
    orchestrator._save()
    print(f"   ✅ {added_categories} módulos com metadados de categoria adicionados")
    
    # Gerar relatório
    report = orchestrator.generate_report(detailed=False)
    
    print(f"\n📊 ESTADO APÓS INTEGRAÇÃO:")
    print(f"   Total de Módulos: {report['TOTAL_MODULES']}")
    print(f"   Distribuição por Status:")
    for status, count in report["BY_STATUS"].items():
        print(f"     {status}: {count}")
    
    return {
        "modules_found": len(modules_found),
        "modules_imported": report['TOTAL_MODULES'],
        "modules_list": modules_found[:20],  # Primeiros 20 para não sobrecarregar
        "by_category": {k: len(v) for k, v in by_category.items()},
        "report": report,
        "dry_run": False
    }


def main():
    """Função principal"""
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        result = integrate_aurora_modules_v2(dry_run=dry_run)
        
        print("\n" + "=" * 80)
        if dry_run:
            print("✅ DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")
            print(f"\n📊 RESUMO:")
            print(f"   Módulos identificados: {result['modules_found']}")
            print(f"   Distribuição por categoria:")
            for cat, count in sorted(result['by_category'].items()):
                print(f"     {cat}: {count}")
        else:
            print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO")
            print(f"\n📊 RESUMO:")
            print(f"   Módulos identificados: {result['modules_found']}")
            print(f"   Módulos importados: {result['modules_imported']}")
            print(f"   Distribuição por categoria:")
            for cat, count in sorted(result['by_category'].items()):
                print(f"     {cat}: {count}")
        print("=" * 80)
        
        # Salvar relatório
        if not dry_run:
            report_file = "RELATORIO_INTEGRACAO_GOVERNANCA_V2.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n📄 Relatório salvo em: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Erro durante integração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

