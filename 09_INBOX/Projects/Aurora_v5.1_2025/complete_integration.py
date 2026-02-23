#!/usr/bin/env python3
"""
Script de Integração Completa Final
Atualiza orquestrador, cria main.py e atualiza requirements
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
SOURCE_FILE = BASE_DIR / "ncnt_system_complete.py"

def extract_full_class(content: str, class_name: str) -> str:
    """Extrair classe completa incluindo métodos"""
    pattern = rf'^class {class_name}\(.*?\):'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return ""
    
    start = match.start()
    
    # Encontrar fim da classe
    lines = content[start:].split('\n')
    indent_level = len(lines[0]) - len(lines[0].lstrip())
    end = start
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # Nova classe ou função no nível raiz
            if re.match(r'^(class |def |async def |if __name__)', line):
                end = start + sum(len(l) + 1 for l in lines[:i])
                break
        elif line.strip() and (len(line) - len(line.lstrip())) <= indent_level:
            # Mesmo nível de indentação - fim da classe
            if re.match(r'^[A-Z]', line.strip()):
                end = start + sum(len(l) + 1 for l in lines[:i])
                break
    
    if end == start:
        end = len(content)
    
    return content[start:end].strip()

def main():
    print("=" * 80)
    print("INTEGRACAO COMPLETA FINAL - AURORA NCNT")
    print("=" * 80)
    print()
    
    if not SOURCE_FILE.exists():
        print(f"ERRO: Arquivo nao encontrado: {SOURCE_FILE}")
        return
    
    content = SOURCE_FILE.read_text(encoding='utf-8')
    print(f"Lendo arquivo: {SOURCE_FILE}")
    print()
    
    # 1. Atualizar orquestrador
    print("1. Atualizando orquestrador...")
    orchestrator_code = extract_full_class(content, "NCNTOrchestrator")
    
    if orchestrator_code:
        orchestrator_file = BASE_DIR / "system_core" / "ncnt_orchestrator_complete.py"
        orchestrator_content = f'''#!/usr/bin/env python3
"""
Orquestrador NCNT Completo
Sistema principal de controle e coordenação
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ncnt_base import (
    ModuleType, NCNTTransmission, NCNTBaseModule
)
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio

# Importar todos os módulos
from {BASE_DIR.name}.00-Governanca.governance_module import GovernanceModule
from {BASE_DIR.name}.01-Departamentos.Treasury-Capital.treasury_module import TreasuryModule
from {BASE_DIR.name}.01-Departamentos.Engineering-Infra.coreengine_module import CoreEngineModule
from {BASE_DIR.name}.01-Departamentos.Execution-Trading.strategy_module import StrategyModule
from {BASE_DIR.name}.01-Departamentos.Risk-Controls.risk_module import RiskModule
from {BASE_DIR.name}.01-Departamentos.Compliance-Audit.compliance_module import ComplianceModule
from {BASE_DIR.name}.01-Departamentos.Innovation-Lab.innovationlab_module import InnovationLabModule
from {BASE_DIR.name}.02-Processos-Chave.CI-CD.cicdpipeline_module import CICDPipelineModule
from {BASE_DIR.name}.02-Processos-Chave.QA-Backtesting.qabacktesting_module import QABacktestingModule
from {BASE_DIR.name}.02-Processos-Chave.Onboarding.onboarding_module import OnboardingModule
from {BASE_DIR.name}.02-Processos-Chave.Incident-Response.incidentresponse_module import IncidentResponseModule
from {BASE_DIR.name}.03-Operacoes-Diarias.Pre-Market.premarketchecklist_module import PreMarketChecklistModule
from {BASE_DIR.name}.03-Operacoes-Diarias.Execution-Window.executionwindow_module import ExecutionWindowModule
from {BASE_DIR.name}.03-Operacoes-Diarias.Real-Time-Dashboard.realtimedashboard_module import RealTimeDashboardModule
from {BASE_DIR.name}.03-Operacoes-Diarias.Post-Trade.posttradereconciliation_module import PostTradeReconciliationModule
from {BASE_DIR.name}.04-Infraestrutura.moduleregistry import ModuleRegistry
from {BASE_DIR.name}.05-Documentacao.sops_module import SOPsModule
from {BASE_DIR.name}.06-Monitoramento.feedbackloop_module import FeedbackLoopModule

{orchestrator_code}
'''
        orchestrator_file.write_text(orchestrator_content, encoding='utf-8')
        print(f"   [OK] Criado: {orchestrator_file}")
    print()
    
    # 2. Criar main.py integrado
    print("2. Criando main.py integrado...")
    main_content = '''#!/usr/bin/env python3
"""
AURORA NCNT System - Entry Point
Sistema de Trading Modular Completo
"""

import asyncio
import sys
from pathlib import Path

# Adicionar raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from system_core.ncnt_orchestrator_complete import NCNTOrchestrator


async def main():
    """Função principal"""
    print("=" * 80)
    print("AURORA NCNT SYSTEM - v2.0")
    print("=" * 80)
    print()
    
    orchestrator = NCNTOrchestrator()
    
    try:
        # Inicializar sistema completo
        await orchestrator.initialize()
        
        # Mostrar status
        print("\\nSistema inicializado com sucesso!")
        print(f"Modulos ativos: {len(orchestrator.modules)}")
        print(f"Status: {orchestrator.system_status}")
        
        # Executar demo workflow
        print("\\nExecutando workflow de demonstracao...")
        await orchestrator.run_demo_workflow()
        
        # Manter sistema rodando
        print("\\nSistema rodando. Pressione Ctrl+C para parar...")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\\n\\nRecebido sinal de parada...")
    except Exception as e:
        print(f"\\nERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\\nSistema encerrado.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nEncerrado pelo usuario.")
'''
    
    main_file = BASE_DIR / "main_ncnt.py"
    main_file.write_text(main_content, encoding='utf-8')
    print(f"   [OK] Criado: {main_file}")
    print()
    
    # 3. Atualizar requirements.txt
    print("3. Atualizando requirements.txt...")
    requirements_content = '''# AURORA NCNT System - Dependências Completas
# Python 3.8+

# Core
asyncio>=3.4.3

# Data & Serialization
pydantic>=2.0.0
pyyaml>=6.0

# Utilities
python-dateutil>=2.8.2
hashlib-compat>=1.0.0

# Optional: Trading (quando necessário)
# MetaTrader5>=5.0.45
# pandas>=2.0.0
# numpy>=1.24.0

# Development
# pytest>=7.0.0
# black>=23.0.0
'''
    
    req_file = BASE_DIR / "requirements.txt"
    req_file.write_text(requirements_content, encoding='utf-8')
    print(f"   [OK] Atualizado: {req_file}")
    print()
    
    print("=" * 80)
    print("INTEGRACAO COMPLETA FINALIZADA!")
    print("=" * 80)
    print()
    print("Proximo passo: Executar 'python main_ncnt.py' para testar")

if __name__ == "__main__":
    main()

