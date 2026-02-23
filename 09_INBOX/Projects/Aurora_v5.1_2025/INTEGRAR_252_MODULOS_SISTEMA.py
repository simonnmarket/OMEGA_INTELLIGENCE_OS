#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para integrar EXATAMENTE os 252 módulos do sistema documentados
Usa a lista completa da PARTE 4 do AURORA_COMPLETE_TECHNICAL_DOCUMENT.md
"""

import sys
import os
import re
from pathlib import Path
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: Modulo financial_governance_orchestrator nao encontrado")
    sys.exit(1)


def extract_modules_from_document():
    """
    Extrai a lista completa de 252 módulos da PARTE 4 do documento técnico.
    """
    doc_path = "AURORA_COMPLETE_TECHNICAL_DOCUMENT.md"
    
    if not os.path.exists(doc_path):
        print(f"ERRO: Documento {doc_path} nao encontrado")
        return None
    
    print(f"Lendo documento: {doc_path}")
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção PARTE 4
    parte4_start = content.find("## PARTE 4: LISTA COMPLETA DE MÓDULOS (252 System Modules)")
    if parte4_start == -1:
        print("ERRO: Secao PARTE 4 nao encontrada no documento")
        return None
    
    # Encontrar o início da lista (após "## 4.1 Complete Module List")
    list_start = content.find("## 4.1 Complete Module List", parte4_start)
    if list_start == -1:
        print("ERRO: Lista de modulos nao encontrada")
        return None
    
    # Extrair o bloco de código text
    code_start = content.find("```text", list_start)
    if code_start == -1:
        code_start = content.find("```", list_start)
    
    if code_start == -1:
        print("ERRO: Bloco de codigo nao encontrado")
        return None
    
    code_end = content.find("```", code_start + 7)
    if code_end == -1:
        print("ERRO: Fim do bloco de codigo nao encontrado")
        return None
    
    # Extrair linhas do bloco
    code_block = content[code_start + 7:code_end].strip()
    lines = [line.strip() for line in code_block.split('\n') if line.strip()]
    
    # Filtrar apenas linhas que são caminhos de arquivos .py
    modules = []
    for line in lines:
        line = line.strip()
        # Remover backslashes e normalizar
        if line.endswith('.py'):
            # Normalizar caminho (Windows usa \, documento pode usar /)
            normalized = line.replace('\\', '/')
            modules.append(normalized)
    
    print(f"Modulos extraidos do documento: {len(modules)}")
    return modules


def verify_modules_exist(module_list):
    """Verifica quais módulos da lista realmente existem no sistema."""
    base = Path('.')
    existing = []
    missing = []
    
    for module_path in module_list:
        # Tentar diferentes variações do caminho
        paths_to_try = [
            module_path,
            module_path.replace('/', '\\'),  # Windows
            module_path.replace('\\', '/'),  # Unix
        ]
        
        found = False
        for path_variant in paths_to_try:
            full_path = base / path_variant
            if full_path.exists():
                existing.append({
                    "documented_path": module_path,
                    "actual_path": str(full_path),
                    "exists": True
                })
                found = True
                break
        
        if not found:
            missing.append(module_path)
    
    return existing, missing


def categorize_module(module_path):
    """Categoriza módulo baseado no caminho."""
    path_lower = module_path.lower()
    
    if '00-governanca' in path_lower or '00-governance' in path_lower:
        return "Governance"
    elif '01-departamentos' in path_lower or '01-departments' in path_lower:
        return "Departments"
    elif '02-processos' in path_lower or '02-processes' in path_lower:
        return "Processes"
    elif '03-operacoes' in path_lower or '03-operations' in path_lower:
        return "Operations"
    elif '04-infraestrutura' in path_lower or '04-infrastructure' in path_lower:
        return "Infrastructure"
    elif '05-documentacao' in path_lower or '05-documentation' in path_lower:
        return "Documentation"
    elif '06-monitoramento' in path_lower or '06-monitoring' in path_lower:
        return "Monitoring"
    elif 'system_core' in path_lower:
        return "Core"
    elif 'modules' in path_lower:
        return "Modules"
    else:
        return "Root"


def integrate_252_modules(dry_run=False):
    """Integra os 252 módulos documentados ao sistema de governança."""
    print("\n" + "=" * 80)
    print("INTEGRACAO DOS 252 MODULOS DO SISTEMA - AURORA v5.1")
    print("=" * 80)
    
    # Extrair lista do documento
    print("\n[1/4] Extraindo lista de modulos do documento...")
    module_list = extract_modules_from_document()
    
    if not module_list:
        print("ERRO: Nao foi possivel extrair lista de modulos")
        return None
    
    print(f"   Total de modulos na lista: {len(module_list)}")
    
    # Verificar quais existem
    print("\n[2/4] Verificando existencia dos modulos...")
    existing, missing = verify_modules_exist(module_list)
    
    print(f"   Modulos existentes: {len(existing)}")
    print(f"   Modulos nao encontrados: {len(missing)}")
    
    if missing:
        print(f"\n   AVISO: {len(missing)} modulos da lista nao foram encontrados:")
        for mod in missing[:10]:
            print(f"      - {mod}")
        if len(missing) > 10:
            print(f"      ... e mais {len(missing) - 10} modulos")
    
    # Categorizar
    print("\n[3/4] Categorizando modulos...")
    by_category = {}
    for mod_info in existing:
        cat = categorize_module(mod_info["documented_path"])
        by_category.setdefault(cat, [])
        by_category[cat].append(mod_info)
    
    print(f"   Distribuicao por categoria:")
    for cat, mods in sorted(by_category.items()):
        print(f"      {cat:20s}: {len(mods):3d} modulos")
    
    if dry_run:
        print("\n[4/4] DRY RUN: Nenhuma alteracao sera feita")
        return {
            "total_documented": len(module_list),
            "total_existing": len(existing),
            "total_missing": len(missing),
            "missing_list": missing,
            "by_category": {k: len(v) for k, v in by_category.items()},
            "dry_run": True
        }
    
    # Integrar ao sistema de governança
    print("\n[4/4] Integrando ao sistema de governanca...")
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    # Criar nomes únicos para cada módulo
    module_names = []
    for mod_info in existing:
        # Criar nome baseado no caminho
        path = mod_info["documented_path"]
        name = path.replace('\\', '_').replace('/', '_').replace('.py', '')
        module_names.append(name)
    
    print(f"   Importando {len(module_names)} modulos...")
    result = orchestrator.import_from_list(module_names)
    print(f"   {result}")
    
    # Adicionar metadados
    print("\n   Adicionando metadados...")
    modules_dict = orchestrator.state["modules"]
    added_metadata = 0
    
    for i, mod_info in enumerate(existing):
        # Encontrar módulo correspondente (pode ter ID diferente)
        mod_id = f"MOD-{i+1:03d}"
        if mod_id in modules_dict:
            mod_data = modules_dict[mod_id]
            if "metadata" not in mod_data:
                mod_data["metadata"] = {}
            mod_data["metadata"]["category"] = categorize_module(mod_info["documented_path"])
            mod_data["metadata"]["documented_path"] = mod_info["documented_path"]
            mod_data["metadata"]["actual_path"] = mod_info["actual_path"]
            added_metadata += 1
    
    orchestrator._save()
    print(f"   {added_metadata} modulos com metadados adicionados")
    
    # Relatório final
    report = orchestrator.generate_report(detailed=False)
    
    print(f"\n" + "=" * 80)
    print("INTEGRACAO CONCLUIDA")
    print("=" * 80)
    print(f"   Modulos documentados: {len(module_list)}")
    print(f"   Modulos encontrados: {len(existing)}")
    print(f"   Modulos importados: {report['TOTAL_MODULES']}")
    print(f"   Modulos nao encontrados: {len(missing)}")
    
    return {
        "total_documented": len(module_list),
        "total_existing": len(existing),
        "total_imported": report['TOTAL_MODULES'],
        "total_missing": len(missing),
        "missing_list": missing,
        "by_category": {k: len(v) for k, v in by_category.items()},
        "report": report,
        "dry_run": False
    }


def main():
    """Funcao principal"""
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        result = integrate_252_modules(dry_run=dry_run)
        
        if result and not dry_run:
            report_file = "RELATORIO_INTEGRACAO_252_MODULOS.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"\nRelatorio salvo em: {report_file}")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

