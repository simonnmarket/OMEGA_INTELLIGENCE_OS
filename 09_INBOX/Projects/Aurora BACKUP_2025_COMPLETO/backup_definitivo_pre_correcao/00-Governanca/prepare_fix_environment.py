"""
PREPARAÇÃO DO AMBIENTE PARA RECEBER ARQUIVO DE CORREÇÃO
AURORA Project v5.0

Prepara métricas, validações e estrutura para receber arquivo de correção.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Módulos com falha - Baseline
FAILED_MODULES_BASELINE = {
    "04-Infraestrutura\\api\\__init__.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error",
        "priority": "medium"
    },
    "04-Infraestrutura\\api\\endpoints\\__init__.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error",
        "priority": "medium"
    },
    "04-Infraestrutura\\api\\endpoints\\strategies.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error",
        "priority": "medium"
    },
    "04-Infraestrutura\\api\\main.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error",
        "priority": "medium"
    },
    "06-Monitoramento\\feedbackloop_module.py": {
        "error": "unterminated string literal (detected at line 477)",
        "type": "syntax_error",
        "line": 477,
        "priority": "low"
    },
    "main_ncnt.py": {
        "error": "unterminated string literal (ncnt_orchestrator_complete.py, line 213)",
        "type": "syntax_error",
        "line": 213,
        "priority": "low"
    },
    "ncnt_system_complete.py": {
        "error": "unterminated string literal (line 7849)",
        "type": "syntax_error",
        "line": 7849,
        "priority": "low"
    },
    "system_core\\ncnt_orchestrator_complete.py": {
        "error": "unterminated string literal (detected at line 213)",
        "type": "syntax_error",
        "line": 213,
        "priority": "low"
    }
}

def calculate_baseline_checksums(project_root: Path) -> Dict[str, str]:
    """Calcula checksums SHA3-256 dos módulos com falha"""
    checksums = {}
    
    for module_path, info in FAILED_MODULES_BASELINE.items():
        full_path = project_root / module_path
        if full_path.exists():
            hasher = hashlib.sha3_256()
            with open(full_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            checksums[module_path] = hasher.hexdigest()
    
    return checksums

def prepare_metrics(project_root: Path) -> Dict[str, Any]:
    """Prepara métricas baseline para comparação"""
    
    # Carregar relatório técnico baseline
    baseline_report_path = project_root / "AURORA_RELATORIO_TECNICO_COMPLETO_20251218_123318.json"
    baseline_data = {}
    
    if baseline_report_path.exists():
        with open(baseline_report_path, 'r', encoding='utf-8') as f:
            baseline_data = json.load(f)
    
    # Calcular checksums dos módulos com falha
    checksums = calculate_baseline_checksums(project_root)
    
    # Preparar métricas
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "project_root": str(project_root),
        "baseline": {
            "total_files": baseline_data.get("files_scanned", 239),
            "modules_operational": baseline_data.get("modules_operational", 231),
            "modules_failed": baseline_data.get("modules_failed", 8),
            "success_rate": (baseline_data.get("modules_operational", 231) / baseline_data.get("files_scanned", 239)) * 100,
            "total_lines_of_code": baseline_data.get("overall_stats", {}).get("total_lines_of_code", 32077),
            "total_classes": baseline_data.get("overall_stats", {}).get("total_classes", 209),
            "total_functions": baseline_data.get("overall_stats", {}).get("total_functions", 69)
        },
        "failed_modules": {
            "count": len(FAILED_MODULES_BASELINE),
            "details": FAILED_MODULES_BASELINE,
            "checksums_before": checksums,
            "by_type": {
                "import_error": sum(1 for m in FAILED_MODULES_BASELINE.values() if m["type"] == "import_error"),
                "syntax_error": sum(1 for m in FAILED_MODULES_BASELINE.values() if m["type"] == "syntax_error")
            },
            "by_priority": {
                "high": sum(1 for m in FAILED_MODULES_BASELINE.values() if m.get("priority") == "high"),
                "medium": sum(1 for m in FAILED_MODULES_BASELINE.values() if m.get("priority") == "medium"),
                "low": sum(1 for m in FAILED_MODULES_BASELINE.values() if m.get("priority") == "low")
            }
        },
        "environment": {
            "backup_directory": str(project_root / "BACKUPS"),
            "temp_directory": str(project_root / "TEMP_FIX_EXTRACT"),
            "processor_script": "00-Governanca\\process_fix_file.py",
            "ready": True
        },
        "expected_improvement": {
            "target_modules_fixed": len(FAILED_MODULES_BASELINE),
            "target_success_rate": 100.0,
            "target_modules_operational": baseline_data.get("modules_operational", 231) + len(FAILED_MODULES_BASELINE),
            "target_modules_failed": 0
        }
    }
    
    return metrics

def create_directories(project_root: Path):
    """Cria diretórios necessários"""
    directories = [
        project_root / "BACKUPS",
        project_root / "TEMP_FIX_EXTRACT"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[PREP] Diretório criado/verificado: {directory}")

def save_preparation_metrics(metrics: Dict[str, Any], project_root: Path) -> Path:
    """Salva métricas de preparação"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_path = project_root / f"AURORA_FIX_PREPARATION_{timestamp}.json"
    
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    return metrics_path

def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent
    
    print("\n" + "="*70)
    print("PREPARAÇÃO DO AMBIENTE - CORREÇÃO DE MÓDULOS COM FALHA")
    print("="*70)
    print(f"Projeto: {project_root}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Criar diretórios
    print("[PREP] Criando diretórios necessários...")
    create_directories(project_root)
    
    # Preparar métricas
    print("[PREP] Preparando métricas baseline...")
    metrics = prepare_metrics(project_root)
    
    # Salvar métricas
    metrics_path = save_preparation_metrics(metrics, project_root)
    
    # Exibir resumo
    print("\n" + "="*70)
    print("MÉTRICAS BASELINE PREPARADAS")
    print("="*70)
    print(f"Total de arquivos: {metrics['baseline']['total_files']}")
    print(f"Módulos operacionais: {metrics['baseline']['modules_operational']}")
    print(f"Módulos com falha: {metrics['baseline']['modules_failed']}")
    print(f"Taxa de sucesso atual: {metrics['baseline']['success_rate']:.2f}%")
    print(f"\nMódulos com falha por tipo:")
    print(f"  - Erros de importação: {metrics['failed_modules']['by_type']['import_error']}")
    print(f"  - Erros de sintaxe: {metrics['failed_modules']['by_type']['syntax_error']}")
    print(f"\nMódulos com falha por prioridade:")
    print(f"  - Alta: {metrics['failed_modules']['by_priority']['high']}")
    print(f"  - Média: {metrics['failed_modules']['by_priority']['medium']}")
    print(f"  - Baixa: {metrics['failed_modules']['by_priority']['low']}")
    print(f"\nMelhoria esperada:")
    print(f"  - Módulos a corrigir: {metrics['expected_improvement']['target_modules_fixed']}")
    print(f"  - Taxa de sucesso alvo: {metrics['expected_improvement']['target_success_rate']:.2f}%")
    print(f"  - Módulos operacionais alvo: {metrics['expected_improvement']['target_modules_operational']}")
    print(f"\nMétricas salvas em: {metrics_path.name}")
    print("="*70)
    print("\n✅ AMBIENTE PREPARADO E PRONTO PARA RECEBER ARQUIVO DE CORREÇÃO")
    print("\nPara processar arquivo de correção, execute:")
    print(f"  python {metrics['environment']['processor_script']} <caminho_do_arquivo>")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

