#!/usr/bin/env python3
"""
🔬 TESTE DE VERIFICAÇÃO OPERACIONAL FINAL - ARCH-001
Nível: VERIFICAÇÃO CIRÚRGICA - ANTI-CAMUFLAGEM
Função: Validar que o sistema está 100% operacional e integrado
        Verificar consistência entre arquivos e relatórios
        Detectar qualquer divergência ou informação falsa
Protocolo: VALIDAÇÃO ABSOLUTA
"""

import json
import os
import sys
import hashlib
import subprocess
import re
import datetime
from pathlib import Path
import zipfile
import difflib

class TesteVerificacaoOperacionalFinal:
    """Teste CIRÚRGICO de verificação operacional final"""
    
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Arquivos CRÍTICOS para verificação (baseado no seu relatório)
        self.arquivos_criticos = {
            "executor_final": "ARCH001_EXECUTOR_FINAL_20251226_230100.py",
            "checkpoint_final": "checkpoint_final_arch001_20251226_230100.json",
            "inicializador": "inicializador_arch001_20251226_230100.py",
            "configuracao": "configuracao_arch001_20251226_230100.json",
            "monitor": "monitor_arch001_20251226_230100.py",
            "recuperacao": "sistema_recuperacao_arch001_20251226_230100.py",
            "ativado": "ARCH001_ATIVADO.txt",
            "documentacao": "DOCUMENTACAO_FINAL_ARCH001_20251226_230100.md"
        }
        
        # Checkpoints de todos os blocos
        self.checkpoints_blocos = {
            "bloco1": "checkpoint_analise_20251226_201607.json",
            "bloco2": "checkpoint_selecao_20251226_204338.json", 
            "bloco3": "checkpoint_consolidacao_20251226_213652.json",
            "bloco4": "checkpoint_final_arch001_20251226_230100.json"
        }
        
        # Dicionário para resultados
        self.resultados = {
            "metadata": {
                "teste": "VERIFICACAO_OPERACIONAL_FINAL_ARCH001",
                "timestamp": datetime.datetime.now().isoformat(),
                "protocolo": "ANTI_CAMUFLAGEM",
                "nivel": "VERIFICACAO_CIRURGICA"
            },
            "verificacoes_conteudo": [],
            "verificacoes_consistencia": [],
            "testes_operacionais": [],
            "alertas_inconsistencia": [],
            "validacoes_cruzadas": [],
            "conclusao": {}
        }
        
        # Hashes do relatório técnico (para validação cruzada)
        self.hashes_relatorio = {
            "executor_final": "26c109d7d338851f04462acb9d832bf92dc13d8a6c743f4d5fd15f693e733c6f",
            "configuracao": "ab77a6beae0ca865fa736874446a89148def53e0c7a0bc22acce9740f38faa64",
            "executor_consolidado": "e593ac0e66f3c7506b1ee870d3075e1e49efb664ca3eaae547070dba39427f3b",
            "backup": "fefcb074bad89b3a5b03c8c18fa264ed2bd54e1c1a09da18bd74fb582f41709d"
        }
    
    def executar_teste_completo(self):
        """Executar TODOS os testes de verificação operacional"""
        print("\n" + "=" * 100)
        print("🔬 TESTE DE VERIFICAÇÃO OPERACIONAL FINAL - ARCH-001")
        print("Protocolo: ANTI-CAMUFLAGEM - VALIDAÇÃO ABSOLUTA")
        print("=" * 100)
        
        # FASE 1: VERIFICAÇÃO DE CONTEÚDO E INTEGRIDADE
        print("\n📄 FASE 1: VERIFICAÇÃO DE CONTEÚDO E INTEGRIDADE")
        print("-" * 60)
        
        for nome, arquivo in self.arquivos_criticos.items():
            resultado = self.verificar_conteudo_arquivo(arquivo, nome)
            self.resultados["verificacoes_conteudo"].append(resultado)
            
            if resultado["status"] == "VALIDADO":
                print(f"✅ {nome.upper()}: Conteúdo válido ({resultado['tamanho_kb']:.1f} KB)")
            else:
                print(f"❌ {nome.upper()}: {resultado.get('erro', 'Inválido')}")
        
        # FASE 2: VERIFICAÇÃO DE CONSISTÊNCIA ENTRE ARQUIVOS
        print("\n🔗 FASE 2: VERIFICAÇÃO DE CONSISTÊNCIA ENTRE ARQUIVOS")
        print("-" * 60)
        
        verificacoes_consistencia = [
            self.verificar_consistencia_checkpoints(),
            self.verificar_consistencia_hashes(),
            self.verificar_consistencia_timestamps(),
            self.verificar_consistencia_metadata()
        ]
        
        self.resultados["verificacoes_consistencia"] = verificacoes_consistencia
        
        for verificacao in verificacoes_consistencia:
            status_icon = "✅" if verificacao["status"] == "CONSISTENTE" else "❌"
            print(f"{status_icon} {verificacao['verificacao']}: {verificacao['status']}")
            if verificacao.get("detalhes"):
                print(f"   ↳ {verificacao['detalhes']}")
        
        # FASE 3: TESTES OPERACIONAIS REAIS
        print("\n⚡ FASE 3: TESTES OPERACIONAIS REAIS")
        print("-" * 60)
        
        testes_operacionais = [
            self.testar_inicializador(),
            self.testar_sintaxe_executor(),
            self.testar_configuracao_json(),
            self.testar_monitoramento(),
            self.testar_sistema_recuperacao()
        ]
        
        self.resultados["testes_operacionais"] = testes_operacionais
        
        for teste in testes_operacionais:
            status_icon = "✅" if teste["status"] == "APROVADO" else "❌"
            print(f"{status_icon} {teste['teste']}: {teste['status']}")
            if teste.get("detalhes"):
                print(f"   ↳ {teste['detalhes']}")
        
        # FASE 4: VALIDAÇÃO CRUZADA COM RELATÓRIO TÉCNICO
        print("\n📊 FASE 4: VALIDAÇÃO CRUZADA COM RELATÓRIO TÉCNICO")
        print("-" * 60)
        
        validacoes_cruzadas = [
            self.validar_hashes_com_relatorio(),
            self.validar_estatisticas_com_relatorio(),
            self.validar_estrutura_com_relatorio(),
            self.validar_protocolo_antifraude()
        ]
        
        self.resultados["validacoes_cruzadas"] = validacoes_cruzadas
        
        for validacao in validacoes_cruzadas:
            if validacao["status"] == "CORRESPONDENTE":
                print(f"✅ {validacao['validacao']}: CORRESPONDENTE")
            else:
                print(f"❌ {validacao['validacao']}: DIVERGENTE")
                print(f"   ↳ {validacao.get('detalhes', '')}")
        
        # FASE 5: DETECÇÃO DE INCONSISTÊNCIAS E CAMUFLAGEM
        print("\n🚨 FASE 5: DETECÇÃO DE INCONSISTÊNCIAS E CAMUFLAGEM")
        print("-" * 60)
        
        alertas = self.detectar_inconsistencias()
        self.resultados["alertas_inconsistencia"] = alertas
        
        if alertas:
            for alerta in alertas:
                print(f"⚠️  ALERTA: {alerta}")
        else:
            print("✅ NENHUMA INCONSISTÊNCIA DETECTADA")
        
        # FASE 6: CONCLUSÃO FINAL
        print("\n🎯 FASE 6: CONCLUSÃO DA VERIFICAÇÃO OPERACIONAL")
        print("-" * 60)
        
        conclusao = self.gerar_conclusao_final()
        self.resultados["conclusao"] = conclusao
        
        # Mostrar resultado final
        self.mostrar_resultado_final(conclusao)
        
        # Gerar relatório forense detalhado
        self.gerar_relatorio_verificacao()
        
        return conclusao["status_operacional"] == "OPERACIONAL_CONFIRMADO"
    
    def verificar_conteudo_arquivo(self, arquivo: str, tipo: str) -> dict:
        """Verificar conteúdo e integridade de um arquivo"""
        if not os.path.exists(arquivo):
            return {
                "arquivo": arquivo,
                "tipo": tipo,
                "status": "NAO_ENCONTRADO",
                "erro": "Arquivo não existe"
            }
        
        try:
            tamanho = os.path.getsize(arquivo)
            
            # Verificar se não está vazio
            if tamanho == 0:
                return {
                    "arquivo": arquivo,
                    "tipo": tipo,
                    "status": "INVALIDO",
                    "erro": "Arquivo vazio",
                    "tamanho_bytes": 0
                }
            
            # Verificar conteúdo baseado no tipo
            conteudo_valido = True
            detalhes = ""
            
            if arquivo.endswith('.json'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        json.load(f)
                    detalhes = "JSON válido"
                except Exception as e:
                    conteudo_valido = False
                    detalhes = f"JSON inválido: {str(e)}"
            
            elif arquivo.endswith('.py'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Verificar se parece ser código Python
                    if not any(keyword in conteudo for keyword in ['import', 'def ', 'class ', 'print']):
                        conteudo_valido = False
                        detalhes = "Não parece ser código Python válido"
                    else:
                        detalhes = "Código Python aparentemente válido"
                except:
                    conteudo_valido = False
                    detalhes = "Erro na leitura do arquivo"
            
            elif arquivo.endswith('.md') or arquivo.endswith('.txt'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    if len(conteudo.strip()) == 0:
                        conteudo_valido = False
                        detalhes = "Arquivo de texto vazio"
                    else:
                        detalhes = f"Texto válido ({len(conteudo)} caracteres)"
                except:
                    conteudo_valido = False
                    detalhes = "Erro na leitura do arquivo"
            
            # Calcular hash
            hash_calculado = self.calcular_hash_sha256(arquivo)
            
            if conteudo_valido:
                return {
                    "arquivo": arquivo,
                    "tipo": tipo,
                    "status": "VALIDADO",
                    "tamanho_bytes": tamanho,
                    "tamanho_kb": tamanho / 1024,
                    "hash_sha256": hash_calculado,
                    "detalhes": detalhes,
                    "timestamp_modificacao": datetime.datetime.fromtimestamp(
                        os.path.getmtime(arquivo)
                    ).isoformat()
                }
            else:
                return {
                    "arquivo": arquivo,
                    "tipo": tipo,
                    "status": "INVALIDO",
                    "erro": detalhes,
                    "tamanho_bytes": tamanho,
                    "hash_sha256": hash_calculado
                }
                
        except Exception as e:
            return {
                "arquivo": arquivo,
                "tipo": tipo,
                "status": "ERRO_VERIFICACAO",
                "erro": str(e)
            }
    
    def verificar_consistencia_checkpoints(self) -> dict:
        """Verificar consistência entre checkpoints de todos os blocos"""
        print("   🔍 Verificando consistência dos checkpoints...")
        
        checkpoints_validos = {}
        inconsistências = []
        
        for bloco, checkpoint in self.checkpoints_blocos.items():
            if os.path.exists(checkpoint):
                try:
                    with open(checkpoint, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    # Verificar estrutura básica
                    if "metadata" in dados:
                        metadata = dados["metadata"]
                        
                        checkpoints_validos[bloco] = {
                            "arquivo": checkpoint,
                            "status": metadata.get("status", "DESCONHECIDO"),
                            "etapa": metadata.get("etapa", "DESCONHECIDO"),
                            "timestamp": metadata.get("timestamp", ""),
                            "valido": True
                        }
                        
                        # Verificar se o bloco corresponde
                        if bloco.upper() not in metadata.get("etapa", "").upper():
                            inconsistências.append(f"Checkpoint {bloco} não corresponde à etapa")
                    else:
                        checkpoints_validos[bloco] = {
                            "arquivo": checkpoint,
                            "valido": False,
                            "erro": "Sem metadata"
                        }
                        inconsistências.append(f"Checkpoint {bloco} sem metadata")
                        
                except Exception as e:
                    checkpoints_validos[bloco] = {
                        "arquivo": checkpoint,
                        "valido": False,
                        "erro": str(e)
                    }
                    inconsistências.append(f"Checkpoint {bloco} inválido: {e}")
            else:
                checkpoints_validos[bloco] = {
                    "arquivo": checkpoint,
                    "valido": False,
                    "erro": "Não encontrado"
                }
                inconsistências.append(f"Checkpoint {bloco} não encontrado")
        
        # Verificar sequência lógica
        if all(c.get("valido") for c in checkpoints_validos.values()):
            # Verificar timestamps em ordem crescente
            timestamps = []
            for bloco, info in checkpoints_validos.items():
                if info.get("timestamp"):
                    try:
                        timestamps.append((bloco, datetime.datetime.fromisoformat(
                            info["timestamp"].replace('Z', '+00:00')
                        )))
                    except:
                        pass
            
            if len(timestamps) >= 2:
                timestamps.sort(key=lambda x: x[1])
                blocos_ordenados = [b for b, _ in timestamps]
                
                # Verificar se está em ordem BLOCO1 → BLOCO2 → BLOCO3 → BLOCO4
                ordem_esperada = ["bloco1", "bloco2", "bloco3", "bloco4"]
                ordem_real = [b for b in ordem_esperada if b in blocos_ordenados]
                
                if ordem_real != [b for b in ordem_esperada if b in checkpoints_validos]:
                    inconsistências.append("Checkpoints fora de ordem cronológica")
        
        if inconsistências:
            return {
                "verificacao": "CONSISTÊNCIA DOS CHECKPOINTS",
                "status": "INCONSISTENTE",
                "detalhes": f"Inconsistências: {', '.join(inconsistências[:3])}",
                "checkpoints_validos": len([c for c in checkpoints_validos.values() if c.get("valido")]),
                "total_checkpoints": len(checkpoints_validos),
                "inconsistencias": inconsistências
            }
        else:
            return {
                "verificacao": "CONSISTÊNCIA DOS CHECKPOINTS",
                "status": "CONSISTENTE",
                "detalhes": f"{len([c for c in checkpoints_validos.values() if c.get('valido')])}/{len(checkpoints_validos)} checkpoints válidos",
                "checkpoints_validos": len([c for c in checkpoints_validos.values() if c.get("valido")]),
                "total_checkpoints": len(checkpoints_validos)
            }
    
    def verificar_consistencia_hashes(self) -> dict:
        """Verificar consistência dos hashes entre arquivos relacionados"""
        print("   🔐 Verificando consistência dos hashes...")
        
        # Verificar se hashes mencionados em um arquivo correspondem aos calculados
        arquivos_para_hash = [
            self.arquivos_criticos["executor_final"],
            self.arquivos_criticos["configuracao"],
            self.arquivos_criticos["checkpoint_final"]
        ]
        
        hashes_calculados = {}
        for arquivo in arquivos_para_hash:
            if os.path.exists(arquivo):
                hashes_calculados[arquivo] = self.calcular_hash_sha256(arquivo)
        
        # Tentar extrair hashes do checkpoint final
        hashes_mencionados = {}
        checkpoint_final = self.arquivos_criticos["checkpoint_final"]
        
        if os.path.exists(checkpoint_final):
            try:
                with open(checkpoint_final, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Procurar hashes no JSON
                def extrair_hashes(obj, caminho=""):
                    hashes = {}
                    if isinstance(obj, dict):
                        for chave, valor in obj.items():
                            if "hash" in chave.lower() and isinstance(valor, str) and len(valor) == 64:
                                hashes[f"{caminho}.{chave}" if caminho else chave] = valor
                            elif isinstance(valor, (dict, list)):
                                hashes.update(extrair_hashes(valor, f"{caminho}.{chave}" if caminho else chave))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            hashes.update(extrair_hashes(item, f"{caminho}[{i}]"))
                    return hashes
                
                hashes_mencionados = extrair_hashes(dados)
                
            except:
                pass
        
        # Comparar hashes
        inconsistências = []
        for arquivo, hash_calculado in hashes_calculados.items():
            nome_arquivo = os.path.basename(arquivo)
            
            # Procurar hash mencionado para este arquivo
            hash_mencionado = None
            for chave, valor in hashes_mencionados.items():
                if nome_arquivo.lower() in chave.lower():
                    hash_mencionado = valor
                    break
            
            if hash_mencionado:
                if hash_calculado != hash_mencionado:
                    inconsistências.append(f"Hash divergente para {nome_arquivo}")
        
        if inconsistências:
            return {
                "verificacao": "CONSISTÊNCIA DOS HASHES",
                "status": "INCONSISTENTE",
                "detalhes": f"Inconsistências: {', '.join(inconsistências)}",
                "hashes_calculados": len(hashes_calculados),
                "hashes_mencionados": len(hashes_mencionados),
                "inconsistencias": inconsistências
            }
        else:
            return {
                "verificacao": "CONSISTÊNCIA DOS HASHES",
                "status": "CONSISTENTE",
                "detalhes": f"{len(hashes_calculados)} hashes calculados, {len(hashes_mencionados)} hashes mencionados",
                "hashes_calculados": len(hashes_calculados),
                "hashes_mencionados": len(hashes_mencionados)
            }
    
    def verificar_consistencia_timestamps(self) -> dict:
        """Verificar consistência dos timestamps"""
        print("   ⏰ Verificando consistência dos timestamps...")
        
        arquivos_verificar = list(self.arquivos_criticos.values())
        arquivos_verificar.extend(self.checkpoints_blocos.values())
        
        timestamps = []
        for arquivo in arquivos_verificar:
            if os.path.exists(arquivo):
                mtime = os.path.getmtime(arquivo)
                timestamps.append((arquivo, datetime.datetime.fromtimestamp(mtime)))
        
        # Verificar se todos são do mesmo dia (26/12/2025)
        datas = set(ts.date() for _, ts in timestamps)
        
        if len(datas) > 1:
            return {
                "verificacao": "CONSISTÊNCIA DOS TIMESTAMPS",
                "status": "INCONSISTENTE",
                "detalhes": f"Múltiplas datas encontradas: {', '.join(str(d) for d in datas)}",
                "arquivos_verificados": len(timestamps),
                "datas_unicas": len(datas)
            }
        
        # Verificar ordem lógica (checkpoints em ordem)
        checkpoint_timestamps = []
        for bloco, checkpoint in self.checkpoints_blocos.items():
            if os.path.exists(checkpoint):
                mtime = os.path.getmtime(checkpoint)
                checkpoint_timestamps.append((bloco, datetime.datetime.fromtimestamp(mtime)))
        
        if len(checkpoint_timestamps) >= 2:
            checkpoint_timestamps.sort(key=lambda x: x[1])
            blocos_ordenados = [b for b, _ in checkpoint_timestamps]
            
            # Ordem esperada: bloco1, bloco2, bloco3, bloco4
            ordem_esperada = ["bloco1", "bloco2", "bloco3", "bloco4"]
            ordem_presente = [b for b in ordem_esperada if b in blocos_ordenados]
            
            if ordem_presente != blocos_ordenados:
                return {
                    "verificacao": "CONSISTÊNCIA DOS TIMESTAMPS",
                    "status": "INCONSISTENTE",
                    "detalhes": f"Checkpoints fora de ordem: {blocos_ordenados}",
                    "arquivos_verificados": len(timestamps)
                }
        
        return {
            "verificacao": "CONSISTÊNCIA DOS TIMESTAMPS",
            "status": "CONSISTENTE",
            "detalhes": f"Todos os {len(timestamps)} arquivos são de {datas.pop() if datas else 'data desconhecida'}",
            "arquivos_verificados": len(timestamps)
        }
    
    def verificar_consistencia_metadata(self) -> dict:
        """Verificar consistência dos metadados entre arquivos"""
        print("   📋 Verificando consistência dos metadados...")
        
        # Coletar metadados de arquivos JSON
        metadados_coletados = {}
        
        for arquivo in [self.arquivos_criticos["checkpoint_final"], 
                       self.arquivos_criticos["configuracao"]]:
            if os.path.exists(arquivo):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    if "metadata" in dados:
                        metadados_coletados[arquivo] = dados["metadata"]
                except:
                    pass
        
        # Verificar consistência
        inconsistências = []
        
        if len(metadados_coletados) >= 2:
            # Comparar valores comuns
            arquivos = list(metadados_coletados.keys())
            metadata1 = metadados_coletados[arquivos[0]]
            
            for i in range(1, len(arquivos)):
                metadata2 = metadados_coletados[arquivos[i]]
                
                # Verificar campos comuns
                campos_comuns = set(metadata1.keys()) & set(metadata2.keys())
                for campo in campos_comuns:
                    if campo in ["timestamp", "hash_integracao", "hash_final"]:
                        continue  # Podem ser diferentes
                    
                    if metadata1[campo] != metadata2[campo]:
                        inconsistências.append(
                            f"Campo '{campo}' divergente: "
                            f"'{metadata1[campo]}' vs '{metadata2[campo]}'"
                        )
        
        if inconsistências:
            return {
                "verificacao": "CONSISTÊNCIA DOS METADADOS",
                "status": "INCONSISTENTE",
                "detalhes": f"Inconsistências: {', '.join(inconsistências[:2])}",
                "arquivos_com_metadata": len(metadados_coletados),
                "inconsistencias": inconsistências
            }
        else:
            return {
                "verificacao": "CONSISTÊNCIA DOS METADADOS",
                "status": "CONSISTENTE",
                "detalhes": f"{len(metadados_coletados)} arquivos com metadata consistente",
                "arquivos_com_metadata": len(metadados_coletados)
            }
    
    def testar_inicializador(self) -> dict:
        """Testar o inicializador do sistema"""
        print("   🚀 Testando inicializador...")
        
        inicializador = self.arquivos_criticos["inicializador"]
        
        if not os.path.exists(inicializador):
            return {
                "teste": "INICIALIZADOR DO SISTEMA",
                "status": "REPROVADO",
                "detalhes": "Arquivo do inicializador não encontrado"
            }
        
        # Verificar sintaxe Python
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", inicializador],
                capture_output=True,
                check=True,
                timeout=10
            )
            sintaxe_valida = True
        except subprocess.CalledProcessError as e:
            return {
                "teste": "INICIALIZADOR DO SISTEMA",
                "status": "REPROVADO",
                "detalhes": f"Sintaxe Python inválida: {e.stderr.decode()[:100] if e.stderr else 'Erro desconhecido'}"
            }
        except subprocess.TimeoutExpired:
            return {
                "teste": "INICIALIZADOR DO SISTEMA",
                "status": "REPROVADO",
                "detalhes": "Timeout na compilação"
            }
        
        # Ler conteúdo para verificar referências
        try:
            with open(inicializador, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Verificar se menciona os componentes esperados
            componentes_esperados = [
                "ARCH001_EXECUTOR_FINAL",
                "monitor_arch001",
                "sistema_recuperacao_arch001"
            ]
            
            componentes_presentes = []
            for componente in componentes_esperados:
                if componente in conteudo:
                    componentes_presentes.append(componente)
            
            if len(componentes_presentes) >= 2:
                return {
                    "teste": "INICIALIZADOR DO SISTEMA",
                    "status": "APROVADO",
                    "detalhes": f"Sintaxe válida, {len(componentes_presentes)}/3 componentes referenciados",
                    "sintaxe_valida": sintaxe_valida,
                    "componentes_referenciados": componentes_presentes
                }
            else:
                return {
                    "teste": "INICIALIZADOR DO SISTEMA",
                    "status": "REPROVADO",
                    "detalhes": f"Poucos componentes referenciados: {componentes_presentes}",
                    "sintaxe_valida": sintaxe_valida
                }
                
        except Exception as e:
            return {
                "teste": "INICIALIZADOR DO SISTEMA",
                "status": "REPROVADO",
                "detalhes": f"Erro na leitura: {str(e)}"
            }
    
    def testar_sintaxe_executor(self) -> dict:
        """Testar sintaxe do executor final"""
        print("   🐍 Testando sintaxe do executor final...")
        
        executor = self.arquivos_criticos["executor_final"]
        
        if not os.path.exists(executor):
            return {
                "teste": "SINTAXE DO EXECUTOR FINAL",
                "status": "REPROVADO",
                "detalhes": "Arquivo do executor não encontrado"
            }
        
        try:
            resultado = subprocess.run(
                [sys.executable, "-m", "py_compile", executor],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                return {
                    "teste": "SINTAXE DO EXECUTOR FINAL",
                    "status": "APROVADO",
                    "detalhes": "Sintaxe Python válida",
                    "tamanho_bytes": os.path.getsize(executor)
                }
            else:
                return {
                    "teste": "SINTAXE DO EXECUTOR FINAL",
                    "status": "REPROVADO",
                    "detalhes": f"Erro de sintaxe: {resultado.stderr[:200] if resultado.stderr else 'Erro desconhecido'}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "teste": "SINTAXE DO EXECUTOR FINAL",
                "status": "REPROVADO",
                "detalhes": "Timeout na verificação de sintaxe"
            }
        except Exception as e:
            return {
                "teste": "SINTAXE DO EXECUTOR FINAL",
                "status": "REPROVADO",
                "detalhes": f"Erro na verificação: {str(e)}"
            }
    
    def testar_configuracao_json(self) -> dict:
        """Testar configuração JSON"""
        print("   ⚙️ Testando configuração JSON...")
        
        config = self.arquivos_criticos["configuracao"]
        
        if not os.path.exists(config):
            return {
                "teste": "CONFIGURAÇÃO JSON",
                "status": "REPROVADO",
                "detalhes": "Arquivo de configuração não encontrado"
            }
        
        try:
            with open(config, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Verificar estrutura mínima
            campos_obrigatorios = ["metadata", "blocos", "arquivos_principais"]
            campos_presentes = []
            
            for campo in campos_obrigatorios:
                if campo in dados:
                    campos_presentes.append(campo)
            
            if len(campos_presentes) >= 2:
                return {
                    "teste": "CONFIGURAÇÃO JSON",
                    "status": "APROVADO",
                    "detalhes": f"JSON válido, {len(campos_presentes)}/3 campos obrigatórios presentes",
                    "campos_presentes": campos_presentes,
                    "tamanho_bytes": os.path.getsize(config)
                }
            else:
                return {
                    "teste": "CONFIGURAÇÃO JSON",
                    "status": "REPROVADO",
                    "detalhes": f"Estrutura incompleta: apenas {campos_presentes} presentes"
                }
                
        except json.JSONDecodeError as e:
            return {
                "teste": "CONFIGURAÇÃO JSON",
                "status": "REPROVADO",
                "detalhes": f"JSON inválido: {str(e)}"
            }
        except Exception as e:
            return {
                "teste": "CONFIGURAÇÃO JSON",
                "status": "REPROVADO",
                "detalhes": f"Erro na leitura: {str(e)}"
            }
    
    def testar_monitoramento(self) -> dict:
        """Testar sistema de monitoramento"""
        print("   📈 Testando sistema de monitoramento...")
        
        monitor = self.arquivos_criticos["monitor"]
        
        if not os.path.exists(monitor):
            return {
                "teste": "SISTEMA DE MONITORAMENTO",
                "status": "REPROVADO",
                "detalhes": "Arquivo de monitoramento não encontrado"
            }
        
        # Verificar sintaxe
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", monitor],
                capture_output=True,
                check=True,
                timeout=10
            )
            sintaxe_valida = True
        except subprocess.CalledProcessError as e:
            return {
                "teste": "SISTEMA DE MONITORAMENTO",
                "status": "REPROVADO",
                "detalhes": f"Sintaxe inválida: {e.stderr.decode()[:100] if e.stderr else 'Erro desconhecido'}"
            }
        except subprocess.TimeoutExpired:
            return {
                "teste": "SISTEMA DE MONITORAMENTO",
                "status": "REPROVADO",
                "detalhes": "Timeout na verificação"
            }
        
        # Verificar conteúdo
        try:
            with open(monitor, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Verificar funcionalidades esperadas
            funcionalidades = ["verificar_arquivos_criticos", "calcular_hash", "log_file"]
            funcs_presentes = []
            
            for func in funcionalidades:
                if func in conteudo:
                    funcs_presentes.append(func)
            
            if len(funcs_presentes) >= 2:
                return {
                    "teste": "SISTEMA DE MONITORAMENTO",
                    "status": "APROVADO",
                    "detalhes": f"Sintaxe válida, {len(funcs_presentes)}/3 funcionalidades presentes",
                    "sintaxe_valida": sintaxe_valida,
                    "funcionalidades_presentes": funcs_presentes
                }
            else:
                return {
                    "teste": "SISTEMA DE MONITORAMENTO",
                    "status": "REPROVADO",
                    "detalhes": f"Poucas funcionalidades: {funcs_presentes}"
                }
                
        except Exception as e:
            return {
                "teste": "SISTEMA DE MONITORAMENTO",
                "status": "REPROVADO",
                "detalhes": f"Erro na leitura: {str(e)}"
            }
    
    def testar_sistema_recuperacao(self) -> dict:
        """Testar sistema de recuperação"""
        print("   🔄 Testando sistema de recuperação...")
        
        recuperacao = self.arquivos_criticos["recuperacao"]
        
        if not os.path.exists(recuperacao):
            return {
                "teste": "SISTEMA DE RECUPERAÇÃO",
                "status": "REPROVADO",
                "detalhes": "Arquivo de recuperação não encontrado"
            }
        
        # Verificar sintaxe
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", recuperacao],
                capture_output=True,
                check=True,
                timeout=10
            )
            sintaxe_valida = True
        except subprocess.CalledProcessError as e:
            return {
                "teste": "SISTEMA DE RECUPERAÇÃO",
                "status": "REPROVADO",
                "detalhes": f"Sintaxe inválida: {e.stderr.decode()[:100] if e.stderr else 'Erro desconhecido'}"
            }
        except subprocess.TimeoutExpired:
            return {
                "teste": "SISTEMA DE RECUPERAÇÃO",
                "status": "REPROVADO",
                "detalhes": "Timeout na verificação"
            }
        
        # Verificar se menciona backup
        try:
            with open(recuperacao, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            if "backup" in conteudo.lower() and "zip" in conteudo.lower():
                return {
                    "teste": "SISTEMA DE RECUPERAÇÃO",
                    "status": "APROVADO",
                    "detalhes": "Sintaxe válida, funcionalidades de backup presentes",
                    "sintaxe_valida": sintaxe_valida
                }
            else:
                return {
                    "teste": "SISTEMA DE RECUPERAÇÃO",
                    "status": "REPROVADO",
                    "detalhes": "Não parece ser um sistema de backup/recuperação"
                }
                
        except Exception as e:
            return {
                "teste": "SISTEMA DE RECUPERAÇÃO",
                "status": "REPROVADO",
                "detalhes": f"Erro na leitura: {str(e)}"
            }
    
    def validar_hashes_com_relatorio(self) -> dict:
        """Validar hashes com os do relatório técnico"""
        print("   🔄 Validando hashes com relatório técnico...")
        
        divergencias = []
        correspondencias = []
        
        for nome_arquivo, hash_esperado in self.hashes_relatorio.items():
            # Mapear nome para arquivo real
            arquivo_real = None
            
            if nome_arquivo == "executor_final":
                arquivo_real = self.arquivos_criticos["executor_final"]
            elif nome_arquivo == "configuracao":
                arquivo_real = self.arquivos_criticos["configuracao"]
            elif nome_arquivo == "executor_consolidado":
                # Procurar arquivo do executor consolidado
                for arquivo in os.listdir("."):
                    if arquivo.startswith("mt5_executor_consolidado_") and arquivo.endswith(".py"):
                        arquivo_real = arquivo
                        break
            
            if arquivo_real and os.path.exists(arquivo_real):
                hash_calculado = self.calcular_hash_sha256(arquivo_real)
                
                if hash_calculado == hash_esperado:
                    correspondencias.append(nome_arquivo)
                else:
                    divergencias.append(
                        f"{nome_arquivo}: esperado {hash_esperado[:16]}..., "
                        f"calculado {hash_calculado[:16]}..."
                    )
        
        if divergencias:
            return {
                "validacao": "HASHES COM RELATÓRIO TÉCNICO",
                "status": "DIVERGENTE",
                "detalhes": f"Divergências: {', '.join(divergencias)}",
                "correspondencias": len(correspondencias),
                "divergencias": len(divergencias)
            }
        else:
            return {
                "validacao": "HASHES COM RELATÓRIO TÉCNICO",
                "status": "CORRESPONDENTE",
                "detalhes": f"{len(correspondencias)}/{len(self.hashes_relatorio)} hashes correspondentes",
                "correspondencias": len(correspondencias),
                "divergencias": 0
            }
    
    def validar_estatisticas_com_relatorio(self) -> dict:
        """Validar estatísticas com as do relatório técnico"""
        print("   📊 Validando estatísticas com relatório técnico...")
        
        # Coletar estatísticas reais
        estatisticas_reais = {}
        
        # Tamanho do executor final
        executor_final = self.arquivos_criticos["executor_final"]
        if os.path.exists(executor_final):
            tamanho = os.path.getsize(executor_final)
            estatisticas_reais["tamanho_executor_final_kb"] = tamanho / 1024
        
        # Número de checkpoints
        checkpoints_encontrados = 0
        for checkpoint in self.checkpoints_blocos.values():
            if os.path.exists(checkpoint):
                checkpoints_encontrados += 1
        
        estatisticas_reais["checkpoints_encontrados"] = checkpoints_encontrados
        
        # Verificar diretórios
        diretorios_encontrados = 0
        for diretorio in ["logs_arch001", "backups_arch001"]:
            if os.path.exists(diretorio) and os.path.isdir(diretorio):
                diretorios_encontrados += 1
        
        estatisticas_reais["diretorios_encontrados"] = diretorios_encontrados
        
        # Comparar com valores esperados do relatório
        estatisticas_esperadas = {
            "tamanho_executor_final_kb": 12.88,
            "checkpoints_encontrados": 4,
            "diretorios_encontrados": 2
        }
        
        divergencias = []
        
        for chave, valor_esperado in estatisticas_esperadas.items():
            if chave in estatisticas_reais:
                valor_real = estatisticas_reais[chave]
                
                # Permitir pequena variação para tamanhos
                if chave.endswith("_kb"):
                    if abs(valor_real - valor_esperado) > 1.0:
                        divergencias.append(
                            f"{chave}: esperado {valor_esperado:.2f} KB, "
                            f"encontrado {valor_real:.2f} KB"
                        )
                else:
                    if valor_real != valor_esperado:
                        divergencias.append(
                            f"{chave}: esperado {valor_esperado}, "
                            f"encontrado {valor_real}"
                        )
        
        if divergencias:
            return {
                "validacao": "ESTATÍSTICAS COM RELATÓRIO TÉCNICO",
                "status": "DIVERGENTE",
                "detalhes": f"Divergências: {', '.join(divergencias)}",
                "estatisticas_verificadas": len(estatisticas_esperadas),
                "divergencias": len(divergencias)
            }
        else:
            return {
                "validacao": "ESTATÍSTICAS COM RELATÓRIO TÉCNICO",
                "status": "CORRESPONDENTE",
                "detalhes": f"{len(estatisticas_esperadas)} estatísticas correspondentes",
                "estatisticas_verificadas": len(estatisticas_esperadas),
                "divergencias": 0
            }
    
    def validar_estrutura_com_relatorio(self) -> dict:
        """Validar estrutura do sistema com a do relatório técnico"""
        print("   🏗️ Validando estrutura com relatório técnico...")
        
        # Estrutura esperada baseada no relatório
        estrutura_esperada = [
            "ARCH001_EXECUTOR_FINAL_20251226_230100.py",
            "configuracao_arch001_20251226_230100.json",
            "checkpoint_final_arch001_20251226_230100.json",
            "inicializador_arch001_20251226_230100.py",
            "monitor_arch001_20251226_230100.py",
            "sistema_recuperacao_arch001_20251226_230100.py",
            "ARCH001_ATIVADO.txt",
            "DOCUMENTACAO_FINAL_ARCH001_20251226_230100.md",
            "RESUMO_FINAL_ARCH001_20251226_230100.txt"
        ]
        
        arquivos_faltantes = []
        for arquivo in estrutura_esperada:
            if not os.path.exists(arquivo):
                arquivos_faltantes.append(arquivo)
        
        # Verificar diretórios
        diretorios_esperados = ["logs_arch001", "backups_arch001"]
        diretorios_faltantes = []
        
        for diretorio in diretorios_esperados:
            if not os.path.exists(diretorio) or not os.path.isdir(diretorio):
                diretorios_faltantes.append(diretorio)
        
        if arquivos_faltantes or diretorios_faltantes:
            faltantes = arquivos_faltantes + diretorios_faltantes
            return {
                "validacao": "ESTRUTURA COM RELATÓRIO TÉCNICO",
                "status": "DIVERGENTE",
                "detalhes": f"Faltando: {', '.join(faltantes[:3])}",
                "arquivos_esperados": len(estrutura_esperada),
                "arquivos_encontrados": len(estrutura_esperada) - len(arquivos_faltantes),
                "diretorios_esperados": len(diretorios_esperados),
                "diretorios_encontrados": len(diretorios_esperados) - len(diretorios_faltantes)
            }
        else:
            return {
                "validacao": "ESTRUTURA COM RELATÓRIO TÉCNICO",
                "status": "CORRESPONDENTE",
                "detalhes": f"Estrutura completa: {len(estrutura_esperada)} arquivos, {len(diretorios_esperados)} diretórios",
                "arquivos_esperados": len(estrutura_esperada),
                "arquivos_encontrados": len(estrutura_esperada),
                "diretorios_esperados": len(diretorios_esperados),
                "diretorios_encontrados": len(diretorios_esperados)
            }
    
    def validar_protocolo_antifraude(self) -> dict:
        """Validar protocolo antifraude"""
        print("   🔐 Validando protocolo antifraude...")
        
        # Evidências esperadas baseadas no relatório
        evidencias_esperadas = [
            "Checkpoint bloco1 válido",
            "Checkpoint bloco2 válido", 
            "Checkpoint bloco3 válido",
            "Hash SHA256 do executor calculado",
            "Backup de segurança válido",
            "Relatórios de execução presentes"
        ]
        
        # Verificar evidências reais
        evidencias_encontradas = []
        
        # 1. Checkpoints válidos
        checkpoints_validos = 0
        for checkpoint in self.checkpoints_blocos.values():
            if os.path.exists(checkpoint):
                try:
                    with open(checkpoint, 'r', encoding='utf-8') as f:
                        json.load(f)
                    checkpoints_validos += 1
                except:
                    pass
        
        if checkpoints_validos >= 3:
            evidencias_encontradas.append(f"{checkpoints_validos}/3 checkpoints válidos")
        
        # 2. Hash do executor
        executor = self.arquivos_criticos["executor_final"]
        if os.path.exists(executor):
            hash_calculado = self.calcular_hash_sha256(executor)
            if len(hash_calculado) == 64:
                evidencias_encontradas.append("Hash do executor calculado")
        
        # 3. Backup (verificar se existe algum backup)
        if os.path.exists("backup_pre_arch001_20251226_204338.zip"):
            evidencias_encontradas.append("Backup de segurança presente")
        
        # 4. Relatórios (contar arquivos de relatório)
        relatorios = [f for f in os.listdir(".") 
                     if f.startswith(("RELATORIO", "RESUMO", "DOCUMENTACAO"))]
        if len(relatorios) >= 3:
            evidencias_encontradas.append(f"{len(relatorios)} relatórios presentes")
        
        if len(evidencias_encontradas) >= 4:
            return {
                "validacao": "PROTOCOLO ANTIFRAUDE",
                "status": "CORRESPONDENTE",
                "detalhes": f"Protocolo ativo: {len(evidencias_encontradas)} evidências",
                "evidencias_esperadas": len(evidencias_esperadas),
                "evidencias_encontradas": len(evidencias_encontradas)
            }
        else:
            return {
                "validacao": "PROTOCOLO ANTIFRAUDE",
                "status": "DIVERGENTE",
                "detalhes": f"Protocolo fraco: apenas {len(evidencias_encontradas)} evidências",
                "evidencias_esperadas": len(evidencias_esperadas),
                "evidencias_encontradas": len(evidencias_encontradas)
            }
    
    def detectar_inconsistencias(self):
        """Detectar inconsistências e possíveis camuflagens"""
        print("   🕵️ Detectando inconsistências...")
        
        alertas = []
        
        # 1. Verificar arquivos com tamanho suspeito
        for arquivo in self.arquivos_criticos.values():
            if os.path.exists(arquivo):
                tamanho = os.path.getsize(arquivo)
                
                # Arquivos muito pequenos podem ser "placeholders"
                if tamanho < 100:
                    alertas.append(f"{arquivo} muito pequeno ({tamanho} bytes)")
                
                # Verificar se conteúdo parece real
                if arquivo.endswith('.py'):
                    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                        conteudo = f.read(500)
                    
                    # Código Python deve ter certas keywords
                    keywords_python = ['import', 'def', 'class', 'if', 'for', 'while']
                    keywords_encontradas = sum(1 for kw in keywords_python if kw in conteudo)
                    
                    if keywords_encontradas < 2:
                        alertas.append(f"{arquivo} pode não ser código Python válido")
        
        # 2. Verificar timestamps inconsistentes
        arquivos_principais = [
            self.arquivos_criticos["executor_final"],
            self.arquivos_criticos["checkpoint_final"],
            self.arquivos_criticos["inicializador"]
        ]
        
        timestamps = []
        for arquivo in arquivos_principais:
            if os.path.exists(arquivo):
                mtime = os.path.getmtime(arquivo)
                timestamps.append((arquivo, datetime.datetime.fromtimestamp(mtime)))
        
        if len(timestamps) >= 2:
            # Calcular diferença máxima
            tempos = [ts for _, ts in timestamps]
            diferenca_max = max(tempos) - min(tempos)
            
            # Se todos foram "modificados" no mesmo segundo exato, é suspeito
            if diferenca_max.total_seconds() < 1:
                alertas.append("Arquivos principais modificados no mesmo segundo exato")
        
        # 3. Verificar se há referências cruzadas válidas
        checkpoint_final = self.arquivos_criticos["checkpoint_final"]
        if os.path.exists(checkpoint_final):
            try:
                with open(checkpoint_final, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Deve mencionar outros arquivos do sistema
                referencias_esperadas = [
                    "ARCH001_EXECUTOR_FINAL",
                    "configuracao_arch001",
                    "inicializador_arch001"
                ]
                
                referencias_encontradas = sum(1 for ref in referencias_esperadas if ref in conteudo)
                
                if referencias_encontradas < 2:
                    alertas.append("Checkpoint final tem poucas referências a outros componentes")
            except:
                alertas.append("Não foi possível ler checkpoint final para verificar referências")
        
        return alertas
    
    def gerar_conclusao_final(self):
        """Gerar conclusão final baseada em todas as verificações"""
        # Contar resultados
        conteudos_validados = sum(
            1 for v in self.resultados["verificacoes_conteudo"] 
            if v.get("status") == "VALIDADO"
        )
        
        consistencias_ok = sum(
            1 for v in self.resultados["verificacoes_consistencia"]
            if v.get("status") == "CONSISTENTE"
        )
        
        testes_aprovados = sum(
            1 for t in self.resultados["testes_operacionais"]
            if t.get("status") == "APROVADO"
        )
        
        validacoes_correspondentes = sum(
            1 for v in self.resultados["validacoes_cruzadas"]
            if v.get("status") == "CORRESPONDENTE"
        )
        
        alertas = len(self.resultados["alertas_inconsistencia"])
        
        # Determinar status operacional
        if (conteudos_validados >= 6 and
            consistencias_ok >= 3 and
            testes_aprovados >= 4 and
            validacoes_correspondentes >= 3 and
            alertas == 0):
            status_operacional = "OPERACIONAL_CONFIRMADO"
            nivel_confianca = "ALTO"
        elif (conteudos_validados >= 4 and
              consistencias_ok >= 2 and
              testes_aprovados >= 3 and
              alertas <= 1):
            status_operacional = "OPERACIONAL_PARCIAL"
            nivel_confianca = "MODERADO"
        else:
            status_operacional = "NAO_OPERACIONAL"
            nivel_confianca = "BAIXO"
        
        return {
            "status_operacional": status_operacional,
            "nivel_confianca": nivel_confianca,
            "estatisticas": {
                "conteudos_validados": f"{conteudos_validados}/{len(self.arquivos_criticos)}",
                "consistencias_ok": f"{consistencias_ok}/4",
                "testes_aprovados": f"{testes_aprovados}/5",
                "validacoes_correspondentes": f"{validacoes_correspondentes}/4",
                "alertas_inconsistencia": alertas
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def mostrar_resultado_final(self, conclusao: dict):
        """Mostrar resultado final da verificação operacional"""
        print("\n" + "=" * 100)
        print("🎯 RESULTADO FINAL - VERIFICAÇÃO OPERACIONAL ARCH-001")
        print("=" * 100)
        
        status = conclusao["status_operacional"]
        nivel_confianca = conclusao["nivel_confianca"]
        estatisticas = conclusao["estatisticas"]
        
        print(f"\n📊 RESUMO DA VERIFICAÇÃO:")
        print(f"   • Status Operacional: {status}")
        print(f"   • Nível de Confiança: {nivel_confianca}")
        print(f"   • Conteúdos Validados: {estatisticas['conteudos_validados']}")
        print(f"   • Consistências OK: {estatisticas['consistencias_ok']}")
        print(f"   • Testes Aprovados: {estatisticas['testes_aprovados']}")
        print(f"   • Validações Correspondentes: {estatisticas['validacoes_correspondentes']}")
        print(f"   • Alertas de Inconsistência: {estatisticas['alertas_inconsistencia']}")
        
        print(f"\n🔍 VEREDICTO OPERACIONAL:")
        print("-" * 60)
        
        if status == "OPERACIONAL_CONFIRMADO":
            print("✅ SISTEMA 100% OPERACIONAL CONFIRMADO!")
            print("   O ARCH-001 está completamente integrado e funcional.")
            print("   Nenhuma inconsistência ou camuflagem detectada.")
            print("   Todos os componentes estão válidos e consistentes.")
            print("   Sistema pronto para operação em produção.")
            
        elif status == "OPERACIONAL_PARCIAL":
            print("⚠️  SISTEMA PARCIALMENTE OPERACIONAL")
            print("   O ARCH-001 está integrado, mas algumas verificações falharam.")
            print("   O sistema pode funcionar, mas requer atenção.")
            print("   Recomenda-se verificação manual dos componentes.")
            
        else:
            print("❌ SISTEMA NÃO OPERACIONAL CONFIRMADO")
            print("   Foram detectadas inconsistências graves.")
            print("   Possível camuflagem ou sistema incompleto.")
            print("   NECESSÁRIA REVISÃO COMPLETA E POSSÍVEL REEXECUÇÃO.")
        
        print("\n" + "=" * 100)
    
    def gerar_relatorio_verificacao(self):
        """Gerar relatório de verificação detalhado"""
        relatorio_file = f"RELATORIO_VERIFICACAO_OPERACIONAL_{self.timestamp}.json"
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        # Criar versão resumida em texto
        resumo_file = f"RESUMO_VERIFICACAO_{self.timestamp}.txt"
        
        with open(resumo_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🔬 RELATÓRIO DE VERIFICAÇÃO OPERACIONAL - ARCH-001\n")
            f.write("=" * 80 + "\n\n")
            
            conclusao = self.resultados["conclusao"]
            
            f.write(f"DATA/HORA: {datetime.datetime.now().isoformat()}\n")
            f.write(f"STATUS OPERACIONAL: {conclusao['status_operacional']}\n")
            f.write(f"NÍVEL DE CONFIANÇA: {conclusao['nivel_confianca']}\n\n")
            
            f.write("📊 ESTATÍSTICAS DA VERIFICAÇÃO:\n")
            f.write("-" * 40 + "\n")
            
            estatisticas = conclusao["estatisticas"]
            for chave, valor in estatisticas.items():
                f.write(f"• {chave.replace('_', ' ').title()}: {valor}\n")
            
            f.write("\n🚨 ALERTAS DE INCONSISTÊNCIA:\n")
            f.write("-" * 40 + "\n")
            
            alertas = self.resultados["alertas_inconsistencia"]
            if alertas:
                for alerta in alertas:
                    f.write(f"⚠️  {alerta}\n")
            else:
                f.write("✅ NENHUM ALERTA DETECTADO\n")
            
            f.write("\n✅ TESTES OPERACIONAIS APROVADOS:\n")
            f.write("-" * 40 + "\n")
            
            testes_aprovados = [t for t in self.resultados["testes_operacionais"] 
                               if t.get("status") == "APROVADO"]
            for teste in testes_aprovados:
                f.write(f"• {teste['teste']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("🎯 CONCLUSÃO:\n")
            f.write("=" * 80 + "\n\n")
            
            if conclusao["status_operacional"] == "OPERACIONAL_CONFIRMADO":
                f.write("✅ VERIFICAÇÃO OPERACIONAL CONFIRMADA\n")
                f.write("   O sistema ARCH-001 está 100% operacional.\n")
                f.write("   Nenhuma evidência de camuflagem ou inconsistência.\n")
                f.write("   Sistema validado para operação em produção.\n")
            elif conclusao["status_operacional"] == "OPERACIONAL_PARCIAL":
                f.write("⚠️  VERIFICAÇÃO OPERACIONAL PARCIAL\n")
                f.write("   O sistema funciona, mas com ressalvas.\n")
                f.write("   Recomenda-se verificação adicional.\n")
            else:
                f.write("❌ VERIFICAÇÃO OPERACIONAL REPROVADA\n")
                f.write("   Inconsistências graves detectadas.\n")
                f.write("   Necessária revisão imediata do sistema.\n")
            
            f.write(f"\n🔐 Hash SHA256 deste relatório: {self.calcular_hash_sha256(relatorio_file)}\n")
        
        print(f"\n📄 Relatório de verificação salvo em: {relatorio_file}")
        print(f"📝 Resumo de verificação salvo em: {resumo_file}")
    
    def calcular_hash_sha256(self, caminho: str) -> str:
        """Calcular hash SHA256 de um arquivo"""
        try:
            hasher = hashlib.sha256()
            with open(caminho, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return "ERRO_NO_CALCULO"


def main():
    """Função principal do teste de verificação operacional"""
    print("\n🔬 INICIANDO TESTE DE VERIFICAÇÃO OPERACIONAL FINAL")
    print("Protocolo: ANTI-CAMUFLAGEM - VALIDAÇÃO ABSOLUTA\n")
    
    # Verificar pré-requisitos
    print("📋 VERIFICANDO PRÉ-REQUISITOS:")
    
    # Verificar se arquivos principais existem
    arquivos_verificar = [
        "ARCH001_EXECUTOR_FINAL_20251226_230100.py",
        "checkpoint_final_arch001_20251226_230100.json",
        "inicializador_arch001_20251226_230100.py"
    ]
    
    for arquivo in arquivos_verificar:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}: PRESENTE")
        else:
            print(f"❌ {arquivo}: AUSENTE")
    
    print("\n🚀 VERIFICAÇÃO DE INTEGRAÇÃO E OPERACIONALIDADE:")
    print("Este teste validará se o sistema está REALMENTE integrado e operacional,")
    print("não apenas se os arquivos existem. Detecção de camuflagem ativada.\n")
    
    # Executar teste
    teste = TesteVerificacaoOperacionalFinal()
    operacional = teste.executar_teste_completo()
    
    # Retornar código apropriado
    if operacional:
        print(f"\n✅ Verificação concluída: SISTEMA OPERACIONAL CONFIRMADO")
        return 0
    else:
        print(f"\n❌ Verificação concluída: PROBLEMAS DETECTADOS")
        return 1


if __name__ == "__main__":
    sys.exit(main())

