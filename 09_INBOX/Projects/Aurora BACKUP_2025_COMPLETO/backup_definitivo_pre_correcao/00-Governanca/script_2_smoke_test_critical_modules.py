#!/usr/bin/env python3
"""
TESTE EMPÍRICO 2: SMOKE TEST MÓDULOS CRÍTICOS
Testa se 5 módulos críticos inicializam e executam função básica
Resultado: PASS (5/5) ou FAIL (qualquer < 5)
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path


class SmokeTestTester:
    """Teste de fumaça binário - módulo funciona ou não"""
    
    CRITICAL_MODULES = [
        {
            "name": "ncnt_module_template_v2.py",
            "test_function": "NCNTModule",
            "import_test": True,
            "instantiate": True,
            "required_methods": ["_initialize_module", "get_vitals"]
        },
        {
            "name": "regulatory_context.py", 
            "test_function": "RegulatoryContext",
            "import_test": True,
            "instantiate": True,
            "required_methods": ["run_compliance_check"]
        },
        {
            "name": "audit_system_complete.py",
            "test_function": "AuroraAuditSystem",
            "import_test": True,
            "instantiate": True,
            "instantiate_args": {"project_root": "."},
            "required_methods": ["run_complete_audit"]
        },
        {
            "name": "integration_gate_v3.py",
            "test_function": "IntegrationGateV3",
            "import_test": True,
            "instantiate": True,
            "required_methods": ["validate_module_integration", "get_status"]
        },
        {
            "name": "neural_connection_monitor_v2.py",
            "test_function": "NeuralConnectionMonitor",
            "import_test": True,
            "instantiate": True,
            "required_methods": ["scan_all_modules"]
        }
    ]
    
    def __init__(self):
        self.results = {}
        self.pass_count = 0
        self.fail_count = 0
    
    def find_module(self, module_name):
        """Busca módulo no sistema de arquivos"""
        base_path = Path(__file__).parent.parent
        for root, dirs, files in os.walk(base_path):
            if module_name in files:
                return os.path.join(root, module_name)
        return None
    
    def test_module(self, module_info):
        """Teste binário: módulo funciona ou não"""
        module_name = module_info["name"]
        print(f"\n[TEST] Testing: {module_name}")
        
        # 1. Encontrar arquivo
        filepath = self.find_module(module_name)
        if not filepath:
            print(f"   [FAIL] FILE NOT FOUND")
            return False, "FILE_NOT_FOUND"
        
        print(f"   [INFO] Found at: {filepath}")
        
        try:
            # 2. Carregar módulo
            spec = importlib.util.spec_from_file_location(
                module_name.replace(".py", ""), 
                filepath
            )
            if spec is None:
                print(f"   [FAIL] CANNOT LOAD SPEC")
                return False, "LOAD_SPEC_FAILED"
            
            module = importlib.util.module_from_spec(spec)
            
            # 3. Executar módulo
            spec.loader.exec_module(module)
            print(f"   [PASS] Module loaded")
            
            # 4. Verificar se classe existe
            if module_info["import_test"]:
                if not hasattr(module, module_info["test_function"]):
                    print(f"   [FAIL] CLASS {module_info['test_function']} NOT FOUND")
                    return False, "CLASS_NOT_FOUND"
                
                print(f"   [PASS] Class {module_info['test_function']} found")
                
                # 5. Instanciar se necessário
                if module_info["instantiate"]:
                    try:
                        # NCNTModule precisa de module_name
                        if module_info["test_function"] == "NCNTModule":
                            instance = getattr(module, module_info["test_function"])("TestModule")
                        # AuroraAuditSystem precisa de project_root
                        elif "instantiate_args" in module_info:
                            instance = getattr(module, module_info["test_function"])(**module_info["instantiate_args"])
                        else:
                            instance = getattr(module, module_info["test_function"])()
                        print(f"   [PASS] Instance created")
                        
                        # 6. Verificar métodos obrigatórios
                        for method in module_info["required_methods"]:
                            if not hasattr(instance, method):
                                print(f"   [FAIL] METHOD {method} NOT FOUND")
                                return False, f"METHOD_{method}_MISSING"
                            print(f"   [PASS] Method {method} exists")
                    
                    except Exception as e:
                        print(f"   [FAIL] INSTANTIATION FAILED: {str(e)}")
                        return False, f"INSTANTIATION_ERROR: {str(e)}"
            
            return True, "ALL_TESTS_PASSED"
            
        except Exception as e:
            print(f"   [FAIL] LOAD/EXECUTION ERROR: {str(e)}")
            print(f"   [INFO] Traceback:")
            for line in traceback.format_exc().split('\n')[-5:]:
                if line:
                    print(f"      {line}")
            return False, f"EXECUTION_ERROR: {str(e)}"
    
    def run(self):
        """Executa todos os smoke tests"""
        print("=" * 80)
        print("SMOKE TEST CRITICAL MODULES - BINARY PASS/FAIL")
        print("=" * 80)
        
        for module_info in self.CRITICAL_MODULES:
            success, reason = self.test_module(module_info)
            self.results[module_info["name"]] = {
                "success": success,
                "reason": reason
            }
            
            if success:
                self.pass_count += 1
            else:
                self.fail_count += 1
        
        # RESULTADO FINAL BINÁRIO
        print("\n" + "=" * 80)
        print("FINAL RESULT - BINARY:")
        print("=" * 80)
        
        print(f"\n[STATS] Summary:")
        print(f"   [PASS] PASS: {self.pass_count}/5")
        print(f"   [FAIL] FAIL: {self.fail_count}/5")
        
        if self.fail_count > 0:
            print("\n[FAIL] FAILING MODULES:")
            for module_name, result in self.results.items():
                if not result["success"]:
                    print(f"   * {module_name}: {result['reason']}")
        
        # CRITÉRIO BINÁRIO: 5/5 PASS ou FAIL
        if self.pass_count == 5:
            print("\n[PASS] PASS - ALL 5 CRITICAL MODULES OPERATIONAL")
            return True
        else:
            print(f"\n[FAIL] FAIL - {self.fail_count} MODULE(S) FAILED")
            return False


if __name__ == "__main__":
    tester = SmokeTestTester()
    result = tester.run()
    sys.exit(0 if result else 1)

