#!/usr/bin/env python3
"""
Script de Integração Completa NCNT
Extrai e organiza todos os módulos do arquivo completo
"""

import re
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).parent
SOURCE_FILE = BASE_DIR / "ncnt_system_complete.py"

# Mapeamento de classes para pastas
MODULE_MAPPING = {
    "ModuleType": "modules",
    "AssetClass": "modules",
    "TransmissionPriority": "modules",
    "NCNTTransmission": "modules",
    "NCNTBaseModule": "modules",
    "GovernanceModule": "00-Governanca",
    "TreasuryModule": "01-Departamentos/Treasury-Capital",
    "CapitalAllocation": "01-Departamentos/Treasury-Capital",
    "CoreEngineModule": "01-Departamentos/Engineering-Infra",
    "StrategyModule": "01-Departamentos/Execution-Trading",
    "RiskModule": "01-Departamentos/Risk-Controls",
    "ComplianceModule": "01-Departamentos/Compliance-Audit",
    "InnovationLabModule": "01-Departamentos/Innovation-Lab",
    "CICDPipelineModule": "02-Processos-Chave/CI-CD",
    "QABacktestingModule": "02-Processos-Chave/QA-Backtesting",
    "OnboardingModule": "02-Processos-Chave/Onboarding",
    "IncidentResponseModule": "02-Processos-Chave/Incident-Response",
    "PreMarketChecklistModule": "03-Operacoes-Diarias/Pre-Market",
    "ExecutionWindowModule": "03-Operacoes-Diarias/Execution-Window",
    "RealTimeDashboardModule": "03-Operacoes-Diarias/Real-Time-Dashboard",
    "PostTradeReconciliationModule": "03-Operacoes-Diarias/Post-Trade",
    "ModuleRegistry": "04-Infraestrutura",
    "SOPsModule": "05-Documentacao",
    "FeedbackLoopModule": "06-Monitoramento",
    "NCNTOrchestrator": "system_core",
}

def extract_class_content(content: str, class_name: str) -> Tuple[str, int, int]:
    """Extrair conteúdo de uma classe do arquivo"""
    pattern = rf'^class {class_name}\(.*?\):'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        return None, 0, 0
    
    start = match.start()
    
    # Encontrar fim da classe (próxima classe ou fim do arquivo)
    next_class_pattern = r'^class [A-Z]\w+\(|^if __name__'
    next_match = re.search(next_class_pattern, content[start+1:], re.MULTILINE)
    
    if next_match:
        end = start + next_match.start()
    else:
        end = len(content)
    
    class_content = content[start:end].strip()
    return class_content, start, end

def extract_imports_and_enums(content: str) -> str:
    """Extrair imports e enums do início do arquivo"""
    # Encontrar onde começa a primeira classe
    first_class = re.search(r'^class [A-Z]', content, re.MULTILINE)
    if first_class:
        return content[:first_class.start()].strip()
    return ""

def main():
    print("=" * 80)
    print("INTEGRAÇÃO COMPLETA NCNT - AURORA")
    print("=" * 80)
    print()
    
    if not SOURCE_FILE.exists():
        print(f"ERRO: Arquivo não encontrado: {SOURCE_FILE}")
        return
    
    print(f"Lendo arquivo: {SOURCE_FILE}")
    content = SOURCE_FILE.read_text(encoding='utf-8')
    print(f"Tamanho: {len(content)} caracteres")
    print()
    
    # 1. Criar módulo base com imports, enums e base classes
    print("1. Criando módulo base (modules/ncnt_base.py)...")
    base_content = extract_imports_and_enums(content)
    
    # Adicionar classes base
    base_classes = ["ModuleType", "AssetClass", "TransmissionPriority", "NCNTTransmission", "NCNTBaseModule"]
    for cls_name in base_classes:
        cls_content, _, _ = extract_class_content(content, cls_name)
        if cls_content:
            base_content += "\n\n" + cls_content
    
    base_file = BASE_DIR / "modules" / "ncnt_base.py"
    base_file.parent.mkdir(parents=True, exist_ok=True)
    base_file.write_text(base_content, encoding='utf-8')
    print(f"   [OK] Criado: {base_file}")
    print()
    
    # 2. Extrair e criar cada módulo
    print("2. Extraindo módulos individuais...")
    created_modules = []
    
    for class_name, folder_path in MODULE_MAPPING.items():
        if class_name in ["ModuleType", "AssetClass", "TransmissionPriority", "NCNTTransmission", "NCNTBaseModule"]:
            continue  # Já incluído no base
        
        print(f"   Processando: {class_name} -> {folder_path}/")
        cls_content, _, _ = extract_class_content(content, class_name)
        
        if not cls_content:
            print(f"      [WARN] Classe nao encontrada: {class_name}")
            continue
        
        # Criar arquivo do módulo
        folder = BASE_DIR / folder_path
        folder.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo baseado no nome da classe
        file_name = f"{class_name.lower().replace('module', '_module')}.py"
        if file_name.startswith("_"):
            file_name = file_name[1:]
        
        module_file = folder / file_name
        
        # Criar conteúdo do módulo com imports corretos
        module_code = f'''#!/usr/bin/env python3
"""
{class_name} - Módulo NCNT
Extraído do sistema completo NCNT v2.0
"""

import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ncnt_base import (
    ModuleType,
    AssetClass,
    TransmissionPriority,
    NCNTTransmission,
    NCNTBaseModule
)
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import hashlib
import uuid
from pathlib import Path
import logging
import asyncio
from abc import ABC, abstractmethod
import pickle
import csv
from decimal import Decimal

{cls_content}
'''
        
        module_file.write_text(module_code, encoding='utf-8')
        created_modules.append((class_name, module_file))
        print(f"      [OK] Criado: {module_file}")
    
    print()
    print("=" * 80)
    print(f"INTEGRAÇÃO CONCLUÍDA!")
    print(f"Total de módulos criados: {len(created_modules)}")
    print("=" * 80)

if __name__ == "__main__":
    main()

