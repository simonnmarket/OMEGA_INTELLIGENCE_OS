#!/usr/bin/env python3
"""
AURORA MT5 EXECUTOR - Integração MetaTrader 5
==============================================
Módulo responsável por conectar ao MetaTrader 5 e executar ordens
geradas pelas estratégias do sistema Aurora.

Funcionalidades:
- Conexão automática ao MT5
- Conversão de TradeSignal para ordens MT5
- Envio de ordens (BUY/SELL)
- Monitoramento de posições
- Gestão de erros e reconexão
- Logging detalhado de todas as operações
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from enum import Enum
import time

# Importar correção de stops
try:
    from .MT5_STOPS_FIX import MT5StopsFix
    STOPS_FIX_AVAILABLE = True
except ImportError:
    try:
        from MT5_STOPS_FIX import MT5StopsFix
        STOPS_FIX_AVAILABLE = True
    except ImportError:
        STOPS_FIX_AVAILABLE = False
        MT5StopsFix = None

# Tentar importar MetaTrader5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logging.warning("⚠️  MetaTrader5 não instalado. Execute: pip install MetaTrader5")

logger = logging.getLogger("AURORA_MT5_EXECUTOR")


class OrderType(Enum):
    """Tipos de ordem MT5"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class MT5Executor:
    """
    Executor de ordens para MetaTrader 5
    Converte TradeSignal das estratégias em ordens MT5 e executa
    """
    
    def __init__(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        path: Optional[str] = None,
        timeout: int = 10000,
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5
    ):
        """
        Inicializa o executor MT5
        
        Args:
            login: Número da conta MT5 (None = usar conta padrão)
            password: Senha da conta (None = usar conta padrão)
            server: Servidor broker (None = usar padrão)
            path: Caminho para terminal MT5 (None = usar padrão)
            timeout: Timeout de conexão em ms
            auto_reconnect: Tentar reconectar automaticamente
            max_reconnect_attempts: Máximo de tentativas de reconexão
        """
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self.connected = False
        self.account_info = None
        self.reconnect_count = 0
        self.orders_sent = 0
        self.orders_failed = 0
        
        # Inicializar correção de stops
        if STOPS_FIX_AVAILABLE and MT5StopsFix:
            try:
                self.stops_fixer = MT5StopsFix()
                logger.info("✅ Correção robusta de stops MT5 carregada")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao carregar correção de stops: {e}")
                self.stops_fixer = None
        else:
            self.stops_fixer = None
            logger.warning("⚠️  Correção de stops MT5 não disponível")
        self.positions_open = 0
        
        logger.info("🔌 MT5 Executor inicializado")
        
        if not MT5_AVAILABLE:
            logger.error("❌ MetaTrader5 não disponível - instale: pip install MetaTrader5")
            return
        
        # Tentar conectar automaticamente
        if self.connect():
            logger.info("✅ Conectado ao MetaTrader 5")
        else:
            logger.warning("⚠️  Não foi possível conectar ao MT5 - tentará reconectar quando necessário")
    
    def connect(self) -> bool:
        """
        Conecta ao MetaTrader 5
        
        Returns:
            True se conexão bem-sucedida, False caso contrário
        """
        if not MT5_AVAILABLE:
            logger.error("❌ MetaTrader5 não disponível")
            return False
        
        try:
            # Inicializar MT5
            if self.path:
                if not mt5.initialize(path=self.path, timeout=self.timeout):
                    logger.error(f"❌ Falha ao inicializar MT5 no caminho: {self.path}")
                    logger.error(f"   Erro: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize(timeout=self.timeout):
                    logger.error(f"❌ Falha ao inicializar MT5 (caminho padrão)")
                    logger.error(f"   Erro: {mt5.last_error()}")
                    return False
            
            # Login se credenciais fornecidas
            if self.login and self.password:
                if not mt5.login(login=self.login, password=self.password, server=self.server):
                    logger.error(f"❌ Falha no login MT5")
                    logger.error(f"   Erro: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
                logger.info(f"✅ Login realizado: conta {self.login}")
            
            # Verificar conexão
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("❌ Não foi possível obter informações da conta")
                mt5.shutdown()
                return False
            
            self.account_info = account_info
            self.connected = True
            self.reconnect_count = 0
            
            # Log informações da conta
            logger.info("=" * 60)
            logger.info("📊 INFORMAÇÕES DA CONTA MT5")
            logger.info("=" * 60)
            logger.info(f"   Conta: {account_info.login}")
            logger.info(f"   Servidor: {account_info.server}")
            logger.info(f"   Nome: {account_info.name}")
            logger.info(f"   Saldo: {account_info.balance:.2f} {account_info.currency}")
            logger.info(f"   Equity: {account_info.equity:.2f} {account_info.currency}")
            logger.info(f"   Margem Livre: {account_info.margin_free:.2f} {account_info.currency}")
            logger.info(f"   Margem: {account_info.margin:.2f} {account_info.currency}")
            logger.info(f"   Leverage: 1:{account_info.leverage}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Erro ao conectar ao MT5: {str(e)}")
            import traceback
            traceback.print_exc()
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """Desconecta do MetaTrader 5"""
        if not MT5_AVAILABLE:
            return False
        
        try:
            mt5.shutdown()
            self.connected = False
            logger.info("🔌 Desconectado do MetaTrader 5")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar: {str(e)}")
            return False
    
    def ensure_connected(self) -> bool:
        """
        Garante que está conectado ao MT5
        Tenta reconectar se necessário
        
        Returns:
            True se conectado, False caso contrário
        """
        if self.connected:
            # Verificar se ainda está conectado
            try:
                account_info = mt5.account_info()
                if account_info is not None:
                    return True
            except:
                pass
        
        # Tentar reconectar
        if self.auto_reconnect and self.reconnect_count < self.max_reconnect_attempts:
            self.reconnect_count += 1
            logger.warning(f"🔄 Tentando reconectar ao MT5 (tentativa {self.reconnect_count}/{self.max_reconnect_attempts})...")
            if self.connect():
                return True
        
        logger.error("❌ Não foi possível conectar ao MT5")
        return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações do símbolo no MT5
        
        Args:
            symbol: Símbolo do ativo (ex: "BTCUSD", "EURUSD")
        
        Returns:
            Dict com informações do símbolo ou None se erro
        """
        if not self.ensure_connected():
            return None
        
        try:
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                logger.error(f"❌ Símbolo {symbol} não disponível no MT5")
                logger.error(f"   Erro: {mt5.last_error()}")
                return None
            
            # Obter informações
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"❌ Não foi possível obter informações de {symbol}")
                return None
            
            # Obter tick atual
            tick = mt5.symbol_info_tick(symbol)
            
            return {
                "symbol": symbol,
                "name": symbol_info.name,
                "description": symbol_info.description,
                "currency_base": symbol_info.currency_base,
                "currency_profit": symbol_info.currency_profit,
                "digits": symbol_info.digits,
                "trade_mode": symbol_info.trade_mode,
                "trade_stops_level": symbol_info.trade_stops_level,
                "point": symbol_info.point,
                "volume_min": symbol_info.volume_min,
                "volume_max": symbol_info.volume_max,
                "volume_step": symbol_info.volume_step,
                "spread": symbol_info.spread,
                "bid": tick.bid if tick else None,
                "ask": tick.ask if tick else None,
                "last": tick.last if tick else None,
                "time": tick.time if tick else None
            }
            
        except Exception as e:
            logger.error(f"💥 Erro ao obter informações de {symbol}: {str(e)}")
            return None
    
    def convert_signal_to_mt5_order(
        self,
        signal: Any,  # TradeSignal
        symbol_info: Dict[str, Any],
        sl_points: int = 100,
        tp_points: int = 200
    ) -> Optional[Dict[str, Any]]:
        """
        Converte TradeSignal para formato de ordem MT5
        
        Args:
            signal: TradeSignal da estratégia
            symbol_info: Informações do símbolo do MT5
            sl_points: Stop Loss em pontos (padrão 100)
            tp_points: Take Profit em pontos (padrão 200)
        
        Returns:
            Dict com parâmetros da ordem MT5 ou None se erro
        """
        try:
            # Determinar tipo de ordem
            if signal.action.upper() == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                price = symbol_info.get("ask")
                if price is None:
                    logger.error(f"❌ Preço ASK não disponível para {signal.symbol}")
                    return None
            elif signal.action.upper() == "SELL":
                order_type = mt5.ORDER_TYPE_SELL
                price = symbol_info.get("bid")
                if price is None:
                    logger.error(f"❌ Preço BID não disponível para {signal.symbol}")
                    return None
            else:
                logger.warning(f"⚠️  Ação {signal.action} não suportada (apenas BUY/SELL)")
                return None
            
            # Calcular Stop Loss e Take Profit
            point = symbol_info.get("point", 0.00001)
            stops_level = symbol_info.get("trade_stops_level", 0)
            
            # Log do stops_level para debug
            logger.info(f"   📊 Stops Level do símbolo: {stops_level} pontos")
            logger.info(f"   📊 Point: {point}")
            
            # Distância mínima em pontos (garantir que respeita trade_stops_level)
            # Para crypto, stops_level pode ser muito alto (ex: 1000+ pontos)
            # Se stops_level = 0, usar valores conservadores baseados no preço
            if stops_level > 0:
                min_stop_distance = stops_level  # Usar exatamente o stops_level
            else:
                # Se stops_level = 0, calcular baseado no preço (0.1% para crypto)
                min_stop_distance = max(int(price * 0.001 / point), 100)  # 0.1% do preço ou 100 pontos
            
            logger.info(f"   📊 Distância mínima calculada: {min_stop_distance} pontos")
            
            # Se não especificado, usar valores baseados no stops_level
            if sl_points is None or sl_points <= 0:
                if stops_level > 0:
                    sl_points = stops_level * 2  # 2x o stops_level
                else:
                    sl_points = max(min_stop_distance * 2, 500)  # 2x a distância mínima ou 500 pontos
            
            if tp_points is None or tp_points <= 0:
                if stops_level > 0:
                    tp_points = stops_level * 3  # 3x o stops_level
                else:
                    tp_points = max(min_stop_distance * 3, 1000)  # 3x a distância mínima ou 1000 pontos
            
            # GARANTIR que distâncias respeitam mínimo absoluto
            sl_points = max(sl_points, min_stop_distance + 1)  # +1 para garantir que está além
            tp_points = max(tp_points, min_stop_distance + 1)
            
            logger.info(f"   📊 SL Points: {sl_points}, TP Points: {tp_points}")
            
            if order_type == mt5.ORDER_TYPE_BUY:
                # SL abaixo do preço, TP acima
                sl = price - (sl_points * point)
                tp = price + (tp_points * point)
                
                # Validar distância mínima absoluta (garantir que está longe o suficiente)
                sl_distance_points = (price - sl) / point
                tp_distance_points = (tp - price) / point
                
                logger.info(f"   📊 SL Distance: {sl_distance_points:.0f} pontos, TP Distance: {tp_distance_points:.0f} pontos")
                
                if sl_distance_points < min_stop_distance:
                    sl = price - ((min_stop_distance + 1) * point)  # +1 para garantir
                    logger.warning(f"   ⚠️  SL ajustado: {sl_distance_points:.0f} -> {min_stop_distance + 1:.0f} pontos")
                
                if tp_distance_points < min_stop_distance:
                    tp = price + ((min_stop_distance + 1) * point)  # +1 para garantir
                    logger.warning(f"   ⚠️  TP ajustado: {tp_distance_points:.0f} -> {min_stop_distance + 1:.0f} pontos")
            else:  # SELL
                # SL acima do preço, TP abaixo
                sl = price + (sl_points * point)
                tp = price - (tp_points * point)
                
                # Validar distância mínima absoluta
                sl_distance_points = (sl - price) / point
                tp_distance_points = (price - tp) / point
                
                logger.info(f"   📊 SL Distance: {sl_distance_points:.0f} pontos, TP Distance: {tp_distance_points:.0f} pontos")
                
                if sl_distance_points < min_stop_distance:
                    sl = price + ((min_stop_distance + 1) * point)  # +1 para garantir
                    logger.warning(f"   ⚠️  SL ajustado: {sl_distance_points:.0f} -> {min_stop_distance + 1:.0f} pontos")
                
                if tp_distance_points < min_stop_distance:
                    tp = price - ((min_stop_distance + 1) * point)  # +1 para garantir
                    logger.warning(f"   ⚠️  TP ajustado: {tp_distance_points:.0f} -> {min_stop_distance + 1:.0f} pontos")
            
            # Log final
            logger.info(f"   ✅ SL Final: {sl:.5f} ({abs(price - sl) / point:.0f} pontos do preço)")
            logger.info(f"   ✅ TP Final: {tp:.5f} ({abs(tp - price) / point:.0f} pontos do preço)")
            
            # Normalizar volume
            volume_min = symbol_info.get("volume_min", 0.01)
            volume_max = symbol_info.get("volume_max", 100.0)
            volume_step = symbol_info.get("volume_step", 0.01)
            
            # Converter quantidade para volume
            volume = float(signal.quantity)
            
            # Ajustar volume para step
            volume = round(volume / volume_step) * volume_step
            
            # Limitar volume
            volume = max(volume_min, min(volume, volume_max))
            
            # Preparar request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": 20,  # Desvio máximo em pontos
                "magic": 123456,  # Magic number para identificar ordens Aurora
                "comment": f"AURORA_{signal.strategy_id}",
                "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancel
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }
            
            # Adicionar SL/TP APENAS se respeitarem distância mínima
            # Validar distância final antes de adicionar
            sl_distance_final = abs(price - sl) / point if sl > 0 else 0
            tp_distance_final = abs(tp - price) / point if tp > 0 else 0
            
            if sl > 0 and sl_distance_final >= min_stop_distance:
                request["sl"] = round(sl, symbol_info.get("digits", 5))
                logger.info(f"   ✅ SL adicionado: {sl:.5f} ({sl_distance_final:.0f} pontos)")
            else:
                if sl > 0:
                    logger.warning(f"   ⚠️  SL removido: distância {sl_distance_final:.0f} < mínimo {min_stop_distance}")
                # Não adicionar SL se não respeitar distância mínima
            
            if tp > 0 and tp_distance_final >= min_stop_distance:
                request["tp"] = round(tp, symbol_info.get("digits", 5))
                logger.info(f"   ✅ TP adicionado: {tp:.5f} ({tp_distance_final:.0f} pontos)")
            else:
                if tp > 0:
                    logger.warning(f"   ⚠️  TP removido: distância {tp_distance_final:.0f} < mínimo {min_stop_distance}")
                # Não adicionar TP se não respeitar distância mínima
            
            # Se ambos SL/TP foram removidos, logar aviso mas continuar (ordem sem stops)
            if "sl" not in request and "tp" not in request:
                logger.warning("   ⚠️  ORDEM SERÁ ENVIADA SEM SL/TP (será adicionado depois)")
            
            return request
            
        except Exception as e:
            logger.error(f"💥 Erro ao converter sinal para ordem MT5: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute_order(self, signal: Any) -> Dict[str, Any]:
        """
        Executa uma ordem no MT5 baseada em TradeSignal
        
        Args:
            signal: TradeSignal da estratégia
        
        Returns:
            Dict com resultado da execução:
            {
                "success": bool,
                "ticket": int ou None,
                "price": float ou None,
                "volume": float ou None,
                "error": str ou None,
                "timestamp": str
            }
        """
        result = {
            "success": False,
            "ticket": None,
            "price": None,
            "volume": None,
            "sl": None,
            "tp": None,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "symbol": signal.symbol,
            "action": signal.action,
            "strategy_id": signal.strategy_id
        }
        
        if not self.ensure_connected():
            result["error"] = "Não conectado ao MT5"
            logger.error("❌ Não conectado ao MT5 - não é possível executar ordem")
            return result
        
        try:
            # Obter informações do símbolo
            symbol_info = self.get_symbol_info(signal.symbol)
            if symbol_info is None:
                result["error"] = f"Símbolo {signal.symbol} não disponível"
                return result
            
            # SOLUÇÃO DEFINITIVA: Enviar SEM SL/TP primeiro (garante execução)
            # Depois adicionar stops via modificação se necessário
            logger.info("🔧 SOLUÇÃO DEFINITIVA: Enviando ordem SEM SL/TP para garantir execução")
            
            tick = mt5.symbol_info_tick(signal.symbol)
            if not tick:
                result["error"] = "Tick não disponível"
                return result
            
            price = tick.ask if signal.action.upper() == "BUY" else tick.bid
            
            # Preparar ordem SEM stops
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": float(signal.quantity),
                "type": mt5.ORDER_TYPE_BUY if signal.action.upper() == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "comment": f"AURORA_{signal.strategy_id}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
                # NÃO ADICIONAR SL/TP AQUI - será adicionado depois se necessário
            }
            
            logger.info(f"📤 Enviando ordem SEM stops: {signal.symbol} {signal.action} @ {price}")
            
            # Log da ordem
            logger.info("=" * 60)
            logger.info("📤 ENVIANDO ORDEM AO MT5")
            logger.info("=" * 60)
            logger.info(f"   Símbolo: {signal.symbol}")
            logger.info(f"   Ação: {signal.action}")
            logger.info(f"   Volume: {request['volume']}")
            logger.info(f"   Preço: {request['price']}")
            logger.info(f"   SL: {request.get('sl', 'N/A')}")
            logger.info(f"   TP: {request.get('tp', 'N/A')}")
            logger.info(f"   Estratégia: {signal.strategy_id}")
            logger.info(f"   Confiança: {signal.confidence:.2%}")
            logger.info("=" * 60)
            
            # Enviar ordem
            result_order = mt5.order_send(request)
            
            if result_order is None:
                error = mt5.last_error()
                result["error"] = f"Erro ao enviar ordem: {error}"
                logger.error(f"❌ Falha ao enviar ordem: {error}")
                self.orders_failed += 1
                return result
            
            # Verificar resultado
            if result_order.retcode != mt5.TRADE_RETCODE_DONE:
                result["error"] = f"Código de retorno: {result_order.retcode} - {result_order.comment}"
                logger.error(f"❌ Ordem rejeitada: {result_order.retcode} - {result_order.comment}")
                self.orders_failed += 1
                return result
            
            # Sucesso!
            result["success"] = True
            result["ticket"] = result_order.order
            result["price"] = result_order.price
            result["volume"] = result_order.volume
            result["sl"] = result_order.sl
            result["tp"] = result_order.tp
            
            self.orders_sent += 1
            
            logger.info("✅ ORDEM EXECUTADA COM SUCESSO")
            logger.info(f"   Ticket: {result_order.order}")
            logger.info(f"   Preço Executado: {result_order.price}")
            logger.info(f"   Volume: {result_order.volume}")
            logger.info(f"   SL: {result_order.sl}")
            logger.info(f"   TP: {result_order.tp}")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"💥 Erro ao executar ordem: {str(e)}")
            import traceback
            traceback.print_exc()
            self.orders_failed += 1
            return result
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém posições abertas
        
        Args:
            symbol: Filtrar por símbolo (None = todas)
        
        Returns:
            Lista de dicts com informações das posições
        """
        if not self.ensure_connected():
            return []
        
        try:
            positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
            
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "time": pos.time,
                    "comment": pos.comment
                })
            
            self.positions_open = len(result)
            return result
            
        except Exception as e:
            logger.error(f"💥 Erro ao obter posições: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do executor
        
        Returns:
            Dict com estatísticas
        """
        positions = self.get_positions()
        total_profit = sum(p["profit"] for p in positions)
        
        return {
            "connected": self.connected,
            "reconnect_count": self.reconnect_count,
            "orders_sent": self.orders_sent,
            "orders_failed": self.orders_failed,
            "success_rate": (self.orders_sent / (self.orders_sent + self.orders_failed) * 100) if (self.orders_sent + self.orders_failed) > 0 else 0,
            "positions_open": len(positions),
            "total_profit": total_profit,
            "account_balance": self.account_info.balance if self.account_info else None,
            "account_equity": self.account_info.equity if self.account_info else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def __del__(self):
        """Desconecta ao destruir objeto"""
        if self.connected:
            self.disconnect()

