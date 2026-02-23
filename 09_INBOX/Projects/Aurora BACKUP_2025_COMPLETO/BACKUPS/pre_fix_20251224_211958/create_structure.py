#!/usr/bin/env python3
"""
Script para criar estrutura completa do projeto AURORA NCNT
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Estrutura completa de pastas e arquivos
STRUCTURE = {
    "00-Governanca": {
        "charter.md": "# Charter do Projeto\n\n## Objetivo\nSistema de trading modular bank-like\n\n## Escopo\nForex, Metals, Crypto, Indices\n\n## SLA\n99.9% uptime, <50ms latency\n\n## RACI\n- Tech Lead: Arquitetura técnica\n- Risk Officer: Controles de risco\n- Compliance Rep: Conformidade regulatória",
        "comite_decisao.yaml": "# Comitê de Decisão\nmembers:\n  tech_lead: Decisões técnicas/arquitetura\n  risk_officer: Aprovações de risco\n  compliance: Aprovações regulatórias\n  capital_manager: Alocações de capital",
        "ciclo_revisao.md": "# Ciclo de Revisão Trimestral\n\nRevisões arquiteturais a cada 90 dias",
        "decisoes_log.json": "[]",
        "__init__.py": "# 00-Governança"
    },
    "01-Departamentos": {
        "README.md": "# Departamentos Funcionais\n\n6 departamentos principais do sistema",
        "Treasury-Capital": {
            "__init__.py": "# 💰 Treasury & Capital Allocation",
            "capital_manager.py": "# Gestão de Capital (Reservas, ROI tracking)",
            "allocation_engine.py": "# Alocação Dinâmica de Recursos"
        },
        "Engineering-Infra": {
            "__init__.py": "# ⚙️ Engineering & Infrastructure",
            "core_engine.py": "# Core Engine (Motor de execução)",
            "data_layer.py": "# Data Layer (ETL, Storage, Streaming)",
            "api_gateway.py": "# API Gateway / Integration Hub"
        },
        "Execution-Trading": {
            "__init__.py": "# 📈 Execution & Trading Ops",
            "strategy_modules": {
                "__init__.py": "# Strategy Modules",
                "interface.py": "# Interface padrão para todas as estratégias",
                "templates": {
                    "__init__.py": "",
                    "strategy_template.py": "# Template para criar nova estratégia"
                },
                "implementations": {
                    "__init__.py": ""
                }
            },
            "order_management.py": "# Order Management System (OMS)",
            "smart_routing.py": "# Smart Routing & Latency Control"
        },
        "Risk-Controls": {
            "__init__.py": "# 🛡️ Risk & Controls",
            "risk_engine.py": "# Real-Time Risk Engine (VaR, Exposure, Drawdown)",
            "circuit_breakers.py": "# Circuit Breakers & Kill Switches"
        },
        "Compliance-Audit": {
            "__init__.py": "# 📜 Compliance & Audit",
            "reg_tracker.py": "# RegTracker (RegD, MiFID II, SEC, etc.)",
            "audit_trail.py": "# Log Integrity & Immutable Audit Trail",
            "report_generator.py": "# Reporting Templates (Auto-generated)"
        },
        "Innovation-Lab": {
            "__init__.py": "# 🧩 Innovation Lab",
            "prototypes.py": "# Protótipos e R&D",
            "ab_testing.py": "# A/B Testing Framework"
        }
    },
    "02-Processos-Chave": {
        "README.md": "# Processos-Chave (Cross-Departmental)",
        "CI-CD": {
            "__init__.py": "# 🔁 CI/CD & Deployment Pipeline",
            "pipeline.yaml": "# Configuração do pipeline",
            "stages": {
                "__init__.py": "",
                "build.py": "# Build stage",
                "test.py": "# Test stage",
                "deploy.py": "# Deploy stage"
            }
        },
        "QA-Backtesting": {
            "__init__.py": "# 🧪 QA & Backtesting Framework",
            "backtest_engine.py": "# Motor de backtesting",
            "test_suites": {
                "__init__.py": ""
            }
        },
        "Onboarding": {
            "__init__.py": "# 📥 Onboarding",
            "data_onboarding.py": "# Onboarding de dados",
            "strategy_onboarding.py": "# Onboarding de estratégias",
            "counterparty_onboarding.py": "# Onboarding de contrapartes"
        },
        "Incident-Response": {
            "__init__.py": "# 🚨 Incident Response Protocol",
            "playbook.yaml": "# Playbook de resposta a incidentes",
            "severity_levels.yaml": "# Níveis de severidade"
        }
    },
    "03-Operacoes-Diarias": {
        "README.md": "# Operações Diárias (Automatizadas)",
        "Pre-Market": {
            "__init__.py": "# 🕒 Pre-Market Checklist",
            "checklist.yaml": "# Checklist auto-validado",
            "validators": {
                "__init__.py": ""
            }
        },
        "Execution-Window": {
            "__init__.py": "# 📤 Execution Window",
            "schedules.yaml": "# Horários de mercado",
            "throttling.py": "# Controle de throttling"
        },
        "Real-Time-Dashboard": {
            "__init__.py": "# 📊 Real-Time Dashboard",
            "dashboard.py": "# Dashboard principal",
            "widgets": {
                "__init__.py": ""
            }
        },
        "Post-Trade": {
            "__init__.py": "# 📤 Post-Trade Reconciliation",
            "reconciliation.py": "# Reconciliação automática",
            "delta_reports.py": "# Gerador de relatórios delta"
        }
    },
    "04-Infraestrutura": {
        "README.md": "# Infraestrutura Técnica (Modular)",
        "config": {
            "env": {
                "development.yaml": "# Configuração desenvolvimento",
                "staging.yaml": "# Configuração staging",
                "production.yaml": "# Configuração produção"
            },
            "policies": {
                "sla_thresholds.yaml": "# Limites de SLA",
                "rate_limits.yaml": "# Limites de taxa",
                "risk_policies.yaml": "# Políticas de risco"
            }
        },
        "tools": {
            "cli": {
                "__init__.py": "",
                "ncnt_cli.py": "# CLI principal",
                "commands": {
                    "__init__.py": ""
                }
            },
            "scripts": {
                "__init__.py": "",
                "deploy.py": "# Script de deploy",
                "monitor.py": "# Script de monitoramento",
                "backup.py": "# Script de backup"
            }
        }
    },
    "05-Documentacao": {
        "README.md": "# Documentação & Knowledge Base",
        "SOPs": {
            "trading_operations.md": "# SOP: Operações de Trading",
            "risk_management.md": "# SOP: Gestão de Risco",
            "compliance_procedures.md": "# SOP: Procedimentos de Compliance"
        },
        "Decision-Logs": {
            "architecture_decisions.md": "# Decisões de Arquitetura",
            "technology_choices.md": "# Escolhas Tecnológicas",
            "business_decisions.md": "# Decisões de Negócio"
        },
        "Playbooks": {
            "recovery_playbook.md": "# Playbook de Recuperação",
            "upgrade_playbook.md": "# Playbook de Upgrade",
            "migration_playbook.md": "# Playbook de Migração"
        }
    },
    "06-Monitoramento": {
        "README.md": "# Monitoramento & Melhoria Contínua",
        "KPIs": {
            "operational_kpis.yaml": "# 📈 KPIs Operacionais",
            "risk_kpis.yaml": "# 📉 Risk KPIs",
            "business_kpis.yaml": "# 📊 Business KPIs"
        },
        "Feedback-Loop": {
            "__init__.py": "",
            "post_mortem.py": "# Análise post-mortem",
            "rca_templates.py": "# Templates de Root Cause Analysis",
            "action_items.py": "# Gerenciador de itens de ação"
        }
    },
    "modules": {
        "connectors": {
            "__init__.py": "# 🔌 Conectores padrão",
            "strategy_connector.py": "# Conector para estratégias",
            "risk_connector.py": "# Conector para risco",
            "execution_connector.py": "# Conector para execução",
            "data_connector.py": "# Conector para dados"
        }
    }
}


def create_structure(base_path: Path, structure: dict, prefix=""):
    """Criar estrutura recursivamente"""
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # É uma pasta
            path.mkdir(parents=True, exist_ok=True)
            print(f"{prefix}[DIR] {name}/")
            create_structure(path, content, prefix + "  ")
        else:
            # É um arquivo
            if not path.exists():
                path.write_text(content, encoding='utf-8')
                print(f"{prefix}[FILE] {name}")
            else:
                print(f"{prefix}[SKIP] {name} (ja existe)")


if __name__ == "__main__":
    import sys
    import io
    # Configurar stdout para UTF-8
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Criando estrutura completa do AURORA NCNT...\n")
    create_structure(BASE_DIR, STRUCTURE)
    print("\nEstrutura criada com sucesso!")

