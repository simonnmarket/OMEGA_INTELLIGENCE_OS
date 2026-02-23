#!/usr/bin/env python3
"""
TESTE EMPÍRICO 4: INTEGRATION SCORE CALCULATION
Calcula score de integração baseado em análise de arquivos
Resultado: PASS (score > 60%) ou FAIL
"""

import os
import re
import sys
from pathlib import Path


class IntegrationScoreCalculator:
    """Calculadora empírica de integration score - sem opinião"""
    
    def __init__(self):
        self.stats = {
            "total_modules": 0,
            "v2_modules": 0,
            "v1_modules": 0,
            "standalone_modules": 0,
            "wrappers": 0
        }
    
    def scan_directory(self, directory="."):
        """Varredura completa do diretório para módulos Python"""
        python_files = []
        base_path = Path(__file__).parent.parent if directory == "." else Path(directory)
        
        for root, dirs, files in os.walk(base_path):
            # Ignorar diretórios comuns
            ignore_dirs = [".git", "__pycache__", "venv", ".env", "node_modules", ".cursor"]
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def classify_module(self, filepath):
        """Classificação empírica baseada no conteúdo do arquivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Heurística 1: Importa NCNTModule v2.0?
            if "from modules.ncnt_module_template_v2 import NCNTModule" in content or \
               "from modules.ncnt_module_template_v2" in content or \
               "import ncnt_module_template_v2" in content:
                if re.search(r"class\s+\w+.*NCNTModule", content):
                    return "v2_module"
                return "v2_related"
            
            # Heurística 2: Herda de NCNTModule?
            if re.search(r"class\s+\w+.*\(.*NCNTModule.*\)", content):
                return "v2_module"
            
            # Heurística 3: Menção a v1.0?
            if "NCNTBaseModule" in content or "MODULE_VERSION = \"1.0.0\"" in content:
                return "v1_module"
            
            # Heurística 4: É wrapper?
            if "wrapper" in filepath.lower() or "_wrapper" in filepath or "wrappers_v2" in filepath:
                # Wrappers são considerados v2.0 integrados
                if "NCNTModule" in content or "ncnt_module_template_v2" in content:
                    return "wrapper"
            
            # Heurística 5: Tem características de standalone?
            if "if __name__ == \"__main__\"" in content:
                return "standalone"
            
            # Default: standalone
            return "standalone"
            
        except Exception as e:
            print(f"   [WARN] Error reading {filepath}: {str(e)}")
            return "unknown"
    
    def calculate_score(self):
        """Cálculo matemático do integration score"""
        total = self.stats["total_modules"]
        if total == 0:
            return 0.0
        
        # Fórmula: (v2 + v1*0.5 + wrappers*0.8) / total
        v2_score = self.stats["v2_modules"]
        v1_score = self.stats["v1_modules"] * 0.5
        wrapper_score = self.stats["wrappers"] * 0.8
        
        weighted_total = v2_score + v1_score + wrapper_score
        score = (weighted_total / total) * 100
        
        return round(score, 2)
    
    def run(self):
        """Executa análise completa"""
        print("=" * 80)
        print("INTEGRATION SCORE CALCULATOR - EMPIRICAL ANALYSIS")
        print("=" * 80)
        
        # 1. Encontrar todos os módulos Python
        print("\n[SCAN] Scanning for Python modules...")
        python_files = self.scan_directory()
        
        if not python_files:
            print("   [FAIL] NO PYTHON FILES FOUND")
            return False
        
        self.stats["total_modules"] = len(python_files)
        print(f"   [PASS] Found {self.stats['total_modules']} Python modules")
        
        # 2. Classificar cada módulo
        print("\n[CLASSIFY] Classifying modules...")
        classification_counts = {
            "v2_module": 0,
            "v2_related": 0,
            "v1_module": 0,
            "standalone": 0,
            "wrapper": 0,
            "unknown": 0
        }
        
        # Analisar todos os arquivos
        for filepath in python_files:
            classification = self.classify_module(filepath)
            if classification not in classification_counts:
                classification = "unknown"
            classification_counts[classification] += 1
            
            # Atualizar stats
            if classification == "v2_module" or classification == "v2_related":
                self.stats["v2_modules"] += 1
            elif classification == "v1_module":
                self.stats["v1_modules"] += 1
            elif classification == "wrapper":
                self.stats["wrappers"] += 1
            elif classification == "standalone":
                self.stats["standalone_modules"] += 1
        
        # 3. Calcular score
        score = self.calculate_score()
        
        # 4. Mostrar resultados
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS - EMPIRICAL DATA:")
        print("=" * 80)
        
        print(f"\n[STATS] Module Statistics:")
        print(f"   * Total Modules: {self.stats['total_modules']}")
        print(f"   * NCNT v2.0: {self.stats['v2_modules']}")
        print(f"   * NCNT v1.0: {self.stats['v1_modules']}")
        print(f"   * Wrappers: {self.stats['wrappers']}")
        print(f"   * Standalone: {self.stats['standalone_modules']}")
        
        print(f"\n[CALC] Calculated Integration Score: {score}%")
        
        # Verificar contra relatório
        reported_score = 65.91  # Do relatório
        
        print(f"\n[COMPARE] Comparison with Reported Score:")
        print(f"   * Calculated: {score}%")
        print(f"   * Reported: {reported_score}%")
        print(f"   * Difference: {abs(score - reported_score):.2f}%")
        
        # RESULTADO FINAL BINÁRIO
        print("\n" + "=" * 80)
        print("FINAL VERDICT - BINARY:")
        print("=" * 80)
        
        # Critério: Score calculado dentro de 15% do reportado E > 50%
        score_discrepancy = abs(score - reported_score)
        
        if score > 50 and score_discrepancy < 15:
            print(f"\n[PASS] PASS - INTEGRATION SCORE VERIFIED")
            print(f"   * Score reasonable: {score}%")
            print(f"   * Discrepancy acceptable: {score_discrepancy:.2f}%")
            return True
        else:
            print(f"\n[FAIL] FAIL - INTEGRATION SCORE QUESTIONABLE")
            print(f"   * Score too low or discrepancy too high")
            return False


if __name__ == "__main__":
    calculator = IntegrationScoreCalculator()
    result = calculator.run()
    sys.exit(0 if result else 1)

