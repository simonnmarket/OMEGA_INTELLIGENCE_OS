#!/usr/bin/env python3
"""
🚀 AURORA v6.0 MVP - Entry Point
Sistema de Trading com Aprendizado Contínuo

Fluxo:
    1. Load config/settings.py
    2. Initialize MT5 connector
    3. Start Orchestrator
    4. Load strategies via StrategyLoader
    5. Start ExecutionEngine
    6. Start LearningEngine (background thread)
    7. Loop infinito:
       - Strategies geram sinais
       - ExecutionEngine executa
       - ExperienceBuffer salva
       - LearningEngine retreina (a cada 6h)
"""

import asyncio
import signal
import sys
import os
import logging
from datetime import datetime

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports do projeto
from config.settings import SETTINGS, get_setting
from config.database import DATABASE_CONFIG, ensure_directories
from connectors.mt5_connector import MT5Connector
from execution.execution_engine import ExecutionEngine
from learning.experience_buffer import ExperienceBuffer
from learning.learning_engine import LearningEngine
from learning.strategy_loader import StrategyLoader

# Configurar logging
logging.basicConfig(
    level=getattr(logging, get_setting("logging.level", "INFO")),
    format=get_setting("logging.format", "%(asctime)s | %(levelname)s | %(message)s"),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(get_setting("logging.file", "logs/aurora.log"), mode='a')
    ]
)

logger = logging.getLogger("AURORA_MAIN")


