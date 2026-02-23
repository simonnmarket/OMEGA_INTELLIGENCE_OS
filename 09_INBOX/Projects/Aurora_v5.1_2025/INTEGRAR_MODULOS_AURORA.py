#!/usr/bin/env python3
"""
Script para integrar módulos existentes do Aurora ao sistema de governança
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


def scan_aurora_modules(base_path: str = ".") -> list:
    """
    Escaneia estrutura do Aurora e identifica módulos principais.
    
    Returns:
        Lista de nomes de módulos identificados
    """
    base = Path(base_path)
    modules = []
    
    # Diretórios principais do Aurora
    main_dirs = [
        "system_core",
        "modules",
        "00-Governanca",
        "agents",
        "strategies",
        "risk_management",
        "compliance",
        "monitoring",
    ]
    
    # Escanear diretórios principais
    for dir_name in main_dirs:
        dir_path = base / dir_name
        if dir_path.exists() and dir_path.is_dir():
            modules.append(dir_name.replace("_", " ").title())
    
    # Escanear subdiretórios de modules/
    modules_dir = base / "modules"
    if modules_dir.exists():
        for item in modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                modules.append(f"Module: {item.name.replace('_', ' ').title()}")
    
    # Escanear arquivos Python principais na raiz
    for py_file in base.glob("*.py"):
        if py_file.name.startswith("_") or py_file.name in ["setup.py", "test.py"]:
            continue
        module_name = py_file.stem.replace("_", " ").title()
        if module_name not in modules:
            modules.append(f"Core: {module_name}")
    
    return sorted(set(modules))


def integrate_aurora_modules(dry_run: bool = False) -> dict:
    """
    Integra módulos do Aurora ao sistema de governança.
    
    Args:
        dry_run: Se True, apenas mostra o que seria feito sem executar
    
    Returns:
        Relatório da integração
    """
    print("\n" + "=" * 80)
    print("🔄 INTEGRAÇÃO DE MÓDULOS AURORA - SISTEMA DE GOVERNANÇA")
    print("=" * 80)
    
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    # Escanear módulos
    print("\n📦 Escaneando estrutura do Aurora...")
    modules_found = scan_aurora_modules()
    
    print(f"\n✅ {len(modules_found)} módulos identificados:")
    for i, mod in enumerate(modules_found[:20], 1):  # Mostrar primeiros 20
        print(f"   {i:2d}. {mod}")
    if len(modules_found) > 20:
        print(f"   ... e mais {len(modules_found) - 20} módulos")
    
    if dry_run:
        print("\n🔍 DRY RUN: Nenhuma alteração será feita")
        return {
            "modules_found": len(modules_found),
            "modules_list": modules_found,
            "dry_run": True
        }
    
    # Importar módulos
    print("\n📥 Importando módulos para o sistema de governança...")
    result = orchestrator.import_from_list(modules_found)
    print(f"   {result}")
    
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
        "modules_list": modules_found,
        "report": report,
        "dry_run": False
    }


def main():
    """Função principal"""
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        result = integrate_aurora_modules(dry_run=dry_run)
        
        print("\n" + "=" * 80)
        if dry_run:
            print("✅ DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")
        else:
            print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 80)
        
        # Salvar relatório
        if not dry_run:
            report_file = "RELATORIO_INTEGRACAO_GOVERNANCA.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Relatório salvo em: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Erro durante integração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

