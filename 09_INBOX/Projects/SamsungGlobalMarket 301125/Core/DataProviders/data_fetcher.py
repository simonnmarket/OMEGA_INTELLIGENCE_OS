# -*- coding: utf-8 -*-
"""
DATA FETCHER MODULE - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO - FASE 2
DATA: 2025-01-27
FUNÇÃO: Camada de abstração para busca de dados de mercado de múltiplas fontes
CHECKSUM: SHA3-256: FASE2_HASH_PLACEHOLDER
"""

import os
import time
import requests
import logging
import numpy as np
from typing import Dict, Optional, Any
from decimal import Decimal
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==================== CONSTANTES E CONFIGURAÇÕES ====================

# URLs Base das APIs
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Configurações de timeout e retry
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

# Modo de fallback
FALLBACK_TO_MOCK = os.getenv('FALLBACK_TO_MOCK', 'True').lower() == 'true'

# ==================== CLASSE PRINCIPAL ====================

class UnifiedDataFetcher:
    """
    Camada de abstração unificada para buscar dados de mercado de múltiplas fontes.
    
    Fontes Suportadas:
    - Binance: Dados de criptomoedas (BTC, ETH, etc.)
    - Alpha Vantage: Dados de ações (AAPL, GOOGL, etc.)
    
    Funcionalidades:
    - Tratamento robusto de erros
    - Sistema de fallback para dados mock
    - Normalização de dados em formato padronizado
    - Rate limiting e retry logic
    """
    
    def __init__(self):
        """Inicializa o fetcher com credenciais do arquivo .env"""
        self.binance_api_key = os.getenv('BINANCE_API_KEY', '')
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        
        # Cache de último dado válido para fallback
        self.last_valid_data = None
        self.last_fetch_time = 0
        
        # Estatísticas de requisições
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_count': 0
        }
        
        logging.info("🌐 UnifiedDataFetcher inicializado")
        if not self.alpha_vantage_api_key:
            logging.warning("⚠️ ALPHA_VANTAGE_API_KEY não configurada - usando dados de demonstração")
        if not self.binance_api_key:
            logging.info("ℹ️ BINANCE_API_KEY não configurada - Binance API pública será usada")
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """
        Faz uma requisição HTTP com retry logic e tratamento de erros.
        
        Args:
            url: URL completa da API
            params: Parâmetros query string
            headers: Headers HTTP customizados
            
        Returns:
            Dict com resposta JSON ou None em caso de falha
        """
        for attempt in range(MAX_RETRIES):
            try:
                self.stats['total_requests'] += 1
                
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=API_TIMEOUT
                )
                
                # Verificar rate limiting
                if response.status_code == 429:
                    logging.warning(f"⚠️ Rate limit atingido - aguardando {RETRY_DELAY * (attempt + 1)}s...")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                
                # Verificar resposta bem-sucedida
                response.raise_for_status()
                
                self.stats['successful_requests'] += 1
                return response.json()
                
            except requests.exceptions.Timeout:
                logging.error(f"❌ Timeout na requisição (tentativa {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.ConnectionError:
                logging.error(f"❌ Erro de conexão (tentativa {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.HTTPError as e:
                logging.error(f"❌ Erro HTTP: {e.response.status_code} - {e.response.text[:200]}")
                break  # Não retentar erros HTTP (exceto 429 já tratado)
                
            except Exception as e:
                logging.error(f"❌ Erro inesperado: {type(e).__name__}: {str(e)}")
                break
        
        self.stats['failed_requests'] += 1
        return None
    
    def fetch_crypto_data(self, symbol: str = 'BTCUSDT') -> Optional[Dict]:
        """
        Busca dados de criptomoeda da API pública da Binance.
        
        Args:
            symbol: Par de trading (ex: 'BTCUSDT', 'ETHUSDT')
            
        Returns:
            Dict normalizado com estrutura:
            {
                'symbol': str,
                'price': float,
                'volume_24h': float,
                'price_change_24h': float,
                'timestamp': int
            }
        """
        try:
            # Endpoint: 24hr Ticker Price Change Statistics
            url = f"{BINANCE_BASE_URL}/ticker/24hr"
            params = {'symbol': symbol}
            
            logging.info(f"📡 Buscando dados cripto: {symbol} (Binance)")
            
            data = self._make_request(url, params=params)
            
            if not data:
                return None
            
            # Normalizar dados para formato padronizado
            normalized = {
                'symbol': symbol,
                'price': float(data.get('lastPrice', 0)),
                'volume_24h': float(data.get('volume', 0)),
                'price_change_24h': float(data.get('priceChangePercent', 0)),
                'high_24h': float(data.get('highPrice', 0)),
                'low_24h': float(data.get('lowPrice', 0)),
                'timestamp': int(data.get('closeTime', time.time() * 1000)),
                'source': 'binance'
            }
            
            logging.info(f"✅ Cripto obtido: {symbol} = ${normalized['price']:,.2f} (24h: {normalized['price_change_24h']:+.2f}%)")
            
            return normalized
            
        except Exception as e:
            logging.error(f"❌ Erro ao buscar dados cripto {symbol}: {type(e).__name__}: {str(e)}")
            return None
    
    def fetch_stock_data(self, symbol: str = 'AAPL') -> Optional[Dict]:
        """
        Busca dados de ação da API Alpha Vantage.
        
        Args:
            symbol: Ticker da ação (ex: 'AAPL', 'GOOGL', 'MSFT')
            
        Returns:
            Dict normalizado com estrutura similar a fetch_crypto_data()
        """
        try:
            # Verificar se API key está configurada
            if not self.alpha_vantage_api_key:
                logging.warning(f"⚠️ Alpha Vantage API key não configurada - usando dados de demonstração para {symbol}")
                # Retornar dados de demonstração
                return self._generate_demo_stock_data(symbol)
            
            # Endpoint: Global Quote (dados em tempo real)
            url = ALPHA_VANTAGE_BASE_URL
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_api_key
            }
            
            logging.info(f"📡 Buscando dados de ação: {symbol} (Alpha Vantage)")
            
            data = self._make_request(url, params=params)
            
            if not data or 'Global Quote' not in data:
                logging.error(f"❌ Resposta inválida da Alpha Vantage para {symbol}")
                return None
            
            quote = data['Global Quote']
            
            # Verificar se há dados válidos
            if not quote or '05. price' not in quote:
                logging.error(f"❌ Dados vazios retornados para {symbol} - limite de API pode ter sido atingido")
                return None
            
            # Normalizar dados para formato padronizado
            normalized = {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'volume_24h': float(quote.get('06. volume', 0)),
                'price_change_24h': float(quote.get('10. change percent', '0').replace('%', '')),
                'high_24h': float(quote.get('03. high', 0)),
                'low_24h': float(quote.get('04. low', 0)),
                'timestamp': int(time.time() * 1000),
                'source': 'alpha_vantage'
            }
            
            logging.info(f"✅ Ação obtida: {symbol} = ${normalized['price']:,.2f} (24h: {normalized['price_change_24h']:+.2f}%)")
            
            return normalized
            
        except Exception as e:
            logging.error(f"❌ Erro ao buscar dados de ação {symbol}: {type(e).__name__}: {str(e)}")
            return None
    
    def _generate_demo_stock_data(self, symbol: str) -> Dict:
        """Gera dados de demonstração realistas para ações quando API não está disponível"""
        base_prices = {
            'AAPL': 185.30,
            'GOOGL': 142.50,
            'MSFT': 378.90,
            'TSLA': 242.80,
            'NVDA': 495.20
        }
        
        base_price = base_prices.get(symbol, 100.0)
        # Adicionar variação aleatória pequena (-1% a +1%)
        price = base_price * (1 + np.random.uniform(-0.01, 0.01))
        
        return {
            'symbol': symbol,
            'price': float(price),
            'volume_24h': float(np.random.randint(50_000_000, 150_000_000)),
            'price_change_24h': float(np.random.uniform(-2.5, 2.5)),
            'high_24h': float(price * 1.015),
            'low_24h': float(price * 0.985),
            'timestamp': int(time.time() * 1000),
            'source': 'demo'
        }
    
    def _generate_mock_market_data(self) -> Dict:
        """
        Gera dados de mercado simulados completos como fallback.
        Mantém compatibilidade com o formato esperado pelo NumeiaTradingSystem.
        """
        return {
            'prices': [40000 + np.random.randn() * 200],
            'volumes': [1000000 + np.random.randint(-100000, 100000)],
            'forex_prices': {'EUR/USD': 1.0855 + np.random.randn() * 0.001},
            'options': {'AAPL': {'implied_volatility': 0.35}},
            'sectors': {'XLK': {'price': 195.50}},
            'stocks': {'LMT': 450.25, 'AAPL': 185.30},
            'central_banks': {'FED': {'text': 'inflation is a concern'}},
            'liquidity': {},
            'macro': {'dxy': -0.02, 'real_rates': -0.015, 'inflation': 0.03, 'geo_risk': 0.4},
            'sentiment': [np.random.rand() * 0.4 - 0.6]
        }
    
    def get_all_market_data(self) -> Dict:
        """
        Método principal que compila dados de todas as fontes.
        
        Returns:
            Dict no formato esperado pelo NumeiaTradingSystem com dados reais
        """
        try:
            logging.info("🔄 Iniciando coleta de dados de mercado de múltiplas fontes...")
            
            # Buscar dados de criptomoedas
            btc_data = self.fetch_crypto_data('BTCUSDT')
            eth_data = self.fetch_crypto_data('ETHUSDT')
            
            # Buscar dados de ações
            aapl_data = self.fetch_stock_data('AAPL')
            
            # Verificar se conseguimos dados válidos
            if not btc_data and not aapl_data:
                logging.warning("⚠️ Nenhum dado válido obtido das APIs")
                if FALLBACK_TO_MOCK:
                    logging.info("🔄 Ativando modo fallback - usando dados mock")
                    self.stats['fallback_count'] += 1
                    return self._generate_mock_market_data()
                else:
                    raise Exception("Falha ao obter dados de mercado e fallback desativado")
            
            # Compilar dados no formato esperado pelo sistema
            market_data = {
                # Dados de Criptomoedas
                'prices': [btc_data['price']] if btc_data else [40000],
                'volumes': [btc_data['volume_24h']] if btc_data else [1000000],
                
                # Dados de Forex (mock por enquanto)
                'forex_prices': {'EUR/USD': 1.0855 + np.random.randn() * 0.001},
                
                # Dados de Ações
                'stocks': {
                    'AAPL': aapl_data['price'] if aapl_data else 185.30,
                    'LMT': 450.25  # Mock
                },
                
                # Dados de Opções (mock)
                'options': {'AAPL': {'implied_volatility': 0.35}},
                
                # Dados de Setores (mock)
                'sectors': {'XLK': {'price': 195.50}},
                
                # Dados Macroeconômicos (mock)
                'central_banks': {'FED': {'text': 'monitoring inflation'}},
                'liquidity': {},
                'macro': {
                    'dxy': -0.02,
                    'real_rates': -0.015,
                    'inflation': 0.03,
                    'geo_risk': 0.4
                },
                
                # Sentimento de Mercado (derivado de mudanças de preço)
                'sentiment': [
                    btc_data['price_change_24h'] / 100 if btc_data else np.random.rand() * 0.4 - 0.6
                ],
                
                # Metadados de fonte
                '_metadata': {
                    'btc_data': btc_data,
                    'eth_data': eth_data,
                    'aapl_data': aapl_data,
                    'timestamp': int(time.time() * 1000),
                    'sources': {
                        'crypto': 'binance' if btc_data else 'none',
                        'stocks': aapl_data['source'] if aapl_data else 'none'
                    }
                }
            }
            
            # Salvar como último dado válido
            self.last_valid_data = market_data
            self.last_fetch_time = time.time()
            
            logging.info("✅ Coleta de dados de mercado concluída com sucesso")
            logging.info(f"📊 Stats: {self.stats['successful_requests']}/{self.stats['total_requests']} requisições bem-sucedidas")
            
            return market_data
            
        except Exception as e:
            logging.error(f"❌ Erro crítico ao compilar dados de mercado: {type(e).__name__}: {str(e)}")
            
            # Tentar usar último dado válido
            if self.last_valid_data and FALLBACK_TO_MOCK:
                logging.warning("⚠️ Usando último dado válido em cache")
                self.stats['fallback_count'] += 1
                return self.last_valid_data
            
            # Fallback final para dados mock
            if FALLBACK_TO_MOCK:
                logging.warning("⚠️ Fallback final - gerando dados mock")
                self.stats['fallback_count'] += 1
                return self._generate_mock_market_data()
            
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso das APIs"""
        uptime = time.time() - self.last_fetch_time if self.last_fetch_time > 0 else 0
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'fallback_count': self.stats['fallback_count'],
            'success_rate': (
                self.stats['successful_requests'] / self.stats['total_requests'] * 100
                if self.stats['total_requests'] > 0 else 0
            ),
            'uptime_seconds': uptime
        }

# ==================== TESTE STANDALONE ====================

async def main():
    """Função de teste para validar o fetcher de forma independente"""
    print("=" * 60)
    print("TESTE STANDALONE - UNIFIED DATA FETCHER")
    print("=" * 60)
    
    fetcher = UnifiedDataFetcher()
    
    print("\n[TESTE 1] Buscando dados de BTC/USDT...")
    btc = fetcher.fetch_crypto_data('BTCUSDT')
    if btc:
        print(f"[OK] BTC: ${btc['price']:,.2f} | 24h: {btc['price_change_24h']:+.2f}%")
    else:
        print("[FALHA] Erro ao buscar BTC")
    
    print("\n[TESTE 2] Buscando dados de AAPL...")
    aapl = fetcher.fetch_stock_data('AAPL')
    if aapl:
        print(f"[OK] AAPL: ${aapl['price']:,.2f} | 24h: {aapl['price_change_24h']:+.2f}%")
    else:
        print("[FALHA] Erro ao buscar AAPL")
    
    print("\n[TESTE 3] Compilando todos os dados de mercado...")
    market_data = fetcher.get_all_market_data()
    print(f"[OK] Dados compilados: {len(market_data)} categorias")
    print(f"   - BTC Price: ${market_data['prices'][0]:,.2f}")
    print(f"   - AAPL Price: ${market_data['stocks']['AAPL']:,.2f}")
    
    print("\n[ESTATISTICAS]")
    stats = fetcher.get_statistics()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