class AuroraSystem:
    """Sistema principal AURORA v6.0 MVP"""
    
    def __init__(self):
        self.running = False
        self.start_time = None
        
        # Componentes
        self.mt5: MT5Connector = None
        self.execution: ExecutionEngine = None
        self.buffer: ExperienceBuffer = None
        self.learning: LearningEngine = None
        self.strategies: StrategyLoader = None
        
        # Risk engine placeholder (usar o copiado)
        self.risk = None
        
    async def initialize(self):
        """Inicializa todos os componentes"""
        logger.info("=" * 60)
        logger.info(f"🚀 AURORA v{get_setting('system.version')} - Initializing...")
        logger.info("=" * 60)
        
        ensure_directories()
        
        # 1. MT5 Connector
        logger.info("📡 Connecting to MT5...")
        self.mt5 = MT5Connector(
            account=get_setting("mt5.account"),
            server=get_setting("mt5.server")
        )
        
        if not self.mt5.connect():
            logger.error("❌ MT5 connection failed!")
            return False
        
        account_info = self.mt5.get_account_info()
        logger.info(f"✅ MT5 Connected: {account_info['login']} @ {account_info['server']}")
        logger.info(f"💰 Balance: {account_info['currency']} {account_info['balance']:,.2f}")
        
        # 2. Experience Buffer
        logger.info("🗄️ Initializing Experience Buffer...")
        self.buffer = ExperienceBuffer(DATABASE_CONFIG["experience_buffer"])
        logger.info(f"✅ Buffer ready: {self.buffer.count()} experiences")
        
        # 3. Risk Engine (placeholder simples)
        logger.info("🛡️ Initializing Risk Engine...")
        self.risk = SimpleRiskEngine(get_setting("risk"))
        logger.info("✅ Risk Engine ready")
        
        # 4. Execution Engine
        logger.info("⚡ Initializing Execution Engine...")
        self.execution = ExecutionEngine(self.mt5, self.risk)
        self.execution.start()
        logger.info("✅ Execution Engine ready")
        
        # 5. Strategy Loader
        logger.info("📊 Loading Strategies...")
        self.strategies = StrategyLoader("strategies/")
        loaded = self.strategies.load_all_from_directory()
        logger.info(f"✅ {loaded} strategies loaded")
        
        # Ativar estratégias para símbolos
        for symbol in get_setting("strategies.symbols", ["XAUUSD"]):
            for strategy_name in get_setting("strategies.active", []):
                if strategy_name in [s["name"] for s in self.strategies.list_strategies()]:
                    self.strategies.set_active_strategy(symbol, strategy_name)
        
        # 6. Learning Engine
        logger.info("🧠 Initializing Learning Engine...")
        self.learning = LearningEngine(
            self.buffer,
            DATABASE_CONFIG["models_path"],
            get_setting("learning.check_interval_seconds", 3600)
        )
        self.learning.load_latest_model()
        self.learning.start()
        logger.info("✅ Learning Engine ready (background)")
        
        self.start_time = datetime.now()
        self.running = True
        
        logger.info("=" * 60)
        logger.info("✅ AURORA v6.0 MVP - INITIALIZED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return True
    
    async def run(self):
        """Loop principal de execução"""
        if not self.running:
            logger.error("System not initialized!")
            return
        
        logger.info("🔄 Starting main trading loop...")
        
        symbols = get_setting("strategies.symbols", ["XAUUSD"])
        confidence_threshold = get_setting("strategies.confidence_threshold", 0.6)
        paper_trading = get_setting("execution.paper_trading", True)
        
        if paper_trading:
            logger.info("📝 PAPER TRADING MODE - No real trades will be executed")
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                
                for symbol in symbols:
                    # 1. Obter dados do mercado
                    tick = self.mt5.get_tick(symbol)
                    if not tick:
                        continue
                    
                    # 2. Preparar estado
                    state = {
                        "symbol": symbol,
                        "bid": tick["bid"],
                        "ask": tick["ask"],
                        "spread": tick["ask"] - tick["bid"],
                        "time": tick["time"].isoformat()
                    }
                    
                    # 3. Gerar sinal
                    signal = self.strategies.generate_signal(symbol, state)
                    
                    if signal and signal.get("action") != "HOLD":
                        confidence = signal.get("confidence", 0)
                        
                        if confidence >= confidence_threshold:
                            logger.info(f"📈 Signal: {signal['action']} {symbol} (conf={confidence:.2f})")
                            
                            if not paper_trading:
                                # 4. Executar
                                result = self.execution.execute_signal(signal)
                                
                                # 5. Salvar experiência
                                if result.get("success"):
                                    self.buffer.add(
                                        state=state,
                                        action=signal["action"],
                                        reward=0.0,  # Atualizado quando trade fecha
                                        symbol=symbol,
                                        metadata={"signal": signal, "result": result}
                                    )
                            else:
                                logger.info(f"📝 [PAPER] Would execute: {signal['action']} {symbol}")
                
                # Heartbeat
                if cycle % 60 == 0:
                    uptime = (datetime.now() - self.start_time).total_seconds() / 60
                    logger.info(f"💓 Heartbeat: cycle={cycle}, uptime={uptime:.1f}min")
                
                # Aguardar próximo ciclo (5 segundos)
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal...")
                break
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(10)
    
    async def shutdown(self):
        """Encerra sistema graciosamente"""
        logger.info("🛑 Shutting down AURORA...")
        
        self.running = False
        
        if self.learning:
            self.learning.stop()
        
        if self.execution:
            self.execution.stop()
        
        if self.buffer:
            self.buffer.close()
        
        if self.mt5:
            self.mt5.disconnect()
        
        logger.info("👋 AURORA shutdown complete")


class SimpleRiskEngine:
    """Risk Engine simplificado para MVP"""
    
    def __init__(self, config: dict):
        self.config = config
        self.daily_loss = 0.0
        self.trade_count = 0
        
    def validate_trade(self, symbol: str, action: str, confidence: float, risk_params: dict) -> dict:
        """Valida trade contra regras de risco"""
        
        # Verificar perda diária
        if self.daily_loss >= self.config.get("max_daily_loss", 0.05):
            return {"approved": False, "reason": "Daily loss limit reached"}
        
        # Calcular tamanho da posição
        max_risk = risk_params.get("max_risk", self.config.get("max_risk_per_trade", 0.01))
        position_size = 0.01  # Lote mínimo para MVP
        
        return {
            "approved": True,
            "position_size": position_size,
            "stop_loss": None,  # Calcular baseado em ATR
            "take_profit": None
        }


async def main():
    """Função principal"""
    system = AuroraSystem()
    
    # Handler para SIGINT
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal...")
        system.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Inicializar
        if not await system.initialize():
            logger.error("Initialization failed!")
            return
        
        # Executar
        await system.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Encerrar
        await system.shutdown()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AURORA v6.0 MVP - Autonomous Trading System")
    print("=" * 60 + "\n")
    
    asyncio.run(main())

