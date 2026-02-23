#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESTE COMPLETO DO SISTEMA OPENMYMIND - Avaliação de Integração, Funcionalidade e Performance

Objetivo: Validar todas as etapas do pipeline, incluindo coleta, validação, backtest e sistema neural.

Versão: 1.0
Data: 17 de Novembro de 2025
Status: Teste de Integração
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar diretório ao path para importação
sys.path.insert(0, str(Path(__file__).parent))

# Importar o módulo principal
try:
    import openmymind_pipeline_007 as om
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f"Erro na importação do módulo principal: {e}")
    print("Certifique-se de que todas as dependências estão instaladas.")
    sys.exit(1)

# Função de relatório consolidado
def relatorio_completo(status, detalhes):
    """Gera relatório completo do teste em JSON"""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "detalhes": detalhes,
        "versao": "1.0",
        "teste": "OpenMyMind Project 007 - Teste Completo"
    }
    
    # Criar diretório de output se não existir
    output_dir = Path(om.DATA_DIR)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    report_file = output_dir / f"relatorio_teste_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, default=str)
    
    print(f"\n{'='*80}")
    print(f"Relatório completo salvo em: {report_file}")
    print(f"{'='*80}\n")
    
    return report_file

# Execução sequencial das etapas de teste
def executar_teste():
    """Executa teste completo do sistema OpenMyMind"""
    print("="*80)
    print("=== INÍCIO DO TESTE COMPLETO - OPENMYMIND PROJECT 007 ===")
    print("="*80)
    
    sucesso = True
    detalhes = {}
    erros = []
    
    # 1. Testar inicialização do banco de dados
    try:
        print("\n[1/7] Testando inicialização do banco de dados...")
        om.init_db()
        detalhes['db'] = {"status": "OK", "arquivo": str(om.DB_FILE)}
        print("✓ Banco de dados inicializado com sucesso")
    except Exception as e:
        print(f"✗ Falha na inicialização do banco: {e}")
        sucesso = False
        detalhes['db'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"DB Init: {e}")
    
    # 2. Testar coleta de dados
    df_tweets = pd.DataFrame()
    ob = None
    onchain_df = pd.DataFrame()
    wa_df = pd.DataFrame()
    
    # 2.1. Tweets
    try:
        print("\n[2/7] Testando coleta de Tweets...")
        df_tweets = om.scrape_tweets('("whale" OR "large transfer")', max_tweets=10)
        detalhes['tweets'] = {
            "status": "OK",
            "registros": len(df_tweets),
            "coletados": len(df_tweets) > 0
        }
        print(f"✓ Tweets coletados: {len(df_tweets)} registros")
    except Exception as e:
        print(f"✗ Falha na coleta de tweets: {e}")
        sucesso = False
        detalhes['tweets'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Tweets: {e}")
    
    # 2.2. Orderbook
    try:
        print("\n[3/7] Testando coleta de Orderbook...")
        ob = om.fetch_orderbook_snapshot()
        detalhes['orderbook'] = {
            "status": "OK",
            "coletado": ob is not None,
            "dados": ob if ob else None
        }
        if ob:
            print(f"✓ Orderbook coletado: Exchange={ob.get('exchange')}, Symbol={ob.get('symbol')}")
        else:
            print("⚠ Orderbook não disponível (pode ser devido à falta de conexão ou API)")
    except Exception as e:
        print(f"✗ Falha na coleta de orderbook: {e}")
        sucesso = False
        detalhes['orderbook'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Orderbook: {e}")
    
    # 2.3. On-Chain
    try:
        print("\n[4/7] Testando coleta On-chain...")
        onchain_df = om.get_etherscan_txs()
        detalhes['onchain'] = {
            "status": "OK",
            "registros": len(onchain_df),
            "coletados": len(onchain_df) > 0
        }
        print(f"✓ Transações on-chain: {len(onchain_df)} registros")
    except Exception as e:
        print(f"✗ Falha na coleta on-chain: {e}")
        sucesso = False
        detalhes['onchain'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"On-chain: {e}")
    
    # 2.4. Whale Alert
    try:
        print("\n[5/7] Testando coleta Whale Alert...")
        wa_df = om.fetch_whale_alerts()
        detalhes['whale_alert'] = {
            "status": "OK",
            "registros": len(wa_df),
            "coletados": len(wa_df) > 0
        }
        print(f"✓ Whale Alert: {len(wa_df)} registros")
    except Exception as e:
        print(f"✗ Falha na coleta Whale Alert: {e}")
        sucesso = False
        detalhes['whale_alert'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Whale Alert: {e}")
    
    # 3. Validação cruzada
    try:
        print("\n[6/7] Realizando validação cruzada de eventos...")
        validated = om.cross_validate_events(onchain_df, wa_df, df_tweets, [ob] if ob else [])
        detalhes['validacao'] = {
            "status": "OK",
            "eventos_validados": len(validated),
            "exemplos": validated[:3] if validated else []
        }
        print(f"✓ Eventos validados: {len(validated)}")
        if validated:
            for i, v in enumerate(validated[:3], 1):
                print(f"  Exemplo {i}: {v['ts']} | Fontes: {v['sources']} | Score: {v['score']:.2f}")
    except Exception as e:
        print(f"✗ Falha na validação cruzada: {e}")
        sucesso = False
        detalhes['validacao'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Validação: {e}")
        validated = []
    
    # 4. Persistir sinais validados
    try:
        print("\n[7/7] Persistindo sinais validados...")
        persistidos = 0
        for v in validated:
            try:
                om.persist_signal_to_db("teste_pipeline", v["ts"], v, v["score"])
                persistidos += 1
            except Exception as e:
                print(f"  ⚠ Erro ao persistir sinal {v['ts']}: {e}")
        
        detalhes['persistencia'] = {
            "status": "OK",
            "sinais_persistidos": persistidos,
            "total_validados": len(validated)
        }
        print(f"✓ Sinais persistidos: {persistidos}/{len(validated)}")
    except Exception as e:
        print(f"✗ Falha na persistência de sinais: {e}")
        sucesso = False
        detalhes['persistencia'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Persistência: {e}")
    
    # 5. Backtest
    try:
        print("\n[8/7] Executando backtest com sinais validados...")
        if validated:
            data_timestamps = [v["ts"] for v in validated]
            _, stats = om.simple_backtest_on_signals(data_timestamps)
            detalhes['backtest'] = {
                "status": "OK",
                "metricas": stats,
                "sinais_utilizados": len(data_timestamps)
            }
            print("✓ Backtest concluído")
            print(f"  Métricas: {stats}")
        else:
            print("⚠ Nenhum evento validado para backtest")
            detalhes['backtest'] = {
                "status": "SKIP",
                "razao": "Nenhum evento validado"
            }
    except Exception as e:
        print(f"✗ Falha no backtest: {e}")
        sucesso = False
        detalhes['backtest'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Backtest: {e}")
    
    # 6. Testar sistema neural de fusão
    try:
        print("\n[9/7] Testando execução do sistema neural de fusão...")
        config = {
            'orderbook_dim': 64,
            'twitter_dim': 128,
            'onchain_dim': 64,
            'learning_rate': 1e-4
        }
        
        sistema_neural = om.EnhancedOpenMyMind(config)
        
        # Dados simulados de entrada
        dados_simulados = {
            'orderbook_features': np.random.randn(100, config['orderbook_dim']),
            'twitter_embeddings': np.random.randn(100, config['twitter_dim']),
            'onchain_metrics': np.random.randn(100, config['onchain_dim']),
            'whale_features': np.random.randn(100, 10),
            'price_targets': np.random.randn(100, 1)
        }
        
        resultado = sistema_neural.process_cycle(dados_simulados)
        
        detalhes['neural'] = {
            "status": "OK",
            "predictions_shape": str(resultado.get('predictions', np.array([])).shape),
            "risk_params": {k: str(v.shape) if hasattr(v, 'shape') else str(v) 
                           for k, v in resultado.get('risk_params', {}).items()},
            "batch_size": resultado.get('batch_size', 0)
        }
        
        print("✓ Sistema neural executado com sucesso")
        print(f"  Predictions shape: {resultado.get('predictions', np.array([])).shape}")
        print(f"  Batch size: {resultado.get('batch_size', 0)}")
        
        if 'error' in resultado:
            print(f"  ⚠ Aviso: {resultado['error']}")
        
    except Exception as e:
        print(f"✗ Erro no sistema neural: {e}")
        import traceback
        traceback.print_exc()
        sucesso = False
        detalhes['neural'] = {"status": "ERRO", "erro": str(e)}
        erros.append(f"Neural: {e}")
    
    # Resumo final
    detalhes['resumo'] = {
        "total_etapas": 9,
        "sucesso": sucesso,
        "erros_encontrados": len(erros),
        "erros": erros
    }
    
    # Relatório final
    status_final = "SUCESSO" if sucesso else "FALHA_PARCIAL"
    if len(erros) > 0 and sucesso:
        status_final = "SUCESSO_COM_AVISOS"
    
    relatorio_completo(status_final, detalhes)
    
    print("="*80)
    print(f"=== FIM DO TESTE COMPLETO - Status: {status_final} ===")
    print("="*80)
    
    if erros:
        print("\n⚠ Erros encontrados:")
        for i, erro in enumerate(erros, 1):
            print(f"  {i}. {erro}")
    
    return sucesso, detalhes

if __name__ == "__main__":
    try:
        sucesso, detalhes = executar_teste()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Teste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Erro crítico no teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

