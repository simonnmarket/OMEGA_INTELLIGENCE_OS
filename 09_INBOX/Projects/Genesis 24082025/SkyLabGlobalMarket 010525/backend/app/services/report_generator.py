from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import json
from jinja2 import Template

class ReportGenerator:
    def __init__(self, portfolio_id: int, db_session):
        self.portfolio_id = portfolio_id
        self.db_session = db_session
        
    def generate_performance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate a performance report for the portfolio.
        """
        # Get portfolio data
        portfolio = self.db_session.query(Portfolio).filter_by(id=self.portfolio_id).first()
        trades = self.db_session.query(Trade).filter(
            Trade.portfolio_id == self.portfolio_id,
            Trade.timestamp >= start_date,
            Trade.timestamp <= end_date
        ).all()
        
        # Calculate performance metrics
        returns = self._calculate_returns(trades)
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        
        # Generate report content
        content = {
            "portfolio_name": portfolio.name,
            "period": f"{start_date.date()} to {end_date.date()}",
            "total_return": f"{total_return:.2%}",
            "annualized_return": f"{annualized_return:.2%}",
            "trades": len(trades),
            "trades_by_symbol": self._group_trades_by_symbol(trades),
            "daily_returns": returns.tolist()
        }
        
        return {
            "report_type": "performance",
            "title": f"Performance Report - {portfolio.name}",
            "content": json.dumps(content),
            "parameters": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    def generate_risk_report(self, risk_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a risk report based on risk metrics.
        """
        content = {
            "sharpe_ratio": risk_metrics.get("sharpe_ratio", 0),
            "volatility": risk_metrics.get("volatility", 0),
            "beta": risk_metrics.get("beta", 0),
            "value_at_risk_95": risk_metrics.get("value_at_risk_95", 0),
            "max_drawdown": risk_metrics.get("max_drawdown", 0),
            "correlation_with_market": risk_metrics.get("correlation_with_market", 0),
            "alerts": risk_metrics.get("alerts", {})
        }
        
        return {
            "report_type": "risk",
            "title": "Risk Analysis Report",
            "content": json.dumps(content),
            "parameters": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def generate_trading_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate a trading activity report.
        """
        trades = self.db_session.query(Trade).filter(
            Trade.portfolio_id == self.portfolio_id,
            Trade.timestamp >= start_date,
            Trade.timestamp <= end_date
        ).all()
        
        # Calculate trading metrics
        total_volume = sum(trade.quantity for trade in trades)
        total_value = sum(trade.quantity * trade.price for trade in trades)
        trades_by_type = self._group_trades_by_type(trades)
        
        content = {
            "total_trades": len(trades),
            "total_volume": total_volume,
            "total_value": total_value,
            "trades_by_type": trades_by_type,
            "trades_by_symbol": self._group_trades_by_symbol(trades),
            "trades": [trade.to_dict() for trade in trades]
        }
        
        return {
            "report_type": "trading",
            "title": "Trading Activity Report",
            "content": json.dumps(content),
            "parameters": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    def _calculate_returns(self, trades: list) -> pd.Series:
        """
        Calculate daily returns from trades.
        """
        # Group trades by date and calculate daily returns
        trades_df = pd.DataFrame([trade.to_dict() for trade in trades])
        trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
        daily_returns = trades_df.groupby('date').apply(
            lambda x: (x['quantity'] * x['price']).sum()
        ).pct_change()
        
        return daily_returns
    
    def _group_trades_by_symbol(self, trades: list) -> Dict[str, int]:
        """
        Group trades by symbol and count.
        """
        symbol_counts = {}
        for trade in trades:
            symbol_counts[trade.symbol] = symbol_counts.get(trade.symbol, 0) + 1
        return symbol_counts
    
    def _group_trades_by_type(self, trades: list) -> Dict[str, int]:
        """
        Group trades by type and count.
        """
        type_counts = {}
        for trade in trades:
            type_counts[trade.type] = type_counts.get(trade.type, 0) + 1
        return type_counts
    
    def render_report(self, report_type: str, content: Dict[str, Any]) -> str:
        """
        Render report content using Jinja2 templates.
        """
        template_path = f"templates/reports/{report_type}_report.html"
        with open(template_path, 'r') as f:
            template = Template(f.read())
        
        return template.render(**content) 