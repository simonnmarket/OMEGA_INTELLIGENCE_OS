#!/usr/bin/env python3
"""
RED TEAM VALIDATION SCRIPT v2.0 - AURORA v5.1
CEO + CKO Enhanced Validation Protocol
Maximum Potential Implementation
"""

import os
import sys
import hashlib
import importlib.util
import logging
import json
import re
from datetime import datetime
from pathlib import Path

class EnhancedRedTeamValidation:
    def __init__(self):
        self.setup_logging()
        self.resultados = {
            "timestamp": datetime.now().isoformat(),
            "projeto": "AURORA v5.1",
            "versao": "v2.0",
            "testes": {},
            "vulnerabilidades": [],
            "pontuacao": 0,
            "veredito": "PENDENTE",
            "recomendacoes": [],
            "hash_verificacao": None
        }
        
    def setup_logging(self):
        log_file = f'redteam_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            filemode='w'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== INICIANDO VALIDAÇÃO RED TEAM v2.0 ===")
        
    def calcular_hash_arquivo(self, caminho):
        sha256_hash = hashlib.sha256()
        try:
            with open(caminho, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular hash {caminho}: {e}")
            return None
    
    def testar_integracao_critica(self):
        arquivo = "system_core/ncnt_orchestrator_complete.py"
        resultado = {
            "arquivo": arquivo,
            "existe": False,
            "tem_bom": False,
            "import_ok": False,
            "hash": None,
            "tamanho": 0,
            "status": "FALHA",
            "detalhes": []
        }
        
        if not os.path.exists(arquivo):
            resultado["detalhes"].append("Arquivo não encontrado")
            self.resultados["recomendacoes"].append("Criar arquivo crítico")
            self.resultados["testes"]["integracao_critica"] = resultado
            return False
        
        resultado["existe"] = True
        resultado["tamanho"] = os.path.getsize(arquivo)
        resultado["hash"] = self.calcular_hash_arquivo(arquivo)
        
        try:
            with open(arquivo, 'rb') as f:
                resultado["tem_bom"] = f.read(3) == b'\xef\xbb\xbf'
                if resultado["tem_bom"]:
                    resultado["detalhes"].append("BOM detectado")
                    self.resultados["recomendacoes"].append("Remover BOM")
        except Exception as e:
            resultado["detalhes"].append(f"Erro BOM: {e}")

        try:
            spec = importlib.util.spec_from_file_location("ncnt_orchestrator", arquivo)
            if spec and spec.loader:
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                resultado["import_ok"] = True
                resultado["detalhes"].append("Importação OK")
                self.logger.info("Importação bem-sucedida")
        except SyntaxError as e:
            resultado["detalhes"].append(f"SyntaxError: {e}")
            self.resultados["recomendacoes"].append("Corrigir sintaxe")
        except ImportError as e:
            resultado["detalhes"].append(f"ImportError: {e}")
            self.resultados["recomendacoes"].append("Verificar dependências")
        except Exception as e:
            resultado["detalhes"].append(f"Erro: {e}")
            self.resultados["recomendacoes"].append("Investigar erro")
        
        if resultado["existe"] and not resultado["tem_bom"] and resultado["import_ok"]:
            resultado["status"] = "APROVADO"
        elif resultado["existe"] and not resultado["tem_bom"]:
            resultado["status"] = "PARCIAL"
        else:
            resultado["status"] = "FALHA"
            
        self.resultados["testes"]["integracao_critica"] = resultado
        return resultado["status"] == "APROVADO"
    
    def scan_seguranca_completo(self):
        padroes_perigosos = {
            "os.system(": {"tipo": "COMMAND_INJECTION", "severidade": "CRITICA"},
            "eval(": {"tipo": "CODE_INJECTION", "severidade": "CRITICA"},
            "exec(": {"tipo": "CODE_INJECTION", "severidade": "CRITICA"},
            "subprocess.call(": {"tipo": "PROCESS_INJECTION", "severidade": "ALTA"},
            "subprocess.Popen(": {"tipo": "PROCESS_INJECTION", "severidade": "ALTA"},
            "shell=True": {"tipo": "SHELL_INJECTION", "severidade": "ALTA"}
        }

        vulnerabilidades_encontradas = []
        arquivos_verificados = 0
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "node_modules"]]
            
            for file in files:
                if file.endswith('.py'):
                    caminho_completo = os.path.join(root, file)
                    arquivos_verificados += 1
                    
                    try:
                        with open(caminho_completo, 'r', encoding='utf-8', errors='ignore') as f:
                            linha_num = 0
                            for linha in f:
                                linha_num += 1
                                for padrao, info in padroes_perigosos.items():
                                    if padrao in linha:
                                        linha_limpa = linha.split('#')[0].strip()
                                        if padrao in linha_limpa:
                                            vulnerabilidade = {
                                                "arquivo": caminho_completo,
                                                "linha": linha_num,
                                                "tipo": info["tipo"],
                                                "severidade": info["severidade"],
                                                "codigo": linha.strip()
                                            }
                                            vulnerabilidades_encontradas.append(vulnerabilidade)
                    except Exception:
                        continue
        
        resultado = {
            "arquivos_verificados": arquivos_verificados,
            "vulnerabilidades": len(vulnerabilidades_encontradas),
            "detalhes": vulnerabilidades_encontradas,
            "status": "APROVADO" if len(vulnerabilidades_encontradas) == 0 else "FALHA"
        }
        
        self.resultados["testes"]["scan_seguranca"] = resultado
        return len(vulnerabilidades_encontradas) == 0

    def calcular_pontuacao(self):
        pesos = {"integracao_critica": 0.6, "scan_seguranca": 0.4}
        pontuacao = 0
        
        for teste, peso in pesos.items():
            if teste in self.resultados["testes"]:
                if self.resultados["testes"][teste]["status"] == "APROVADO":
                    pontuacao += peso * 100
        
        self.resultados["pontuacao"] = pontuacao
        return pontuacao

    def gerar_veredito(self):
        pontuacao = self.calcular_pontuacao()
        
        if pontuacao >= 90:
            self.resultados["veredito"] = "APROVADO"
        elif pontuacao >= 60:
            self.resultados["veredito"] = "PARCIAL"
        else:
            self.resultados["veredito"] = "REPROVADO"
        
        resultado_str = json.dumps(self.resultados, sort_keys=True)
        self.resultados["hash_verificacao"] = hashlib.sha256(resultado_str.encode()).hexdigest()[:16]
        
        return self.resultados["veredito"]
    
    def executar_validacao_completa(self):
        print("=" * 60)
        print("RED TEAM VALIDATION v2.0 - AURORA v5.1")
        print("=" * 60)
        
        self.testar_integracao_critica()
        self.scan_seguranca_completo()
        
        veredito = self.gerar_veredito()
        
        print(f"\nVeredito Final: {veredito}")
        print(f"Pontuação: {self.resultados['pontuacao']:.1f}/100")
        print(f"Hash: {self.resultados['hash_verificacao']}")
        
        with open(f"redteam_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        return self.resultados

if __name__ == "__main__":
    validator = EnhancedRedTeamValidation()
    resultados = validator.executar_validacao_completa()
    sys.exit(0 if resultados["veredito"] == "APROVADO" else 1)

