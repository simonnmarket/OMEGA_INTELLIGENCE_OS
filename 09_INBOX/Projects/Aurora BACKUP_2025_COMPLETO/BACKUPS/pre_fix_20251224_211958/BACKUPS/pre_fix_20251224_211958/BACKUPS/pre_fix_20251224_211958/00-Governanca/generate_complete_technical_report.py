#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO TÉCNICO COMPLETO - AURORA PROJECT
Gera relatório 100% objetivo e verificável
Data: 2025-12-17
"""

import os
import sys
import json
import hashlib
import importlib.util
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

class TechnicalReportGenerator:
    """Gerador de relatório técnico objetivo e verificável"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "files_scanned": 0,
            "modules_tested": 0,
            "modules_operational": 0,
            "modules_failed": 0,
            "files": {},
            "modules": {},
            "classes": {},
            "functions": {},
            "import_errors": [],
            "checksums": {},
            "statistics": {}
        }
        
    def calculate_file_checksum(self, filepath: Path) -> str:
        """Calcula SHA3-256 checksum do arquivo"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            return hashlib.sha3_256(content).hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def count_lines(self, filepath: Path) -> Dict[str, int]:
        """Conta linhas de código, comentários, vazias"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total = len(lines)
            code = 0
            comments = 0
            empty = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    empty += 1
                elif stripped.startswith('#'):
                    comments += 1
                else:
                    code += 1
            
            return {
                "total": total,
                "code": code,
                "comments": comments,
                "empty": empty
            }
        except Exception as e:
            return {"error": str(e)}
    
    def scan_python_files(self) -> List[Path]:
        """Escaneia todos os arquivos Python do projeto"""
        python_files = []
        
        # Diretórios principais
        scan_dirs = [
            "00-Governanca",
            "01-Departamentos",
            "02-Processos-Chave",
            "03-Operacoes-Diarias",
            "04-Infraestrutura",
            "05-Documentacao",
            "06-Monitoramento",
            "modules",
            "wrappers_v2",
            "system_core",
            "scripts"
        ]
        
        # Arquivos raiz
        root_files = [
            "aurora_etapa_a.py",
            "aurora_etapa_b.py",
            "aurora_etapa_c.py",
            "aurora_etapa_d.py",
            "aurora_etapa_e.py",
            "main.py",
            "main_ncnt.py",
            "ncnt_system_complete.py",
            "complete_integration.py",
            "integrate_ncnt.py",
            "ncnt_scan.py",
            "executive_presentation.py",
            "visual_presentation.py",
            "visual_presentation_simple.py"
        ]
        
        for root_file in root_files:
            filepath = self.project_root / root_file
            if filepath.exists():
                python_files.append(filepath)
        
        for scan_dir in scan_dirs:
            dirpath = self.project_root / scan_dir
            if dirpath.exists() and dirpath.is_dir():
                for py_file in dirpath.rglob("*.py"):
                    python_files.append(py_file)
        
        return sorted(set(python_files))
    
    def test_module_import(self, filepath: Path) -> Dict[str, Any]:
        """Testa importação do módulo e extrai informações"""
        result = {
            "filepath": str(filepath),
            "import_status": "NOT_TESTED",
            "import_error": None,
            "module_name": None,
            "classes_found": [],
            "functions_found": [],
            "has_ncnt": False,
            "has_regulatory": False,
            "operational": False
        }
        
        try:
            # Calcular caminho relativo para import
            rel_path = filepath.relative_to(self.project_root)
            module_name = str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')
            
            # Tentar importar
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                result["import_status"] = "FAILED"
                result["import_error"] = "Cannot create spec"
                return result
            
            module = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str(filepath.parent))
            
            try:
                spec.loader.exec_module(module)
                result["import_status"] = "SUCCESS"
                result["module_name"] = module_name
                result["operational"] = True
                
                # Extrair classes
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:
                        result["classes_found"].append({
                            "name": name,
                            "bases": [base.__name__ for base in obj.__bases__],
                            "methods": [m for m in dir(obj) if not m.startswith('_')]
                        })
                        
                        # Verificar se herda de NCNTModule
                        if 'NCNTModule' in [base.__name__ for base in obj.__bases__]:
                            result["has_ncnt"] = True
                
                # Extrair funções
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and obj.__module__ == module_name:
                        result["functions_found"].append(name)
                
                # Verificar RegulatoryContext
                if hasattr(module, 'RegulatoryContext') or 'regulatory' in str(module).lower():
                    result["has_regulatory"] = True
                
            except Exception as e:
                result["import_status"] = "FAILED"
                result["import_error"] = str(e)
                result["traceback"] = traceback.format_exc()
            
            finally:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                if str(filepath.parent) in sys.path:
                    sys.path.remove(str(filepath.parent))
        
        except Exception as e:
            result["import_status"] = "ERROR"
            result["import_error"] = str(e)
        
        return result
    
    def generate_file_report(self, filepath: Path) -> Dict[str, Any]:
        """Gera relatório completo de um arquivo"""
        report = {
            "path": str(filepath.relative_to(self.project_root)),
            "absolute_path": str(filepath),
            "exists": filepath.exists(),
            "size_bytes": 0,
            "checksum_sha3_256": None,
            "lines": None,
            "import_test": None
        }
        
        if not filepath.exists():
            return report
        
        try:
            # Tamanho
            report["size_bytes"] = filepath.stat().st_size
            
            # Checksum
            report["checksum_sha3_256"] = self.calculate_file_checksum(filepath)
            
            # Linhas
            report["lines"] = self.count_lines(filepath)
            
            # Teste de importação
            if filepath.suffix == '.py':
                report["import_test"] = self.test_module_import(filepath)
        
        except Exception as e:
            report["error"] = str(e)
        
        return report
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Gera estatísticas agregadas"""
        stats = {
            "total_files": len(self.results["files"]),
            "total_python_files": 0,
            "total_lines_code": 0,
            "total_lines_comments": 0,
            "total_lines_empty": 0,
            "total_size_bytes": 0,
            "modules_importable": 0,
            "modules_failed_import": 0,
            "classes_total": 0,
            "functions_total": 0,
            "modules_with_ncnt": 0,
            "modules_with_regulatory": 0,
            "operational_modules": 0,
            "non_operational_modules": 0
        }
        
        for filepath, file_data in self.results["files"].items():
            if file_data.get("path", "").endswith('.py'):
                stats["total_python_files"] += 1
            
            if file_data.get("lines"):
                if isinstance(file_data["lines"], dict) and "error" not in file_data["lines"]:
                    stats["total_lines_code"] += file_data["lines"].get("code", 0)
                    stats["total_lines_comments"] += file_data["lines"].get("comments", 0)
                    stats["total_lines_empty"] += file_data["lines"].get("empty", 0)
            
            stats["total_size_bytes"] += file_data.get("size_bytes", 0)
            
            if file_data.get("import_test"):
                import_test = file_data["import_test"]
                if import_test.get("import_status") == "SUCCESS":
                    stats["modules_importable"] += 1
                    stats["operational_modules"] += 1
                else:
                    stats["modules_failed_import"] += 1
                    stats["non_operational_modules"] += 1
                
                if import_test.get("has_ncnt"):
                    stats["modules_with_ncnt"] += 1
                
                if import_test.get("has_regulatory"):
                    stats["modules_with_regulatory"] += 1
                
                stats["classes_total"] += len(import_test.get("classes_found", []))
                stats["functions_total"] += len(import_test.get("functions_found", []))
        
        return stats
    
    def run_full_scan(self):
        """Executa scan completo do projeto"""
        print(f"[SCAN] Iniciando scan completo do projeto...")
        print(f"[SCAN] Project root: {self.project_root}")
        
        # Escanear arquivos
        python_files = self.scan_python_files()
        print(f"[SCAN] Encontrados {len(python_files)} arquivos Python")
        
        # Processar cada arquivo
        for idx, filepath in enumerate(python_files, 1):
            print(f"[SCAN] [{idx}/{len(python_files)}] Processando: {filepath.name}")
            file_report = self.generate_file_report(filepath)
            self.results["files"][str(filepath)] = file_report
            self.results["files_scanned"] += 1
        
        # Gerar estatísticas
        print(f"[SCAN] Gerando estatísticas...")
        self.results["statistics"] = self.generate_statistics()
        
        # Atualizar contadores
        self.results["modules_tested"] = self.results["statistics"]["total_python_files"]
        self.results["modules_operational"] = self.results["statistics"]["modules_importable"]
        self.results["modules_failed"] = self.results["statistics"]["modules_failed_import"]
        
        print(f"[SCAN] Scan completo!")
        print(f"[SCAN] Arquivos processados: {self.results['files_scanned']}")
        print(f"[SCAN] Módulos operacionais: {self.results['modules_operational']}")
        print(f"[SCAN] Módulos com falha: {self.results['modules_failed']}")
    
    def save_json_report(self) -> Path:
        """Salva relatório em JSON"""
        output_file = OUTPUT_DIR / f"AURORA_RELATORIO_TECNICO_COMPLETO_{TIMESTAMP}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] Relatório JSON salvo: {output_file}")
        return output_file
    
    def save_markdown_report(self) -> Path:
        """Salva relatório em Markdown"""
        output_file = OUTPUT_DIR / f"AURORA_RELATORIO_TECNICO_COMPLETO_{TIMESTAMP}.md"
        
        stats = self.results["statistics"]
        
        md_content = f"""# RELATÓRIO TÉCNICO COMPLETO - AURORA PROJECT

