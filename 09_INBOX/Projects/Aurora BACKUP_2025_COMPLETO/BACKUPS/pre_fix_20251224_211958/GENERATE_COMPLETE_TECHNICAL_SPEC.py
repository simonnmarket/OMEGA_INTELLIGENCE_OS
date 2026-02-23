#!/usr/bin/env python3
"""
GENERATE_COMPLETE_TECHNICAL_SPEC.py
===================================
Gera especificação técnica completa de TODOS os módulos do sistema Aurora.

Formato: IEEE/IETF Technical Specification
Cobertura: 100% dos módulos
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import json

class ModuleAnalyzer:
    """Analisa módulos Python e extrai especificações técnicas."""
    
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.modules = {}
        self.dependencies = {}
        self.interfaces = {}
        
    def find_all_modules(self) -> List[Path]:
        """Encontra todos os módulos Python."""
        modules = []
        exclude = {"__pycache__", ".git", "legacy_backup", "backup", "backups_"}
        
        for py_file in self.root.rglob("*.py"):
            if any(excl in str(py_file) for excl in exclude):
                continue
            if py_file.stat().st_size > 0:
                modules.append(py_file)
        
        return sorted(modules)
    
    def analyze_module(self, module_path: Path) -> Dict:
        """Analisa um módulo e extrai especificação técnica."""
        rel_path = str(module_path.relative_to(self.root))
        
        try:
            with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(module_path))
            
            spec = {
                "path": rel_path,
                "size_bytes": module_path.stat().st_size,
                "lines": len(content.splitlines()),
                "classes": [],
                "functions": [],
                "imports": [],
                "exports": []
            }
            
            # Extrair classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    spec["classes"].append({
                        "name": node.name,
                        "methods": methods,
                        "bases": [self._get_name(b) for b in node.bases]
                    })
                
                elif isinstance(node, ast.FunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    spec["functions"].append({
                        "name": node.name,
                        "params": params,
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom):
                        spec["imports"].append(f"from {node.module} import ...")
                    else:
                        spec["imports"].extend([alias.name for alias in node.names])
            
            return spec
            
        except Exception as e:
            return {
                "path": rel_path,
                "error": str(e),
                "size_bytes": module_path.stat().st_size
            }
    
    def _get_name(self, node):
        """Extrai nome de um nó AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "Unknown"
    
    def categorize_module(self, path: str) -> str:
        """Categoriza módulo por caminho."""
        if path.startswith("00-Governanca"):
            return "Governance"
        elif path.startswith("01-Departamentos"):
            return "Departments"
        elif path.startswith("02-Processos-Chave"):
            return "Processes"
        elif path.startswith("03-Operacoes-Diarias"):
            return "Operations"
        elif path.startswith("04-Infraestrutura"):
            return "Infrastructure"
        elif path.startswith("05-Documentacao"):
            return "Documentation"
        elif path.startswith("06-Monitoramento"):
            return "Monitoring"
        elif path.startswith("system_core"):
            return "Core"
        elif path.startswith("modules"):
            return "Modules"
        else:
            return "Root"

def generate_complete_spec():
    """Gera especificação técnica completa."""
    analyzer = ModuleAnalyzer()
    modules = analyzer.find_all_modules()
    
    print(f"Analisando {len(modules)} módulos...")
    
    categorized = {}
    all_specs = []
    
    for i, module_path in enumerate(modules, 1):
        if i % 50 == 0:
            print(f"  Processado: {i}/{len(modules)}")
        
        spec = analyzer.analyze_module(module_path)
        all_specs.append(spec)
        
        category = analyzer.categorize_module(spec["path"])
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(spec)
    
    # Gerar documento
    doc = generate_spec_document(categorized, all_specs, len(modules))
    
    # Salvar
    output_file = "AURORA_COMPLETE_TECHNICAL_SPECIFICATION.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"\n✅ Especificação completa gerada: {output_file}")
    print(f"   Total módulos: {len(modules)}")
    print(f"   Categorias: {len(categorized)}")
    
    # Salvar JSON também
    json_file = "aurora_modules_spec.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "total_modules": len(modules),
                "categories": len(categorized),
                "generated": datetime.now().isoformat()
            },
            "modules": all_specs,
            "categorized": {k: len(v) for k, v in categorized.items()}
        }, f, indent=2, ensure_ascii=False)
    
    print(f"   JSON exportado: {json_file}")

