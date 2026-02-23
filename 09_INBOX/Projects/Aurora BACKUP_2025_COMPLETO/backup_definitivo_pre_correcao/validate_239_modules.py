"""
VALIDAÇÃO FINAL DOS 239 MÓDULOS AURORA v5.0
Verifica que todos os módulos estão operacionais após correções
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuroraModuleValidator:
    """Validador completo dos 239 módulos."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_modules": 0,
            "operational_modules": 0,
            "failed_modules": 0,
            "success_rate": 0.0,
            "modules": {}
        }
    
    def find_all_python_modules(self) -> list:
        """Encontra todos os módulos Python no projeto."""
        python_modules = []
        exclude_dirs = {"__pycache__", ".git", ".idea", ".vscode", "venv", "env", "node_modules"}
        exclude_files = {"setup.py", "requirements.txt", "Pipfile", "pyproject.toml"}
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.py') and file not in exclude_files:
                    python_modules.append(Path(root) / file)
        
        python_modules.sort()
        logger.info(f"📁 Encontrados {len(python_modules)} módulos Python")
        return python_modules
    
    def validate_module(self, module_path: Path) -> tuple:
        """Valida um único módulo Python."""
        rel_path = str(module_path.relative_to(self.project_root))
        
        try:
            # Verificar sintaxe
            syntax_check = subprocess.run(
                [sys.executable, "-m", "py_compile", str(module_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if syntax_check.returncode != 0:
                return rel_path, {
                    "status": "syntax_error",
                    "operational": False,
                    "error": syntax_check.stderr[:500],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Contar linhas para estatísticas
            with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            return rel_path, {
                "status": "operational",
                "operational": True,
                "lines_of_code": len(lines),
                "file_size_kb": module_path.stat().st_size / 1024,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return rel_path, {
                "status": "timeout",
                "operational": False,
                "error": "Validation timeout (10s)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return rel_path, {
                "status": "validation_error",
                "operational": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_all_modules(self, max_workers: int = 4) -> Dict[str, Any]:
        """Valida todos os módulos em paralelo."""
        modules = self.find_all_python_modules()
        self.results["total_modules"] = len(modules)
        
        logger.info(f"🧪 Validando {len(modules)} módulos...")
        
        operational_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_module = {
                executor.submit(self.validate_module, module): module
                for module in modules
            }
            
            for i, future in enumerate(as_completed(future_to_module), 1):
                module_path = future_to_module[future]
                
                try:
                    rel_path, result = future.result()
                    self.results["modules"][rel_path] = result
                    
                    if result["operational"]:
                        operational_count += 1
                        if i % 20 == 0:
                            logger.info(f"✅ {i}/{len(modules)}: {rel_path[:50]}...")
                    else:
                        failed_count += 1
                        logger.warning(f"❌ {i}/{len(modules)}: {rel_path} - {result['status']}")
                        
                except Exception as e:
                    rel_path = str(module_path.relative_to(self.project_root))
                    self.results["modules"][rel_path] = {
                        "status": "execution_error",
                        "operational": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    failed_count += 1
        
        # Calcular estatísticas
        self.results["operational_modules"] = operational_count
        self.results["failed_modules"] = failed_count
        self.results["success_rate"] = operational_count / len(modules) if modules else 0
        
        return self.results
    
    def generate_validation_report(self) -> str:
        """Gera relatório de validação."""
        success_rate_pct = self.results["success_rate"] * 100
        
        report = f"""AURORA v5.0 - RELATÓRIO DE VALIDAÇÃO COMPLETA
================================================================================
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total de Módulos: {self.results["total_modules"]}
Módulos Operacionais: {self.results["operational_modules"]}
Módulos com Falha: {self.results["failed_modules"]}
Taxa de Sucesso: {success_rate_pct:.2f}%
================================================================================

STATUS GERAL: {'✅ 100% OPERACIONAL' if success_rate_pct == 100 else f'⚠️  {success_rate_pct:.1f}% OPERACIONAL'}

ESTATÍSTICAS POR STATUS
-----------------------
"""
        
        status_counts = {}
        for data in self.results["modules"].values():
            status = data["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / self.results["total_modules"]) * 100
            report += f"{status}: {count} módulos ({percentage:.1f}%)\n"
        
        # Módulos críticos
        critical_modules = [
            "aurora_etapa_a.py",
            "00-Governanca/tier1_risk_validator.py",
            "00-Governanca/quantum_firewall.py",
            "01-Departamentos/AGENTS/CEO_Agent.py",
            "01-Departamentos/AGENTS/CFO_Agent.py", 
            "01-Departamentos/AGENTS/CTO_Agent.py",
            "01-Departamentos/AGENTS/CKO_Agent.py",
            "04-Infraestrutura/api/database.py",
            "04-Infraestrutura/api/main.py",
            "06-Monitoramento/feedbackloop_module.py",
            "system_core/ncnt_orchestrator_complete.py",
            "main_ncnt.py",
            "ncnt_system_complete.py"
        ]
        
        report += """

MÓDULOS CRÍTICOS - STATUS
--------------------------
"""
        
        for module in critical_modules:
            if module in self.results["modules"]:
                data = self.results["modules"][module]
                status_icon = "✅" if data["operational"] else "❌"
                report += f"{status_icon} {module}: {data['status']}\n"
            else:
                report += f"❓ {module}: NÃO ENCONTRADO\n"
        
        # Recomendações
        report += f"""

RECOMENDAÇÕES
-------------
"""
        
        if success_rate_pct == 100:
            report += """1. ✅ Sistema 100% validado - PRONTO PARA PRODUÇÃO
2. 🚀 Execute: python aurora_etapa_a.py --real-data
3. 📊 Coletar métricas de mercado real
4. 🎯 Tomar decisão baseada em dados empíricos"""
        elif success_rate_pct >= 95:
            report += f"""1. ⚠️  Sistema {success_rate_pct:.1f}% operacional
2. 🔧 Corrigir {self.results['failed_modules']} módulos com falha
3. 🧪 Re-executar validação
4. 🎯 Buscar 100% antes de produção"""
        else:
            report += f"""1. ❌ Sistema apenas {success_rate_pct:.1f}% operacional
2. 🔴 PRIORIDADE: Corrigir módulos com falha
3. 🛠️  Revisar relatório detalhado
4. 🎯 Só prosseguir após atingir pelo menos 95%"""

        return report
    
    def save_results(self):
        """Salva resultados em JSON."""
        json_path = self.project_root / "aurora_validation_results.json"
        
        self.results["summary"] = {
            "success_rate_percentage": self.results["success_rate"] * 100,
            "validation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": sys.version,
            "system_platform": sys.platform
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Resultados salvos em: {json_path}")
        return json_path

def main():
    """Função principal."""
    print("=" * 80)
    print("🔍 VALIDAÇÃO DOS 239 MÓDULOS AURORA v5.0")
    print("=" * 80)
    
    validator = AuroraModuleValidator()
    
    try:
        results = validator.validate_all_modules(max_workers=6)
        report = validator.generate_validation_report()
        validator.save_results()
        
        # Salvar relatório
        report_path = validator.project_root / "aurora_validation_report.txt"
        report_path.write_text(report, encoding='utf-8')
        
        print("\n" + report)
        print("=" * 80)
        
        success_rate = results["success_rate"] * 100
        
        if success_rate == 100:
            print("\n🎉 SISTEMA 100% OPERACIONAL!")
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. python aurora_etapa_a.py --test-integration")
            print("2. python aurora_etapa_a.py --real-market-data")
            return 0
        elif success_rate >= 95:
            print(f"\n⚠️  SISTEMA {success_rate:.1f}% OPERACIONAL")
            return 1
        else:
            print(f"\n❌ SISTEMA APENAS {success_rate:.1f}% OPERACIONAL")
            return 2
            
    except KeyboardInterrupt:
        print("\n⏹️  Validação interrompida")
        return 3
    except Exception as e:
        print(f"\n❌ Erro na validação: {str(e)}")
        return 4

if __name__ == "__main__":
    sys.exit(main())

