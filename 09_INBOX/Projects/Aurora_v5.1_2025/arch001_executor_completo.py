#!/usr/bin/env python3
"""
ARCH-001: CONSOLIDAR EXECUTORES MT5 - AURORA v5.1
CEO + CTO + CKO Implementation Protocol - Enhanced Surgical Edition
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path

class ARCH001Executor:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()
        
        # Estado completo do sistema
        self.resultados = {
            "metadata": {
                "projeto": "AURORA v5.1",
                "etapa": "ARCH-001",
                "timestamp": datetime.now().isoformat(),
                "sessao_id": f"ARCH001_{self.timestamp}",
                "metodologia": "CONSOLIDACAO_CIRURGICA",
                "criticidade": "ALTA",
                "backup_obrigatorio": True,
                "validacao_obrigatoria": True
            },
            
            "fase_analise": {
                "status": "INICIADO",
                "executores_encontrados": [],
                "analise_funcional": {},
                "dependencias_mapeadas": [],
                "conflictos_identificados": [],
                "metrica_completude": 0,
                "recomendacoes_analise": []
            },
            
            "fase_backup": {
                "status": "PENDENTE",
                "backup_dir": None,
                "arquivos_backupeados": [],
                "hash_backup": None,
                "tamanho_backup_mb": 0
            },
            
            "fase_consolidacao": {
                "status": "PENDENTE",
                "executor_principal": None,
                "executores_removidos": [],
                "executores_mantidos": [],
                "alteracoes_realizadas": [],
                "dependencias_atualizadas": [],
                "riscos_mitigados": []
            },
            
            "fase_validacao": {
                "status": "PENDENTE",
                "testes_realizados": [],
                "importacoes_validadas": [],
                "funcionalidades_testadas": [],
                "erros_encontrados": [],
                "taxa_sucesso": 0
            },
            
            "resultado_final": {
                "veredito": "PENDENTE",
                "pontuacao_consolidacao": 0,
                "sistema_operacional": False,
                "pronto_proxima_etapa": False,
                "recomendacoes_finais": [],
                "hash_integridade": None
            }
        }
    
    def setup_logging(self):
        """Configurar logging estruturado para auditoria"""
        self.log_dir = "logs_arch001"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, f"execucao_{self.timestamp}.log")
        self.audit_file = os.path.join(self.log_dir, f"auditoria_{self.timestamp}.json")
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ARCH-001 - CONSOLIDACAO MT5 - {datetime.now().isoformat()}\n")
            f.write(f"Diretorio: {os.getcwd()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, mensagem, nivel="INFO", etapa=None):
        """Registrar mensagem no log com estrutura completa"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if etapa:
            prefixo = f"[{timestamp}] [{nivel}] [{etapa}]"
        else:
            prefixo = f"[{timestamp}] [{nivel}]"
        
        linha = f"{prefixo} {mensagem}"
        
        # Log para arquivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(linha + "\n")
        
        # Log para console
        print(linha)
    
    def identificar_executores_mt5(self):
        """Fase 1: Identificação completa de executores MT5"""
        self.log("Fase 1: Identificando executores MT5...", "INFO", "ANALISE")
        
        padroes_nomes = [
            "mt5_executor.py",
            "MT5Executor.py",
            "mt5_executor_v",
            "mt5_executor_",
            "executor_mt5",
            "mt5executor",
            "mt5_exec",
            "MT5_EXEC",
            "MT5NoStopsExecutor",
            "MT5_STOPS_FIX",
            "MT5LimitExecutor",
            "MT5MarketExecutor"
        ]
        
        padroes_conteudo = [
            "import MetaTrader5",
            "import mt5",
            "mt5.initialize",
            "mt5.symbol_select",
            "mt5.order_send",
            "MT5_TIMEOUT",
            "MT5_DEVIATION"
        ]
        
        executores_encontrados = []
        diretorios_verificados = []
        
        diretorios_alvo = [
            ".",
            "./executors",
            "./mt5_executors", 
            "./trading",
            "./system_core",
            "./core",
            "./src"
        ]
        
        for dir_alvo in diretorios_alvo:
            if os.path.exists(dir_alvo):
                self.log(f"Buscando em: {dir_alvo}", "INFO", "ANALISE")
                
                for root, dirs, files in os.walk(dir_alvo):
                    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".idea", "node_modules"]]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            diretorios_verificados.append(root)
                            
                            encontrado_nome = any(padrao in file for padrao in padroes_nomes)
                            
                            encontrado_conteudo = False
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    conteudo = f.read(5000)
                                    encontrado_conteudo = any(padrao in conteudo for padrao in padroes_conteudo)
                            except:
                                continue
                            
                            if encontrado_nome or encontrado_conteudo:
                                info = {
                                    "arquivo": file_path,
                                    "nome": file,
                                    "diretorio": root,
                                    "tamanho_bytes": os.path.getsize(file_path),
                                    "linhas": self.contar_linhas(file_path),
                                    "encontrado_por": "NOME" if encontrado_nome else "CONTEUDO",
                                    "padroes_detectados": []
                                }
                                
                                for padrao in padroes_conteudo:
                                    if padrao in conteudo:
                                        info["padroes_detectados"].append(padrao)
                                
                                info["hash_md5"] = self.calcular_hash_arquivo(file_path, "md5")
                                
                                executores_encontrados.append(info)
                                self.log(f"Encontrado: {file_path} ({info['tamanho_bytes']} bytes)", "SUCCESS", "ANALISE")
        
        # Remover duplicatas por hash
        executores_unicos = []
        hashes_vistos = set()
        
        for executor in executores_encontrados:
            if executor["hash_md5"] not in hashes_vistos:
                executores_unicos.append(executor)
                hashes_vistos.add(executor["hash_md5"])
            else:
                self.log(f"Duplicata ignorada: {executor['arquivo']}", "WARNING", "ANALISE")
        
        self.resultados["fase_analise"]["executores_encontrados"] = executores_unicos
        self.resultados["fase_analise"]["diretorios_verificados"] = list(set(diretorios_verificados))
        self.resultados["fase_analise"]["total_encontrados"] = len(executores_unicos)
        
        self.log(f"Identificação concluída: {len(executores_unicos)} executores únicos encontrados", "SUCCESS", "ANALISE")
        return executores_unicos
    
    def analisar_funcionalidades_executores(self, executores):
        """Fase 2: Análise detalhada de funcionalidades"""
        self.log("Fase 2: Analisando funcionalidades dos executores...", "INFO", "ANALISE")
        
        analise_detalhada = {}
        
        for executor in executores:
            arquivo = executor["arquivo"]
            analise = {
                "arquivo": arquivo,
                "funcionalidades": {},
                "classes": [],
                "funcoes": [],
                "dependencias": [],
                "complexidade": 0,
                "score_funcional": 0
            }
            
            try:
                with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()
                
                funcionalidades_mt5 = {
                    "order_send": "mt5.order_send" in conteudo,
                    "positions_get": "mt5.positions_get" in conteudo,
                    "orders_get": "mt5.orders_get" in conteudo,
                    "symbol_info": "mt5.symbol_info" in conteudo,
                    "account_info": "mt5.account_info" in conteudo,
                    "initialize": "mt5.initialize" in conteudo,
                    "shutdown": "mt5.shutdown" in conteudo,
                    "has_stops": "stop_loss" in conteudo.lower() or "sl=" in conteudo.lower(),
                    "has_limits": "take_profit" in conteudo.lower() or "tp=" in conteudo.lower(),
                    "has_deviation": "deviation" in conteudo.lower(),
                    "has_magic": "magic" in conteudo.lower(),
                    "has_comment": "comment" in conteudo.lower(),
                    "has_slippage": "slippage" in conteudo.lower(),
                    "has_timeout": "timeout" in conteudo.lower(),
                    "has_retry": "retry" in conteudo.lower() or "retries" in conteudo.lower(),
                    "has_logging": "logging" in conteudo.lower() or "logger" in conteudo.lower(),
                    "has_error_handling": "try:" in conteudo and "except" in conteudo,
                    "has_validation": "validate" in conteudo.lower() or "check" in conteudo.lower()
                }
                
                analise["funcionalidades"] = funcionalidades_mt5
                
                score = sum(1 for func, presente in funcionalidades_mt5.items() if presente)
                analise["score_funcional"] = score
                analise["complexidade"] = len(conteudo.split('\n'))
                
                linhas = conteudo.split('\n')
                for i, linha in enumerate(linhas):
                    if "class " in linha and "(" in linha:
                        nome_classe = linha.split("class ")[1].split("(")[0].strip()
                        analise["classes"].append({
                            "nome": nome_classe,
                            "linha": i + 1
                        })
                
                for i, linha in enumerate(linhas):
                    if "def " in linha and "(" in linha and "):" in linha:
                        nome_funcao = linha.split("def ")[1].split("(")[0].strip()
                        if not nome_funcao.startswith("_"):
                            analise["funcoes"].append({
                                "nome": nome_funcao,
                                "linha": i + 1
                            })
                
                import_keywords = ["import ", "from "]
                for linha in linhas:
                    if any(kw in linha for kw in import_keywords) and "#" not in linha.split(kw)[0]:
                        analise["dependencias"].append(linha.strip())
                
                self.log(f"Análise concluída: {arquivo} (score: {score}/20)", "INFO", "ANALISE")
                
            except Exception as e:
                analise["erro_analise"] = str(e)
                self.log(f"Erro na análise de {arquivo}: {e}", "ERROR", "ANALISE")
            
            analise_detalhada[arquivo] = analise
        
        self.resultados["fase_analise"]["analise_funcional"] = analise_detalhada
        
        recomendacoes = []
        if len(executores) > 1:
            recomendacoes.append(f"Consolidar {len(executores)} executores em um único")
        
        if analise_detalhada:
            executor_completo = max(analise_detalhada.items(), 
                                  key=lambda x: x[1]["score_funcional"])
            recomendacoes.append(f"Manter como principal: {executor_completo[0]}")
        
        self.resultados["fase_analise"]["recomendacoes_analise"] = recomendacoes
        self.log("Análise funcional concluída", "SUCCESS", "ANALISE")
        
        return analise_detalhada
    
    def criar_backup_completo(self):
        """Fase 3: Criar backup completo antes de qualquer alteração"""
        self.log("Fase 3: Criando backup completo do sistema...", "INFO", "BACKUP")
        
        backup_dir = f"backup_pre_arch001_{self.timestamp}"
        backup_zip = f"{backup_dir}.zip"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            arquivos_backupeados = []
            
            executores = self.resultados["fase_analise"]["executores_encontrados"]
            for executor in executores:
                src = executor["arquivo"]
                if os.path.exists(src):
                    rel_path = os.path.relpath(src, ".")
                    dst = os.path.join(backup_dir, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    arquivos_backupeados.append(rel_path)
            
            config_files = [
                "requirements.txt",
                "config/settings.py",
                "config/mt5_config.py",
                ".env",
                "config.json",
                "settings.json"
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    dst = os.path.join(backup_dir, config_file)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(config_file, dst)
                    arquivos_backupeados.append(config_file)
            
            estrutura_file = os.path.join(backup_dir, "ESTRUTURA_BACKUP.txt")
            with open(estrutura_file, 'w', encoding='utf-8') as f:
                f.write("ESTRUTURA DE BACKUP - ARCH-001\n")
                f.write(f"Data: {datetime.now().isoformat()}\n")
                f.write(f"Timestamp: {self.timestamp}\n\n")
                f.write("ARQUIVOS BACKUPEADOS:\n")
                for arquivo in sorted(arquivos_backupeados):
                    f.write(f"  - {arquivo}\n")
                
                f.write("\nEXECUTORES IDENTIFICADOS:\n")
                for executor in executores:
                    f.write(f"  - {executor['arquivo']} ({executor['tamanho_bytes']} bytes)\n")
            
            hash_backup = self.calcular_hash_diretorio(backup_dir)
            
            shutil.make_archive(backup_dir, 'zip', backup_dir)
            tamanho_mb = os.path.getsize(backup_zip) / (1024 * 1024)
            
            shutil.rmtree(backup_dir)
            
            self.resultados["fase_backup"].update({
                "status": "COMPLETO",
                "backup_dir": backup_zip,
                "arquivos_backupeados": arquivos_backupeados,
                "hash_backup": hash_backup,
                "tamanho_backup_mb": round(tamanho_mb, 2),
                "timestamp_backup": datetime.now().isoformat()
            })
            
            self.log(f"Backup criado com sucesso: {backup_zip} ({tamanho_mb:.2f} MB)", "SUCCESS", "BACKUP")
            self.log(f"Hash de integridade: {hash_backup}", "INFO", "BACKUP")
            
            return backup_zip
            
        except Exception as e:
            self.resultados["fase_backup"]["status"] = "ERRO"
            self.resultados["fase_backup"]["erro"] = str(e)
            self.log(f"ERRO ao criar backup: {e}", "CRITICAL", "BACKUP")
            raise
    
    def executar_consolidacao_cirurgica(self):
        """Fase 4: Executar consolidação cirúrgica dos executores"""
        self.log("Fase 4: Executando consolidação cirúrgica...", "INFO", "CONSOLIDACAO")
        
        executores = self.resultados["fase_analise"]["executores_encontrados"]
        analise = self.resultados["fase_analise"]["analise_funcional"]
        
        if len(executores) <= 1:
            self.log("Nenhuma consolidação necessária - apenas 1 executor encontrado", "WARNING", "CONSOLIDACAO")
            
            self.resultados["fase_consolidacao"].update({
                "status": "NAO_NECESSARIO",
                "executor_principal": executores[0]["arquivo"] if executores else None,
                "executores_removidos": [],
                "executores_mantidos": [e["arquivo"] for e in executores],
                "alteracoes_realizadas": ["Nenhuma alteração necessária"]
            })
            
            return False
        
        executor_principal = None
        maior_score = -1
        
        for arquivo, dados in analise.items():
            score = dados["score_funcional"]
            if score > maior_score:
                maior_score = score
                executor_principal = arquivo
        
        if not executor_principal:
            executor_principal = max(executores, key=lambda x: x["tamanho_bytes"])["arquivo"]
        
        self.log(f"Executor principal selecionado: {executor_principal}", "SUCCESS", "CONSOLIDACAO")
        
        executores_remover = []
        for executor in executores:
            if executor["arquivo"] != executor_principal:
                executores_remover.append(executor["arquivo"])
        
        alteracoes = []
        removidos_com_sucesso = []
        
        for executor_remover in executores_remover:
            try:
                if os.path.exists(executor_remover):
                    backup_individual = f"{executor_remover}.backup_{self.timestamp}"
                    shutil.copy2(executor_remover, backup_individual)
                    
                    os.remove(executor_remover)
                    
                    if not os.path.exists(executor_remover):
                        removidos_com_sucesso.append(executor_remover)
                        alteracoes.append(f"Removido: {executor_remover} (backup: {backup_individual})")
                        self.log(f"Removido com sucesso: {executor_remover}", "INFO", "CONSOLIDACAO")
                    else:
                        self.log(f"Falha ao remover: {executor_remover}", "ERROR", "CONSOLIDACAO")
                else:
                    self.log(f"Arquivo já não existe: {executor_remover}", "WARNING", "CONSOLIDACAO")
                    
            except Exception as e:
                self.log(f"Erro ao remover {executor_remover}: {e}", "ERROR", "CONSOLIDACAO")
        
        dependencias_atualizadas = self.atualizar_referencias_executor(executor_principal, executores_remover)
        
        self.resultados["fase_consolidacao"].update({
            "status": "COMPLETO",
            "executor_principal": executor_principal,
            "executores_removidos": removidos_com_sucesso,
            "executores_mantidos": [executor_principal],
            "alteracoes_realizadas": alteracoes,
            "dependencias_atualizadas": dependencias_atualizadas,
            "riscos_mitigados": ["Backup completo criado", "Validação pós-operação agendada"]
        })
        
        self.log(f"Consolidação concluída: {len(removidos_com_sucesso)} executores removidos", "SUCCESS", "CONSOLIDACAO")
        return True
    
    def atualizar_referencias_executor(self, executor_principal, executores_removidos):
        """Atualizar referências aos executores removidos"""
        self.log("Atualizando referências e dependências...", "INFO", "CONSOLIDACAO")
        
        atualizacoes = []
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "logs_arch001"]]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            conteudo = f.read()
                        
                        conteudo_atualizado = conteudo
                        modificado = False
                        
                        for executor_removido in executores_removidos:
                            nome_base = os.path.basename(executor_removido).replace('.py', '')
                            nome_principal = os.path.basename(executor_principal).replace('.py', '')
                            
                            padroes = [
                                f"import {nome_base}",
                                f"from {nome_base}",
                                f"import.*{nome_base}",
                                f"from.*{nome_base}"
                            ]
                            
                            for padrao in padroes:
                                if padrao in conteudo:
                                    conteudo_atualizado = conteudo_atualizado.replace(
                                        nome_base, nome_principal
                                    )
                                    modificado = True
                        
                        if modificado:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(conteudo_atualizado)
                            
                            atualizacoes.append(file_path)
                            self.log(f"Atualizado: {file_path}", "INFO", "CONSOLIDACAO")
                            
                    except Exception as e:
                        self.log(f"Erro ao atualizar {file_path}: {e}", "ERROR", "CONSOLIDACAO")
        
        return atualizacoes
    
    def validar_consolidacao(self):
        """Fase 5: Validação completa pós-consolidação"""
        self.log("Fase 5: Validando consolidação...", "INFO", "VALIDACAO")
        
        executor_principal = self.resultados["fase_consolidacao"]["executor_principal"]
        testes = []
        importacoes = []
        funcionalidades = []
        erros = []
        
        teste1 = {
            "nome": "Existência executor principal",
            "status": "PENDENTE",
            "detalhes": ""
        }
        
        if executor_principal and os.path.exists(executor_principal):
            teste1["status"] = "APROVADO"
            teste1["detalhes"] = f"Arquivo encontrado: {executor_principal}"
        else:
            teste1["status"] = "REPROVADO"
            teste1["detalhes"] = f"Arquivo não encontrado: {executor_principal}"
            erros.append(teste1["detalhes"])
        
        testes.append(teste1)
        
        executores_removidos = self.resultados["fase_consolidacao"]["executores_removidos"]
        for executor_removido in executores_removidos:
            teste = {
                "nome": f"Remoção de {os.path.basename(executor_removido)}",
                "status": "PENDENTE",
                "detalhes": ""
            }
            
            if not os.path.exists(executor_removido):
                teste["status"] = "APROVADO"
                teste["detalhes"] = "Arquivo removido com sucesso"
            else:
                teste["status"] = "REPROVADO"
                teste["detalhes"] = "Arquivo ainda existe"
                erros.append(teste["detalhes"])
            
            testes.append(teste)
        
        if executor_principal and os.path.exists(executor_principal):
            teste_import = {
                "nome": "Importação do executor principal",
                "status": "PENDENTE",
                "detalhes": ""
            }
            
            try:
                spec = importlib.util.spec_from_file_location(
                    "mt5_executor_temp", 
                    executor_principal
                )
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                
                teste_import["status"] = "APROVADO"
                teste_import["detalhes"] = "Importação bem-sucedida"
                importacoes.append(f"✅ {executor_principal}")
                
            except Exception as e:
                teste_import["status"] = "REPROVADO"
                teste_import["detalhes"] = f"Erro na importação: {str(e)}"
                erros.append(teste_import["detalhes"])
            
            testes.append(teste_import)
        
        if executor_principal and os.path.exists(executor_principal):
            try:
                with open(executor_principal, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                funcs_verificadas = {
                    "MetaTrader5 import": "import MetaTrader5" in conteudo or "import mt5" in conteudo,
                    "Função de envio de ordem": "order_send" in conteudo or "send_order" in conteudo,
                    "Manipulação de posições": "positions_get" in conteudo or "get_positions" in conteudo,
                    "Controle de erros": "try:" in conteudo and "except" in conteudo,
                    "Logging": "logging" in conteudo or "logger" in conteudo
                }
                
                for func, presente in funcs_verificadas.items():
                    func_test = {
                        "funcionalidade": func,
                        "status": "PRESENTE" if presente else "AUSENTE"
                    }
                    funcionalidades.append(func_test)
                    
                    if not presente:
                        self.log(f"Funcionalidade ausente: {func}", "WARNING", "VALIDACAO")
                
            except Exception as e:
                self.log(f"Erro ao verificar funcionalidades: {e}", "ERROR", "VALIDACAO")
        
        total_testes = len(testes)
        testes_aprovados = sum(1 for t in testes if t["status"] == "APROVADO")
        taxa_sucesso = (testes_aprovados / total_testes * 100) if total_testes > 0 else 0
        
        self.resultados["fase_validacao"].update({
            "status": "COMPLETO",
            "testes_realizados": testes,
            "importacoes_validadas": importacoes,
            "funcionalidades_testadas": funcionalidades,
            "erros_encontrados": erros,
            "taxa_sucesso": round(taxa_sucesso, 1)
        })
        
        self.log(f"Validação concluída: {taxa_sucesso:.1f}% de sucesso", 
                "SUCCESS" if taxa_sucesso >= 80 else "WARNING", 
                "VALIDACAO")
        
        return taxa_sucesso >= 80
    
    def gerar_relatorio_final(self):
        """Fase 6: Gerar relatório final completo"""
        self.log("Fase 6: Gerando relatório final...", "INFO", "RELATORIO")
        
        pontos = 0
        max_pontos = 100
        
        if self.resultados["fase_backup"]["status"] == "COMPLETO":
            pontos += 20
        
        if self.resultados["fase_consolidacao"]["status"] == "COMPLETO":
            pontos += 30
        elif self.resultados["fase_consolidacao"]["status"] == "NAO_NECESSARIO":
            pontos += 15
        
        pontos += min(50, self.resultados["fase_validacao"]["taxa_sucesso"] / 2)
        
        if pontos >= 80:
            veredito = "APROVADO"
            sistema_operacional = True
            pronto_proxima_etapa = True
        elif pontos >= 60:
            veredito = "APROVADO_COM_RESSALVAS"
            sistema_operacional = True
            pronto_proxima_etapa = True
        else:
            veredito = "REPROVADO"
            sistema_operacional = False
            pronto_proxima_etapa = False
        
        recomendacoes = []
        
        if self.resultados["fase_validacao"]["erros_encontrados"]:
            recomendacoes.append("Corrigir erros de validação identificados")
        
        if pontos < 80:
            recomendacoes.append("Executar validação manual adicional")
        
        if not self.resultados["fase_backup"]["backup_dir"]:
            recomendacoes.append("Criar backup manual antes de operações futuras")
        
        relatorio_str = json.dumps(self.resultados, indent=2, ensure_ascii=False)
        hash_integridade = hashlib.sha256(relatorio_str.encode()).hexdigest()
        
        self.resultados["resultado_final"].update({
            "veredito": veredito,
            "pontuacao_consolidacao": round(pontos, 1),
            "sistema_operacional": sistema_operacional,
            "pronto_proxima_etapa": pronto_proxima_etapa,
            "recomendacoes_finais": recomendacoes,
            "hash_integridade": hash_integridade
        })
        
        relatorio_file = f"relatorio_arch001_{self.timestamp}.json"
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        resumo_file = f"resumo_arch001_{self.timestamp}.txt"
        self.gerar_resumo_textual(resumo_file)
        
        with open(self.audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        self.log(f"Relatório salvo em: {relatorio_file}", "SUCCESS", "RELATORIO")
        self.log(f"Resumo salvo em: {resumo_file}", "INFO", "RELATORIO")
        
        return relatorio_file
    
    def gerar_resumo_textual(self, caminho_arquivo):
        """Gerar resumo textual do processo"""
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RESUMO EXECUTIVO - ARCH-001: CONSOLIDAÇÃO MT5\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Projeto: {self.resultados['metadata']['projeto']}\n")
            f.write(f"Etapa: {self.resultados['metadata']['etapa']}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Veredito: {self.resultados['resultado_final']['veredito']}\n")
            f.write(f"Pontuação: {self.resultados['resultado_final']['pontuacao_consolidacao']}/100\n\n")
            
            f.write("📊 ESTATÍSTICAS:\n")
            f.write(f"  • Executores encontrados: {self.resultados['fase_analise']['total_encontrados']}\n")
            f.write(f"  • Executores removidos: {len(self.resultados['fase_consolidacao']['executores_removidos'])}\n")
            f.write(f"  • Executor principal: {self.resultados['fase_consolidacao']['executor_principal']}\n")
            f.write(f"  • Taxa de sucesso: {self.resultados['fase_validacao']['taxa_sucesso']}%\n")
            f.write(f"  • Backup criado: {'Sim' if self.resultados['fase_backup']['backup_dir'] else 'Não'}\n\n")
            
            f.write("✅ TESTES REALIZADOS:\n")
            for teste in self.resultados['fase_validacao']['testes_realizados']:
                status_emoji = "✅" if teste['status'] == 'APROVADO' else "❌"
                f.write(f"  {status_emoji} {teste['nome']}: {teste['status']}\n")
            
            f.write("\n💡 RECOMENDAÇÕES:\n")
            for rec in self.resultados['resultado_final']['recomendacoes_finais']:
                f.write(f"  • {rec}\n")
            
            f.write("\n🚀 PRÓXIMOS PASSOS:\n")
            if self.resultados['resultado_final']['pronto_proxima_etapa']:
                f.write("  • Prosseguir para ARCH-002: Definir ponto de entrada único\n")
            else:
                f.write("  • Corrigir problemas identificados\n")
                f.write("  • Reexecutar validação\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"Hash de integridade: {self.resultados['resultado_final']['hash_integridade']}\n")
            f.write("=" * 80 + "\n")
    
    def executar_arch001_completo(self):
        """Executar todo o processo ARCH-001"""
        self.log("🚀 INICIANDO ARCH-001: CONSOLIDAÇÃO DE EXECUTORES MT5", "INFO", "INICIO")
        self.log(f"Timestamp: {self.timestamp}", "INFO", "INICIO")
        self.log(f"Diretório: {os.getcwd()}", "INFO", "INICIO")
        
        try:
            executores = self.identificar_executores_mt5()
            if not executores:
                self.log("Nenhum executor MT5 encontrado!", "WARNING", "ANALISE")
                return self.gerar_relatorio_final()
            
            self.analisar_funcionalidades_executores(executores)
            self.criar_backup_completo()
            consolidacao_realizada = self.executar_consolidacao_cirurgica()
            
            if consolidacao_realizada:
                validacao_ok = self.validar_consolidacao()
            else:
                validacao_ok = True
            
            relatorio = self.gerar_relatorio_final()
            
            veredito = self.resultados["resultado_final"]["veredito"]
            pontuacao = self.resultados["resultado_final"]["pontuacao_consolidacao"]
            
            self.log("\n" + "=" * 60, "INFO", "FINAL")
            self.log(f"🏁 ARCH-001 CONCLUÍDO", "SUCCESS", "FINAL")
            self.log(f"📊 Pontuação: {pontuacao}/100", "INFO", "FINAL")
            self.log(f"🏷️ Veredito: {veredito}", 
                    "SUCCESS" if veredito == "APROVADO" else "WARNING", "FINAL")
            
            if self.resultados["resultado_final"]["pronto_proxima_etapa"]:
                self.log(f"🚀 Sistema pronto para ARCH-002", "SUCCESS", "FINAL")
            else:
                self.log(f"⚠️ Revisar problemas antes de prosseguir", "WARNING", "FINAL")
            
            return relatorio
            
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO no processo ARCH-001: {e}", "CRITICAL", "ERRO")
            self.resultados["resultado_final"]["veredito"] = "ERRO_CRITICO"
            self.gerar_relatorio_final()
            raise
    
    def contar_linhas(self, arquivo):
        """Contar linhas de um arquivo"""
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def calcular_hash_arquivo(self, arquivo, algoritmo="md5"):
        """Calcular hash de um arquivo"""
        try:
            if algoritmo == "md5":
                hasher = hashlib.md5()
            elif algoritmo == "sha256":
                hasher = hashlib.sha256()
            else:
                hasher = hashlib.md5()
            
            with open(arquivo, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except:
            return None
    
    def calcular_hash_diretorio(self, diretorio):
        """Calcular hash de um diretório completo"""
        hasher = hashlib.sha256()
        
        for root, dirs, files in os.walk(diretorio):
            for file in sorted(files):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
                except:
                    pass
        
        return hasher.hexdigest()

def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("ARCH-001: CONSOLIDAÇÃO DE EXECUTORES MT5 - AURORA v5.1")
    print("CEO + CTO + CKO Implementation Protocol")
    print("=" * 70)
    
    if not os.path.exists("system_core"):
        print("❌ ERRO: Diretório 'system_core' não encontrado!")
        print("   Execute este script no diretório raiz do projeto AURORA.")
        return 1
    
    print("\n⚠️  ATENÇÃO: Esta operação irá:")
    print("   1. Identificar todos os executores MT5")
    print("   2. Criar backup completo do sistema")
    print("   3. Consolidar executores (manter 1, remover duplicatas)")
    print("   4. Validar resultado")
    
    # Execução automática - confirmação automática
    print("\n🔍 Executando automaticamente (confirmação automática)...")
    # resposta = input("\n🔍 Deseja prosseguir? (s/N): ").strip().lower()
    # if resposta not in ['s', 'sim', 'y', 'yes']:
    #     print("❌ Operação cancelada pelo usuário.")
    #     return 0
    
    try:
        executor = ARCH001Executor()
        relatorio = executor.executar_arch001_completo()
        
        print(f"\n📄 Relatório completo salvo em: {relatorio}")
        print("📋 Resumo disponível em arquivo .txt com mesmo timestamp")
        print("📁 Logs disponíveis em: logs_arch001/")
        
        if executor.resultados["resultado_final"]["pronto_proxima_etapa"]:
            print(f"\n✅ ARCH-001 CONCLUÍDO COM SUCESSO")
            print(f"🚀 PRÓXIMO PASSO: ARCH-002 - Definir ponto de entrada único")
        else:
            print(f"\n⚠️ ARCH-001 CONCLUÍDO COM RESSALVAS")
            print(f"📝 Verifique recomendações no relatório")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("📁 Verifique logs em logs_arch001/ para detalhes")
        return 1

if __name__ == "__main__":
    sys.exit(main())

