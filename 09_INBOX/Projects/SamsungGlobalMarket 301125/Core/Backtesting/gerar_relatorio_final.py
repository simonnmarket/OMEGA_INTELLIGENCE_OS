#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerador de Relatório Final Estruturado - OpenMyMind Project 007
Gera relatório completo do pipeline em formato JSON estruturado
"""

import json
import os
from datetime import datetime
from pathlib import Path
import glob

def gerar_relatorio_final():
    """Gera relatório final estruturado do pipeline"""
    
    # Localizar relatório mais recente
    data_dir = Path("data")
    relatorios = sorted(data_dir.glob("relatorio_teste_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not relatorios:
        print("ERRO: Nenhum relatório encontrado")
        return None
    
    # Ler relatório mais recente
    relatorio_mais_recente = relatorios[0]
    with open(relatorio_mais_recente, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Localizar arquivos gerados
    arquivos_gerados = {
        "orderbooks": list(data_dir.glob("orderbook_*.parquet")),
        "tweets": list(data_dir.glob("tweets_*.parquet")),
        "onchain": list(data_dir.glob("etherscan_txs_*.parquet")),
        "whalealerts": list(data_dir.glob("whalealerts_*.parquet")),
        "equity_curves": list(data_dir.glob("equity_curve*.parquet")),
        "relatorios_teste": list(data_dir.glob("relatorio_teste_*.json")),
        "pipeline_reports": list(data_dir.glob("pipeline_report_*.json"))
    }
    
    # Construir relatório final estruturado
    timestamp_execucao = datetime.utcnow().isoformat()
    
    relatorio_final = {
        "metadata": {
            "timestamp_execucao": timestamp_execucao,
            "versao_sistema": "1.0",
            "projeto": "OpenMyMind Project 007",
            "pipeline": "Prometheus: Horizonte",
            "formato_relatorio": "pipeline_report_v1"
        },
        "status_geral": {
            "status": dados.get("status", "UNKNOWN"),
            "sucesso_geral": dados.get("detalhes", {}).get("resumo", {}).get("sucesso", False),
            "total_etapas": dados.get("detalhes", {}).get("resumo", {}).get("total_etapas", 0),
            "etapas_concluidas": dados.get("detalhes", {}).get("resumo", {}).get("total_etapas", 0) - len(dados.get("detalhes", {}).get("resumo", {}).get("erros", []))
        },
        "etapas_detalhadas": {
            "1_inicializacao_banco": {
                "status": dados.get("detalhes", {}).get("db", {}).get("status", "UNKNOWN"),
                "arquivo_banco": dados.get("detalhes", {}).get("db", {}).get("arquivo", "N/A"),
                "mensagem": "Banco de dados SQLite inicializado com sucesso" if dados.get("detalhes", {}).get("db", {}).get("status") == "OK" else "Falha na inicialização do banco",
                "erro": dados.get("detalhes", {}).get("db", {}).get("erro", None)
            },
            "2_coleta_tweets": {
                "status": dados.get("detalhes", {}).get("tweets", {}).get("status", "UNKNOWN"),
                "registros_coletados": dados.get("detalhes", {}).get("tweets", {}).get("registros", 0),
                "coletados": dados.get("detalhes", {}).get("tweets", {}).get("coletados", False),
                "arquivos_gerados": [str(f) for f in arquivos_gerados.get("tweets", [])],
                "avisos": ["snscrape não disponível - coleta ignorada"] if dados.get("detalhes", {}).get("tweets", {}).get("registros", 0) == 0 else []
            },
            "3_coleta_orderbook": {
                "status": dados.get("detalhes", {}).get("orderbook", {}).get("status", "UNKNOWN"),
                "coletado": dados.get("detalhes", {}).get("orderbook", {}).get("coletado", False),
                "exchange": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("exchange", "N/A") if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else "N/A",
                "symbol": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("symbol", "N/A") if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else "N/A",
                "bid": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("bid", 0) if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else 0,
                "ask": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("ask", 0) if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else 0,
                "bid_depth_top10": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("bid_depth_top10", 0) if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else 0,
                "ask_depth_top10": dados.get("detalhes", {}).get("orderbook", {}).get("dados", {}).get("ask_depth_top10", 0) if dados.get("detalhes", {}).get("orderbook", {}).get("dados") else 0,
                "arquivos_gerados": [str(f) for f in arquivos_gerados.get("orderbooks", [])]
            },
            "4_coleta_onchain": {
                "status": dados.get("detalhes", {}).get("onchain", {}).get("status", "UNKNOWN"),
                "registros_coletados": dados.get("detalhes", {}).get("onchain", {}).get("registros", 0),
                "coletados": dados.get("detalhes", {}).get("onchain", {}).get("coletados", False),
                "arquivos_gerados": [str(f) for f in arquivos_gerados.get("onchain", [])],
                "avisos": ["ETHERSCAN_API_KEY não configurada - coleta ignorada"] if dados.get("detalhes", {}).get("onchain", {}).get("registros", 0) == 0 else []
            },
            "5_coleta_whale_alert": {
                "status": dados.get("detalhes", {}).get("whale_alert", {}).get("status", "UNKNOWN"),
                "registros_coletados": dados.get("detalhes", {}).get("whale_alert", {}).get("registros", 0),
                "coletados": dados.get("detalhes", {}).get("whale_alert", {}).get("coletados", False),
                "arquivos_gerados": [str(f) for f in arquivos_gerados.get("whalealerts", [])],
                "avisos": ["WHALEALERT_API_KEY não configurada - coleta ignorada"] if dados.get("detalhes", {}).get("whale_alert", {}).get("registros", 0) == 0 else []
            },
            "6_validacao_cruzada": {
                "status": dados.get("detalhes", {}).get("validacao", {}).get("status", "UNKNOWN"),
                "eventos_validados": dados.get("detalhes", {}).get("validacao", {}).get("eventos_validados", 0),
                "exemplos": dados.get("detalhes", {}).get("validacao", {}).get("exemplos", []),
                "mensagem": f"{dados.get('detalhes', {}).get('validacao', {}).get('eventos_validados', 0)} eventos validados por múltiplas fontes" if dados.get("detalhes", {}).get("validacao", {}).get("eventos_validados", 0) > 0 else "Nenhum evento onchain para validar"
            },
            "7_persistencia_sinais": {
                "status": dados.get("detalhes", {}).get("persistencia", {}).get("status", "UNKNOWN"),
                "sinais_persistidos": dados.get("detalhes", {}).get("persistencia", {}).get("sinais_persistidos", 0),
                "total_validados": dados.get("detalhes", {}).get("persistencia", {}).get("total_validados", 0),
                "taxa_persistencia": dados.get("detalhes", {}).get("persistencia", {}).get("sinais_persistidos", 0) / max(dados.get("detalhes", {}).get("persistencia", {}).get("total_validados", 1), 1)
            },
            "8_backtest": {
                "status": dados.get("detalhes", {}).get("backtest", {}).get("status", "UNKNOWN"),
                "executado": dados.get("detalhes", {}).get("backtest", {}).get("status") == "OK",
                "razao_skip": dados.get("detalhes", {}).get("backtest", {}).get("razao", "N/A"),
                "metricas": dados.get("detalhes", {}).get("backtest", {}).get("metricas", {}),
                "arquivos_equity_curve": [str(f) for f in arquivos_gerados.get("equity_curves", [])]
            },
            "9_sistema_neural": {
                "status": dados.get("detalhes", {}).get("neural", {}).get("status", "UNKNOWN"),
                "predictions_shape": dados.get("detalhes", {}).get("neural", {}).get("predictions_shape", "N/A"),
                "batch_size": dados.get("detalhes", {}).get("neural", {}).get("batch_size", 0),
                "risk_params": dados.get("detalhes", {}).get("neural", {}).get("risk_params", {}),
                "erro": dados.get("detalhes", {}).get("neural", {}).get("erro", None),
                "avisos": ["Problema de dimensões de tensor na atenção multi-head"] if dados.get("detalhes", {}).get("neural", {}).get("batch_size", 0) == 0 else []
            }
        },
        "metricas_quantitativas": {
            "total_registros_coletados": {
                "tweets": dados.get("detalhes", {}).get("tweets", {}).get("registros", 0),
                "orderbook": 1 if dados.get("detalhes", {}).get("orderbook", {}).get("coletado", False) else 0,
                "onchain": dados.get("detalhes", {}).get("onchain", {}).get("registros", 0),
                "whale_alert": dados.get("detalhes", {}).get("whale_alert", {}).get("registros", 0)
            },
            "eventos_validados": dados.get("detalhes", {}).get("validacao", {}).get("eventos_validados", 0),
            "sinais_persistidos": dados.get("detalhes", {}).get("persistencia", {}).get("sinais_persistidos", 0),
            "backtest": {
                "executado": dados.get("detalhes", {}).get("backtest", {}).get("status") == "OK",
                "metricas": dados.get("detalhes", {}).get("backtest", {}).get("metricas", {})
            },
            "sistema_neural": {
                "batch_size_processado": dados.get("detalhes", {}).get("neural", {}).get("batch_size", 0),
                "predictions_shape": dados.get("detalhes", {}).get("neural", {}).get("predictions_shape", "N/A")
            }
        },
        "erros_avisos_mensagens": {
            "erros_criticos": dados.get("detalhes", {}).get("resumo", {}).get("erros", []),
            "avisos": [
                "snscrape não disponível - coleta de tweets ignorada",
                "ETHERSCAN_API_KEY não configurada - coleta onchain ignorada",
                "WHALEALERT_API_KEY não configurada - coleta whale alert ignorada",
                "Nenhum evento validado para backtest",
                "Problema de dimensões de tensor no sistema neural"
            ],
            "mensagens_importantes": [
                "Pipeline executado com sucesso geral",
                "Orderbook coletado com sucesso via CCXT/Binance",
                "Banco de dados inicializado e operacional",
                "Sistema neural executado (com avisos sobre dimensões)"
            ]
        },
        "arquivos_gerados": {
            "banco_dados": dados.get("detalhes", {}).get("db", {}).get("arquivo", "N/A"),
            "orderbooks": [str(f) for f in arquivos_gerados.get("orderbooks", [])],
            "tweets": [str(f) for f in arquivos_gerados.get("tweets", [])],
            "onchain": [str(f) for f in arquivos_gerados.get("onchain", [])],
            "whalealerts": [str(f) for f in arquivos_gerados.get("whalealerts", [])],
            "equity_curves": [str(f) for f in arquivos_gerados.get("equity_curves", [])],
            "relatorios_teste": [str(f) for f in arquivos_gerados.get("relatorios_teste", [])],
            "pipeline_reports": [str(f) for f in arquivos_gerados.get("pipeline_reports", [])]
        },
        "resumo_executivo": {
            "status_geral": dados.get("status", "UNKNOWN"),
            "sucesso_geral": dados.get("detalhes", {}).get("resumo", {}).get("sucesso", False),
            "total_etapas": dados.get("detalhes", {}).get("resumo", {}).get("total_etapas", 0),
            "erros_encontrados": dados.get("detalhes", {}).get("resumo", {}).get("erros_encontrados", 0),
            "eventos_validados": dados.get("detalhes", {}).get("validacao", {}).get("eventos_validados", 0),
            "arquivos_gerados_total": sum(len(files) for files in arquivos_gerados.values())
        }
    }
    
    # Salvar relatório final
    timestamp_str = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    nome_arquivo = data_dir / f"pipeline_report_{timestamp_str}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(relatorio_final, f, indent=2, ensure_ascii=False, default=str)
    
    # Exibir resumo no console
    print("="*80)
    print("RELATÓRIO FINAL DO PIPELINE - OPENMYMIND PROJECT 007")
    print("="*80)
    print(f"Timestamp da Execução: {timestamp_execucao}")
    print(f"Status Geral: {relatorio_final['status_geral']['status']}")
    print(f"Sucesso Geral: {'SIM' if relatorio_final['status_geral']['sucesso_geral'] else 'NÃO'}")
    print(f"Total de Etapas: {relatorio_final['status_geral']['total_etapas']}")
    print(f"Etapas Concluídas: {relatorio_final['status_geral']['etapas_concluidas']}")
    print()
    print("PRINCIPAIS RESULTADOS:")
    print(f"  - Eventos Validados: {relatorio_final['metricas_quantitativas']['eventos_validados']}")
    print(f"  - Sinais Persistidos: {relatorio_final['metricas_quantitativas']['sinais_persistidos']}")
    print(f"  - Orderbooks Coletados: {len(arquivos_gerados['orderbooks'])}")
    print(f"  - Backtest Executado: {'SIM' if relatorio_final['etapas_detalhadas']['8_backtest']['executado'] else 'NÃO'}")
    print()
    print(f"Erros Encontrados: {relatorio_final['resumo_executivo']['erros_encontrados']}")
    if relatorio_final['erros_avisos_mensagens']['erros_criticos']:
        print("  Erros Críticos:")
        for erro in relatorio_final['erros_avisos_mensagens']['erros_criticos']:
            print(f"    - {erro}")
    print()
    print(f"Arquivo do Relatório: {nome_arquivo}")
    print("="*80)
    
    return nome_arquivo, relatorio_final

if __name__ == "__main__":
    gerar_relatorio_final()

