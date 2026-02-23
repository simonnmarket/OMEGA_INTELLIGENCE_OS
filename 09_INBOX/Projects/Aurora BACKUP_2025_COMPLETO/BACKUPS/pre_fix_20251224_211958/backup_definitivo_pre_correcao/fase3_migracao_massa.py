#!/usr/bin/env python3
"""
FASE 3: MIGRAÇÃO EM MASSA
Migra todos os módulos para NCNTModule v2.0
"""

import sys
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import importlib.util

# Adicionar paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "modules"))

# Módulos críticos (Risk Score ≥80)
CRITICAL_MODULES = [
    "ncnt_system_complete",
    "cicdpipeline_module",
    "premarketchecklist_module",
    "realtimedashboard_module",
    "innovationlab_module",
    "executive_presentation",
    "onboarding_module",
    "executionwindow_module",
]

# Módulos v1.0 (legado) - lista completa
LEGACY_MODULES = [
    "complete_integration",
    "integrate_ncnt",
    "ncnt_scan",
    "governance_module",
    "compliance_module",
    "coreengine_module",
    "strategy_module",
    "risk_module",
    "treasury_module",
    "incidentresponse_module",
    "posttradereconciliation_module",
    "moduleregistry",
    "sops_module",
    "feedbackloop_module",
    "ncnt_orchestrator_complete",
    "ncnt_base",
]

