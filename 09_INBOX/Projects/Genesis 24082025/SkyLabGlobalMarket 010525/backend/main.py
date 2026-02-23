from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from datetime import datetime
import logging
import uvicorn

# Import configurations
from .core.config import Config

# Import modules
from .api.mt5_connector import MT5Connector
from .core.database import Database
from .agents.traderbot import TraderBot
from .agents.analystagent import AnalystAgent
from .agents.riskguardian import RiskGuardian

# Configure logging
logging.basicConfig(
    level=Config.LOGGING['level'],
    format=Config.LOGGING['format'],
    filename=Config.LOGGING['file']
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SkyLab Global Market API",
    description="API for the SkyLab Global Market trading platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.API['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules with their configurations
db = Database(Config.DATABASE)
mt5 = MT5Connector(**Config.MT5)
trader_bot = TraderBot(mt5, db, Config.TRADER_BOT)
analyst_agent = AnalystAgent(db, Config.ANALYST_AGENT)
risk_guardian = RiskGuardian(db, Config.RISK_GUARDIAN)

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    try:
        if not mt5.connect():
            logger.error("Failed to connect to MT5")
            raise Exception("MT5 connection failed")
        logger.info("Successfully connected to MT5")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        mt5.disconnect()
        logger.info("Disconnected from MT5")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

@app.get("/api/positions", response_model=List[Dict])
async def get_positions():
    """Get all open positions."""
    try:
        positions = mt5.get_positions()
        if positions is None:
            raise HTTPException(status_code=500, detail="Failed to get positions")
        return positions
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-data", response_model=List[Dict])
async def get_market_data(symbol: str = "EURUSD", timeframe: int = 1, count: int = 100):
    """Get market data for a symbol."""
    try:
        data = mt5.get_market_data(symbol, timeframe, count)
        if data is None:
            raise HTTPException(status_code=500, detail="Failed to get market data")
        return data.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance", response_model=Dict)
async def get_performance():
    """Get trading performance metrics."""
    try:
        account_info = mt5.get_account_info()
        if account_info is None:
            raise HTTPException(status_code=500, detail="Failed to get account info")

        today = datetime.now()
        start_date = datetime(today.year, today.month, today.day)
        performance = analyst_agent.analyze_performance(start_date, today)

        return {
            "balance": account_info["balance"],
            "equity": account_info["equity"],
            "margin": account_info["margin"],
            "free_margin": account_info["free_margin"],
            "margin_level": account_info["margin_level"],
            "dailyPL": performance.get("total_profit", 0) - performance.get("total_loss", 0),
            "winRate": performance.get("win_rate", 0),
            "sharpeRatio": performance.get("sharpe_ratio", 0),
            "maxDrawdown": performance.get("max_drawdown", 0)
        }
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade")
async def execute_trade(trade_data: Dict):
    """Execute a trade."""
    try:
        required_fields = ["symbol", "action", "volume", "entry_price", "stop_loss"]
        if not all(field in trade_data for field in required_fields):
            raise HTTPException(status_code=400, detail="Missing required trade data")

        risk_assessment = risk_guardian.assess_trade_risk(
            trade_data["symbol"],
            trade_data["action"],
            trade_data["volume"],
            trade_data["entry_price"],
            trade_data["stop_loss"]
        )

        if not risk_assessment["approved"]:
            raise HTTPException(status_code=400, detail=risk_assessment["reason"])

        result = trader_bot.execute_trade(
            trade_data["symbol"],
            trade_data["action"],
            trade_data["volume"],
            trade_data["entry_price"],
            trade_data["stop_loss"],
            trade_data.get("take_profit", 0.0)
        )

        if result is None:
            raise HTTPException(status_code=500, detail="Trade execution failed")

        return JSONResponse(
            status_code=200,
            content={"message": "Trade executed successfully", "result": result}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/close-position")
async def close_position(position_data: Dict):
    """Close an open position."""
    try:
        if "symbol" not in position_data:
            raise HTTPException(status_code=400, detail="Symbol is required")

        result = trader_bot.close_position(position_data["symbol"])
        if not result:
            raise HTTPException(status_code=500, detail="Failed to close position")

        return JSONResponse(
            status_code=200,
            content={"message": "Position closed successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis", response_model=Dict)
async def get_analysis(symbol: str = "EURUSD", timeframe: str = "H1"):
    """Get market analysis."""
    try:
        analysis = analyst_agent.analyze_market_conditions(symbol, timeframe)
        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze market")

        signals = analyst_agent.generate_signals(symbol, timeframe)
        return {
            "market_conditions": analysis,
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk", response_model=Dict)
async def get_risk():
    """Get current risk assessment."""
    try:
        risk = risk_guardian.monitor_positions()
        return risk
    except Exception as e:
        logger.error(f"Error getting risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.API['host'],
        port=Config.API['port'],
        reload=Config.API['debug']
    ) 