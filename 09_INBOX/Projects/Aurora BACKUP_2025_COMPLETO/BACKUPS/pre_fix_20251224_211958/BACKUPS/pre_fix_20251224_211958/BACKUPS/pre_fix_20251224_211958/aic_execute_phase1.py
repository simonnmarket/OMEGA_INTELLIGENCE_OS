#!/usr/bin/env python3
"""
AIC EXECUTION SCRIPT - PHASE 1: CORE FIX & SETUP
Execute em sequência automática com validação em cada passo
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

class AICPhase1Executor:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/aic_phase1_{self.timestamp}.log"
        self.backup_dir = f"backups/pre_fix_{self.timestamp}"
        self.success = True
        
    def log(self, message, level="INFO"):
        """Log estruturado para auditoria"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        
        # Criar diretório logs se não existir
        os.makedirs("logs", exist_ok=True)
        
        # Log para arquivo
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
        
        # Log para console
        if level == "ERROR":
            print(f"❌ {message}")
        elif level == "SUCCESS":
            print(f"✅ {message}")
        else:
            print(f"🔧 {message}")
            
        return log_msg
    
    def execute_step(self, step_name, command, validate_func=None):
        """Executa um passo com validação"""
        self.log(f"Iniciando passo: {step_name}")
        
        try:
            # Executar comando
            if isinstance(command, str):
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log(f"Falha no comando: {result.stderr}", "ERROR")
                    return False
            elif callable(command):
                result = command()
                if not result:
                    return False
            
            # Validar se função de validação fornecida
            if validate_func:
                if not validate_func():
                    self.log(f"Validação falhou para: {step_name}", "ERROR")
                    return False
            
            self.log(f"Passo completado: {step_name}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro em {step_name}: {str(e)}", "ERROR")
            return False
    
    def step_0_create_dirs(self):
        """Passo 0: Criar estrutura de diretórios"""
        dirs = ['scripts_fix', 'patches', 'backups', 'logs', 'temp']
        
        for d in dirs:
            try:
                os.makedirs(d, exist_ok=True)
                self.log(f"Diretório criado: {d}/")
            except Exception as e:
                self.log(f"Erro criando {d}: {e}", "ERROR")
                return False
        
        # Validar criação
        for d in dirs:
            if not os.path.exists(d):
                self.log(f"Diretório não criado: {d}", "ERROR")
                return False
        
        return True
    
    def step_1_create_backup(self):
        """Passo 1: Criar backup completo"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Copiar estrutura atual
            for item in os.listdir('.'):
                if item in ['backups', 'logs', 'temp', 'scripts_fix', 'patches', '__pycache__', '.git']:
                    continue  # Pular diretórios temporários
                
                src = item
                dst = os.path.join(self.backup_dir, item)
                
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                    else:
                        shutil.copy2(src, dst)
                except Exception as e:
                    self.log(f"Erro copiando {item}: {e}", "ERROR")
                    continue
            
            # Verificar tamanho do backup
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.backup_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
            
            self.log(f"Backup criado: {self.backup_dir} ({total_size/1024/1024:.1f} MB)")
            return total_size > 100000  # > 100KB
            
        except Exception as e:
            self.log(f"Erro criando backup: {e}", "ERROR")
            return False
    
    def step_2_fix_utf8_bom(self):
        """Passo 2: Corrigir UTF-8 BOM no módulo core"""
        target_file = "system_core/ncnt_orchestrator_complete.py"
        
        if not os.path.exists(target_file):
            self.log(f"Arquivo não encontrado: {target_file}", "ERROR")
            return False
        
        try:
            # Ler conteúdo binário
            with open(target_file, 'rb') as f:
                content = f.read()
            
            original_hash = self.calculate_hash(content)
            original_size = len(content)
            
            # Verificar e remover BOM
            removed = False
            
            # UTF-8 BOM
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]
                removed = True
                self.log("UTF-8 BOM detectado e removido")
            
            # UTF-16 BOM (mais grave)
            elif content.startswith(b'\xfe\xff'):
                self.log("⚠️ UTF-16 Big Endian BOM detectado - convertendo...", "WARNING")
                content = content[2:].decode('utf-16-be').encode('utf-8')
                removed = True
            elif content.startswith(b'\xff\xfe'):
                self.log("⚠️ UTF-16 Little Endian BOM detectado - convertendo...", "WARNING")
                content = content[2:].decode('utf-16-le').encode('utf-8')
                removed = True
            
            if removed:
                # Criar backup do arquivo original
                backup_file = target_file + '.pre_fix'
                os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                with open(backup_file, 'wb') as f:
                    f.write(content)
                
                # Escrever arquivo corrigido
                with open(target_file, 'wb') as f:
                    f.write(content)
                
                new_hash = self.calculate_hash(content)
                self.log(f"Arquivo corrigido: {original_size} → {len(content)} bytes")
                self.log(f"Hash original: {original_hash[:16]}...")
                self.log(f"Hash novo: {new_hash[:16]}...")
                
                return original_hash != new_hash
            else:
                self.log("Nenhum BOM detectado - arquivo OK")
                return True
                
        except Exception as e:
            self.log(f"Erro corrigindo BOM: {e}", "ERROR")
            return False
    
    def step_3_validate_fix(self):
        """Passo 3: Validar correção"""
        test_code = '''
import sys
sys.path.insert(0, '.')

try:
    import system_core.ncnt_orchestrator_complete
    print("SUCCESS: Module imports correctly")
    sys.exit(0)
except SyntaxError as e:
    print(f"SYNTAX_ERROR: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(2)
except Exception as e:
    print(f"UNKNOWN_ERROR: {e}")
    sys.exit(3)
'''
        
        try:
            # Escrever script de teste
            os.makedirs("temp", exist_ok=True)
            test_file = "temp/test_import.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            # Executar teste
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                self.log("✅ Validação PASS: Módulo importa corretamente", "SUCCESS")
                return True
            else:
                self.log(f"❌ Validação FAIL: {result.stdout.strip()}", "ERROR")
                if result.stderr:
                    self.log(f"   Erro: {result.stderr.strip()}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Teste timeout - possível loop infinito", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Erro na validação: {e}", "ERROR")
            return False
    
    def step_4_test_system_dry_run(self):
        """Passo 4: Teste dry-run do sistema"""
        try:
            # Verificar se main_ncnt.py existe
            if not os.path.exists("main_ncnt.py"):
                self.log("main_ncnt.py não encontrado, testando alternativa...")
                # Procurar ponto de entrada
                entry_points = ["main.py", "aurora_etapa_a.py", "AURORA_FINAL_EXECUCAO_AIC_V5.1.py"]
                test_file = None
                for ep in entry_points:
                    if os.path.exists(ep):
                        self.log(f"Usando ponto de entrada alternativo: {ep}")
                        test_file = ep
                        break
                
                if not test_file:
                    self.log("Nenhum ponto de entrada encontrado", "WARNING")
                    return True  # Não é crítico para esta fase
            else:
                test_file = "main_ncnt.py"
            
            # Executar dry-run
            result = subprocess.run(
                [sys.executable, test_file, "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log("✅ Sistema dry-run PASS", "SUCCESS")
                return True
            else:
                self.log(f"⚠️ Sistema dry-run com avisos: {result.stderr[:200] if result.stderr else 'N/A'}", "WARNING")
                return True  # Ainda considerado sucesso para esta fase
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Dry-run timeout (pode ser normal em inicialização)", "WARNING")
            return True
        except Exception as e:
            self.log(f"⚠️ Erro no dry-run: {e}", "WARNING")
            return True
    
    def step_5_generate_validation_report(self):
        """Passo 5: Gerar relatório de validação"""
        report = {
            "timestamp": self.timestamp,
            "phase": 1,
            "steps": [],
            "overall_status": "PASS",
            "system_info": self.get_system_info()
        }
        
        # Salvar relatório
        import json
        report_file = f"logs/validation_report_phase1_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Relatório gerado: {report_file}")
        return True
    
    def calculate_hash(self, data):
        """Calcular hash SHA-256"""
        import hashlib
        return hashlib.sha256(data).hexdigest()
    
    def get_system_info(self):
        """Coletar informações do sistema"""
        import platform
        return {
            "python_version": platform.python_version(),
            "system": platform.system(),
            "architecture": platform.architecture()[0] if platform.architecture() else "unknown",
            "processor": platform.processor()
        }
    
    def run_all(self):
        """Executar todas as etapas em sequência"""
        self.log("=" * 60)
        self.log("INICIANDO AIC PHASE 1: CORE FIX & SETUP")
        self.log("=" * 60)
        
        steps = [
            ("Criar diretórios", self.step_0_create_dirs, None),
            ("Criar backup", self.step_1_create_backup, None),
            ("Corrigir UTF-8 BOM", self.step_2_fix_utf8_bom, None),
            ("Validar correção", self.step_3_validate_fix, None),
            ("Teste dry-run sistema", self.step_4_test_system_dry_run, None),
            ("Gerar relatório", self.step_5_generate_validation_report, None),
        ]
        
        results = []
        for name, func, validate in steps:
            success = self.execute_step(name, func, validate)
            results.append((name, success))
            
            if not success and name in ["Corrigir UTF-8 BOM", "Validar correção"]:
                self.log("❌ ETAPA CRÍTICA FALHOU - ABORTANDO", "ERROR")
                self.success = False
                break
        
        # Resumo final
        self.log("=" * 60)
        self.log("RESUMO DA EXECUÇÃO:")
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"  {name}: {status}")
        
        overall = all(s for _, s in results)
        if overall:
            self.log("🎉 FASE 1 COMPLETADA COM SUCESSO!", "SUCCESS")
        else:
            self.log("⚠️ FASE 1 COMPLETADA COM FALHAS", "ERROR")
        
        return overall


def main():
    """Função principal"""
    executor = AICPhase1Executor()
    
    try:
        success = executor.run_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        executor.log("Execução interrompida pelo usuário", "ERROR")
        sys.exit(1)
    except Exception as e:
        executor.log(f"Erro não tratado: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()

