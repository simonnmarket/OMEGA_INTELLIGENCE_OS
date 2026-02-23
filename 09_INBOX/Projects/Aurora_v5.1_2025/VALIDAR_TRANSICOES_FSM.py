#!/usr/bin/env python3
"""
Script para validar transições FSM antes de executar alterações
"""

import sys
import os
from pathlib import Path

# Adicionar path do módulo de governança
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator, ALLOWED_TRANSITIONS, Status
except ImportError:
    print("❌ Erro: Módulo financial_governance_orchestrator não encontrado")
    sys.exit(1)


def validate_transition(mod_id: str, current_status: str, requested_status: str):
    """
    Valida se uma transição FSM é permitida.
    
    Returns:
        (is_valid, message)
    """
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    # Verificar se módulo existe
    if mod_id not in orchestrator.state["modules"]:
        return False, f"❌ Módulo {mod_id} não encontrado no manifesto."
    
    # Verificar Pivot Protection
    if current_status == Status.INACTIVE.value and requested_status != Status.ACTIVE.value:
        return False, (
            f"🚨 BLOQUEIO POR PIVOT PROTECTION: Módulo {mod_id} está INATIVO.\n"
            f"   REQUER: Reativação explícita com status_type='active' ou 'confirmed'"
        )
    
    # Validar transição FSM
    if not orchestrator._can_transition(current_status, requested_status):
        allowed = orchestrator.get_allowed_transitions(current_status)
        return False, (
            f"🚨 TRANSIÇÃO FSM NÃO AUTORIZADA: {current_status} → {requested_status}\n"
            f"   Módulo: {mod_id}\n"
            f"   Transições permitidas: {allowed if allowed else 'Nenhuma'}"
        )
    
    return True, f"✅ Transição autorizada: {current_status} → {requested_status}"


def check_module_status(mod_id: str) -> dict:
    """Verifica status atual de um módulo"""
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    if mod_id not in orchestrator.state["modules"]:
        return {"exists": False, "error": f"Módulo {mod_id} não encontrado"}
    
    module = orchestrator.state["modules"][mod_id]
    current_status = module.get("status", Status.BACKLOG.value)
    allowed = orchestrator.get_allowed_transitions(current_status)
    
    return {
        "exists": True,
        "mod_id": mod_id,
        "name": module.get("name", "Unknown"),
        "current_status": current_status,
        "allowed_transitions": allowed,
        "is_inactive": current_status == Status.INACTIVE.value,
        "action_count": len(module.get("actions", [])),
        "compliance_tags": module.get("compliance_tags", [])
    }


def main():
    """Função principal para validação interativa"""
    print("\n" + "=" * 80)
    print("🔍 VALIDADOR DE TRANSIÇÕES FSM - AURORA v5.1")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("\n📋 Uso:")
        print("   python VALIDAR_TRANSICOES_FSM.py <MOD_ID> [status_type]")
        print("\n   Exemplos:")
        print("   python VALIDAR_TRANSICOES_FSM.py MOD-001")
        print("   python VALIDAR_TRANSICOES_FSM.py MOD-001 active")
        print("   python VALIDAR_TRANSICOES_FSM.py MOD-001 completed")
        return
    
    mod_id = sys.argv[1]
    
    # Verificar status atual
    print(f"\n🔍 Verificando módulo: {mod_id}")
    status_info = check_module_status(mod_id)
    
    if not status_info["exists"]:
        print(f"   {status_info['error']}")
        return
    
    print(f"\n📊 STATUS ATUAL:")
    print(f"   Nome: {status_info['name']}")
    print(f"   Status: {status_info['current_status']}")
    print(f"   Ações registradas: {status_info['action_count']}")
    print(f"   Tags de compliance: {len(status_info['compliance_tags'])}")
    
    if status_info["is_inactive"]:
        print(f"\n   ⚠️  ATENÇÃO: Módulo está INACTIVE (Pivot Protection ativo)")
    
    print(f"\n🔄 TRANSIÇÕES PERMITIDAS:")
    allowed = status_info["allowed_transitions"]
    if allowed:
        for trans in allowed:
            print(f"   → {trans}")
    else:
        print("   Nenhuma transição permitida (estado final)")
    
    # Se status_type foi fornecido, validar transição
    if len(sys.argv) >= 3:
        status_type = sys.argv[2].lower()
        status_mapping = {
            "completed": Status.COMPLETED.value,
            "active": Status.ACTIVE.value,
            "confirmed": Status.ACTIVE.value,
            "inactive": Status.INACTIVE.value,
        }
        requested_status = status_mapping.get(status_type, status_info["current_status"])
        
        print(f"\n🔍 VALIDANDO TRANSIÇÃO:")
        print(f"   De: {status_info['current_status']}")
        print(f"   Para: {requested_status}")
        
        is_valid, message = validate_transition(
            mod_id,
            status_info["current_status"],
            requested_status
        )
        
        print(f"\n{message}")
        
        if is_valid:
            print(f"\n✅ PRONTO PARA EXECUTAR:")
            print(f"   orchestrator.log_event(")
            print(f"       mod_id='{mod_id}',")
            print(f"       action_desc='[DESCREVER AÇÃO]',")
            print(f"       status_type='{status_type}',")
            print(f"       actor='AIC_Agent'")
            print(f"   )")
    else:
        print(f"\n💡 Para validar uma transição específica, adicione o status_type:")
        print(f"   python VALIDAR_TRANSICOES_FSM.py {mod_id} active")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

