#!/usr/bin/env python3
"""
MASTER TEST RUNNER - Executa todos os testes e gera relatório binário
Resultado final: SISTEMA VERIFICADO ou SISTEMA NÃO VERIFICADO
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class MasterTestRunner:
    """Orquestrador de testes empíricos"""
    
    TESTS = [
        {
            "name": "Command Injection Test",
            "script": "script_1_command_injection_test.py",
            "timeout": 300,  # 5 minutos
            "weight": 30  # 30% do score
        },
        {
            "name": "Smoke Test Critical Modules", 
            "script": "script_2_smoke_test_critical_modules.py",
            "timeout": 600,  # 10 minutos
            "weight": 25  # 25% do score
        },
        {
            "name": "Compliance Implementation Validator",
            "script": "script_3_compliance_quick_validator.py",
            "timeout": 300,  # 5 minutos
            "weight": 25  # 25% do score
        },
        {
            "name": "Integration Score Calculator",
            "script": "script_4_integration_score_calculator.py", 
            "timeout": 300,  # 5 minutos
            "weight": 20  # 20% do score
        }
    ]
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.script_dir = Path(__file__).parent
    
    def run_test(self, test_info):
        """Executa um teste individual"""
        print(f"\n{'='*80}")
        print(f"[RUN] RUNNING: {test_info['name']}")
        print(f"{'='*80}")
        
        script_path = self.script_dir / test_info["script"]
        
        if not script_path.exists():
            print(f"   [FAIL] SCRIPT NOT FOUND: {script_path}")
            return {
                "name": test_info["name"],
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Script not found: {test_info['script']}",
                "elapsed_time": 0,
                "weight": test_info["weight"]
            }
        
        try:
            start = time.time()
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=test_info["timeout"],
                cwd=str(self.script_dir)
            )
            
            elapsed = time.time() - start
            
            # Determinar se passou (exit code 0) ou falhou
            passed = result.returncode == 0
            
            # Mostrar output
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"STDERR:\n{result.stderr}")
            
            return {
                "name": test_info["name"],
                "passed": passed,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "elapsed_time": elapsed,
                "weight": test_info["weight"]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "name": test_info["name"],
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"TIMEOUT after {test_info['timeout']} seconds",
                "elapsed_time": test_info["timeout"],
                "weight": test_info["weight"]
            }
        except Exception as e:
            return {
                "name": test_info["name"],
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "elapsed_time": 0,
                "weight": test_info["weight"]
            }
    
    def calculate_overall_score(self):
        """Calcula score geral baseado em pesos"""
        if not self.results:
            return 0
        
        total_weight = sum(test["weight"] for test in self.TESTS)
        weighted_score = 0
        
        for result in self.results:
            if result["passed"]:
                weighted_score += result["weight"]
        
        return (weighted_score / total_weight) * 100
    
    def generate_report(self):
        """Gera relatório final binário"""
        overall_score = self.calculate_overall_score()
        total_time = self.end_time - self.start_time
        
        print("\n" + "="*80)
        print("[REPORT] MASTER TEST REPORT - BINARY VERDICT")
        print("="*80)
        
        print(f"\n[TIME] Total Test Time: {total_time:.1f} seconds")
        print(f"[DATE] Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-"*80)
        print("INDIVIDUAL TEST RESULTS:")
        print("-"*80)
        
        for result in self.results:
            status = "[PASS] PASS" if result["passed"] else "[FAIL] FAIL"
            print(f"\n{result['name']}:")
            print(f"  Status: {status}")
            print(f"  Time: {result['elapsed_time']:.1f}s")
            print(f"  Weight: {result['weight']}%")
            
            if result["stderr"] and not result["passed"]:
                print(f"  Errors: {result['stderr'][:200]}...")
        
        print("\n" + "="*80)
        print("[VERDICT] FINAL BINARY VERDICT:")
        print("="*80)
        
        print(f"\n[SCORE] Overall Score: {overall_score:.1f}%")
        
        # CRITÉRIO BINÁRIO FINAL
        if overall_score >= 80:  # 80% ou mais
            print("\n" + "="*80)
            print("[PASS] SISTEMA VERIFICADO - RELATORIO CONFIAVEL")
            print("="*80)
            print("\nRecomendacao: Considerar producao com monitoramento intensivo")
            return True
        elif overall_score >= 60:  # 60-79%
            print("\n" + "="*80)
            print("[WARN] SISTEMA PARCIALMENTE VERIFICADO")
            print("="*80)
            print("\nRecomendacao: Correcoes necessarias antes de producao")
            return False
        else:  # < 60%
            print("\n" + "="*80)
            print("[FAIL] SISTEMA NAO VERIFICADO - RELATORIO QUESTIONAVEL")
            print("="*80)
            print("\nRecomendacao: Executar Rescue Plan v4.0 completo")
            return False
    
    def run(self):
        """Executa todos os testes"""
        print("="*80)
        print("🔬 AURORA SYSTEM EMPIRICAL VALIDATION SUITE")
        print("="*80)
        print("\nIniciando validação empírica completa...")
        
        self.start_time = time.time()
        
        # Executar cada teste
        for test_info in self.TESTS:
            result = self.run_test(test_info)
            self.results.append(result)
            
            if not result["passed"]:
                print(f"\n[WARN] Test failed: {test_info['name']}")
        
        self.end_time = time.time()
        
        # Gerar relatório final
        final_result = self.generate_report()
        
        return final_result


if __name__ == "__main__":
    runner = MasterTestRunner()
    result = runner.run()
    
    # Exit code baseado no resultado
    sys.exit(0 if result else 1)

