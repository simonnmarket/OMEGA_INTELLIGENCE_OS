"""
PROCESSADOR DE ARQUIVO DE CORREÇÃO - MÓDULOS COM FALHA
AURORA Project v5.0

Este script recebe e processa arquivo de correção para os 8 módulos com falha.
Valida checksum, aplica correções, testa módulos e gera relatório.
"""

import os
import sys
import json
import hashlib
import importlib.util
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Módulos com falha identificados
FAILED_MODULES = {
    "04-Infraestrutura\\api\\__init__.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error"
    },
    "04-Infraestrutura\\api\\endpoints\\__init__.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error"
    },
    "04-Infraestrutura\\api\\endpoints\\strategies.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error"
    },
    "04-Infraestrutura\\api\\main.py": {
        "error": "No module named '04-Infraestrutura.api.database'",
        "type": "import_error"
    },
    "06-Monitoramento\\feedbackloop_module.py": {
        "error": "unterminated string literal (detected at line 477)",
        "type": "syntax_error",
        "line": 477
    },
    "main_ncnt.py": {
        "error": "unterminated string literal (ncnt_orchestrator_complete.py, line 213)",
        "type": "syntax_error",
        "line": 213
    },
    "ncnt_system_complete.py": {
        "error": "unterminated string literal (line 7849)",
        "type": "syntax_error",
        "line": 7849
    },
    "system_core\\ncnt_orchestrator_complete.py": {
        "error": "unterminated string literal (detected at line 213)",
        "type": "syntax_error",
        "line": 213
    }
}

