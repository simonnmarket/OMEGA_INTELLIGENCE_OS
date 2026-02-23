#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera relatório de estrutura hierárquica dos módulos com status"""

import json
import os
from pathlib import Path

# Carregar manifest
manifest_file = "project_manifest.json"
if os.path.exists(manifest_file):
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    modules = manifest.get("modules", {})
else:
    modules = {}

# Mapear módulos por caminho
modules_by_path = {}
for mod_id, mod_data in modules.items():
    path = mod_data.get("name", "")
    status = mod_data.get("status", "BACKLOG")
    modules_by_path[path] = status

# Estrutura hierárquica
estrutura = {
    "00-Governanca": {
        "quantum_firewall.py": modules_by_path.get("quantum_firewall", "BACKLOG"),
        "tier1_risk_validator.py": modules_by_path.get("tier1_risk_validator", "BACKLOG"),
        "governance_module.py": modules_by_path.get("governance_module", "BACKLOG"),
        "regulatory_context.py": modules_by_path.get("regulatory_context", "BACKLOG"),
        "financial_governance_orchestrator.py": modules_by_path.get("financial_governance_orchestrator", "ACTIVE"),
    },
    "01-Departamentos": {
        "AGENTS": {
            "CEO_Agent.py": modules_by_path.get("CEO_Agent", "BACKLOG"),
            "CFO_Agent.py": modules_by_path.get("CFO_Agent", "BACKLOG"),
            "CTO_Agent.py": modules_by_path.get("CTO_Agent", "BACKLOG"),
            "CKO_Agent.py": modules_by_path.get("CKO_Agent", "BACKLOG"),
        },
        "Execution-Trading": {
            "strategies": {
                "alpha_momentum.py": modules_by_path.get("alpha_momentum", "BACKLOG"),
                "mean_reversion.py": modules_by_path.get("mean_reversion", "BACKLOG"),
                "breakout_detection.py": modules_by_path.get("breakout_detection", "BACKLOG"),
            },
            "order_management.py": modules_by_path.get("order_management", "BACKLOG"),
        },
        "Risk-Controls": {
            "risk_engine.py": modules_by_path.get("risk_engine", "BACKLOG"),
            "circuit_breakers.py": modules_by_path.get("circuit_breakers", "BACKLOG"),
        },
        "Compliance-Audit": {
            "compliance_module.py": modules_by_path.get("compliance_module", "BACKLOG"),
        },
    },
    "02-Processos-Chave": {
        "[Process orchestration modules]": "PLACEHOLDER",
    },
    "03-Operacoes-Diarias": {
        "[Daily operations automation]": "PLACEHOLDER",
    },
    "04-Infraestrutura": {
        "mt5_executor.py": modules_by_path.get("mt5_executor", "BACKLOG"),
        "api": {
            "database.py": modules_by_path.get("database", "BACKLOG"),
            "endpoints": "[Endpoints]",
        },
        "ML_MODELS": "[ML Models]",
    },
    "05-Documentacao": {
        "[Knowledge base]": "PLACEHOLDER",
    },
    "06-Monitoramento": {
        "feedbackloop_module.py": modules_by_path.get("feedbackloop_module", "BACKLOG"),
    },
}

def gerar_arvore(estrutura, prefix="", is_last=True):
    """Gera árvore hierárquica"""
    output = []
    
    items = list(estrutura.items())
    for i, (key, value) in enumerate(items):
        is_last_item = (i == len(items) - 1)
        current_prefix = "└── " if is_last_item else "├── "
        
        if isinstance(value, dict):
            status_icon = ""
            output.append(f"{prefix}{current_prefix}{key}/")
            next_prefix = prefix + ("    " if is_last_item else "│   ")
            output.extend(gerar_arvore(value, next_prefix, is_last_item))
        else:
            if value == "PLACEHOLDER":
                status_icon = " [PLACEHOLDER]"
            else:
                status_map = {
                    "ACTIVE": " 🟢 ACTIVE",
                    "INACTIVE": " 🔴 INACTIVE",
                    "BACKLOG": " 🟡 BACKLOG",
                    "COMPLETED": " 🔵 COMPLETED",
                }
                status_icon = status_map.get(value, f" [{value}]")
            output.append(f"{prefix}{current_prefix}{key}{status_icon}")
    
    return output

# Gerar relatório
print("AURORA_NCNT\n")
output = gerar_arvore(estrutura)
print("\n".join(output))

# Salvar em arquivo
with open("ESTRUTURA_MODULOS_STATUS.md", "w", encoding="utf-8") as f:
    f.write("# ESTRUTURA HIERÁRQUICA DE MÓDULOS - AURORA v5.1\n\n")
    f.write("```\n")
    f.write("AURORA_NCNT\n\n")
    f.write("\n".join(output))
    f.write("\n```\n\n")
    f.write("## Legenda de Status:\n")
    f.write("- 🟢 ACTIVE: Módulo ativo e operacional\n")
    f.write("- 🔴 INACTIVE: Módulo inativo/descontinuado\n")
    f.write("- 🟡 BACKLOG: Módulo identificado, não iniciado\n")
    f.write("- 🔵 COMPLETED: Módulo implementado e validado\n")
    f.write("- [PLACEHOLDER]: Estrutura definida, módulos a serem implementados\n")

print("\n✅ Relatório salvo em: ESTRUTURA_MODULOS_STATUS.md")

