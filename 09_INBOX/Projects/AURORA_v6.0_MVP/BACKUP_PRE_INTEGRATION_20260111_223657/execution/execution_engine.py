"""
Execution Engine - AURORA v6.0 MVP
Motor de execução de trades
"""

from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger("EXECUTION_ENGINE")


class ExecutionEngine:
    """
    Motor de Execução de Trades
    
    Responsabilidades:
    - Receber sinais das estratégias
    - Validar com RiskEngine antes de executar
    - Executar via MT5Connector
    - Notificar MessageBus sobre resultados
    """
    
    def __init__(self, mt5_connector, risk_engine, message_bus=None):
        """
        Args:
            mt5_connector: Instância do MT5Connector
            risk_engine: Instância do RiskEngine
            message_bus: Instância do MessageBus (opcional)
        """
        self.mt5 = mt5_connector
        self.risk = risk_engine
        self.bus = message_bus
        self.active = False
        self.execution_count = 0
        self.last_execution = None
        
    def start(self):
        """Inicia o engine"""
        self.active = True
        logger.info("ExecutionEngine started")
        
    def stop(self):
        """Para o engine"""
        self.active = False
        logger.info("ExecutionEngine stopped")
    
    def execute_signal(
        self,
        signal: Dict,
        risk_params: Dict = None
    ) -> Dict:
        """
        Executa um sinal de trading
        
        Args:
            signal: {
                "symbol": str,
                "action": "BUY" | "SELL" | "HOLD",
                "confidence": float (0-1),
                "strategy": str,
                "metadata": dict
            }
            risk_params: {
                "max_risk": float,
                "position_size": float (opcional)
            }
            
        Returns:
            trade_result: {
                "success": bool,
                "order_id": int,
                "executed_price": float,
                "volume": float,
                "error": str (se falhou)
            }
        """
        if not self.active:
            return {"success": False, "error": "Engine not active"}
        
        # 1. Ignorar HOLD
        if signal.get("action") == "HOLD":
            return {"success": True, "action": "HOLD", "message": "No action needed"}
        
        symbol = signal.get("symbol")
        action = signal.get("action")
        confidence = signal.get("confidence", 0.5)
        
        # 2. Validar com RiskEngine
        risk_check = self.risk.validate_trade(
            symbol=symbol,
            action=action,
            confidence=confidence,
            risk_params=risk_params or {}
        )
        
        if not risk_check.get("approved"):
            logger.warning(f"Trade rejected by RiskEngine: {risk_check.get('reason')}")
            return {
                "success": False,
                "error": f"Risk rejected: {risk_check.get('reason')}",
                "risk_check": risk_check
            }
        
        # 3. Calcular volume
        volume = risk_check.get("position_size", 0.01)
        sl = risk_check.get("stop_loss")
        tp = risk_check.get("take_profit")
        
        # 4. Executar via MT5
        logger.info(f"Executing: {action} {volume} {symbol}")
        
        result = self.mt5.execute_order(
            symbol=symbol,
            action=action,
            volume=volume,
            sl=sl,
            tp=tp,
            comment=f"AURORA_{signal.get('strategy', 'unknown')}"
        )
        
        # 5. Processar resultado
        self.execution_count += 1
        self.last_execution = datetime.now()
        
        trade_result = {
            "success": result.get("success", False),
            "order_id": result.get("order_id"),
            "executed_price": result.get("price"),
            "volume": result.get("volume"),
            "symbol": symbol,
            "action": action,
            "strategy": signal.get("strategy"),
            "confidence": confidence,
            "timestamp": self.last_execution.isoformat(),
            "error": result.get("error")
        }
        
        # 6. Notificar MessageBus
        if self.bus and result.get("success"):
            self.bus.publish("trade_executed", trade_result)
        
        if result.get("success"):
            logger.info(f"Trade executed: {trade_result}")
        else:
            logger.error(f"Trade failed: {trade_result}")
        
        return trade_result
    
    def close_all_positions(self, symbol: str = None) -> Dict:
        """
        Fecha todas as posições (emergency close)
        
        Args:
            symbol: Se especificado, fecha apenas deste símbolo
            
        Returns:
            dict: {closed: int, failed: int, results: list}
        """
        positions = self.mt5.get_positions(symbol)
        
        results = []
        closed = 0
        failed = 0
        
        for pos in positions:
            result = self.mt5.close_position(pos["ticket"])
            results.append(result)
            
            if result.get("success"):
                closed += 1
            else:
                failed += 1
        
        logger.info(f"Close all positions: {closed} closed, {failed} failed")
        
        return {
            "closed": closed,
            "failed": failed,
            "results": results
        }
    
    def get_status(self) -> Dict:
        """Retorna status do engine"""
        return {
            "active": self.active,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "mt5_connected": self.mt5.connected if self.mt5 else False
        }

