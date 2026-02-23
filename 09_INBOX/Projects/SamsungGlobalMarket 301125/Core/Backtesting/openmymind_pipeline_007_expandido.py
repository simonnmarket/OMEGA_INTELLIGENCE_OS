#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenMyMind Project 007 - Pipeline Expandido com Fontes Alternativas de Sentimento

Inclui coleta Reddit, Telegram, Discord + adaptação da validação cruzada.
Pronto para execução imediata na conta demo.

Versão: 2.0 (Expandida)
Data: 20 de Novembro de 2025
Status: Integração com Sistema Principal
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
import asyncio
import aiohttp

import pandas as pd
import numpy as np

# Importar módulo principal para compatibilidade
try:
    import openmymind_pipeline_007 as om_main
except ImportError:
    logging.warning("Módulo principal não encontrado. Usando implementação standalone.")
    om_main = None

# Configure logging para clareza nas execuções
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')

# Configurações gerais
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True, parents=True)

# Configurações de coleta
REDDIT_SUBREDDITS = os.getenv("REDDIT_SUBREDDITS", "CryptoCurrency,Bitcoin,ethereum").split(",")
REDDIT_LIMIT = int(os.getenv("REDDIT_LIMIT", "100"))
TELEGRAM_DISCORD_TIMEOUT = int(os.getenv("TELEGRAM_DISCORD_TIMEOUT", "10"))

# --------------------------------------------
# COLETORES ALTERNATIVOS
# --------------------------------------------

