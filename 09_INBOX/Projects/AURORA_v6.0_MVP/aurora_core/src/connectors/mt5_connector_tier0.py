"""
MT5 Connector Tier-0
Com rate limiting, circuit breakers, e validação de segurança
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
import hashlib
import logging

logger = logging.getLogger(__name__)


class Tier0MT5Connector:
    """
    MT5 Connector com todas as proteções Tier-0
    
    Features:
    - Rate limiting por símbolo
    - Circuit breaker integration
    - Validação de integridade de dados
    - Connection pooling simulation
    """
    
    def __init__(
        self, 
        account: str, 
        password: str, 
        server: str,
        circuit_breaker: Any,
        requests_per_minute: int = 60
    ):
        """
        Initialize MT5 connector
        
        Args:
            account: Número da conta MT5
            password: Senha da conta
            server: Servidor MT5
            circuit_breaker: Instância do Tier0CircuitBreaker
            requests_per_minute: Limite de requests por minuto por símbolo
        """
        self.account = account
        self.password = password
        self.server = server
        self.circuit_breaker = circuit_breaker
        
        # Rate limiting
        self.requests_per_minute = requests_per_minute
        self.request_log: Dict[str, List[datetime]] = defaultdict(list)
        
        # Connection state
        self.connected = False
        self.last_connection_test: Optional[datetime] = None
        
        # Simulated prices for demo mode
        self._base_prices: Dict[str, float] = {
            "EURUSD": 1.0850,
            "XAUUSD": 2650.00,
            "BTCUSD": 95000.0,
            "GBPUSD": 1.2650,
            "USDJPY": 157.50
        }
        
        logger.info(f"MT5 Connector initialized for account {account[-4:]}***")
    
    async def connect(self) -> bool:
        """Estabelecer conexão com MT5"""
        if not await self.circuit_breaker.can_execute():
            logger.warning("Cannot connect: circuit breaker is OPEN")
            return False
        
        try:
            # Simulação de conexão
            await asyncio.sleep(0.1)
            self.connected = True
            self.last_connection_test = datetime.utcnow()
            
            logger.info(f"MT5 connected successfully to {self.server}")
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection failed: {e}")
            self.connected = False
            await self.circuit_breaker.record_failure(str(e))
            return False
    
    async def disconnect(self) -> None:
        """Desconectar do MT5"""
        self.connected = False
        logger.info("MT5 disconnected")
    
    async def _check_rate_limit(self, symbol: str) -> bool:
        """Verificar rate limit para símbolo específico"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Limpar registros antigos
        self.request_log[symbol] = [
            t for t in self.request_log[symbol] 
            if t > minute_ago
        ]
        
        # Verificar limite
        if len(self.request_log[symbol]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {symbol}")
            return False
        
        self.request_log[symbol].append(now)
        return True
    
    async def get_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obter tick com todas as validações Tier-0
        
        Args:
            symbol: Símbolo do instrumento
            
        Returns:
            Dict com dados do tick ou None em caso de erro
        """
        # 1. Verificar circuit breaker
        if not await self.circuit_breaker.can_execute():
            return None
        
        # 2. Verificar rate limiting
        if not await self._check_rate_limit(symbol):
            return None
        
        # 3. Verificar conexão
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            # Simulação de tick data
            await asyncio.sleep(0.05)  # Latência de rede
            
            # Gerar tick simulado
            tick_time = datetime.utcnow()
            base_price = self._base_prices.get(symbol, 1.0)
            
            # Adicionar variação aleatória pequena
            import random
            variation = random.uniform(-0.0005, 0.0005) * base_price
            price = base_price + variation
            
            # Spread baseado no instrumento
            spread = 0.0002 if "USD" in symbol else 0.50
            
            # Hash para integridade
            tick_str = f"{symbol}:{tick_time.timestamp()}:{price}"
            integrity_hash = hashlib.sha256(tick_str.encode()).hexdigest()
            
            tick_data = {
                "symbol": symbol,
                "bid": round(price, 5 if "USD" in symbol else 2),
                "ask": round(price + spread, 5 if "USD" in symbol else 2),
                "timestamp": tick_time.isoformat(),
                "integrity_hash": integrity_hash[:32],
                "source": "MT5_DEMO",
                "volume": random.randint(1, 100)
            }
            
            logger.debug(f"Tick: {symbol} bid={tick_data['bid']}")
            return tick_data
            
        except Exception as e:
            logger.error(f"Failed to get tick for {symbol}: {e}")
            await self.circuit_breaker.record_failure(str(e))
            return None
    
    async def collect_ticks(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Coletar ticks para múltiplos símbolos em paralelo
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Lista de ticks válidos
        """
        tasks = [self.get_tick(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos
        valid_ticks: List[Dict[str, Any]] = []
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Tick collection failed for {symbol}: {result}")
            elif result:
                valid_ticks.append(result)
        
        return valid_ticks
    
    async def execute_order(
        self, 
        symbol: str, 
        order_type: str, 
        volume: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executar ordem no MT5
        
        Args:
            symbol: Símbolo do instrumento
            order_type: "BUY" ou "SELL"
            volume: Volume em lotes
            price: Preço (None para market order)
            sl: Stop Loss
            tp: Take Profit
            
        Returns:
            Dict com resultado da execução
        """
        if not await self.circuit_breaker.can_execute():
            return {
                "success": False,
                "error": "circuit_breaker_open",
                "ticket": None
            }
        
        if not self.connected:
            if not await self.connect():
                return {
                    "success": False,
                    "error": "not_connected",
                    "ticket": None
                }
        
        try:
            # Simulação de execução
            await asyncio.sleep(0.1)
            
            # Gerar ticket simulado
            import random
            ticket = random.randint(100000000, 999999999)
            
            # Obter preço atual
            tick = await self.get_tick(symbol)
            if not tick:
                return {
                    "success": False,
                    "error": "no_tick_data",
                    "ticket": None
                }
            
            execution_price = tick["ask"] if order_type == "BUY" else tick["bid"]
            
            result = {
                "success": True,
                "ticket": ticket,
                "symbol": symbol,
                "order_type": order_type,
                "volume": volume,
                "price": execution_price,
                "sl": sl,
                "tp": tp,
                "timestamp": datetime.utcnow().isoformat(),
                "demo": True
            }
            
            await self.circuit_breaker.record_success()
            logger.info(f"Order executed: {order_type} {volume} {symbol} @ {execution_price}")
            
            return result
            
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            await self.circuit_breaker.record_failure(str(e))
            return {
                "success": False,
                "error": str(e),
                "ticket": None
            }
    
    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """
        Fechar posição existente
        
        Args:
            ticket: Ticket da posição
            
        Returns:
            Dict com resultado do fechamento
        """
        try:
            await asyncio.sleep(0.05)
            
            return {
                "success": True,
                "ticket": ticket,
                "closed_at": datetime.utcnow().isoformat(),
                "demo": True
            }
            
        except Exception as e:
            logger.error(f"Failed to close position {ticket}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ticket": ticket
            }
    
    def is_connected(self) -> bool:
        """Verificar status da conexão"""
        return self.connected
    
    def get_account_info(self) -> Dict[str, Any]:
        """Obter informações da conta"""
        return {
            "account": self.account[-4:] + "***",
            "server": self.server,
            "connected": self.connected,
            "demo": True,
            "balance": 10000.0,  # Demo balance
            "equity": 10000.0,
            "margin": 0.0,
            "free_margin": 10000.0
        }