class FixFileProcessor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.baseline_report = self._load_baseline_report()
        self.metrics = {
            "timestamp_start": datetime.now().isoformat(),
            "files_received": 0,
            "files_validated": 0,
            "files_processed": 0,
            "modules_tested": 0,
            "modules_fixed": 0,
            "modules_still_failing": 0,
            "checksums_validated": [],
            "backups_created": [],
            "errors": []
        }
        
    def _load_baseline_report(self) -> Dict[str, Any]:
        """Carrega relatório técnico baseline para comparação"""
        report_path = self.project_root / "AURORA_RELATORIO_TECNICO_COMPLETO_20251218_123318.json"
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _calculate_file_checksum(self, filepath: Path) -> str:
        """Calcula checksum SHA3-256 do arquivo"""
        hasher = hashlib.sha3_256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _backup_file(self, filepath: Path) -> Path:
        """Cria backup do arquivo antes de aplicar correção"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / "BACKUPS" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        relative_path = filepath.relative_to(self.project_root)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(filepath, backup_path)
        logger.info(f"[BACKUP] Criado: {backup_path}")
        self.metrics["backups_created"].append(str(backup_path))
        return backup_path
    
    def _test_module_import(self, filepath: Path) -> Dict[str, Any]:
        """Testa importação do módulo"""
        module_name = str(filepath.relative_to(self.project_root)).replace(os.sep, '.')[:-3]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        
        if spec is None:
            return {
                "import_status": "FAILED",
                "import_error": "Could not create module spec",
                "operational": False
            }
        
        module = None
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            return {
                "import_status": "SUCCESS",
                "import_error": None,
                "module_name": module_name,
                "operational": True
            }
        except Exception as e:
            return {
                "import_status": "FAILED",
                "import_error": str(e),
                "operational": False
            }
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]
    
    def validate_fix_file(self, fix_file_path: Path) -> Dict[str, Any]:
        """Valida arquivo de correção recebido"""
        logger.info(f"[VALIDATE] Validando arquivo: {fix_file_path}")
        
        if not fix_file_path.exists():
            return {
                "valid": False,
                "error": f"Arquivo não encontrado: {fix_file_path}"
            }
        
        # Calcular checksum
        checksum = self._calculate_file_checksum(fix_file_path)
        file_size = fix_file_path.stat().st_size
        
        # Verificar extensão
        if fix_file_path.suffix not in ['.py', '.zip', '.json', '.txt']:
            return {
                "valid": False,
                "error": f"Extensão não suportada: {fix_file_path.suffix}"
            }
        
        validation_result = {
            "valid": True,
            "filepath": str(fix_file_path),
            "filename": fix_file_path.name,
            "size_bytes": file_size,
            "checksum_sha3_256": checksum,
            "extension": fix_file_path.suffix,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics["files_received"] += 1
        self.metrics["files_validated"] += 1
        self.metrics["checksums_validated"].append({
            "file": fix_file_path.name,
            "checksum": checksum
        })
        
        logger.info(f"[VALIDATE] Arquivo validado: {fix_file_path.name} ({file_size} bytes)")
        return validation_result
    
    def process_fix_file(self, fix_file_path: Path) -> Dict[str, Any]:
        """Processa arquivo de correção"""
        logger.info(f"[PROCESS] Processando arquivo de correção: {fix_file_path}")
        
        validation = self.validate_fix_file(fix_file_path)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation.get("error", "Validação falhou")
            }
        
        # Se for arquivo Python único, aplicar diretamente
        if fix_file_path.suffix == '.py':
            return self._process_single_python_file(fix_file_path)
        
        # Se for ZIP, extrair e processar
        elif fix_file_path.suffix == '.zip':
            return self._process_zip_file(fix_file_path)
        
        # Se for JSON, processar como lista de correções
        elif fix_file_path.suffix == '.json':
            return self._process_json_fixes(fix_file_path)
        
        else:
            return {
                "success": False,
                "error": f"Tipo de arquivo não suportado: {fix_file_path.suffix}"
            }
    
    def _process_single_python_file(self, filepath: Path) -> Dict[str, Any]:
        """Processa arquivo Python único"""
        # Identificar qual módulo está sendo corrigido pelo nome do arquivo
        filename = filepath.name
        
        # Tentar mapear para módulo com falha
        target_module = None
        for module_path in FAILED_MODULES.keys():
            if filename in module_path or Path(module_path).name == filename:
                target_module = module_path
                break
        
        if not target_module:
            return {
                "success": False,
                "error": f"Não foi possível identificar módulo alvo para: {filename}"
            }
        
        target_path = self.project_root / target_module
        if not target_path.exists():
            return {
                "success": False,
                "error": f"Módulo alvo não encontrado: {target_path}"
            }
        
        # Criar backup
        self._backup_file(target_path)
        
        # Copiar arquivo corrigido
        shutil.copy2(filepath, target_path)
        logger.info(f"[FIX] Arquivo corrigido aplicado: {target_path}")
        
        # Testar módulo
        test_result = self._test_module_import(target_path)
        self.metrics["modules_tested"] += 1
        
        if test_result["operational"]:
            self.metrics["modules_fixed"] += 1
            logger.info(f"[SUCCESS] Módulo corrigido: {target_module}")
        else:
            self.metrics["modules_still_failing"] += 1
            logger.warning(f"[FAIL] Módulo ainda com falha: {target_module} - {test_result['import_error']}")
        
        return {
            "success": test_result["operational"],
            "module": target_module,
            "test_result": test_result
        }
    
    def _process_zip_file(self, zip_path: Path) -> Dict[str, Any]:
        """Processa arquivo ZIP com múltiplas correções"""
        import zipfile
        
        results = []
        extract_dir = self.project_root / "TEMP_FIX_EXTRACT"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Processar cada arquivo extraído
            for extracted_file in extract_dir.rglob('*.py'):
                result = self._process_single_python_file(extracted_file)
                results.append(result)
            
            # Limpar diretório temporário
            shutil.rmtree(extract_dir)
            
            fixed_count = sum(1 for r in results if r.get("success", False))
            
            return {
                "success": fixed_count > 0,
                "files_processed": len(results),
                "files_fixed": fixed_count,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar ZIP: {str(e)}"
            }
    
    def _process_json_fixes(self, json_path: Path) -> Dict[str, Any]:
        """Processa arquivo JSON com correções"""
        with open(json_path, 'r', encoding='utf-8') as f:
            fixes_data = json.load(f)
        
        results = []
        
        # Processar cada correção no JSON
        for fix_entry in fixes_data.get("fixes", []):
            module_path = fix_entry.get("module")
            fix_content = fix_entry.get("content")
            
            if not module_path or not fix_content:
                continue
            
            target_path = self.project_root / module_path
            if not target_path.exists():
                logger.warning(f"[SKIP] Módulo não encontrado: {target_path}")
                continue
            
            # Criar backup
            self._backup_file(target_path)
            
            # Aplicar correção
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(fix_content)
            
            # Testar
            test_result = self._test_module_import(target_path)
            self.metrics["modules_tested"] += 1
            
            if test_result["operational"]:
                self.metrics["modules_fixed"] += 1
                results.append({
                    "success": True,
                    "module": module_path,
                    "test_result": test_result
                })
            else:
                self.metrics["modules_still_failing"] += 1
                results.append({
                    "success": False,
                    "module": module_path,
                    "test_result": test_result
                })
        
        fixed_count = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": fixed_count > 0,
            "files_processed": len(results),
            "files_fixed": fixed_count,
            "results": results
        }
    
    def generate_fix_report(self) -> Dict[str, Any]:
        """Gera relatório de correções aplicadas"""
        self.metrics["timestamp_end"] = datetime.now().isoformat()
        
        # Comparar com baseline
        baseline_operational = self.baseline_report.get("modules_operational", 231)
        baseline_failed = self.baseline_report.get("modules_failed", 8)
        
        new_operational = baseline_operational + self.metrics["modules_fixed"]
        new_failed = baseline_failed - self.metrics["modules_fixed"]
        
        report = {
            "fix_session": {
                "timestamp_start": self.metrics["timestamp_start"],
                "timestamp_end": self.metrics["timestamp_end"],
                "baseline": {
                    "modules_operational": baseline_operational,
                    "modules_failed": baseline_failed,
                    "success_rate": (baseline_operational / 239) * 100
                },
                "after_fix": {
                    "modules_operational": new_operational,
                    "modules_failed": new_failed,
                    "success_rate": (new_operational / 239) * 100
                },
                "improvement": {
                    "modules_fixed": self.metrics["modules_fixed"],
                    "success_rate_delta": ((new_operational / 239) * 100) - ((baseline_operational / 239) * 100)
                }
            },
            "metrics": self.metrics,
            "status": "SUCCESS" if self.metrics["modules_fixed"] > 0 else "NO_CHANGES"
        }
        
        return report
    
    def save_fix_report(self, report: Dict[str, Any]) -> Path:
        """Salva relatório de correções"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.project_root / f"AURORA_FIX_REPORT_{timestamp}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[REPORT] Relatório salvo: {report_path}")
        return report_path


