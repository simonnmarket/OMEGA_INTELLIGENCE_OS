#!/usr/bin/env python3
"""
Script para gerar relatórios visuais de governança com cores e formatação
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Adicionar path do módulo de governança
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("❌ Erro: Módulo financial_governance_orchestrator não encontrado")
    sys.exit(1)


def generate_visual_report():
    """Gerar relatório visual de governança"""
    
    print("\n" + "=" * 80)
    print("🏛️  RELATÓRIO DE GOVERNANÇA INSTITUCIONAL - AURORA v5.1")
    print("=" * 80)
    
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    report = orchestrator.generate_report(detailed=True)
    
    # Cabeçalho
    print(f"\n📊 ESTATÍSTICAS GERAIS")
    print("-" * 80)
    print(f"   Total de Módulos: {report['TOTAL_MODULES']}")
    print(f"   Última Atualização: {orchestrator.state['metadata']['last_updated']}")
    
    # Distribuição por Status (com cores)
    print(f"\n🔄 DISTRIBUIÇÃO POR STATUS")
    print("-" * 80)
    
    status_colors = {
        "BACKLOG": "🟡",
        "ACTIVE": "🟢",
        "INACTIVE": "🔴",
        "COMPLETED": "🔵"
    }
    
    for status, count in sorted(report["BY_STATUS"].items()):
        icon = status_colors.get(status, "⚪")
        percentage = (count / report["TOTAL_MODULES"] * 100) if report["TOTAL_MODULES"] > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"   {icon} {status:12s}: {count:3d} módulos ({percentage:5.1f}%) {bar}")
    
    # Análise de Risco
    print(f"\n⚠️  ANÁLISE DE RISCO")
    print("-" * 80)
    risk = report["RISK_ANALYSIS"]
    
    if risk["high_risk_indicator"]:
        print("   🚨 ALTO RISCO: Mais de 50 módulos em ACTIVE")
    else:
        print("   ✅ RISCO CONTROLADO: Número de módulos ACTIVE dentro do limite")
    
    if risk["stagnation_warning"]:
        print("   ⚠️  AVISO: Mais de 30% dos módulos em BACKLOG (possível estagnação)")
    else:
        print("   ✅ BACKLOG SAUDÁVEL: Menos de 30% dos módulos em BACKLOG")
    
    print(f"   📊 Cobertura Compliance: {risk['compliance_coverage']:.1f}%")
    
    # Módulos Detalhados (se disponível)
    if "MODULES_DETAILED" in report:
        print(f"\n📋 MÓDULOS DETALHADOS (Primeiros 10)")
        print("-" * 80)
        
        for i, (mod_id, details) in enumerate(list(report["MODULES_DETAILED"].items())[:10], 1):
            status = details["status"]
            icon = status_colors.get(status, "⚪")
            print(f"   {i:2d}. {icon} {mod_id}: {details['name']}")
            print(f"       Status: {status} | Ações: {details['action_count']} | Tags: {len(details['compliance_tags'])}")
    
    # Relatório de Compliance
    print(f"\n🏛️  RELATÓRIO DE COMPLIANCE")
    print("-" * 80)
    compliance_report = orchestrator.get_compliance_report()
    
    if compliance_report:
        for framework, modules in compliance_report.items():
            print(f"   📌 {framework}: {len(modules)} módulos")
            if len(modules) <= 5:
                print(f"      Módulos: {', '.join(modules)}")
    else:
        print("   ⚠️  Nenhuma tag de compliance registrada")
    
    # Eventos Recentes
    print(f"\n📜 EVENTOS RECENTES (Últimos 5)")
    print("-" * 80)
    recent_events = orchestrator.search_events(
        start_date=(datetime.now() - timedelta(days=7)).isoformat()
    )
    
    for event in recent_events[-5:]:
        timestamp = event.get("timestamp", "")[:16]
        module = event.get("module_id", "Unknown")
        action = event.get("action", "")[:50]
        actor = event.get("actor", "Unknown")
        print(f"   [{timestamp}] {module} | {actor}: {action}")
    
    print("\n" + "=" * 80)
    print("✅ RELATÓRIO GERADO COM SUCESSO")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    try:
        generate_visual_report()
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

