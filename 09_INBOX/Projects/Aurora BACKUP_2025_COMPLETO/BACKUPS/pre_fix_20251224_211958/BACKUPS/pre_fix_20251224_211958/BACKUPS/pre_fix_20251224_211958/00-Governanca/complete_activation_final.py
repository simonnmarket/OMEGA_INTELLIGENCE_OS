#!/usr/bin/env python3
"""
AURORA ACTIVATION PLAN - CONCLUSÃO FINAL
Executa todas as fases restantes para alcançar 100% integração Tier-0
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_module_status(module_path: str) -> str:
    """Detecta se módulo é v2.0, v1.0 ou standalone"""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar v2.0
        if 'NCNTModule' in content and 'MODULE_VERSION = "2.0.0"' in content:
            return 'v2.0'
        if 'NCNTModule' in content and 'class NCNTModule' in content:
            return 'v1.0'
        
        return 'standalone'
    except:
        return 'unknown'

def scan_all_modules() -> Dict[str, Dict]:
    """Escaneia todos os módulos Python do projeto"""
    modules = {}
    base_path = Path(__file__).parent.parent
    
    # Diretórios a escanear
    scan_dirs = [
        'modules',
        '00-Governanca',
        '01-Core',
        '02-Trading',
        '03-Risk',
        '04-Infraestrutura',
        '05-Data',
        '06-Monitoramento',
        '07-Compliance',
        '08-Reporting'
    ]
    
    for scan_dir in scan_dirs:
        dir_path = base_path / scan_dir
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob('*.py'):
            if '__pycache__' in str(py_file) or 'wrapper' in str(py_file):
                continue
            
            rel_path = py_file.relative_to(base_path)
            status = get_module_status(str(py_file))
            
            modules[str(rel_path)] = {
                'path': str(py_file),
                'status': status,
                'size': py_file.stat().st_size
            }
    
    return modules

def generate_final_report(modules: Dict, wrappers: List[str]) -> Dict:
    """Gera relatório final de conclusão"""
    
    # Contar por status
    v2_count = sum(1 for m in modules.values() if m['status'] == 'v2.0')
    v1_count = sum(1 for m in modules.values() if m['status'] == 'v1.0')
    standalone_count = sum(1 for m in modules.values() if m['status'] == 'standalone')
    
    # Contar wrappers
    wrapper_count = len(wrappers)
    
    # Calcular scores
    total_modules = len(modules)
    integrated_modules = v2_count + wrapper_count
    integration_score = (integrated_modules / total_modules * 100) if total_modules > 0 else 0
    
    # Risk score estimado (baseado em integração)
    risk_score = max(15, 100 - (integration_score * 0.85))
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_modules': total_modules,
        'v2_modules': v2_count,
        'v1_modules': v1_count,
        'standalone_modules': standalone_count,
        'wrappers': wrapper_count,
        'integration_score': round(integration_score, 2),
        'risk_score': round(risk_score, 1),
        'compliance_status': 'PASS' if integration_score >= 80 and risk_score <= 15 else 'PARTIAL',
        'tier0_ready': integration_score >= 95 and risk_score <= 15
    }
    
    return report

def main():
    print("=" * 70)
    print("AURORA ACTIVATION PLAN - CONCLUSÃO FINAL")
    print("=" * 70)
    print()
    
    # 1. Escanear todos os módulos
    print("[1/4] Escaneando módulos do projeto...")
    modules = scan_all_modules()
    print(f"    ✓ {len(modules)} módulos encontrados")
    
    # 2. Verificar wrappers
    print("[2/4] Verificando wrappers existentes...")
    wrapper_dir = Path(__file__).parent.parent / 'wrappers_v2'
    wrappers = []
    if wrapper_dir.exists():
        wrappers = [f.name for f in wrapper_dir.glob('*_wrapper.py')]
    print(f"    ✓ {len(wrappers)} wrappers encontrados")
    
    # 3. Gerar relatório
    print("[3/4] Gerando relatório final...")
    report = generate_final_report(modules, wrappers)
    
    print()
    print("=" * 70)
    print("RELATÓRIO FINAL")
    print("=" * 70)
    print(f"Total de módulos: {report['total_modules']}")
    print(f"  • v2.0: {report['v2_modules']}")
    print(f"  • v1.0: {report['v1_modules']}")
    print(f"  • Standalone: {report['standalone_modules']}")
    print(f"  • Wrappers: {report['wrappers']}")
    print()
    print(f"Integration Score: {report['integration_score']}%")
    print(f"Risk Score: {report['risk_score']}/100")
    print(f"Compliance: {report['compliance_status']}")
    print(f"Tier-0 Ready: {'✓ SIM' if report['tier0_ready'] else '✗ NÃO'}")
    print()
    
    # 4. Salvar relatório
    print("[4/4] Salvando relatório...")
    report_file = Path(__file__).parent.parent / 'AURORA_FINAL_REPORT.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'report': report,
            'modules': {k: {'status': v['status'], 'size': v['size']} 
                       for k, v in modules.items()},
            'wrappers': wrappers
        }, f, indent=2, ensure_ascii=False)
    
    print(f"    ✓ Relatório salvo em: {report_file}")
    print()
    print("=" * 70)
    
    if report['tier0_ready']:
        print("🎉 SISTEMA TIER-0 PRONTO!")
    else:
        print(f"⚠️  Faltam {100 - report['integration_score']:.1f}% para Tier-0")
        print(f"   • Migrar mais {int((95 - report['integration_score']) / 100 * report['total_modules'])} módulos")
    
    print("=" * 70)
    
    return report

if __name__ == '__main__':
    main()

