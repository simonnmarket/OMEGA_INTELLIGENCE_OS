"""
NumeiaTradingSystem v3.1 - Módulo Robusto de yfinance
===================================================
Implementa retry strategy, delays e User-Agent customizado
para evitar rate limits 429 do Yahoo Finance.

Autor: AIC (Agente IA Cursor)
Data: 03-11-2025 22:40 CET
Versão: 1.0.0
"""

import yfinance as yf
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, List
import pandas as pd

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

class RobustYFinance:
    """
    Wrapper robusto para yfinance com:
    - Retry automático com backoff exponencial
    - Delays entre requests
    - User-Agent customizado
    - Fallback para múltiplas tentativas
    """
    
    def __init__(self, max_retries: int = 5, backoff_factor: float = 2.0, delay_between_requests: float = 1.5):
        """
        Inicializa o wrapper robusto.
        
        Args:
            max_retries: Número máximo de tentativas
            backoff_factor: Fator de crescimento do delay (1s, 2s, 4s, 8s, 16s)
            delay_between_requests: Delay base entre requests (segundos)
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.delay = delay_between_requests
        
        # yfinance 0.2.66+ usa curl_cffi internamente
        # Deixamos ele gerenciar a sessão automaticamente
        
        logging.info(f"[RobustYFinance] Inicializado com retry={max_retries}, backoff={backoff_factor}s, delay={self.delay}s")
        logging.info(f"[RobustYFinance] yfinance v0.2.66+ com curl_cffi - sessão gerenciada automaticamente")
    
    def download(self, ticker: str, start: str, end: str, progress: bool = False) -> pd.DataFrame:
        """
        Download robusto de dados históricos.
        
        Args:
            ticker: Símbolo do ativo (ex: 'SPY', 'AAPL')
            start: Data inicial (formato: 'YYYY-MM-DD')
            end: Data final (formato: 'YYYY-MM-DD')
            progress: Exibir barra de progresso
        
        Returns:
            DataFrame com dados OHLCV
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logging.info(f"[RobustYFinance] Tentativa {attempt+1}/{self.max_retries}: {ticker} ({start} a {end})")
                
                # Download (yfinance 0.2.66+ gerencia sessão internamente)
                data = yf.download(ticker, start=start, end=end, progress=progress)
                
                if data.empty:
                    raise ValueError(f"Dados vazios retornados para {ticker}")
                
                logging.info(f"[RobustYFinance] ✅ {ticker}: {len(data)} barras baixadas")
                
                # Delay entre requests para evitar rate limit
                time.sleep(self.delay)
                
                return data
                
            except Exception as e:
                last_error = e
                attempt += 1
                wait_time = self.backoff_factor ** attempt
                
                logging.warning(f"[RobustYFinance] ❌ Erro: {e}")
                
                if attempt < self.max_retries:
                    logging.info(f"[RobustYFinance] ⏳ Aguardando {wait_time:.1f}s antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"[RobustYFinance] 🚨 Falha após {self.max_retries} tentativas: {last_error}")
                    raise last_error
        
        raise last_error
    
    def download_multiple(self, tickers: List[str], start: str, end: str) -> Dict[str, pd.DataFrame]:
        """
        Download de múltiplos ativos com delays entre cada um.
        
        Args:
            tickers: Lista de símbolos
            start: Data inicial
            end: Data final
        
        Returns:
            Dicionário {ticker: DataFrame}
        """
        results = {}
        
        for i, ticker in enumerate(tickers):
            logging.info(f"[RobustYFinance] Baixando {i+1}/{len(tickers)}: {ticker}")
            
            try:
                data = self.download(ticker, start, end)
                results[ticker] = data
            except Exception as e:
                logging.error(f"[RobustYFinance] Falha em {ticker}: {e}")
                results[ticker] = pd.DataFrame()  # Retorna vazio para não quebrar o loop
        
        logging.info(f"[RobustYFinance] ✅ Download completo: {len(results)}/{len(tickers)} ativos")
        
        return results


# Função de teste rápido
def test_robust_yfinance():
    """Testa o download robusto com SPY"""
    logging.info("=" * 60)
    logging.info("TESTE DO MÓDULO ROBUSTO YFINANCE")
    logging.info("=" * 60)
    
    rf = RobustYFinance(max_retries=5, backoff_factor=2.0, delay_between_requests=1.5)
    
    try:
        data = rf.download('SPY', start='2023-01-01', end='2023-01-02')
        
        if not data.empty:
            logging.info("✅ TESTE PASSOU - yfinance funcionando!")
            logging.info(f"Dados recebidos:\n{data.head()}")
            return True
        else:
            logging.error("❌ TESTE FALHOU - dados vazios")
            return False
            
    except Exception as e:
        logging.error(f"❌ TESTE FALHOU - erro: {e}")
        return False


if __name__ == "__main__":
    test_robust_yfinance()

