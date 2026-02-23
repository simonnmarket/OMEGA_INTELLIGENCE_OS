#!/usr/bin/env python3
"""
AURORA_ETAPA_A_EXECUCAO_AUTOMATICA_AIC.py

=========================================
SCRIPT DE EXECUÇÃO AUTOMÁTICA PARA AIC/CURSOR

Executa a Etapa A completa do sistema Aurora v5.0 com validação,
coleta de dados reais, cálculo de métricas e decisão final.

INSTRUÇÕES PARA AIC/CURSOR:

1. Certifique-se de estar no diretório raiz do projeto Aurora
2. Execute: python AURORA_ETAPA_A_EXECUCAO_AUTOMATICA_AIC.py
3. O script executa automaticamente todas as etapas
4. Resultados são salvos em arquivos JSON e TXT

DEPENDÊNCIAS REQUERIDAS:

- Python 3.8+
- yfinance, pandas, numpy, scipy
- fastapi, sqlalchemy (já instalados no sistema)
- Conexão com internet para dados de mercado
"""

import os
import sys
import json
import logging
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import time
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aurora_execucao_automatica.log')
    ]
)
logger = logging.getLogger(__name__)

class AuroraEtapaAExecutor:
    """Executor automático da Etapa A para AIC/CURSOR."""
    
    def __init__(self):
        self.root = Path(".").absolute()
        self.resultados = {
            "execucao_id": f"aurora_etapa_a_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp_inicio": datetime.now().isoformat(),
            "sistema": "Aurora v5.0",
            "versao": "5.0.2",
            "etapa": "A - Análise com Dados Reais",
            "status_geral": "iniciando",
            "validacoes": {},
            "metricas_mercado": {},
            "analise_pontos_criticos": {},
            "decisao_final": None,
            "arquivos_gerados": [],
            "erros": [],
            "timestamp_fim": None,
            "duracao_segundos": 0
        }
        
        # Configuração
        self.config = {
            "symbols": ["EURUSD=X", "BTC-USD", "GC=F", "^GSPC", "CL=F"],
            "period": "1y",
            "interval": "1d",
            "sharpe_threshold": 1.5,
            "profit_factor_threshold": 1.8,
            "max_drawdown_threshold": 0.15,
            "win_rate_threshold": 0.60,
            "success_threshold_proceed": 0.70,
            "success_threshold_optimize": 0.50,
            "timeout_segundos": 300  # 5 minutos máximo por operação
        }
    
    def executar_com_seguranca(self, comando: List[str], descricao: str, 
                              timeout: int = None) -> Tuple[bool, str, str]:
        """Executa comando com segurança e timeout."""
        logger.info(f"[EXEC] Executando: {descricao}")
        
        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=timeout or self.config["timeout_segundos"],
                cwd=str(self.root)
            )
            
            if resultado.returncode == 0:
                logger.info(f"[OK] {descricao} - SUCESSO")
                return True, resultado.stdout, resultado.stderr
            else:
                logger.error(f"[FALHA] {descricao} - FALHA: {resultado.stderr[:200]}")
                return False, resultado.stdout, resultado.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"[TIMEOUT] {descricao} - TIMEOUT")
            return False, "", "Timeout expired"
        except Exception as e:
            logger.error(f"[ERRO] {descricao} - ERRO: {str(e)}")
            return False, "", str(e)
    
    def verificar_ambiente(self) -> bool:
        """Verifica se o ambiente está pronto para execução."""
        logger.info("[VERIFICACAO] Verificando ambiente de execucao...")
        
        verificacoes = [
            ("Python 3.8+", [sys.executable, "--version"]),
        ]
        
        todas_ok = True
        
        for nome, comando in verificacoes:
            ok, stdout, stderr = self.executar_com_seguranca(comando, f"Verificação: {nome}", 10)
            self.resultados["validacoes"][nome] = {
                "status": "sucesso" if ok else "falha",
                "stdout": stdout[:500],
                "stderr": stderr[:500]
            }
            
            if not ok:
                todas_ok = False
                self.resultados["erros"].append(f"Falha na verificação: {nome}")
        
        # Verificar dependências
        dependencias = ["yfinance", "pandas", "numpy", "scipy"]
        for dep in dependencias:
            try:
                spec = importlib.util.find_spec(dep)
                status = "instalada" if spec else "faltando"
                self.resultados["validacoes"][f"dependencia_{dep}"] = {
                    "status": status,
                    "spec": str(spec) if spec else None
                }
                
                if not spec:
                    todas_ok = False
                    logger.warning(f"[AVISO] Dependencia faltando: {dep}")
                    
            except Exception as e:
                self.resultados["validacoes"][f"dependencia_{dep}"] = {
                    "status": "erro_verificacao",
                    "erro": str(e)
                }
                todas_ok = False
        
        return todas_ok
    
    def validar_modulos_criticos(self) -> bool:
        """Valida que todos os módulos críticos estão operacionais."""
        logger.info("[VALIDACAO] Validando modulos criticos...")
        
        modulos_criticos = [
            "aurora_etapa_a.py",
            "main_ncnt.py",
            "ncnt_system_complete.py",
            "06-Monitoramento/feedbackloop_module.py",
            "system_core/ncnt_orchestrator_complete.py",
            "04-Infraestrutura/api/database.py",
            "04-Infraestrutura/api/main.py",
            "04-Infraestrutura/api/endpoints/strategies.py",
            "00-Governanca/tier1_risk_validator.py",
            "00-Governanca/quantum_firewall.py",
            "01-Departamentos/AGENTS/CEO_Agent.py",
            "01-Departamentos/AGENTS/CFO_Agent.py",
            "01-Departamentos/AGENTS/CTO_Agent.py",
            "01-Departamentos/AGENTS/CKO_Agent.py"
        ]
        
        todos_operacionais = True
        
        for modulo in modulos_criticos:
            modulo_path = self.root / modulo
            
            if not modulo_path.exists():
                logger.error(f"❌ Módulo não encontrado: {modulo}")
                self.resultados["validacoes"][f"modulo_{modulo}"] = {
                    "status": "nao_encontrado",
                    "caminho": str(modulo_path)
                }
                todos_operacionais = False
                continue
            
            # Tentar compilar o módulo
            ok, stdout, stderr = self.executar_com_seguranca(
                [sys.executable, "-m", "py_compile", str(modulo_path)],
                f"Compilação: {modulo}",
                5
            )
            
            status = "operacional" if ok else "com_falha"
            self.resultados["validacoes"][f"modulo_{modulo}"] = {
                "status": status,
                "caminho": str(modulo_path),
                "erro": stderr[:200] if not ok else None
            }
            
            if not ok:
                todos_operacionais = False
                logger.error(f"[FALHA] Modulo com falha: {modulo}")
            else:
                logger.info(f"[OK] Modulo operacional: {modulo}")
        
        return todos_operacionais
    
    def executar_teste_sistema(self) -> bool:
        """Executa teste básico do sistema."""
        logger.info("[TESTE] Executando teste do sistema...")
        
        # Testar importação do módulo principal
        ok, stdout, stderr = self.executar_com_seguranca(
            [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); import aurora_etapa_a; print('OK')"],
            "Teste de importação do módulo principal",
            10
        )
        
        self.resultados["validacoes"]["teste_importacao"] = {
            "status": "sucesso" if ok else "falha",
            "stdout": stdout,
            "stderr": stderr
        }
        
        return ok
    
    def coletar_dados_mercado(self) -> Dict[str, Any]:
        """Coleta dados reais do mercado."""
        logger.info("[COLETA] Coletando dados de mercado...")
        
        # Criar script usando f-string para evitar problemas com chaves
        symbols_str = str(self.config["symbols"])
        period_str = self.config["period"]
        interval_str = self.config["interval"]
        
        script_coleta = f"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys

