#!/usr/bin/env python3
"""
EXECUTOR PRINCIPAL - ETAPA 1 AURORA v5.1
Correção dos bloqueadores críticos do sistema
CEO + CTO + CKO Approval Required
"""

import os
import sys
import subprocess
import hashlib
import json
from datetime import datetime
from pathlib import Path

class Etapa1Executor:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "projeto": "AURORA v5.1",
            "etapa": 1,
            "status": "INICIADO",
            "correcoes_aplicadas": [],
            "validacoes": [],
            "erros": [],
            "veredito_final": "PENDENTE"
        }
        
    def verificar_bom_arquivo_critico(self):
        """Verificar e remover BOM do arquivo principal"""
        arquivo = "system_core/ncnt_orchestrator_complete.py"
        resultado = {
            "id": "CRIT-001",
            "arquivo": arquivo,
            "acao": "verificar_bom",
            "status": "INICIADO"
        }
        
        try:
            if not os.path.exists(arquivo):
                resultado["status"] = "ERRO"
                resultado["mensagem"] = "Arquivo não encontrado"
                return resultado
            
            with open(arquivo, 'rb') as f:
                conteudo_bytes = f.read()
            
            tem_bom = conteudo_bytes.startswith(b'\xef\xbb\xbf')
            resultado["tem_bom"] = tem_bom
            
            if tem_bom:
                conteudo_sem_bom = conteudo_bytes[3:]
                with open(arquivo, 'wb') as f:
                    f.write(conteudo_sem_bom)
                resultado["acao_tomada"] = "BOM removido"
                resultado["status"] = "CORRIGIDO"
            else:
                resultado["acao_tomada"] = "Verificado - sem BOM"
                resultado["status"] = "VALIDADO"
            
            hash_atual = hashlib.sha256(conteudo_bytes).hexdigest()
            resultado["hash_antes"] = hash_atual
            
            if tem_bom:
                hash_depois = hashlib.sha256(conteudo_sem_bom).hexdigest()
                resultado["hash_depois"] = hash_depois
                
        except Exception as e:
            resultado["status"] = "ERRO"
            resultado["mensagem"] = str(e)
        
        self.resultados["correcoes_aplicadas"].append(resultado)
        return resultado
    
    def scan_seguranca_arquivos(self):
        """Scan por command injection e outras vulnerabilidades"""
        arquivos_alvo = ["visual_presentation.py", "visual_presentation_simple.py"]
        resultado = {
            "id": "SEC-SCAN",
            "tipo": "scan_seguranca",
            "arquivos_verificados": arquivos_alvo,
            "vulnerabilidades": [],
            "status": "INICIADO"
        }
        
        try:
            for arquivo in arquivos_alvo:
                if os.path.exists(arquivo):
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    padroes_perigosos = {
                        "os.system(": "COMMAND_INJECTION",
                        "eval(": "CODE_INJECTION",
                        "exec(": "CODE_INJECTION",
                        "subprocess.call(": "PROCESS_INJECTION",
                        "subprocess.Popen(": "PROCESS_INJECTION",
                        "shell=True": "SHELL_INJECTION"
                    }
                    
                    for padrao, tipo in padroes_perigosos.items():
                        if padrao in conteudo:
                            resultado["vulnerabilidades"].append({
                                "arquivo": arquivo,
                                "tipo": tipo,
                                "padrao": padrao,
                                "linha": conteudo.find(padrao)
                            })
                else:
                    resultado["vulnerabilidades"].append({
                        "arquivo": arquivo,
                        "tipo": "ARQUIVO_AUSENTE",
                        "status": "NÃO ENCONTRADO"
                    })
            
            if not resultado["vulnerabilidades"]:
                resultado["status"] = "NENHUMA VULNERABILIDADE ENCONTRADA"
            else:
                resultado["status"] = "VULNERABILIDADES DETECTADAS"
                
        except Exception as e:
            resultado["status"] = "ERRO"
            resultado["mensagem"] = str(e)
        
        self.resultados["validacoes"].append(resultado)
        return resultado
    
    def validar_importacao_sistema(self):
        """Validar que o sistema pode ser importado"""
        resultado = {
            "id": "VAL-IMPORT",
            "tipo": "validacao_importacao",
            "status": "INICIADO",
            "importacao_ok": False
        }
        
        try:
            codigo_import = '''
import sys
sys.path.insert(0, '.')
try:
    import system_core.ncnt_orchestrator_complete
    print("SUCCESS: Importação bem-sucedida")
    exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
'''
            
            proc = subprocess.run(
                [sys.executable, '-c', codigo_import],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0:
                resultado["importacao_ok"] = True
                resultado["status"] = "IMPORTAÇÃO VALIDADA"
                resultado["output"] = proc.stdout.strip()
            else:
                resultado["status"] = "FALHA NA IMPORTAÇÃO"
                resultado["erro"] = proc.stderr.strip()
                
        except subprocess.TimeoutExpired:
            resultado["status"] = "TIMEOUT"
            resultado["erro"] = "Importação excedeu tempo limite"
        except Exception as e:
            resultado["status"] = "ERRO"
            resultado["erro"] = str(e)
        
        self.resultados["validacoes"].append(resultado)
        return resultado
    
    def criar_backup_estado(self):
        """Criar backup do estado atual"""
        backup_dir = f"backup_etapa1_{self.timestamp}"
        resultado = {
            "id": "BACKUP",
            "tipo": "backup_estado",
            "diretorio": backup_dir,
            "status": "INICIADO"
        }
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            arquivos_criticos = [
                "system_core/ncnt_orchestrator_complete.py",
                "requirements.txt",
                "README.md"
            ]
            
            for arquivo in arquivos_criticos:
                if os.path.exists(arquivo):
                    dest = os.path.join(backup_dir, arquivo)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(arquivo, 'rb') as src, open(dest, 'wb') as dst:
                        dst.write(src.read())
            
            resultado["arquivos_backup"] = len(arquivos_criticos)
            resultado["status"] = "BACKUP CRIADO"
            
        except Exception as e:
            resultado["status"] = "ERRO NO BACKUP"
            resultado["erro"] = str(e)
        
        self.resultados["correcoes_aplicadas"].append(resultado)
        return resultado
    
    def gerar_relatorio_execucao(self):
        """Gerar relatório JSON da execução"""
        correcoes_ok = all(
            c.get("status") in ["CORRIGIDO", "VALIDADO", "BACKUP CRIADO"] 
            for c in self.resultados["correcoes_aplicadas"]
        )
        
        validacoes_ok = all(
            v.get("status") in ["IMPORTAÇÃO VALIDADA", "NENHUMA VULNERABILIDADE ENCONTRADA"]
            for v in self.resultados["validacoes"]
        )
        
        if correcoes_ok and validacoes_ok:
            self.resultados["veredito_final"] = "APROVADO"
        else:
            self.resultados["veredito_final"] = "REPROVADO"
        
        relatorio_file = f"relatorio_etapa1_{self.timestamp}.json"
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        return relatorio_file
    
    def executar_etapa_completa(self):
        """Executar toda a etapa 1"""
        print("=" * 60)
        print("🏁 INICIANDO ETAPA 1 - CORREÇÃO DE BLOQUEADORES CRÍTICOS")
        print("=" * 60)
        
        print("\n📦 1. Criando backup do estado atual...")
        backup_result = self.criar_backup_estado()
        print(f"   ✅ {backup_result['status']}")
        
        print("\n🔍 2. Verificando BOM no arquivo crítico...")
        bom_result = self.verificar_bom_arquivo_critico()
        print(f"   ✅ {bom_result['status']}")
        if bom_result.get('acao_tomada'):
            print(f"   📝 {bom_result['acao_tomada']}")
        
        print("\n🛡️ 3. Executando scan de segurança...")
        security_result = self.scan_seguranca_arquivos()
        print(f"   ✅ {security_result['status']}")
        
        print("\n🧪 4. Validando importação do sistema...")
        import_result = self.validar_importacao_sistema()
        print(f"   ✅ {import_result['status']}")
        
        print("\n📊 5. Gerando relatório de execução...")
        relatorio = self.gerar_relatorio_execucao()
        print(f"   ✅ Relatório salvo em: {relatorio}")
        
        print("\n" + "=" * 60)
        print("🎯 RESULTADO FINAL DA ETAPA 1")
        print("=" * 60)
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"📁 Projeto: {self.resultados['projeto']}")
        print(f"🏷️ Etapa: {self.resultados['etapa']}")
        print(f"📊 Veredito: {self.resultados['veredito_final']}")
        print(f"✅ Correções aplicadas: {len(self.resultados['correcoes_aplicadas'])}")
        print(f"✅ Validações realizadas: {len(self.resultados['validacoes'])}")
        
        if self.resultados["veredito_final"] == "APROVADO":
            print("\n🚀 ETAPA 1 CONCLUÍDA COM SUCESSO!")
            print("📈 Próximo passo: ARCH-001 (Consolidar Executores MT5)")
        else:
            print("\n⚠️ ETAPA 1 COM PROBLEMAS - VERIFICAR RELATÓRIO")
        
        return self.resultados["veredito_final"]

if __name__ == "__main__":
    executor = Etapa1Executor()
    resultado = executor.executar_etapa_completa()
    sys.exit(0 if resultado == "APROVADO" else 1)