**Data de Geração:** {self.results['timestamp']}  
**Project Root:** {self.results['project_root']}  
**Timestamp:** {TIMESTAMP}

---

## RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| **Total de Arquivos Escaneados** | {self.results['files_scanned']} |
| **Arquivos Python** | {stats['total_python_files']} |
| **Módulos Operacionais** | {stats['modules_importable']} |
| **Módulos com Falha de Importação** | {stats['modules_failed_import']} |
| **Taxa de Sucesso** | {(stats['modules_importable'] / stats['total_python_files'] * 100) if stats['total_python_files'] > 0 else 0:.2f}% |
| **Total de Classes** | {stats['classes_total']} |
| **Total de Funções** | {stats['functions_total']} |
| **Módulos com NCNT** | {stats['modules_with_ncnt']} |
| **Módulos com Regulatory** | {stats['modules_with_regulatory']} |
| **Linhas de Código** | {stats['total_lines_code']:,} |
| **Linhas de Comentários** | {stats['total_lines_comments']:,} |
| **Tamanho Total** | {stats['total_size_bytes'] / 1024 / 1024:.2f} MB |

---

## ESTATÍSTICAS DETALHADAS

### Código
- **Linhas de Código:** {stats['total_lines_code']:,}
- **Linhas de Comentários:** {stats['total_lines_comments']:,}
- **Linhas Vazias:** {stats['total_lines_empty']:,}
- **Total de Linhas:** {stats['total_lines_code'] + stats['total_lines_comments'] + stats['total_lines_empty']:,}