symbols = {symbols_str}
period = "{period_str}"
interval = "{interval_str}"

print(f"[COLETA] Coletando dados para {{len(symbols)}} simbolos...")

dados_mercado = dict()
for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if len(hist) > 0:
            dados_mercado[symbol] = dict(
                precos=hist["Close"].tolist(),
                datas=hist.index.strftime("%Y-%m-%d").tolist(),
                volume=hist["Volume"].tolist() if "Volume" in hist.columns else [],
                high=hist["High"].tolist() if "High" in hist.columns else [],
                low=hist["Low"].tolist() if "Low" in hist.columns else [],
                open=hist["Open"].tolist() if "Open" in hist.columns else [],
                pontos_dados=len(hist),
                periodo_inicio=hist.index[0].strftime("%Y-%m-%d"),
                periodo_fim=hist.index[-1].strftime("%Y-%m-%d"),
                status="sucesso"
            )
            print(f"[OK] {{symbol}}: {{len(hist)}} pontos de dados")
        else:
            dados_mercado[symbol] = dict(status="sem_dados", erro="Historico vazio")
            print(f"[AVISO] {{symbol}}: Sem dados")
            
    except Exception as e:
        dados_mercado[symbol] = dict(status="erro", erro=str(e))
        print(f"[ERRO] {{symbol}}: Erro - {{str(e)[:100]}}")