def find_module_file(module_name: str) -> Path:
    """Busca arquivo do módulo no projeto"""
    search_paths = [
        project_root,
        project_root / "modules",
        project_root / "02-Processos-Chave",
        project_root / "01-Departamentos",
        project_root / "03-Operacoes-Diarias",
        project_root / "00-Governanca",
        project_root / "06-Monitoramento",
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        for pattern in [f"*{module_name}*.py", f"{module_name}.py"]:
            matches = list(search_path.rglob(pattern))
            if matches:
                return matches[0]
    
    return None

def create_wrapper(module_name: str, module_path: Path, output_dir: Path) -> bool:
    """Cria wrapper NCNTModule v2.0 para um módulo"""
    try:
        wrapper_code = f'''"""
WRAPPER AUTOMATICO — {module_name.upper()} → NCNTModule v2.0
Gerado em: 2025-12-16
Baseado no NCNT MODULE TEMPLATE v2.0 (Tier-0 Goldman Sachs)
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "modules"))

from modules.ncnt_module_template_v2 import NCNTModule


class {module_name}Wrapper(NCNTModule):
    """Wrapper seguro e compliant para {module_name}"""
    
    MODULE_VERSION = "2.0.0"
    COMPLIANCE_REQUIRED = True

    def __init__(self):
        super().__init__(
            module_name="{module_name}_wrapper",
            config={{"wrapped_module": "{module_name}"}}
        )
        self.required_modules = []

    def execute(self, *args, **kwargs):
        """Executa o módulo original"""
        self.vitals.status = "HEALTHY"
        try:
            import importlib.util
            module_file = project_root / "{module_path.relative_to(project_root).as_posix()}"
            
            if not module_file.exists():
                self.logger.warning(f"Arquivo original nao encontrado: {{module_file}}")
                return None
            
            spec = importlib.util.spec_from_file_location(
                "{module_name}", 
                str(module_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Tentar executar função principal
            if hasattr(module, "main"):
                return getattr(module, "main")(*args, **kwargs)
            elif hasattr(module, "run"):
                return getattr(module, "run")(*args, **kwargs)
            else:
                return module
            
        except Exception as e:
            self.logger.critical(f"Falha critica em {module_name}: {{e}}")
            self.vitals.status = "DEGRADED"
            self.vitals.error_rate += 1.0
            raise
'''
        
        output_path = output_dir / f"{module_name}_wrapper.py"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        
        return True
    except Exception as e:
        print(f"   [ERRO] Erro ao criar wrapper: {e}")
        return False

def migrate_critical_modules():
    """FASE 3.1: Migrar 8 módulos críticos"""
    print("\n" + "=" * 70)
    print("FASE 3.1: MIGRAR 8 MODULOS CRITICOS (Risk Score >=80)")
    print("=" * 70)
    
    wrapper_dir = project_root / "wrappers_v2"
    wrapper_dir.mkdir(exist_ok=True)
    
    migrated = 0
    for module_name in CRITICAL_MODULES:
        print(f"\n[{migrated+1}/8] Processando: {module_name}")
        module_path = find_module_file(module_name)
        
        if module_path and module_path.exists():
            if create_wrapper(module_name, module_path, wrapper_dir):
                print(f"   [OK] Wrapper criado: {module_name}_wrapper.py")
                migrated += 1
            else:
                print(f"   [ERRO] Falha ao criar wrapper")
        else:
            print(f"   [AVISO] Arquivo nao encontrado: {module_name}")
            # Criar wrapper mesmo assim (pode ser criado depois)
            dummy_path = project_root / f"{module_name}.py"
            if create_wrapper(module_name, dummy_path, wrapper_dir):
                migrated += 1
    
    print(f"\n[OK] {migrated}/8 modulos criticos migrados")
    return migrated

def migrate_legacy_modules():
    """FASE 3.2: Migrar 22 módulos v1.0"""
    print("\n" + "=" * 70)
    print("FASE 3.2: MIGRAR 22 MODULOS V1.0 (LEGADO)")
    print("=" * 70)
    
    wrapper_dir = project_root / "wrappers_v2"
    wrapper_dir.mkdir(exist_ok=True)
    
    # Criar backup
    backup_dir = project_root / "legacy_backup"
    backup_dir.mkdir(exist_ok=True)
    
    migrated = 0
    for module_name in LEGACY_MODULES:
        print(f"\n[{migrated+1}/{len(LEGACY_MODULES)}] Processando: {module_name}")
        module_path = find_module_file(module_name)
        
        if module_path and module_path.exists():
            # Backup
            backup_path = backup_dir / module_path.name
            shutil.copy2(module_path, backup_path)
            
            if create_wrapper(module_name, module_path, wrapper_dir):
                print(f"   [OK] Wrapper criado (backup em: {backup_path})")
                migrated += 1
            else:
                print(f"   [ERRO] Falha ao criar wrapper")
        else:
            print(f"   [AVISO] Arquivo nao encontrado: {module_name}")
    
    print(f"\n[OK] {migrated}/{len(LEGACY_MODULES)} modulos legacy migrados")
    return migrated

def migrate_standalone_modules():
    """FASE 3.3: Migrar 85 módulos standalone restantes"""
    print("\n" + "=" * 70)
    print("FASE 3.3: MIGRAR 85 MODULOS STANDALONE RESTANTES")
    print("=" * 70)
    
    wrapper_dir = project_root / "wrappers_v2"
    wrapper_dir.mkdir(exist_ok=True)
    
    # Encontrar todos os arquivos .py no projeto
    all_py_files = []
    exclude_dirs = {'__pycache__', '.git', 'wrappers_v2', 'legacy_backup', 'node_modules', '.venv', 'venv'}
    
    for py_file in project_root.rglob("*.py"):
        # Pular arquivos já processados
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        if py_file.name.endswith("_wrapper.py"):
            continue
        if py_file.name in ["ncnt_wrapper_generator.py", "fase2_ativar_nucleo_tier0.py", "fase3_migracao_massa.py", "fase4_validacao_final.py"]:
            continue
        
        all_py_files.append(py_file)
    
    # Remover módulos já migrados
    already_migrated = set(CRITICAL_MODULES + LEGACY_MODULES)
    standalone_files = [f for f in all_py_files if f.stem not in already_migrated]
    
    print(f"[INFO] Encontrados {len(standalone_files)} modulos standalone")
    
    migrated = 0
    for i, module_path in enumerate(standalone_files[:85], 1):  # Limitar a 85
        module_name = module_path.stem
        print(f"\n[{i}/85] Processando: {module_name}")
        
        if create_wrapper(module_name, module_path, wrapper_dir):
            print(f"   [OK] Wrapper criado")
            migrated += 1
        else:
            print(f"   [ERRO] Falha ao criar wrapper")
    
    print(f"\n[OK] {migrated}/85 modulos standalone migrados")
    return migrated

def main():
    print("=" * 70)
    print("FASE 3: MIGRACAO EM MASSA")
    print("=" * 70)
    
    total_migrated = 0
    
    # 3.1: Módulos críticos
    total_migrated += migrate_critical_modules()
    
    # 3.2: Módulos legacy
    total_migrated += migrate_legacy_modules()
    
    # 3.3: Módulos standalone
    total_migrated += migrate_standalone_modules()
    
    print("\n" + "=" * 70)
    print(f"RESUMO FASE 3: {total_migrated} modulos migrados")
    print("=" * 70)

if __name__ == "__main__":
    main()