### Módulos
- **Módulos Importáveis:** {stats['modules_importable']}
- **Módulos com Falha:** {stats['modules_failed_import']}
- **Taxa de Sucesso:** {(stats['modules_importable'] / stats['total_python_files'] * 100) if stats['total_python_files'] > 0 else 0:.2f}%

### Integração
- **Módulos com NCNT v2.0:** {stats['modules_with_ncnt']}
- **Módulos com RegulatoryContext:** {stats['modules_with_regulatory']}

### Estrutura
- **Total de Classes:** {stats['classes_total']}
- **Total de Funções:** {stats['functions_total']}

---

## ARQUIVOS POR STATUS DE IMPORTAÇÃO

### Módulos Operacionais ({stats['modules_importable']})

"""
        
        # Listar módulos operacionais
        operational_count = 0
        for filepath, file_data in sorted(self.results["files"].items()):
            if file_data.get("import_test") and file_data["import_test"].get("import_status") == "SUCCESS":
                operational_count += 1
                md_content += f"{operational_count}. `{file_data['path']}`\n"
                if file_data["import_test"].get("classes_found"):
                    md_content += f"   - Classes: {', '.join([c['name'] for c in file_data['import_test']['classes_found']])}\n"
                if file_data["import_test"].get("has_ncnt"):
                    md_content += f"   - ✅ NCNT v2.0\n"
                if file_data["import_test"].get("has_regulatory"):
                    md_content += f"   - ✅ RegulatoryContext\n"
        
        md_content += f"\n### Módulos com Falha de Importação ({stats['modules_failed_import']})\n\n"
        
        # Listar módulos com falha
        failed_count = 0
        for filepath, file_data in sorted(self.results["files"].items()):
            if file_data.get("import_test") and file_data["import_test"].get("import_status") != "SUCCESS":
                failed_count += 1
                error = file_data["import_test"].get("import_error", "Unknown error")
                md_content += f"{failed_count}. `{file_data['path']}`\n"
                md_content += f"   - ❌ Erro: {error[:100]}\n"
        
        md_content += f"\n---\n\n## CHECKSUMS SHA3-256\n\n"
        md_content += "| Arquivo | Checksum |\n"
        md_content += "|---------|----------|\n"
        
        # Listar checksums (primeiros 20)
        checksum_count = 0
        for filepath, file_data in sorted(self.results["files"].items()):
            if file_data.get("checksum_sha3_256") and checksum_count < 20:
                checksum_count += 1
                checksum = file_data["checksum_sha3_256"]
                if len(checksum) > 16:
                    checksum = checksum[:16] + "..."
                md_content += f"| `{file_data['path']}` | `{checksum}` |\n"
        
        if checksum_count >= 20:
            md_content += f"\n*... e mais {len(self.results['files']) - 20} arquivos*\n"
        
        md_content += f"\n---\n\n## DADOS COMPLETOS\n\n"
        md_content += "Para dados completos e verificáveis, consulte o arquivo JSON:\n"
        md_content += f"`AURORA_RELATORIO_TECNICO_COMPLETO_{TIMESTAMP}.json`\n"
        
        md_content += f"\n---\n\n**Relatório gerado automaticamente em {self.results['timestamp']}**\n"
        md_content += f"**Total de arquivos processados: {self.results['files_scanned']}**\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"[SAVE] Relatório Markdown salvo: {output_file}")
        return output_file

def main():
    """Função principal"""
    print("=" * 70)
    print("AURORA PROJECT - RELATÓRIO TÉCNICO COMPLETO")
    print("=" * 70)
    print()
    
    generator = TechnicalReportGenerator()
    
    try:
        generator.run_full_scan()
        json_file = generator.save_json_report()
        md_file = generator.save_markdown_report()
        
        print()
        print("=" * 70)
        print("RELATÓRIO GERADO COM SUCESSO")
        print("=" * 70)
        print(f"JSON: {json_file.name}")
        print(f"Markdown: {md_file.name}")
        print()
        print("ESTATÍSTICAS FINAIS:")
        stats = generator.results["statistics"]
        print(f"  - Arquivos Python: {stats['total_python_files']}")
        print(f"  - Módulos Operacionais: {stats['modules_importable']}")
        print(f"  - Módulos com Falha: {stats['modules_failed_import']}")
        print(f"  - Taxa de Sucesso: {(stats['modules_importable'] / stats['total_python_files'] * 100) if stats['total_python_files'] > 0 else 0:.2f}%")
        print(f"  - Linhas de Código: {stats['total_lines_code']:,}")
        print(f"  - Classes: {stats['classes_total']}")
        print(f"  - Funções: {stats['functions_total']}")
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] Erro ao gerar relatório: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