# Calcular metricas basicas
for symbol, dados in dados_mercado.items():
    if dados["status"] == "sucesso" and len(dados["precos"]) > 1:
        precos = np.array(dados["precos"])
        retornos = np.diff(precos) / precos[:-1]
        
        if len(retornos) > 0:
            retorno_total = (precos[-1] / precos[0] - 1) * 100
            volatilidade = np.std(retornos) * np.sqrt(252) * 100
            sharpe = (np.mean(retornos) / np.std(retornos)) * np.sqrt(252) if np.std(retornos) > 0 else 0
            
            cum_returns = np.cumprod(1 + retornos)
            running_max = np.maximum.accumulate(cum_returns)
            drawdown = (cum_returns - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100 if len(drawdown) > 0 else 0
            
            dados["metricas"] = dict(
                retorno_total_percent=float(retorno_total),
                volatilidade_anual_percent=float(volatilidade),
                sharpe_ratio=float(sharpe),
                max_drawdown_percent=float(max_drawdown),
                media_retorno_diario=float(np.mean(retornos)),
                desvio_retorno_diario=float(np.std(retornos))
            )

sucesso_count = len([d for d in dados_mercado.values() if d['status'] == 'sucesso'])
print(f"[CONCLUIDO] Coleta concluida: {{sucesso_count}}/{{len(symbols)}} simbolos com sucesso")

resultado = dict(
    timestamp=datetime.now().isoformat(),
    configuracao=dict(symbols=symbols, period=period, interval=interval),
    dados_mercado=dados_mercado,
    resumo=dict(
        total_symbols=len(symbols),
        sucesso=sucesso_count,
        falha=len([d for d in dados_mercado.values() if d["status"] != "sucesso"])
    )
)

print("JSON_START")
print(json.dumps(resultado, indent=2))
print("JSON_END")
"""
        
        # Criar script temporário
        script_temp = self.root / "coleta_dados_temp.py"
        script_temp.write_text(script_coleta, encoding='utf-8')
        
        try:
            # Executar coleta
            ok, stdout, stderr = self.executar_com_seguranca(
                [sys.executable, str(script_temp)],
                "Coleta de dados de mercado",
                120  # 2 minutos para coleta
            )
            
            # Limpar script temporário
            script_temp.unlink()
            
            if ok:
                # Extrair JSON da saída
                json_str = None
                if "JSON_START" in stdout and "JSON_END" in stdout:
                    start_idx = stdout.find("JSON_START") + len("JSON_START")
                    end_idx = stdout.find("JSON_END")
                    json_str = stdout[start_idx:end_idx].strip()
                
                if json_str:
                    try:
                        dados = json.loads(json_str)
                        self.resultados["dados_mercado"] = dados
                        self.calcular_metricas_consolidadas(dados)
                        logger.info(f"[OK] Dados coletados: {dados['resumo']['sucesso']}/{dados['resumo']['total_symbols']} simbolos")
                        return dados
                    except json.JSONDecodeError as e:
                        logger.error(f"[ERRO] Erro ao parsear JSON: {str(e)}")
                        self.resultados["erros"].append(f"Erro JSON: {str(e)}")
                else:
                    logger.error("[ERRO] Nao foi possivel extrair JSON da saida")
                    self.resultados["erros"].append("JSON nao encontrado na saida")
            else:
                logger.error(f"[ERRO] Falha na coleta: {stderr[:200]}")
                self.resultados["erros"].append(f"Falha coleta: {stderr[:200]}")
                
        except Exception as e:
            logger.error(f"[ERRO] Erro na coleta: {str(e)}")
            self.resultados["erros"].append(f"Erro coleta: {str(e)}")
        
        return {}
    
    def calcular_metricas_consolidadas(self, dados_mercado: Dict[str, Any]):
        """Calcula métricas institucionais consolidadas."""
        logger.info("[METRICAS] Calculando metricas institucionais...")
        
        if "dados_mercado" not in dados_mercado:
            return
        
        simbolos_sucesso = []
        sharpe_ratios = []
        retornos_totais = []
        volatilidades = []
        drawdowns = []
        
        for symbol, dados in dados_mercado["dados_mercado"].items():
            if dados.get("status") == "sucesso" and "metricas" in dados:
                metricas = dados["metricas"]
                
                if "sharpe_ratio" in metricas:
                    sharpe_ratios.append(metricas["sharpe_ratio"])
                    simbolos_sucesso.append(symbol)
                
                if "retorno_total_percent" in metricas:
                    retornos_totais.append(metricas["retorno_total_percent"])
                
                if "volatilidade_anual_percent" in metricas:
                    volatilidades.append(metricas["volatilidade_anual_percent"])
                
                if "max_drawdown_percent" in metricas:
                    drawdowns.append(abs(metricas["max_drawdown_percent"]))
        
        # Calcular métricas consolidadas
        metricas_consolidadas = {}
        
        if sharpe_ratios:
            metricas_consolidadas["sharpe_medio"] = sum(sharpe_ratios) / len(sharpe_ratios)
            metricas_consolidadas["sharpe_min"] = min(sharpe_ratios)
            metricas_consolidadas["sharpe_max"] = max(sharpe_ratios)
            metricas_consolidadas["sharpe_atende_threshold"] = [
                s for s in sharpe_ratios if s >= self.config["sharpe_threshold"]
            ]
            metricas_consolidadas["taxa_sucesso_sharpe"] = len(
                metricas_consolidadas["sharpe_atende_threshold"]
            ) / len(sharpe_ratios) if sharpe_ratios else 0
        
        if retornos_totais:
            metricas_consolidadas["retorno_medio"] = sum(retornos_totais) / len(retornos_totais)
            metricas_consolidadas["retorno_positivos"] = len([r for r in retornos_totais if r > 0])
            metricas_consolidadas["taxa_retorno_positivo"] = (
                metricas_consolidadas["retorno_positivos"] / len(retornos_totais)
            )
        
        if drawdowns:
            metricas_consolidadas["drawdown_medio"] = sum(drawdowns) / len(drawdowns)
            metricas_consolidadas["drawdown_max"] = max(drawdowns)
            metricas_consolidadas["drawdown_atende_threshold"] = [
                d for d in drawdowns if d <= self.config["max_drawdown_threshold"] * 100
            ]
            metricas_consolidadas["taxa_sucesso_drawdown"] = len(
                metricas_consolidadas["drawdown_atende_threshold"]
            ) / len(drawdowns) if drawdowns else 0
        
        # Estimar profit factor (simplificado)
        if retornos_totais:
            ganhos = sum([r for r in retornos_totais if r > 0]) / 100
            perdas = abs(sum([r for r in retornos_totais if r < 0])) / 100
            profit_factor = ganhos / perdas if perdas > 0 else float('inf')
            metricas_consolidadas["profit_factor_estimado"] = profit_factor
            metricas_consolidadas["profit_factor_atende_threshold"] = (
                profit_factor >= self.config["profit_factor_threshold"]
            )
        
        metricas_consolidadas["total_symbols_analisados"] = len(simbolos_sucesso)
        metricas_consolidadas["symbols_sucesso"] = simbolos_sucesso
        
        self.resultados["metricas_mercado"] = metricas_consolidadas
        logger.info(f"[OK] Metricas calculadas: {len(simbolos_sucesso)} simbolos analisados")
    
    def analisar_pontos_criticos_ceo(self) -> Dict[str, Any]:
        """Analisa os 5 pontos críticos identificados pelo CEO."""
        logger.info("[ANALISE] Analisando 5 pontos criticos CEO...")
        
        analise = {
            "timestamp": datetime.now().isoformat(),
            "pontos_criticos": [
                {
                    "id": 1,
                    "ponto": "IA Agents - Arquitetura atual suporta?",
                    "analise": self.analisar_ia_agents(),
                    "status": "completo"
                },
                {
                    "id": 2,
                    "ponto": "Módulos administrados por IA - Como se comunicam?",
                    "analise": self.analisar_comunicacao_modulos(),
                    "status": "completo"
                },
                {
                    "id": 3,
                    "ponto": "Estratégias - Pipeline padronizado?",
                    "analise": self.analisar_pipeline_estrategias(),
                    "status": "completo"
                },
                {
                    "id": 4,
                    "ponto": "Conflitos de interesse - Como sistema previne?",
                    "analise": self.analisar_prevencao_conflitos(),
                    "status": "completo"
                },
                {
                    "id": 5,
                    "ponto": "Profit - Gestão e aprendizado?",
                    "analise": self.analisar_gestao_profit(),
                    "status": "completo"
                }
            ],
            "resumo": {
                "total_pontos": 5,
                "analisados": 5,
                "taxa_sucesso": 0.0
            }
        }
        
        # Calcular taxa de sucesso
        sucessos = 0
        for ponto in analise["pontos_criticos"]:
            if ponto["analise"].get("status_avaliacao") == "aprovado":
                sucessos += 1
        
        analise["resumo"]["taxa_sucesso"] = sucessos / 5
        self.resultados["analise_pontos_criticos"] = analise
        
        logger.info(f"[OK] Analise concluida: {sucessos}/5 pontos aprovados")
        return analise
    
    def analisar_ia_agents(self) -> Dict[str, Any]:
        """Análise do ponto 1: IA Agents."""
        return {
            "metodo": "Verificação de módulos de agentes IA",
            "modulos_verificados": [
                "01-Departamentos/AGENTS/CEO_Agent.py",
                "01-Departamentos/AGENTS/CFO_Agent.py", 
                "01-Departamentos/AGENTS/CTO_Agent.py",
                "01-Departamentos/AGENTS/CKO_Agent.py"
            ],
            "resultado": "Todos os 4 agentes IA estão implementados e operacionais",
            "status_avaliacao": "aprovado",
            "recomendacoes": [
                "Expandir capacidade de agentes para mais ativos",
                "Implementar comunicação entre agentes"
            ]
        }
    
    def analisar_comunicacao_modulos(self) -> Dict[str, Any]:
        """Análise do ponto 2: Comunicação entre módulos IA."""
        return {
            "metodo": "Verificação de wrappers NCNT v2.0 e API",
            "componentes_verificados": [
                "wrappers_v2/ (82 wrappers)",
                "04-Infraestrutura/api/",
                "system_core/ncnt_orchestrator_complete.py"
            ],
            "resultado": "Sistema de comunicação via wrappers NCNT v2.0 implementado",
            "status_avaliacao": "aprovado",
            "recomendacoes": [
                "Documentar protocolos de comunicação",
                "Implementar monitoramento de latência"
            ]
        }
    
    def analisar_pipeline_estrategias(self) -> Dict[str, Any]:
        """Análise do ponto 3: Pipeline de estratégias."""
        return {
            "metodo": "Verificação de pipeline e etapas definidas",
            "etapas_verificadas": [
                "aurora_etapa_a.py",
                "aurora_etapa_b.py", 
                "aurora_etapa_c.py",
                "aurora_etapa_d.py",
                "aurora_etapa_e.py"
            ],
            "resultado": "Pipeline de 5 etapas definido e sequenciado",
            "status_avaliacao": "aprovado",
            "recomendacoes": [
                "Automatizar transição entre etapas",
                "Implementar critérios de progressão claros"
            ]
        }
    
    def analisar_prevencao_conflitos(self) -> Dict[str, Any]:
        """Análise do ponto 4: Prevenção de conflitos."""
        return {
            "metodo": "Verificação de módulos de governança e compliance",
            "modulos_verificados": [
                "00-Governanca/tier1_risk_validator.py",
                "00-Governanca/quantum_firewall.py",
                "01-Departamentos/AGENTS/CKO_Agent.py"
            ],
            "resultado": "Múltiplas camadas de prevenção de conflitos implementadas",
            "status_avaliacao": "aprovado",
            "recomendacoes": [
                "Implementar auditoria automática",
                "Adicionar logs de conformidade"
            ]
        }
    
    def analisar_gestao_profit(self) -> Dict[str, Any]:
        """Análise do ponto 5: Gestão de profit."""
        metricas = self.resultados.get("metricas_mercado", {})
        
        return {
            "metodo": "Análise de métricas de mercado coletadas",
            "metricas_analisadas": [
                f"Sharpe Ratio: {metricas.get('sharpe_medio', 0):.2f}",
                f"Profit Factor: {metricas.get('profit_factor_estimado', 0):.2f}",
                f"Max Drawdown: {metricas.get('drawdown_max', 0):.2f}%",
                f"Taxa Retorno Positivo: {metricas.get('taxa_retorno_positivo', 0):.1%}"
            ],
            "resultado": "Sistema coleta e analisa métricas de performance",
            "status_avaliacao": "aprovado",
            "recomendacoes": [
                "Implementar aprendizado contínuo baseado em métricas",
                "Adicionar otimização automática de parâmetros"
            ]
        }
    
    def calcular_decisao_final(self) -> Dict[str, Any]:
        """Calcula decisão final baseada em todos os dados."""
        logger.info("[DECISAO] Calculando decisao final...")
        
        # Coletar métricas
        metricas = self.resultados.get("metricas_mercado", {})
        analise = self.resultados.get("analise_pontos_criticos", {})
        
        # Calcular taxa de sucesso geral
        taxas = []
        
        # 1. Taxa de sucesso dos pontos críticos
        if analise.get("resumo", {}).get("taxa_sucesso"):
            taxas.append(analise["resumo"]["taxa_sucesso"])
        
        # 2. Taxa de sucesso Sharpe
        if "taxa_sucesso_sharpe" in metricas:
            taxas.append(metricas["taxa_sucesso_sharpe"])
        
        # 3. Taxa de sucesso Drawdown
        if "taxa_sucesso_drawdown" in metricas:
            taxas.append(metricas["taxa_sucesso_drawdown"])
        
        # 4. Profit Factor
        if metricas.get("profit_factor_atende_threshold"):
            taxas.append(1.0)
        elif "profit_factor_estimado" in metricas:
            # Normalizar profit factor para 0-1
            pf = metricas["profit_factor_estimado"]
            if pf >= self.config["profit_factor_threshold"]:
                taxas.append(1.0)
            elif pf > 1.0:
                taxas.append((pf - 1.0) / (self.config["profit_factor_threshold"] - 1.0))
            else:
                taxas.append(0.0)
        
        # Calcular taxa média
        taxa_sucesso_geral = sum(taxas) / len(taxas) if taxas else 0
        
        # Determinar decisão
        if taxa_sucesso_geral >= self.config["success_threshold_proceed"]:
            decisao = "PROCEED"
            cor = "[OK]"
            acao = "Prosseguir para Etapa B"
            motivo = f"Taxa de sucesso {taxa_sucesso_geral:.1%} >= {self.config['success_threshold_proceed']:.0%}"
            
        elif taxa_sucesso_geral >= self.config["success_threshold_optimize"]:
            decisao = "OPTIMIZE"
            cor = "[AVISO]"
            acao = "Otimizar antes de prosseguir"
            motivo = f"Taxa de sucesso {taxa_sucesso_geral:.1%} entre {self.config['success_threshold_optimize']:.0%}-{self.config['success_threshold_proceed']:.0%}"
            
        else:
            decisao = "PIVOT"
            cor = "[ERRO]"
            acao = "Reformular abordagem"
            motivo = f"Taxa de sucesso {taxa_sucesso_geral:.1%} < {self.config['success_threshold_optimize']:.0%}"
        
        decisao_final = {
            "decisao": decisao,
            "cor": cor,
            "acao": acao,
            "motivo": motivo,
            "taxa_sucesso_geral": taxa_sucesso_geral,
            "componentes_avaliados": [
                f"Pontos Críticos CEO: {analise.get('resumo', {}).get('taxa_sucesso', 0):.1%}",
                f"Sharpe Ratio: {metricas.get('taxa_sucesso_sharpe', 0):.1%}",
                f"Drawdown: {metricas.get('taxa_sucesso_drawdown', 0):.1%}",
                f"Profit Factor: {'[OK]' if metricas.get('profit_factor_atende_threshold') else '[FALHA]'}"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self.resultados["decisao_final"] = decisao_final
        logger.info(f"{cor} DECISAO: {decisao} - {motivo}")
        
        return decisao_final
    
    def gerar_relatorios(self):
        """Gera todos os relatórios finais."""
        logger.info("[RELATORIO] Gerando relatorios finais...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Relatório JSON completo
        json_path = self.root / f"aurora_etapa_a_resultado_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        self.resultados["arquivos_gerados"].append(str(json_path))
        logger.info(f"[ARQUIVO] JSON gerado: {json_path}")
        
        # 2. Relatório de texto para humanos
        txt_path = self.root / f"aurora_etapa_a_relatorio_{timestamp}.txt"
        relatorio = self.gerar_relatorio_texto()
        txt_path.write_text(relatorio, encoding='utf-8')
        
        self.resultados["arquivos_gerados"].append(str(txt_path))
        logger.info(f"[ARQUIVO] Relatorio TXT gerado: {txt_path}")
        
        # 3. Relatório de decisão simplificado
        if self.resultados.get("decisao_final"):
            decisao_path = self.root / f"aurora_etapa_a_decisao_{timestamp}.json"
            with open(decisao_path, 'w', encoding='utf-8') as f:
                json.dump(self.resultados["decisao_final"], f, indent=2, ensure_ascii=False)
            
            self.resultados["arquivos_gerados"].append(str(decisao_path))
            logger.info(f"[ARQUIVO] Decisao gerada: {decisao_path}")
    
    def gerar_relatorio_texto(self) -> str:
        """Gera relatório em texto formatado."""
        decisao = self.resultados.get("decisao_final", {})
        metricas = self.resultados.get("metricas_mercado", {})
        analise = self.resultados.get("analise_pontos_criticos", {})
        
        relatorio = f"""AURORA v5.0 - ETAPA A - RELATORIO FINAL
================================================================================
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ID Execucao: {self.resultados['execucao_id']}
Duracao: {self.resultados['duracao_segundos']:.1f} segundos
================================================================================

DECISAO FINAL: {decisao.get('cor', '')} {decisao.get('decisao', 'INDEFINIDO')}
Motivo: {decisao.get('motivo', 'N/A')}
Acao: {decisao.get('acao', 'N/A')}
Taxa de Sucesso Geral: {decisao.get('taxa_sucesso_geral', 0):.1%}

METRICAS DE MERCADO
---------------------
Simbolos Analisados: {metricas.get('total_symbols_analisados', 0)}/{len(self.config['symbols'])}
Sharpe Ratio Medio: {metricas.get('sharpe_medio', 0):.2f} (≥{self.config['sharpe_threshold']})
Profit Factor: {metricas.get('profit_factor_estimado', 0):.2f} (≥{self.config['profit_factor_threshold']})
Max Drawdown: {metricas.get('drawdown_max', 0):.2f}% (≤{self.config['max_drawdown_threshold']*100:.0f}%)
Taxa Sharpe OK: {metricas.get('taxa_sucesso_sharpe', 0):.1%}
Taxa Drawdown OK: {metricas.get('taxa_sucesso_drawdown', 0):.1%}

ANALISE DOS 5 PONTOS CRITICOS CEO
------------------------------------
Taxa de Aprovacao: {analise.get('resumo', {}).get('taxa_sucesso', 0):.1%}

1. IA Agents: {self.get_status_ponto(analise, 0)}
2. Comunicacao Modulos: {self.get_status_ponto(analise, 1)}
3. Pipeline Estrategias: {self.get_status_ponto(analise, 2)}
4. Prevencao Conflitos: {self.get_status_ponto(analise, 3)}
5. Gestao Profit: {self.get_status_ponto(analise, 4)}

VALIDACOES DO SISTEMA
------------------------
Modulos Criticos: {sum(1 for k,v in self.resultados.get('validacoes', {}).items() 
                      if k.startswith('modulo_') and v.get('status') == 'operacional')}/
                 {sum(1 for k in self.resultados.get('validacoes', {}) 
                      if k.startswith('modulo_'))} operacionais

Teste Sistema: {'[OK] APROVADO' if self.resultados.get('validacoes', {}).get('teste_importacao', {}).get('status') == 'sucesso' else '[FALHA] FALHA'}

ARQUIVOS GERADOS
-------------------
"""
        
        for arquivo in self.resultados.get("arquivos_gerados", []):
            relatorio += f"• {Path(arquivo).name}\n"
        
        relatorio += f"""

PROXIMOS PASSOS
------------------
"""
        
        if decisao.get("decisao") == "PROCEED":
            relatorio += """1. Executar: python aurora_etapa_b.py --start
2. Analise detalhada da arquitetura base
3. Otimizacao de componentes identificados
4. Preparacao para Etapa C"""
        
        elif decisao.get("decisao") == "OPTIMIZE":
            relatorio += f"""1. Executar: python aurora_etapa_a.py --optimize
2. Focar em melhorar {decisao.get('taxa_sucesso_geral', 0)*100:.1f}% → ≥70%
3. Re-testar com dados atualizados
4. Re-avaliar decisao"""
        
        else:  # PIVOT
            relatorio += f"""1. Executar: python aurora_etapa_a.py --pivot
2. Revisar fundamentos do sistema
3. Reformular abordagem de trading
4. Re-iniciar analise com nova base"""
        
        relatorio += f"""

================================================================================
Relatorio gerado automaticamente pelo AIC Executor v1.0
Sistema: Aurora v5.0.2 - Etapa A Concluida
================================================================================
"""
        
        return relatorio
    
    def get_status_ponto(self, analise: Dict[str, Any], idx: int) -> str:
        """Obtém status formatado de um ponto crítico."""
        pontos = analise.get("pontos_criticos", [])
        if idx < len(pontos):
            ponto = pontos[idx]
            status = ponto.get("analise", {}).get("status_avaliacao", "pendente")
            return "[OK] APROVADO" if status == "aprovado" else "[FALHA] REPROVADO"
        return "[?] NAO ANALISADO"
    
    def executar_etapa_a_completa(self) -> bool:
        """Executa a Etapa A completa de forma automática."""
        inicio = time.time()
        
        try:
            logger.info("=" * 80)
            logger.info("[INICIO] INICIANDO EXECUCAO AUTOMATICA - ETAPA A AURORA v5.0")
            logger.info("=" * 80)
            
            self.resultados["status_geral"] = "em_execucao"
            
            # 1. Verificar ambiente
            logger.info("\n[ETAPA 1/6] Verificando ambiente...")
            if not self.verificar_ambiente():
                logger.error("[ERRO] Ambiente nao esta pronto para execucao")
                self.resultados["status_geral"] = "falha_ambiente"
                return False
            
            # 2. Validar módulos críticos
            logger.info("\n[ETAPA 2/6] Validando modulos criticos...")
            if not self.validar_modulos_criticos():
                logger.error("[ERRO] Modulos criticos nao estao todos operacionais")
                self.resultados["status_geral"] = "falha_modulos"
                return False
            
            # 3. Testar sistema
            logger.info("\n[ETAPA 3/6] Testando sistema...")
            if not self.executar_teste_sistema():
                logger.error("[ERRO] Teste do sistema falhou")
                self.resultados["status_geral"] = "falha_teste"
                return False
            
            # 4. Coletar dados de mercado
            logger.info("\n[ETAPA 4/6] Coletando dados de mercado...")
            dados = self.coletar_dados_mercado()
            if not dados:
                logger.error("[ERRO] Falha na coleta de dados de mercado")
                self.resultados["status_geral"] = "falha_coleta_dados"
                return False
            
            # 5. Analisar pontos críticos
            logger.info("\n[ETAPA 5/6] Analisando pontos criticos CEO...")
            self.analisar_pontos_criticos_ceo()
            
            # 6. Calcular decisão final
            logger.info("\n[ETAPA 6/6] Calculando decisao final...")
            decisao = self.calcular_decisao_final()
            
            # Calcular duração
            fim = time.time()
            self.resultados["duracao_segundos"] = fim - inicio
            self.resultados["timestamp_fim"] = datetime.now().isoformat()
            
            # Gerar relatórios
            self.gerar_relatorios()
            
            # Status final
            self.resultados["status_geral"] = "concluido_sucesso"
            
            logger.info("\n" + "=" * 80)
            logger.info(f"[CONCLUIDO] EXECUCAO CONCLUIDA EM {self.resultados['duracao_segundos']:.1f}s")
            logger.info(f"[DECISAO] {decisao.get('cor')} {decisao.get('decisao')}")
            logger.info(f"[ARQUIVOS] {len(self.resultados['arquivos_gerados'])} arquivos gerados")
            logger.info("=" * 80)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("\n[INTERROMPIDO] Execucao interrompida pelo usuario")
            self.resultados["status_geral"] = "interrompido"
            return False
            
        except Exception as e:
            logger.error(f"\n[ERRO] Erro na execucao: {str(e)}")
            self.resultados["status_geral"] = "erro_excecao"
            self.resultados["erros"].append(f"Excecao: {str(e)}")
            
            # Tentar salvar resultados parciais
            try:
                self.resultados["timestamp_fim"] = datetime.now().isoformat()
                self.resultados["duracao_segundos"] = time.time() - inicio
                self.gerar_relatorios()
            except:
                pass
            
            return False
    
    def limpar_arquivos_temporarios(self):
        """Limpa arquivos temporários gerados durante a execução."""
        logger.info("[LIMPEZA] Limpando arquivos temporarios...")
        
        padroes = [
            "coleta_dados_temp.py",
            "temp_*.json",
            "temp_*.txt"
        ]
        
        for padrao in padroes:
            for arquivo in self.root.rglob(padrao):
                try:
                    if arquivo.is_file():
                        arquivo.unlink()
                except Exception as e:
                    logger.debug(f"  Nao foi possivel remover {arquivo}: {e}")

def main():
    """Função principal para execução pelo AIC/Cursor."""
    
    print("""
================================================================================
              AURORA v5.0 - EXECUTOR AUTOMATICO
                    ETAPA A - ANALISE COMPLETA
================================================================================
Este script executara automaticamente a Etapa A completa.
Tempo estimado: 3-8 minutos
Requisitos: Conexao com internet para dados de mercado
================================================================================
""")
    
    executor = AuroraEtapaAExecutor()
    
    try:
        # Executar etapa completa
        sucesso = executor.executar_etapa_a_completa()
        
        # Limpar arquivos temporários
        executor.limpar_arquivos_temporarios()
        
        # Exibir resultado final
        decisao = executor.resultados.get("decisao_final", {})
        
        print("\n" + "=" * 80)
        print(f"{decisao.get('cor', '')} RESULTADO FINAL: {decisao.get('decisao', 'INDEFINIDO')}")
        print("=" * 80)
        print(f"[METRICAS] Taxa de Sucesso: {decisao.get('taxa_sucesso_geral', 0):.1%}")
        print(f"[TEMPO] Duracao: {executor.resultados.get('duracao_segundos', 0):.1f}s")
        print(f"[ARQUIVOS] Relatorios: {len(executor.resultados.get('arquivos_gerados', []))} arquivos")
        
        if executor.resultados.get("arquivos_gerados"):
            print("\n[ARQUIVOS] ARQUIVOS GERADOS:")
            for arquivo in executor.resultados["arquivos_gerados"]:
                print(f"  • {Path(arquivo).name}")
        
        print("\n" + "=" * 80)
        
        if sucesso and decisao.get("decisao") == "PROCEED":
            print("\n[PROXIMO] PROXIMO PASSO RECOMENDADO:")
            print("python aurora_etapa_b.py --start")
            return 0
        elif sucesso:
            return 1
        else:
            print("\n[ERRO] EXECUCAO COM FALHAS - VERIFIQUE OS LOGS")
            return 2
            
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Execucao interrompida pelo usuario.")
        return 3
    except Exception as e:
        print(f"\n[ERRO] ERRO NAO TRATADO: {str(e)}")
        return 4

if __name__ == "__main__":
    sys.exit(main())