def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent
    
    print("\n" + "="*70)
    print("PROCESSADOR DE ARQUIVO DE CORREÇÃO - AURORA v5.0")
    print("="*70)
    print(f"Projeto: {project_root}")
    print(f"Módulos com falha: {len(FAILED_MODULES)}")
    print("="*70 + "\n")
    
    # Verificar se arquivo foi passado como argumento
    if len(sys.argv) < 2:
        print("USO: python process_fix_file.py <caminho_do_arquivo>")
        print("\nExemplos:")
        print("  python process_fix_file.py fix_module.py")
        print("  python process_fix_file.py fixes.zip")
        print("  python process_fix_file.py fixes.json")
        return
    
    fix_file_path = Path(sys.argv[1])
    if not fix_file_path.is_absolute():
        fix_file_path = project_root / fix_file_path
    
    processor = FixFileProcessor(str(project_root))
    
    # Processar arquivo
    result = processor.process_fix_file(fix_file_path)
    
    # Gerar relatório
    report = processor.generate_fix_report()
    report_path = processor.save_fix_report(report)
    
    # Exibir resultados
    print("\n" + "="*70)
    print("RESULTADO DO PROCESSAMENTO")
    print("="*70)
    print(f"Arquivo processado: {fix_file_path.name}")
    print(f"Módulos testados: {processor.metrics['modules_tested']}")
    print(f"Módulos corrigidos: {processor.metrics['modules_fixed']}")
    print(f"Módulos ainda com falha: {processor.metrics['modules_still_failing']}")
    print(f"\nTaxa de sucesso ANTES: {report['fix_session']['baseline']['success_rate']:.2f}%")
    print(f"Taxa de sucesso DEPOIS: {report['fix_session']['after_fix']['success_rate']:.2f}%")
    print(f"Melhoria: +{report['fix_session']['improvement']['success_rate_delta']:.2f}%")
    print(f"\nRelatório salvo: {report_path.name}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