# 1. Coletor Reddit básico para subreddits financeiros
def coletar_reddit(subreddits=None, limit=100):
    """
    Coleta posts do Reddit de subreddits financeiros/crypto
    
    Args:
        subreddits: Lista de subreddits para coletar (default: REDDIT_SUBREDDITS)
        limit: Número máximo de posts por subreddit (default: 100)
    
    Returns:
        DataFrame com posts coletados
    """
    if subreddits is None:
        subreddits = REDDIT_SUBREDDITS
    
    logging.info("Iniciando coleta Reddit para subreddits: %s", subreddits)
    headers = {'User-Agent': 'OpenMyMindBot/1.0 (Educational Purpose)'}
    posts = []
    base_url = "https://www.reddit.com/r/{}/new.json"
    
    for sub in subreddits:
        sub = sub.strip()
        url = base_url.format(sub)
        try:
            r = requests.get(url, headers=headers, params={'limit': limit}, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            for post in data.get('data', {}).get('children', []):
                p = post.get('data', {})
                try:
                    posts.append({
                        'subreddit': sub,
                        'id': p.get('id', ''),
                        'title': p.get('title', ''),
                        'created_utc': datetime.utcfromtimestamp(p.get('created_utc', 0)),
                        'score': p.get('score', 0),
                        'num_comments': p.get('num_comments', 0),
                        'url': p.get('url', ''),
                        'selftext': p.get('selftext', ''),
                        'author': p.get('author', ''),
                        'upvote_ratio': p.get('upvote_ratio', 0.0)
                    })
                except Exception as e:
                    logging.warning("Erro ao processar post do Reddit: %s", str(e))
                    continue
            
            logging.info("Coleta Reddit %s finalizada, %d posts obtidos", sub, len([p for p in posts if p.get('subreddit') == sub]))
        except requests.exceptions.RequestException as e:
            logging.warning("Erro ao coletar Reddit %s: %s", sub, str(e))
        except Exception as e:
            logging.error("Erro inesperado ao coletar Reddit %s: %s", sub, str(e))
    
    df = pd.DataFrame(posts)
    
    if not df.empty:
        filename = DATA_DIR / f"reddit_posts_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.parquet"
        df.to_parquet(filename, index=False)
        logging.info("Dados Reddit salvos em %s (%d registros)", filename, len(df))
    else:
        logging.info("Nenhum post do Reddit coletado")
    
    return df


# 2. Coletor Telegram/Discord placeholder (assíncrono básico para scraping de canais públicos)
async def coletar_telegram_discord(channels=None):
    """
    Placeholder para coleta de Telegram/Discord
    
    Nota: Esta função deve ser adaptada para scraping real via frameworks externos
    ou APIs dedicadas (ex: Telegram Bot API, Discord API)
    
    Args:
        channels: Lista de URLs de canais (opcional)
    
    Returns:
        Lista de mensagens coletadas
    """
    if channels is None:
        # Exemplos de canais públicos (adaptar para canais reais)
        channels = [
            'https://t.me/crypto_news',
            'https://discord.com/channels/123456789/987654321'
        ]
    
    logging.info("Placeholder coleta Telegram/Discord iniciada para canais: %s", channels)
    collected = []
    
    # Exemplo simplificado - simula espera e coleta dummy
    await asyncio.sleep(2)
    
    for ch in channels:
        try:
            # Placeholder: Aqui deve ser implementada a coleta real
            collected.append({
                'channel': ch,
                'timestamp': datetime.utcnow(),
                'message': f'Placeholder message from {ch}',
                'source': 'telegram' if 't.me' in ch else 'discord'
            })
        except Exception as e:
            logging.warning("Erro ao coletar canal %s: %s", ch, str(e))
            continue
    
    logging.info("Placeholder Telegram/Discord coleta finalizada (%d mensagens)", len(collected))
    
    # Salvar JSON
    if collected:
        filename = DATA_DIR / f"telegram_discord_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(collected, f, indent=2, default=str)
        logging.info("Dados Telegram/Discord salvos em %s", filename)
    
    return collected


def run_async_collect_telegram_discord(channels=None):
    """
    Wrapper síncrono para coleta assíncrona de Telegram/Discord
    
    Args:
        channels: Lista de canais (opcional)
    
    Returns:
        Lista de mensagens coletadas
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coletar_telegram_discord(channels))


# --------------------------------------------
# ADAPTAÇÃO DA VALIDAÇÃO CRUZADA PARA NOVAS FONTES
# --------------------------------------------

def cross_validate_extended(onchain_df=None, whale_df=None, tweets_df=None, 
                           orderbook_list=None, reddit_df=None, tg_dc_data=None):
    """
    Validação cruzada com inclusão de dados Reddit e Telegram/Discord.
    O objetivo é validar eventos com ao menos duas fontes diferentes.
    
    Args:
        onchain_df: DataFrame com transações on-chain
        whale_df: DataFrame com whale alerts
        tweets_df: DataFrame com tweets
        orderbook_list: Lista de snapshots de orderbook
        reddit_df: DataFrame com posts do Reddit
        tg_dc_data: Lista de mensagens de Telegram/Discord
    
    Returns:
        Lista de eventos validados
    """
    validated = []
    time_window_sec = int(os.getenv("ONCHAIN_TIME_WINDOW_SEC", "3600"))
    
    # Converte mensagens Reddit em timestamp para validação
    reddit_times = []
    if reddit_df is not None and not reddit_df.empty and 'created_utc' in reddit_df.columns:
        try:
            reddit_times = pd.to_datetime(reddit_df['created_utc']).tolist()
        except Exception as e:
            logging.warning("Erro ao processar timestamps do Reddit: %s", str(e))
    
    # Converte mensagens Telegram/Discord em timestamp
    tg_dc_times = []
    if tg_dc_data is not None:
        for entry in tg_dc_data:
            ts = entry.get('timestamp')
            if ts:
                try:
                    if isinstance(ts, str):
                        tg_dc_times.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                    elif isinstance(ts, datetime):
                        tg_dc_times.append(ts)
                except Exception as e:
                    logging.warning("Erro ao processar timestamp Telegram/Discord: %s", str(e))
    
    # Base: onchain_df consideramos a variável base para detectar eventos importantes
    if onchain_df is None or onchain_df.empty:
        logging.info("Nenhum dado onchain para validação cruzada.")
        return validated
    
    # Ajusta dados temporais e janelas
    for idx, row in onchain_df.iterrows():
        try:
            oc_time = row.get('timeStamp') or row.get('timestamp')
            if not oc_time:
                continue
            
            # Converter para datetime
            if isinstance(oc_time, (int, float)):
                oc_time = datetime.utcfromtimestamp(oc_time)
            elif isinstance(oc_time, str):
                try:
                    oc_time = datetime.fromisoformat(oc_time.replace('Z', '+00:00'))
                except:
                    oc_time = pd.to_datetime(oc_time)
            elif not isinstance(oc_time, datetime):
                oc_time = pd.to_datetime(oc_time)
        except Exception as e:
            logging.warning("Erro ao processar timestamp on-chain: %s", str(e))
            continue
        
        sources = set(['onchain'])
        score = 0.5  # base
        
        def check_time_close(target_times, window_sec=time_window_sec):
            """Verifica se há timestamps próximos dentro da janela de tempo"""
            for t in target_times:
                try:
                    if isinstance(t, str):
                        t = datetime.fromisoformat(t.replace('Z', '+00:00'))
                    elif isinstance(t, (int, float)):
                        t = datetime.utcfromtimestamp(t)
                    if abs((oc_time - t).total_seconds()) <= window_sec:
                        return True
                except Exception as e:
                    continue
            return False
        
        # Checa Whale alerts
        if whale_df is not None and not whale_df.empty:
            try:
                if 'timestamp' in whale_df.columns:
                    whale_times = pd.to_datetime(whale_df['timestamp']).tolist()
                else:
                    whale_times = []
                if check_time_close(whale_times):
                    sources.add('whale_alert')
                    score += 0.5
            except Exception as e:
                logging.warning("Erro ao validar whale alerts: %s", str(e))
        
        # Tweets (se disponíveis)
        if tweets_df is not None and not tweets_df.empty:
            try:
                if 'date' in tweets_df.columns:
                    tweet_times = pd.to_datetime(tweets_df['date']).tolist()
                else:
                    tweet_times = []
                if check_time_close(tweet_times):
                    sources.add('twitter')
                    score += 0.3
            except Exception as e:
                logging.warning("Erro ao validar tweets: %s", str(e))
        
        # Orderbook - considerar snapshots próximos
        if orderbook_list:
            try:
                for ob in orderbook_list:
                    obs_time = ob.get('ts')
                    if obs_time:
                        if isinstance(obs_time, str):
                            obs_time = datetime.fromisoformat(obs_time.replace('Z', '+00:00'))
                        if abs((obs_time - oc_time).total_seconds()) <= time_window_sec:
                            sources.add('orderbook')
                            score += 0.3
                            break
            except Exception as e:
                logging.warning("Erro ao validar orderbook: %s", str(e))
        
        # Reddit
        if reddit_times:
            try:
                if check_time_close(reddit_times):
                    sources.add('reddit')
                    score += 0.4
            except Exception as e:
                logging.warning("Erro ao validar Reddit: %s", str(e))
        
        # Telegram/Discord
        if tg_dc_times:
            try:
                if check_time_close(tg_dc_times):
                    sources.add('telegram_discord')
                    score += 0.4
            except Exception as e:
                logging.warning("Erro ao validar Telegram/Discord: %s", str(e))
        
        # Valida se pelo menos 2 fontes diferentes para considerar evento validado
        if len(sources) >= 2:
            validated.append({
                'timestamp': oc_time.isoformat(),
                'sources': list(sources),
                'score': float(score),
                'onchain_data': row.to_dict() if hasattr(row, 'to_dict') else dict(row)
            })
    
    logging.info("Total eventos validados com fontes estendidas: %d", len(validated))
    return validated


# --------------------------------------------
# EXECUÇÃO CONSOLIDADA SIMPLIFICADA
# --------------------------------------------

def executar_pipeline_expandido():
    """
    Executa pipeline expandido completo com novas fontes (Reddit, Telegram, Discord)
    
    Returns:
        dict com resultados da execução
    """
    logging.info("="*80)
    logging.info("Executando pipeline expandido completo com novas fontes")
    logging.info("="*80)
    
    resultados = {
        'timestamp_inicio': datetime.utcnow().isoformat(),
        'coleta_reddit': {},
        'coleta_telegram_discord': {},
        'validacao_cruzada': {},
        'status': 'em_execucao'
    }
    
    # Carregar dados tradicionais (se módulo principal disponível)
    onchain_df = pd.DataFrame()
    whale_df = pd.DataFrame()
    tweets_df = pd.DataFrame()
    orderbook_list = []
    
    if om_main:
        try:
            logging.info("Coletando dados tradicionais via módulo principal...")
            # Tentar coletar orderbook
            try:
                orderbook_snap = om_main.fetch_orderbook_snapshot()
                if orderbook_snap:
                    orderbook_list = [orderbook_snap]
            except Exception as e:
                logging.warning("Erro ao coletar orderbook: %s", str(e))
            
            # Tentar coletar on-chain (se API key configurada)
            try:
                if os.getenv("ETHERSCAN_API_KEY"):
                    onchain_df = om_main.get_etherscan_txs()
            except Exception as e:
                logging.warning("Erro ao coletar on-chain: %s", str(e))
            
            # Tentar coletar whale alerts (se API key configurada)
            try:
                if os.getenv("WHALEALERT_API_KEY"):
                    whale_df = om_main.fetch_whale_alerts()
            except Exception as e:
                logging.warning("Erro ao coletar whale alerts: %s", str(e))
        except Exception as e:
            logging.warning("Erro ao usar módulo principal: %s", str(e))
    
    # Coleta alternativa Reddit
    try:
        logging.info("Coletando dados do Reddit...")
        reddit_df = coletar_reddit()
        resultados['coleta_reddit'] = {
            'status': 'sucesso',
            'registros': len(reddit_df),
            'subreddits': list(reddit_df['subreddit'].unique()) if not reddit_df.empty else []
        }
    except Exception as e:
        logging.error("Erro na coleta do Reddit: %s", str(e))
        reddit_df = pd.DataFrame()
        resultados['coleta_reddit'] = {'status': 'erro', 'erro': str(e)}
    
    # Coleta alternativa Telegram / Discord
    try:
        logging.info("Coletando dados do Telegram/Discord (placeholder)...")
        tg_dc_data = run_async_collect_telegram_discord()
        resultados['coleta_telegram_discord'] = {
            'status': 'sucesso',
            'registros': len(tg_dc_data)
        }
    except Exception as e:
        logging.error("Erro na coleta Telegram/Discord: %s", str(e))
        tg_dc_data = []
        resultados['coleta_telegram_discord'] = {'status': 'erro', 'erro': str(e)}
    
    # Realizar validação cruzada estendida
    try:
        logging.info("Realizando validação cruzada estendida...")
        validated_events = cross_validate_extended(
            onchain_df=onchain_df,
            whale_df=whale_df,
            tweets_df=tweets_df,
            orderbook_list=orderbook_list,
            reddit_df=reddit_df,
            tg_dc_data=tg_dc_data
        )
        resultados['validacao_cruzada'] = {
            'status': 'sucesso',
            'eventos_validados': len(validated_events),
            'eventos': validated_events[:10]  # Limitar exemplos
        }
    except Exception as e:
        logging.error("Erro na validação cruzada: %s", str(e))
        validated_events = []
        resultados['validacao_cruzada'] = {'status': 'erro', 'erro': str(e)}
    
    # Gerar relatório simplificado e salvar
    resultados['timestamp_termino'] = datetime.utcnow().isoformat()
    resultados['status'] = 'concluido'
    
    relatorio_arquivo = DATA_DIR / f"relatorio_expandido_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    with open(relatorio_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, default=str, ensure_ascii=False)
    
    logging.info("="*80)
    logging.info("Relatório expandido salvo em %s", relatorio_arquivo)
    logging.info("Total de eventos validados: %d", len(validated_events))
    logging.info("="*80)
    
    # Finalização
    logging.info("Pipeline expandido concluído com sucesso.")
    
    return resultados


if __name__ == "__main__":
    try:
        resultados = executar_pipeline_expandido()
        print("\n" + "="*80)
        print("RESUMO DA EXECUÇÃO")
        print("="*80)
        print(f"Status: {resultados.get('status', 'desconhecido')}")
        print(f"Reddit: {resultados.get('coleta_reddit', {}).get('registros', 0)} registros")
        print(f"Telegram/Discord: {resultados.get('coleta_telegram_discord', {}).get('registros', 0)} registros")
        print(f"Eventos Validados: {resultados.get('validacao_cruzada', {}).get('eventos_validados', 0)}")
        print("="*80)
    except KeyboardInterrupt:
        logging.info("Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        logging.error("Erro crítico na execução: %s", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

