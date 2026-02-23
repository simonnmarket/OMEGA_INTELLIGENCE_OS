from typing import Dict, Any, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketDataLoader:
    """Loader for market data from various sources."""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timeout = timedelta(minutes=5)
    
    async def initialize(self) -> None:
        """Initialize the data loader."""
        # TODO: Initialize connections to data sources
        pass
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        self.cache.clear()
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get market data for specified symbols."""
        market_data = {}
        
        for symbol in symbols:
            # Check cache first
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                market_data[symbol] = cached_data
                continue
            
            # Fetch new data
            try:
                data = await self._fetch_market_data(symbol)
                market_data[symbol] = data
                self._cache_data(symbol, data)
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                continue
        
        return market_data
    
    async def _fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch market data for a symbol."""
        # Get historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m")
        
        if hist.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Calculate metrics
        current_price = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[0]
        price_change = (current_price - prev_close) / prev_close
        
        volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].mean()
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
        
        returns = hist["Close"].pct_change()
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Get additional info
        info = ticker.info
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        dividend_yield = info.get("dividendYield", 0)
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "price_change": price_change,
            "volume": volume,
            "volume_ratio": volume_ratio,
            "volatility": volatility,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_cached_data(self, symbol: str) -> Dict[str, Any]:
        """Get cached data for a symbol."""
        if symbol not in self.cache:
            return None
        
        cached_data = self.cache[symbol]
        cache_time = datetime.fromisoformat(cached_data["timestamp"])
        
        if datetime.utcnow() - cache_time > self.cache_timeout:
            del self.cache[symbol]
            return None
        
        return cached_data
    
    def _cache_data(self, symbol: str, data: Dict[str, Any]) -> None:
        """Cache market data for a symbol."""
        self.cache[symbol] = data
    
    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical market data for a symbol."""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        
        if hist.empty:
            raise ValueError(f"No historical data available for {symbol}")
        
        return hist
    
    async def get_technical_indicators(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate technical indicators for a symbol."""
        # Get historical data
        hist = await self.get_historical_data(symbol, start_date, end_date)
        
        # Calculate indicators
        sma_20 = hist["Close"].rolling(window=20).mean()
        sma_50 = hist["Close"].rolling(window=50).mean()
        sma_200 = hist["Close"].rolling(window=200).mean()
        
        rsi = self._calculate_rsi(hist["Close"])
        macd, signal = self._calculate_macd(hist["Close"])
        
        return {
            "sma_20": sma_20.iloc[-1],
            "sma_50": sma_50.iloc[-1],
            "sma_200": sma_200.iloc[-1],
            "rsi": rsi.iloc[-1],
            "macd": macd.iloc[-1],
            "macd_signal": signal.iloc[-1]
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(
        self,
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line."""
        exp1 = prices.ewm(span=fast_period, adjust=False).mean()
        exp2 = prices.ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd, signal 