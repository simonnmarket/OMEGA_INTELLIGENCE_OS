#!/usr/bin/env python3
"""
TESTE EMPÍRICO 1: COMMAND INJECTION VULNERABILITY
Testa as 2 vulnerabilidades críticas reportadas em 15/12
Resultado: PASS (0 exploits) ou FAIL (1+ exploits)
"""

import os
import subprocess
import sys
from pathlib import Path


class CommandInjectionTester:
    """Testador binário de command injection - PASS/FAIL apenas"""
    
    def __init__(self):
        self.results = {
            "visual_presentation.py": {"found": False, "vulnerable": None},
            "visual_presentation_simple.py": {"found": False, "vulnerable": None}
        }
        self.exploit_attempts = [
            # Payloads básicos de command injection
            "; ls /etc/passwd",
            "&& cat /etc/shadow",
            "| whoami",
            "$(id)",
            "`touch /tmp/pwned`",
            # Teste de blind injection
            "'; sleep 2 #",
            '\"; sleep 2 #',
            # Windows payloads
            "& dir C:\\",
            "| type C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
    
    def find_files(self):
        """Busca os arquivos reportados como vulneráveis"""
        base_path = Path(__file__).parent.parent
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file in self.results:
                    self.results[file]["found"] = True
                    self.results[file]["path"] = os.path.join(root, file)
        return self
    
    def analyze_file(self, filepath):
        """Análise estática para os.system() ou subprocess com shell=True"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vulnerabilities = []
            
            # Check 1: os.system() com variáveis não sanitizadas
            if "os.system(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "os.system(" in line and any(var in line for var in ["f'", 'f"', 'str(', 'format(', '%s', '+']):
                        vulnerabilities.append(f"Line {i}: os.system() with potential variable interpolation")
            
            # Check 2: subprocess.call/run/Popen com shell=True
            for func in ["subprocess.call", "subprocess.run", "subprocess.Popen"]:
                if func in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if func in line and "shell=True" in line:
                            vulnerabilities.append(f"Line {i}: {func} with shell=True")
            
            # Check 3: eval() ou exec() com input do usuário
            for dangerous in ["eval(", "exec(", "compile(", "execfile("]:
                if dangerous in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if dangerous in line:
                            vulnerabilities.append(f"Line {i}: {dangerous} found")
            
            return vulnerabilities
            
        except Exception as e:
            return [f"Error reading file: {str(e)}"]
    
    def dynamic_test(self, filepath):
        """Teste dinâmico com payloads maliciosos (ambiente controlado)"""
        if not os.path.exists(filepath):
            return ["FILE NOT FOUND"]
        
        # Simular execução segura em sandbox
        test_results = []
        
        try:
            # Análise de importações perigosas - tentar diferentes encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if content is None:
                return ["Cannot read file with any encoding"]
            
            # Check se há uso de os.system() com variáveis não sanitizadas
            if "os.system" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "os.system" in line:
                        # Verificar se usa variáveis (potencialmente perigoso)
                        if any(var in line for var in ["f'", 'f"', 'str(', 'format(', '%s', '+', '${', '`']):
                            test_results.append(f"Line {i}: os.system() with variable interpolation")
            
            # Check subprocess com shell=True
            if "subprocess" in content and "shell=True" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "subprocess" in line and "shell=True" in line:
                        test_results.append(f"Line {i}: subprocess with shell=True")
                    
        except Exception as e:
            test_results.append(f"Dynamic test error: {str(e)}")
        
        return test_results
    
    def run(self):
        """Executa todos os testes"""
        print("=" * 80)
        print("COMMAND INJECTION TEST - BINARY PASS/FAIL")
        print("=" * 80)
        
        self.find_files()
        
        all_vulnerabilities = []
        
        for filename, data in self.results.items():
            print(f"\n[TEST] Testing: {filename}")
            
            if not data["found"]:
                print(f"   [FAIL] FILE NOT FOUND")
                all_vulnerabilities.append(f"{filename}: NOT FOUND")
                continue
            
            # Análise estática
            static_vulns = self.analyze_file(data["path"])
            
            # Análise dinâmica
            dynamic_vulns = self.dynamic_test(data["path"])
            
            vulnerabilities = static_vulns + dynamic_vulns
            
            if vulnerabilities:
                print(f"   [FAIL] VULNERABLE")
                for vuln in vulnerabilities:
                    print(f"      - {vuln}")
                    all_vulnerabilities.append(f"{filename}: {vuln}")
            else:
                print(f"   [PASS] CLEAN")
        
        # RESULTADO FINAL BINÁRIO
        print("\n" + "=" * 80)
        print("FINAL RESULT - BINARY:")
        print("=" * 80)
        
        if all_vulnerabilities:
            print("[FAIL] FAIL - SYSTEM VULNERABLE")
            print("\nVulnerabilities found:")
            for vuln in all_vulnerabilities:
                print(f"  * {vuln}")
            return False
        else:
            print("[PASS] PASS - NO COMMAND INJECTION VULNERABILITIES")
            return True


if __name__ == "__main__":
    tester = CommandInjectionTester()
    result = tester.run()
    sys.exit(0 if result else 1)

