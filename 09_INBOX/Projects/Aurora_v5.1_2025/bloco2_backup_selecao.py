#!/usr/bin/env python3
"""
BLOCO 2: BACKUP E SELEÇÃO - ARCH-001
Fase 3: Criar backup completo e selecionar executor principal
Entrada: checkpoint_analise_*.json (do BLOCO 1)
Saída: backup_pre_arch001_*.zip + checkpoint_selecao_*.json
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
from datetime import datetime
from pathlib import Path
import glob

class ARCH001BackupSelecao:
    def __init__(self, checkpoint_path=None):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_path = checkpoint_path
        self.setup_logging()
        
        # Carregar dados do BLOCO 1
        self.dados_analise = self.carregar_checkpoint()
        
        # Estado do BLOCO 2
        self.resultados_selecao = {
            "metadata": {
                "projeto": "AURORA v5.1",
                "etapa": "ARCH-001 - BLOCO 2",
                "timestamp": datetime.now().isoformat(),
                "sessao_id": f"ARCH001_B2_{self.timestamp}",
                "criticidade": "BACKUP_CRITICO",
                "dependencias": ["checkpoint_analise_*.json"],
                "input": checkpoint_path,
                "outputs": ["backup_pre_arch001_*.zip", "checkpoint_selecao_*.json"]
            },
            
            "fase_backup": {
                "status": "INICIADO",
                "backup_dir": None,
                "backup_zip": None,
                "arquivos_backupeados": [],
                "hash_backup": None,
                "tamanho_backup_mb": 0,
                "timestamp_backup": None
            },
            
            "fase_selecao": {
                "status": "PENDENTE",
                "executor_principal": None,
                "executores_candidatos": [],
                "criterios_selecao": {},
                "score_detalhado": {},
                "timestamp_selecao": None
            },
            
            "estatisticas": {
                "inicio_execucao": datetime.now().isoformat(),
                "python_version": sys.version,
                "diretorio_execucao": os.getcwd(),
                "espaco_livre_gb": self.obter_espaco_livre()
            }
        }
    
    def setup_logging(self):
        """Configurar logging para o bloco 2"""
        self.log_dir = "logs_arch001_bloco2"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, f"backup_selecao_{self.timestamp}.log")
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"ARCH-001 BLOCO 2 - BACKUP E SELEÇÃO - {datetime.now().isoformat()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Checkpoint: {self.checkpoint_path}\n")
            f.write("=" * 80 + "\n\n")
    
    def log(self, mensagem, nivel="INFO", etapa="BACKUP"):
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
            "BACKUP": "\033[95m",    # Magenta
            "SELECT": "\033[96m",    # Ciano
        }
        reset = "\033[0m"
        
        cor = cores.get(nivel, "\033[94m")
        if sys.stdout.isatty():
            print(f"{cor}{linha}{reset}")
        else:
            print(linha)
    
    def carregar_checkpoint(self):
        """Carregar checkpoint do BLOCO 1"""
        if not self.checkpoint_path or not os.path.exists(self.checkpoint_path):
            # Tentar encontrar automaticamente
            checkpoints = [f for f in os.listdir('.') 
                          if f.startswith('checkpoint_analise_') and f.endswith('.json')]
            
            if not checkpoints:
                self.log("❌ Nenhum checkpoint do BLOCO 1 encontrado!", "ERROR", "INICIO")
                raise FileNotFoundError("Checkpoint do BLOCO 1 não encontrado!")
            
            self.checkpoint_path = max(checkpoints)  # Mais recente
            self.log(f"Checkpoint auto-encontrado: {self.checkpoint_path}", "INFO", "INICIO")
        
        try:
            with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.log(f"✅ Checkpoint carregado: {self.checkpoint_path}", "SUCCESS", "INICIO")
            self.log(f"   Executores identificados: {dados['fase_analise']['total_encontrados']}", "INFO", "INICIO")
            
            return dados
            
        except Exception as e:
            self.log(f"❌ Erro ao carregar checkpoint: {e}", "ERROR", "INICIO")
            raise
    
    def obter_espaco_livre(self):
        """Obter espaço livre em disco em GB"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.getcwd()), 
                    None, None, 
                    ctypes.pointer(free_bytes)
                )
                return free_bytes.value / (1024**3)
            else:  # Linux/Mac
                stat = os.statvfs('.')
                return (stat.f_bavail * stat.f_frsize) / (1024**3)
        except:
            return None
    
    def criar_backup_completo(self):
        """Criar backup completo baseado na análise do BLOCO 1"""
        self.log("Fase 3: Criando backup completo do sistema...", "BACKUP", "BACKUP")
        
        executores = self.dados_analise["fase_analise"]["executores_encontrados"]
        
        if not executores:
            self.log("⚠️ Nenhum executor para backup!", "WARNING", "BACKUP")
            self.resultados_selecao["fase_backup"]["status"] = "VAZIO"
            return None
        
        backup_dir = f"backup_pre_arch001_{self.timestamp}"
        backup_zip = f"{backup_dir}.zip"
        
        try:
            # Verificar espaço em disco
            espaco_livre = self.obter_espaco_livre()
            if espaco_livre and espaco_livre < 0.5:  # Menos de 500MB
                self.log(f"⚠️ Espaço em disco baixo: {espaco_livre:.2f}GB", "WARNING", "BACKUP")
            
            # Criar estrutura de backup
            os.makedirs(backup_dir, exist_ok=True)
            
            arquivos_backupeados = []
            total_size = 0
            
            # 1. Backup de todos os executores encontrados
            self.log(f"Backup de {len(executores)} executores...", "INFO", "BACKUP")
            
            for executor in executores:
                src = executor["arquivo"]
                if os.path.exists(src):
                    # Criar estrutura de diretórios relativa
                    rel_path = os.path.relpath(src, ".")
                    dst = os.path.join(backup_dir, rel_path)
                    
                    # Criar diretórios necessários
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(src, dst)
                    
                    tamanho = os.path.getsize(src)
                    total_size += tamanho
                    
                    arquivos_backupeados.append({
                        "arquivo": rel_path,
                        "tamanho_bytes": tamanho,
                        "hash_md5": executor.get("hash_md5", ""),
                        "timestamp_copia": datetime.now().isoformat()
                    })
                    
                    self.log(f"  📁 {rel_path} ({tamanho:,} bytes)", "INFO", "BACKUP")
                else:
                    self.log(f"  ⚠️ Arquivo não encontrado: {src}", "WARNING", "BACKUP")
            
            # 2. Backup de arquivos relacionados
            arquivos_relacionados = self.buscar_arquivos_relacionados()
            for arquivo in arquivos_relacionados:
                try:
                    rel_path = os.path.relpath(arquivo, ".")
                    dst = os.path.join(backup_dir, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(arquivo, dst)
                    
                    tamanho = os.path.getsize(arquivo)
                    total_size += tamanho
                    
                    arquivos_backupeados.append({
                        "arquivo": rel_path,
                        "tipo": "RELACIONADO",
                        "tamanho_bytes": tamanho
                    })
                    
                    self.log(f"  🔗 {rel_path}", "INFO", "BACKUP")
                except Exception as e:
                    self.log(f"  ⚠️ Erro ao copiar {arquivo}: {e}", "WARNING", "BACKUP")
            
            # 3. Criar manifesto do backup
            self.criar_manifesto_backup(backup_dir, arquivos_backupeados, executores)
            
            # 4. Criar ZIP
            self.log(f"Criando ZIP: {backup_zip}...", "INFO", "BACKUP")
            shutil.make_archive(backup_dir, 'zip', backup_dir)
            
            # Calcular hash do backup
            hash_backup = self.calcular_hash_arquivo(backup_zip, "sha256")
            tamanho_mb = os.path.getsize(backup_zip) / (1024 * 1024)
            
            # 5. Limpar diretório temporário
            shutil.rmtree(backup_dir)
            
            # Atualizar resultados
            self.resultados_selecao["fase_backup"].update({
                "status": "COMPLETO",
                "backup_dir": backup_dir,
                "backup_zip": backup_zip,
                "arquivos_backupeados": arquivos_backupeados,
                "hash_backup": hash_backup,
                "tamanho_backup_mb": round(tamanho_mb, 2),
                "tamanho_total_bytes": total_size,
                "total_arquivos": len(arquivos_backupeados),
                "timestamp_backup": datetime.now().isoformat()
            })
            
            self.log(f"✅ Backup criado: {backup_zip} ({tamanho_mb:.2f} MB)", "SUCCESS", "BACKUP")
            self.log(f"   Hash SHA256: {hash_backup}", "INFO", "BACKUP")
            self.log(f"   Total arquivos: {len(arquivos_backupeados)}", "INFO", "BACKUP")
            
            return backup_zip
            
        except Exception as e:
            self.log(f"❌ ERRO ao criar backup: {e}", "ERROR", "BACKUP")
            self.resultados_selecao["fase_backup"]["status"] = "ERRO"
            self.resultados_selecao["fase_backup"]["erro"] = str(e)
            
            # Tentar limpar em caso de erro
            if os.path.exists(backup_dir):
                try:
                    shutil.rmtree(backup_dir)
                except:
                    pass
            
            raise
    
    def buscar_arquivos_relacionados(self):
        """Buscar arquivos relacionados aos executores MT5"""
        padroes = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "Pipfile.lock",
            "*.ini",
            "*.cfg",
            "*.yaml",
            "*.yml",
            ".env",
            "config.json",
            "settings.json",
            "mt5_config*"
        ]
        
        arquivos_encontrados = []
        
        for padrao in padroes:
            try:
                if '*' in padrao:
                    # É um arquivo com wildcard
                    for arquivo in glob.glob(padrao, recursive=True):
                        if os.path.isfile(arquivo) and not arquivo.startswith('backup_'):
                            arquivos_encontrados.append(arquivo)
                else:
                    # É um arquivo específico
                    if os.path.exists(padrao) and os.path.isfile(padrao):
                        arquivos_encontrados.append(padrao)
            except:
                pass
        
        # Remover duplicatas
        return list(set(arquivos_encontrados))[:50]  # Limitar a 50 arquivos
    
    def criar_manifesto_backup(self, backup_dir, arquivos, executores):
        """Criar arquivo manifesto do backup"""
        manifesto_path = os.path.join(backup_dir, "MANIFEST_BACKUP.txt")
        
        with open(manifesto_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MANIFESTO DE BACKUP - ARCH-001 BLOCO 2\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Data criação: {datetime.now().isoformat()}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Checkpoint origem: {self.checkpoint_path}\n\n")
            
            f.write("EXECUTORES MT5 BACKUPEADOS:\n")
            f.write("-" * 40 + "\n")
            for executor in executores:
                f.write(f"• {executor['arquivo']}\n")
                f.write(f"  Tamanho: {executor['tamanho_bytes']:,} bytes\n")
                f.write(f"  Linhas: {executor.get('linhas', 'N/A')}\n")
                f.write(f"  Hash MD5: {executor.get('hash_md5', 'N/A')}\n")
                f.write(f"  Diretório: {executor.get('diretorio', 'N/A')}\n\n")
            
            f.write("\nARQUIVOS RELACIONADOS:\n")
            f.write("-" * 40 + "\n")
            for arquivo in arquivos:
                if arquivo.get("tipo") == "RELACIONADO":
                    f.write(f"• {arquivo['arquivo']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("INSTRUÇÕES DE RESTAURAÇÃO:\n")
            f.write("=" * 80 + "\n")
            f.write("Para restaurar este backup:\n")
            f.write("1. Extrair o arquivo ZIP\n")
            f.write("2. Verificar MANIFEST_BACKUP.txt\n")
            f.write("3. Copiar arquivos de volta para suas localizações originais\n")
    
    def selecionar_executor_principal(self):
        """Selecionar executor principal baseado em critérios"""
        self.log("Selecionando executor principal...", "SELECT", "SELECAO")
        
        executores = self.dados_analise["fase_analise"]["executores_encontrados"]
        analise_funcional = self.dados_analise["fase_analise"]["analise_funcional"]
        
        if not executores:
            self.log("❌ Nenhum executor para selecionar!", "ERROR", "SELECAO")
            return None
        
        if len(executores) == 1:
            executor = executores[0]
            self.log(f"Apenas 1 executor: {executor['arquivo']}", "INFO", "SELECAO")
            
            self.resultados_selecao["fase_selecao"].update({
                "status": "UNICO",
                "executor_principal": executor["arquivo"],
                "criterios_selecao": {"tipo": "UNICO_EXECUTOR"},
                "timestamp_selecao": datetime.now().isoformat()
            })
            
            return executor["arquivo"]
        
        # Sistema de pontuação para múltiplos executores
        candidatos = []
        
        for executor in executores:
            arquivo = executor["arquivo"]
            analise = analise_funcional.get(arquivo, {})
            
            # Critérios de pontuação
            pontuacao = {
                "arquivo": arquivo,
                "pontos_totais": 0,
                "detalhes": {}
            }
            
            # 1. Score funcional (0-200)
            score_func = analise.get("score_funcional", 0)
            pontuacao["detalhes"]["score_funcional"] = score_func * 10  # 0-200
            pontuacao["pontos_totais"] += score_func * 10
            
            # 2. Tamanho (0-100) - Maior é melhor (mais completo)
            tamanho = executor.get("tamanho_bytes", 0)
            if tamanho > 10000:  # >10KB
                pontuacao["detalhes"]["tamanho"] = 100
            elif tamanho > 5000:  # >5KB
                pontuacao["detalhes"]["tamanho"] = 70
            elif tamanho > 1000:  # >1KB
                pontuacao["detalhes"]["tamanho"] = 40
            else:
                pontuacao["detalhes"]["tamanho"] = 10
            pontuacao["pontos_totais"] += pontuacao["detalhes"]["tamanho"]
            
            # 3. Nome padrão (0-100)
            nome_arquivo = executor.get("nome", "").lower()
            if "mt5_executor.py" in nome_arquivo:
                pontuacao["detalhes"]["nome_padrao"] = 100
            elif "mt5executor" in nome_arquivo.replace("_", ""):
                pontuacao["detalhes"]["nome_padrao"] = 80
            elif "executor" in nome_arquivo and "mt5" in nome_arquivo:
                pontuacao["detalhes"]["nome_padrao"] = 60
            else:
                pontuacao["detalhes"]["nome_padrao"] = 20
            pontuacao["pontos_totais"] += pontuacao["detalhes"]["nome_padrao"]
            
            # 4. Diretório padrão (0-50)
            diretorio = executor.get("diretorio", "").lower()
            if "04-infraestrutura" in diretorio or "04-infrastructure" in diretorio:
                pontuacao["detalhes"]["diretorio_padrao"] = 50
            elif "system_core" in diretorio:
                pontuacao["detalhes"]["diretorio_padrao"] = 40
            elif "executors" in diretorio:
                pontuacao["detalhes"]["diretorio_padrao"] = 30
            elif "core" in diretorio:
                pontuacao["detalhes"]["diretorio_padrao"] = 20
            else:
                pontuacao["detalhes"]["diretorio_padrao"] = 10
            pontuacao["pontos_totais"] += pontuacao["detalhes"]["diretorio_padrao"]
            
            # 5. Complexidade (0-50)
            complexidade = analise.get("complexidade", 0)
            if complexidade > 500:
                pontuacao["detalhes"]["complexidade"] = 50
            elif complexidade > 200:
                pontuacao["detalhes"]["complexidade"] = 30
            else:
                pontuacao["detalhes"]["complexidade"] = 10
            pontuacao["pontos_totais"] += pontuacao["detalhes"]["complexidade"]
            
            candidatos.append(pontuacao)
        
        # Ordenar por pontuação
        candidatos.sort(key=lambda x: x["pontos_totais"], reverse=True)
        
        # Registrar seleção
        for i, cand in enumerate(candidatos[:3]):  # Top 3
            self.log(f"Candidato {i+1}: {cand['arquivo']} - {cand['pontos_totais']} pontos", 
                    "INFO", "SELECAO")
        
        executor_principal = candidatos[0]["arquivo"]
        pontuacao_principal = candidatos[0]["pontos_totais"]
        
        self.resultados_selecao["fase_selecao"].update({
            "status": "SELECIONADO",
            "executor_principal": executor_principal,
            "executores_candidatos": candidatos[:5],  # Top 5
            "criterios_selecao": {
                "score_funcional": "0-200",
                "tamanho": "0-100", 
                "nome_padrao": "0-100",
                "diretorio_padrao": "0-50",
                "complexidade": "0-50"
            },
            "score_detalhado": candidatos[0]["detalhes"],
            "pontuacao_total": pontuacao_principal,
            "timestamp_selecao": datetime.now().isoformat()
        })
        
        self.log(f"✅ Executor principal selecionado: {executor_principal}", "SUCCESS", "SELECAO")
        self.log(f"   Pontuação: {pontuacao_principal}/500", "INFO", "SELECAO")
        
        return executor_principal
    
    def gerar_checkpoint_selecao(self):
        """Gerar checkpoint JSON com resultados da seleção"""
        checkpoint_file = f"checkpoint_selecao_{self.timestamp}.json"
        
        # Adicionar metadata final
        self.resultados_selecao["estatisticas"]["fim_execucao"] = datetime.now().isoformat()
        self.resultados_selecao["metadata"]["status"] = "COMPLETO"
        
        # Calcular hash do checkpoint
        checkpoint_str = json.dumps(self.resultados_selecao, indent=2, ensure_ascii=False)
        hash_checkpoint = hashlib.sha256(checkpoint_str.encode()).hexdigest()
        self.resultados_selecao["metadata"]["hash_checkpoint"] = hash_checkpoint
        
        # Salvar checkpoint
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            f.write(checkpoint_str)
        
        self.log(f"✅ Checkpoint gerado: {checkpoint_file}", "SUCCESS", "CHECKPOINT")
        self.log(f"   Hash: {hash_checkpoint}", "INFO", "CHECKPOINT")
        
        return checkpoint_file
    
    def criar_relatorio_backup(self):
        """Criar relatório textual do backup"""
        if not self.resultados_selecao["fase_backup"]["backup_zip"]:
            return None
        
        relatorio_file = f"relatorio_backup_{self.timestamp}.txt"
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE BACKUP - ARCH-001 BLOCO 2\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Data: {datetime.now().isoformat()}\n\n")
            
            f.write("📦 BACKUP CRIADO:\n")
            f.write(f"  Arquivo: {self.resultados_selecao['fase_backup']['backup_zip']}\n")
            f.write(f"  Tamanho: {self.resultados_selecao['fase_backup']['tamanho_backup_mb']:.2f} MB\n")
            f.write(f"  Hash SHA256: {self.resultados_selecao['fase_backup']['hash_backup']}\n")
            f.write(f"  Total arquivos: {self.resultados_selecao['fase_backup']['total_arquivos']}\n\n")
            
            f.write("🎯 EXECUTOR PRINCIPAL SELECIONADO:\n")
            executor = self.resultados_selecao["fase_selecao"]["executor_principal"]
            if executor:
                f.write(f"  {executor}\n")
                f.write(f"  Pontuação: {self.resultados_selecao['fase_selecao']['pontuacao_total']}/500\n\n")
            
            f.write("📋 EXECUTORES BACKUPEADOS:\n")
            for item in self.resultados_selecao["fase_backup"]["arquivos_backupeados"][:10]:
                if "RELACIONADO" not in str(item.get("tipo", "")):
                    f.write(f"  • {item['arquivo']} ({item['tamanho_bytes']:,} bytes)\n")
            
            if len(self.resultados_selecao["fase_backup"]["arquivos_backupeados"]) > 10:
                f.write(f"  ... e mais {len(self.resultados_selecao['fase_backup']['arquivos_backupeados']) - 10} arquivos\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("PRÓXIMOS PASSOS:\n")
            f.write("=" * 80 + "\n")
            f.write("1. Verificar backup criado\n")
            f.write("2. Executar BLOCO 3 (Consolidação)\n")
            f.write("3. Usar checkpoint para próxima fase\n")
        
        self.log(f"📄 Relatório gerado: {relatorio_file}", "INFO", "RELATORIO")
        return relatorio_file
    
    # ========== UTILITÁRIOS ==========
    
    def calcular_hash_arquivo(self, arquivo, algoritmo="sha256"):
        """Calcular hash de um arquivo"""
        try:
            if algoritmo == "md5":
                hasher = hashlib.md5()
            elif algoritmo == "sha256":
                hasher = hashlib.sha256()
            elif algoritmo == "sha1":
                hasher = hashlib.sha1()
            else:
                hasher = hashlib.sha256()
            
            with open(arquivo, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception as e:
            self.log(f"Erro ao calcular hash: {e}", "WARNING", "UTIL")
            return None
    
    def executar_bloco2_completo(self):
        """Executar BLOCO 2 completo"""
        self.log("🚀 INICIANDO BLOCO 2: BACKUP E SELEÇÃO", "INFO", "INICIO")
        self.log(f"Timestamp: {self.timestamp}", "INFO", "INICIO")
        self.log(f"Checkpoint: {self.checkpoint_path}", "INFO", "INICIO")
        
        try:
            # 1. Criar backup
            backup_zip = self.criar_backup_completo()
            
            if not backup_zip and self.resultados_selecao["fase_backup"]["status"] != "VAZIO":
                raise Exception("Falha ao criar backup")
            
            # 2. Selecionar executor principal
            executor_principal = self.selecionar_executor_principal()
            
            if not executor_principal:
                self.log("⚠️ Nenhum executor principal selecionado", "WARNING", "SELECAO")
            
            # 3. Gerar checkpoint
            checkpoint = self.gerar_checkpoint_selecao()
            
            # 4. Gerar relatório
            relatorio = self.criar_relatorio_backup()
            
            # Resumo
            self.log("\n" + "=" * 60, "INFO", "RESUMO")
            self.log("📊 RESUMO DO BLOCO 2:", "SUCCESS", "RESUMO")
            
            if backup_zip:
                tamanho = self.resultados_selecao["fase_backup"]["tamanho_backup_mb"]
                self.log(f"  • Backup criado: {backup_zip} ({tamanho:.2f} MB)", "INFO", "RESUMO")
            
            if executor_principal:
                self.log(f"  • Executor principal: {executor_principal}", "INFO", "RESUMO")
            
            self.log(f"  • Checkpoint: {checkpoint}", "INFO", "RESUMO")
            
            if relatorio:
                self.log(f"  • Relatório: {relatorio}", "INFO", "RESUMO")
            
            self.log("✅ BLOCO 2 CONCLUÍDO - Pronto para BLOCO 3", "SUCCESS", "FINAL")
            
            return checkpoint
            
        except Exception as e:
            self.log(f"❌ ERRO no BLOCO 2: {e}", "ERROR", "ERRO")
            self.resultados_selecao["metadata"]["status"] = "ERRO"
            self.resultados_selecao["metadata"]["erro"] = str(e)
            
            # Tentar salvar checkpoint mesmo com erro
            try:
                self.gerar_checkpoint_selecao()
            except:
                pass
            
            raise


def main():
    """Função principal do Bloco 2"""
    print("\n" + "=" * 70)
    print("ARCH-001 - BLOCO 2: BACKUP E SELEÇÃO")
    print("Fase 3: Criar backup e selecionar executor principal")
    print("=" * 70)
    
    import argparse
    parser = argparse.ArgumentParser(description='ARCH-001 BLOCO 2: Backup e Seleção')
    parser.add_argument('--checkpoint', type=str, 
                       help='Caminho para checkpoint do BLOCO 1 (checkpoint_analise_*.json)',
                       default=None)
    parser.add_argument('--auto', action='store_true',
                       help='Auto-detecta checkpoint mais recente')
    
    args = parser.parse_args()
    
    checkpoint_path = args.checkpoint
    
    if args.auto or not checkpoint_path:
        # Auto-detectar
        checkpoints = [f for f in os.listdir('.') 
                      if f.startswith('checkpoint_analise_') and f.endswith('.json')]
        
        if not checkpoints:
            print("❌ Nenhum checkpoint do BLOCO 1 encontrado!")
            print("   Execute primeiro: python bloco1_analise_identificacao.py")
            return 1
        
        checkpoint_path = max(checkpoints)
        print(f"🔍 Checkpoint auto-detecado: {checkpoint_path}")
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint não encontrado: {checkpoint_path}")
        return 1
    
    print(f"\n📋 Este bloco executará:")
    print(f"   1. Carregar checkpoint: {checkpoint_path}")
    print(f"   2. Criar backup completo (ZIP)")
    print(f"   3. Selecionar executor principal")
    print(f"   4. Gerar checkpoint para BLOCO 3")
    
    # Execução automática (sem interação)
    print("\n🚀 Iniciando backup e seleção automaticamente...\n")
    
    try:
        bloco2 = ARCH001BackupSelecao(checkpoint_path)
        checkpoint = bloco2.executar_bloco2_completo()
        
        print(f"\n✅ BLOCO 2 CONCLUÍDO COM SUCESSO")
        print(f"📄 Checkpoint: {checkpoint}")
        print(f"📁 Logs: logs_arch001_bloco2/")
        
        if bloco2.resultados_selecao["fase_backup"]["backup_zip"]:
            backup = bloco2.resultados_selecao["fase_backup"]["backup_zip"]
            tamanho = bloco2.resultados_selecao["fase_backup"]["tamanho_backup_mb"]
            print(f"💾 Backup: {backup} ({tamanho:.2f} MB)")
        
        executor = bloco2.resultados_selecao["fase_selecao"]["executor_principal"]
        if executor:
            print(f"🎯 Executor principal: {executor}")
        
        print("\n➡️  PRÓXIMO: Executar BLOCO 3 (Consolidação Cirúrgica)")
        print(f"   Usar checkpoint: {checkpoint}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("📁 Verifique logs em logs_arch001_bloco2/")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