def generate_spec_document(categorized: Dict, all_specs: List, total: int) -> str:
    """Gera documento de especificação técnica."""
    
    doc = f"""# AURORA v5.1 - Complete Technical Specification
**Document ID:** TS-AURORA-5.1-COMPLETE-{datetime.now().strftime('%Y%m%d')}  
**Classification:** Technical Specification  
**Format:** IEEE/IETF Standard  
**Version:** 5.1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Production  
**Total Modules:** {total}

---

## 1. EXECUTIVE SUMMARY

```
SYSTEM: AURORA v5.1
TOTAL_MODULES: {total}
ARCHITECTURE: NCNT (Neural Central Transmission Core)
PATTERN: Hierarchical Modular Bank-Like
LANGUAGE: Python 3.8+
COMPLIANCE: Tier-0 Institutional
```

### Module Distribution

"""
    
    for category, modules in sorted(categorized.items()):
        doc += f"- **{category}**: {len(modules)} modules\n"
    
    doc += f"""

---

## 2. MODULE SPECIFICATIONS

### 2.1 Module Index by Category

"""
    
    # Por categoria
    for category, modules in sorted(categorized.items()):
        doc += f"\n#### {category} ({len(modules)} modules)\n\n"
        doc += "```\n"
        
        for spec in sorted(modules, key=lambda x: x["path"]):
            path = spec["path"]
            if "error" not in spec:
                classes = len(spec.get("classes", []))
                functions = len(spec.get("functions", []))
                doc += f"{path:80s} | C:{classes:2d} F:{functions:3d}\n"
            else:
                doc += f"{path:80s} | ERROR\n"
        
        doc += "```\n"
    
    doc += "\n---\n\n## 3. DETAILED MODULE SPECIFICATIONS\n\n"
    
    # Especificações detalhadas (top 50 mais importantes)
    important_modules = [
        "00-Governanca/quantum_firewall.py",
        "00-Governanca/tier1_risk_validator.py",
        "01-Departamentos/Execution-Trading/strategies/alpha_momentum.py",
        "01-Departamentos/Execution-Trading/strategies/mean_reversion.py",
        "01-Departamentos/Execution-Trading/strategies/breakout_detection.py",
        "04-Infraestrutura/mt5_executor.py",
        "04-Infraestrutura/MT5_STOPS_FIX.py",
        "01-Departamentos/AGENTS/CEO_Agent.py",
        "01-Departamentos/Risk-Controls/risk_engine.py",
        "06-Monitoramento/feedbackloop_module.py"
    ]
    
    for spec in all_specs:
        if spec["path"] in important_modules:
            doc += generate_module_detail(spec)
    
    doc += "\n---\n\n## 4. COMPLETE MODULE LIST\n\n"
    doc += "```\n"
    for spec in sorted(all_specs, key=lambda x: x["path"]):
        doc += f"{spec['path']}\n"
    doc += "```\n"
    
    return doc

def generate_module_detail(spec: Dict) -> str:
    """Gera detalhamento de um módulo."""
    doc = f"### {spec['path']}\n\n"
    
    if "error" in spec:
        doc += f"**ERROR:** {spec['error']}\n\n"
        return doc
    
    doc += f"**Size:** {spec['size_bytes']} bytes | **Lines:** {spec['lines']}\n\n"
    
    if spec.get("classes"):
        doc += "**Classes:**\n"
        for cls in spec["classes"]:
            doc += f"- `{cls['name']}`"
            if cls.get("bases"):
                doc += f" extends {', '.join(cls['bases'])}"
            doc += f" ({len(cls['methods'])} methods)\n"
        doc += "\n"
    
    if spec.get("functions"):
        doc += "**Functions:**\n"
        for func in spec["functions"][:10]:  # Limitar a 10
            async_marker = "async " if func.get("is_async") else ""
            params = ", ".join(func["params"][:5])  # Limitar params
            doc += f"- `{async_marker}{func['name']}({params}...)`\n"
        if len(spec["functions"]) > 10:
            doc += f"- ... and {len(spec['functions']) - 10} more\n"
        doc += "\n"
    
    doc += "\n"
    return doc

if __name__ == "__main__":
    print("=" * 60)
    print("AURORA - Complete Technical Specification Generator")
    print("=" * 60)
    generate_complete_spec()

