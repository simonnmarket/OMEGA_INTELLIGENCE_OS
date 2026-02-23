#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLOCO 1: ANÁLISE E IDENTIFICAÇÃO - ARCH-001
Fases 1-2: Identificação e análise funcional de executores MT5
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ARCH001Analise:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()
        
        # Estado da análise
        self.resultados_analise = {
            "metadata": {
                "projeto": "AURORA v5.1",
                "etapa": "ARCH-001 - BLOCO 1",
                "timestamp": datetime.now().isoformat(),
                "sessao_id": f"ARCH001_B1_{self.timestamp}",
                "criticidade": "ANALISE",
                "dependencias": ["Nenhuma"],
                "output_esperado": "checkpoint_analise.json"
            },
            
            "fase_analise": {
                "status": "INICIADO",
                "executores_encontrados": [],
                "analise_funcional": {},
                "diretorios_verificados": [],
                "total_encontrados": 0,
                "recomendacoes_analise": []
            },
            
            "estatisticas": {
                "inicio_analise": datetime.now().isoformat(),
                "diretorio_execucao": os.getcwd(),
                "python_version": sys.version,
                "hash_self": None
            }
        }
        
        # Calcular hash do próprio script
        self.resultados_analise["estatisticas"]["hash_self"] = self.calcular_hash_arquivo(__file__)
    
    def setup_logging(self):
        """Configurar logging para o bloco 1"""
        self.log_dir = "logs_arch001_bloco1"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, f"analise_{self.timestamp}.log")
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ARCH-001 BLOCO 1 - ANÁLISE - {datetime.now().isoformat()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, mensagem, nivel="INFO", etapa="ANALISE"):
        """Registrar mensagem no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        linha = f"[{timestamp}] [{nivel}] [{etapa}] {mensagem}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(linha + "\n")
        
        # Console colorido
        cores = {
            "INFO": "\033[94m",      # Azul
            "SUCCESS": "\033[92m",   # Verde
            "WARNING": "\033[93m",   # Amarelo
            "ERROR": "\033[91m",     # Vermelho
        }
        reset = "\033[0m"
        
        if nivel in cores and sys.stdout.isatty():
            print(f"{cores[nivel]}{linha}{reset}")
        else:
            print(linha)
    
    def identificar_executores_mt5(self):
        """Fase 1: Identificação completa de executores MT5"""
        self.log("Fase 1: Identificando executores MT5...", "INFO", "IDENTIFICACAO")
        
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
        
        # Busca inteligente por diretórios prováveis
        diretorios_alvo = [
            ".",
            "./executors",
            "./mt5_executors", 
            "./trading",
            "./system_core",
            "./core",
            "./src",
            "./04-Infraestrutura",
            "./04-Infrastructure"
        ]
        
        for dir_alvo in diretorios_alvo:
            if os.path.exists(dir_alvo):
                self.log(f"Buscando em: {dir_alvo}", "INFO", "IDENTIFICACAO")
                
                for root, dirs, files in os.walk(dir_alvo):
                    # Ignorar diretórios do sistema
                    dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".idea", "node_modules", "BACKUPS", "backups"]]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            diretorios_verificados.append(root)
                            
                            # Verificar por nome do arquivo
                            encontrado_nome = any(padrao in file for padrao in padroes_nomes)
                            
                            # Verificar por conteúdo
                            encontrado_conteudo = False
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    conteudo = f.read(5000)
                                    encontrado_conteudo = any(padrao in conteudo for padrao in padroes_conteudo)
                            except:
                                continue
                            
                            if encontrado_nome or encontrado_conteudo:
                                # Coletar informações detalhadas
                                info = {
                                    "arquivo": file_path,
                                    "nome": file,
                                    "diretorio": root,
                                    "tamanho_bytes": os.path.getsize(file_path),
                                    "linhas": self.contar_linhas(file_path),
                                    "encontrado_por": "NOME" if encontrado_nome else "CONTEUDO",
                                    "padroes_detectados": []
                                }
                                
                                # Detectar padrões específicos
                                for padrao in padroes_conteudo:
                                    if padrao in conteudo:
                                        info["padroes_detectados"].append(padrao)
                                
                                # Calcular hash para identificação única
                                info["hash_md5"] = self.calcular_hash_arquivo(file_path, "md5")
                                
                                executores_encontrados.append(info)
                                self.log(f"Encontrado: {file_path} ({info['tamanho_bytes']} bytes)", "SUCCESS", "IDENTIFICACAO")
        
        # Remover duplicatas por hash
        executores_unicos = []
        hashes_vistos = set()
        
        for executor in executores_encontrados:
            if executor["hash_md5"] not in hashes_vistos:
                executores_unicos.append(executor)
                hashes_vistos.add(executor["hash_md5"])
            else:
                self.log(f"Duplicata ignorada: {executor['arquivo']}", "WARNING", "IDENTIFICACAO")
        
        self.resultados_analise["fase_analise"]["executores_encontrados"] = executores_unicos
        self.resultados_analise["fase_analise"]["diretorios_verificados"] = list(set(diretorios_verificados))
        self.resultados_analise["fase_analise"]["total_encontrados"] = len(executores_unicos)
        
        self.log(f"Identificação concluída: {len(executores_unicos)} executores únicos encontrados", "SUCCESS", "IDENTIFICACAO")
        return executores_unicos
    
    def analisar_funcionalidades_executores(self, executores):
        """Fase 2: Análise detalhada de funcionalidades"""
        self.log("Fase 2: Analisando funcionalidades dos executores...", "INFO", "ANALISE_FUNCIONAL")
        
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
                
                # Análise de funcionalidades específicas MT5
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
                
                # Calcular score funcional
                score = sum(1 for func, presente in funcionalidades_mt5.items() if presente)
                analise["score_funcional"] = score
                analise["complexidade"] = len(conteudo.split('\n'))
                
                # Identificar classes
                linhas = conteudo.split('\n')
                for i, linha in enumerate(linhas):
                    if "class " in linha and "(" in linha:
                        nome_classe = linha.split("class ")[1].split("(")[0].strip()
                        analise["classes"].append({
                            "nome": nome_classe,
                            "linha": i + 1
                        })
                
                # Identificar funções principais
                for i, linha in enumerate(linhas):
                    if "def " in linha and "(" in linha and "):" in linha:
                        nome_funcao = linha.split("def ")[1].split("(")[0].strip()
                        if not nome_funcao.startswith("_"):  # Ignorar funções privadas
                            analise["funcoes"].append({
                                "nome": nome_funcao,
                                "linha": i + 1
                            })
                
                # Identificar dependências
                import_keywords = ["import ", "from "]
                for linha in linhas:
                    linha_stripped = linha.strip()
                    if any(kw in linha_stripped for kw in import_keywords):
                        # Verificar se não é comentário
                        if not linha_stripped.startswith("#"):
                            analise["dependencias"].append(linha_stripped)
                
                self.log(f"Análise concluída: {arquivo} (score: {score}/20)", "INFO", "ANALISE_FUNCIONAL")
                
            except Exception as e:
                analise["erro_analise"] = str(e)
                self.log(f"Erro na análise de {arquivo}: {e}", "ERROR", "ANALISE_FUNCIONAL")
            
            analise_detalhada[arquivo] = analise
        
        self.resultados_analise["fase_analise"]["analise_funcional"] = analise_detalhada
        
        # Recomendações baseadas na análise
        recomendacoes = []
        if len(executores) > 1:
            recomendacoes.append(f"Consolidar {len(executores)} executores em um único")
        
        # Identificar o executor mais completo
        if analise_detalhada:
            executor_completo = max(analise_detalhada.items(), 
                                  key=lambda x: x[1]["score_funcional"])
            recomendacoes.append(f"Manter como principal: {executor_completo[0]}")
        
        self.resultados_analise["fase_analise"]["recomendacoes_analise"] = recomendacoes
        self.resultados_analise["fase_analise"]["status"] = "COMPLETO"
        
        self.log("Análise funcional concluída", "SUCCESS", "ANALISE_FUNCIONAL")
        
        return analise_detalhada
    
    def gerar_checkpoint_analise(self):
        """Gerar checkpoint JSON com resultados da análise"""
        checkpoint_file = f"checkpoint_analise_{self.timestamp}.json"
        
        # Adicionar metadata final
        self.resultados_analise["estatisticas"]["fim_analise"] = datetime.now().isoformat()
        self.resultados_analise["metadata"]["status"] = "COMPLETO"
        
        # Salvar checkpoint
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados_analise, f, indent=2, ensure_ascii=False)
        
        self.log(f"Checkpoint gerado: {checkpoint_file}", "SUCCESS", "CHECKPOINT")
        self.log(f"Total arquivos analisados: {self.resultados_analise['fase_analise']['total_encontrados']}", "INFO", "RESUMO")
        
        return checkpoint_file
    
    # ========== UTILITÁRIOS ==========
    
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
    
    def executar_analise_completa(self):
        """Executar análise completa (Fases 1-2)"""
        self.log("🚀 INICIANDO BLOCO 1: ANÁLISE E IDENTIFICAÇÃO", "INFO", "INICIO")
        self.log(f"Timestamp: {self.timestamp}", "INFO", "INICIO")
        
        try:
            # Fase 1: Identificação
            executores = self.identificar_executores_mt5()
            
            if not executores:
                self.log("Nenhum executor MT5 encontrado!", "WARNING", "ANALISE")
                return self.gerar_checkpoint_analise()
            
            # Fase 2: Análise funcional
            self.analisar_funcionalidades_executores(executores)
            
            # Gerar checkpoint
            checkpoint = self.gerar_checkpoint_analise()
            
            # Resumo
            self.log("\n" + "=" * 60, "INFO", "RESUMO")
            self.log("📊 RESUMO DA ANÁLISE:", "SUCCESS", "RESUMO")
            self.log(f"  • Executores encontrados: {len(executores)}", "INFO", "RESUMO")
            
            if executores:
                for i, executor in enumerate(executores, 1):
                    self.log(f"  {i}. {executor['arquivo']} ({executor['tamanho_bytes']} bytes)", "INFO", "RESUMO")
            
            self.log(f"📁 Checkpoint salvo em: {checkpoint}", "SUCCESS", "RESUMO")
            self.log("✅ BLOCO 1 CONCLUÍDO - Pronto para BLOCO 2", "SUCCESS", "FINAL")
            
            return checkpoint
            
        except Exception as e:
            self.log(f"❌ ERRO no BLOCO 1: {e}", "ERROR", "ERRO")
            self.resultados_analise["fase_analise"]["status"] = "ERRO"
            self.resultados_analise["fase_analise"]["erro"] = str(e)
            self.gerar_checkpoint_analise()
            raise


def main():
    """Função principal do Bloco 1"""
    print("\n" + "=" * 70)
    print("ARCH-001 - BLOCO 1: ANÁLISE E IDENTIFICAÇÃO")
    print("Fases 1-2: Identificar e analisar executores MT5")
    print("=" * 70)
    
    # Verificar diretório
    if not os.path.exists("."):
        print("❌ ERRO: Não é possível acessar o diretório atual!")
        return 1
    
    print("\n📋 Este bloco executará:")
    print("   1. Identificação de todos os executores MT5")
    print("   2. Análise funcional detalhada")
    print("   3. Geração de checkpoint para próximo bloco")
    
    # Execução automática (sem interação)
    print("\n🚀 Iniciando análise automaticamente...")
    
    try:
        analisador = ARCH001Analise()
        checkpoint = analisador.executar_analise_completa()
        
        print(f"\n✅ BLOCO 1 CONCLUÍDO COM SUCESSO")
        print(f"📄 Checkpoint: {checkpoint}")
        print(f"📁 Logs: logs_arch001_bloco1/")
        print("\n➡️  PRÓXIMO: Executar BLOCO 2 (Backup e Seleção)")
        print("   Usar checkpoint gerado como entrada")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("📁 Verifique logs em logs_arch001_bloco1/")
        return 1


if __name__ == "__main__":
    sys.exit(main())

