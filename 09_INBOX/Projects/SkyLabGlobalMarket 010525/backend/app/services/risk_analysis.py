import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class RiskAnalyzer:
    def __init__(self, returns: pd.Series, risk_free_rate: float = 0.02):
        """
        Initialize the RiskAnalyzer with historical returns.
        
        Args:
            returns (pd.Series): Series of historical returns
            risk_free_rate (float): Annual risk-free rate (default: 2%)
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        
    def calculate_sharpe_ratio(self, period: str = 'annual') -> float:
        """
        Calculate the Sharpe Ratio.
        
        Args:
            period (str): 'annual' or 'daily'
            
        Returns:
            float: Sharpe Ratio
        """
        excess_returns = self.returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        if period == 'annual':
            return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return excess_returns.mean() / excess_returns.std()
    
    def calculate_volatility(self, period: str = 'annual') -> float:
        """
        Calculate the volatility (standard deviation of returns).
        
        Args:
            period (str): 'annual' or 'daily'
            
        Returns:
            float: Volatility
        """
        if period == 'annual':
            return self.returns.std() * np.sqrt(252)
        return self.returns.std()
    
    def calculate_beta(self, market_returns: pd.Series) -> float:
        """
        Calculate the Beta coefficient.
        
        Args:
            market_returns (pd.Series): Series of market returns
            
        Returns:
            float: Beta coefficient
        """
        covariance = np.cov(self.returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance
    
    def calculate_var(self, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            confidence_level (float): Confidence level (default: 95%)
            
        Returns:
            float: Value at Risk
        """
        return np.percentile(self.returns, (1 - confidence_level) * 100)
    
    def calculate_max_drawdown(self) -> float:
        """
        Calculate the maximum drawdown.
        
        Returns:
            float: Maximum drawdown
        """
        cumulative_returns = (1 + self.returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        return drawdowns.min()
    
    def calculate_correlation(self, other_returns: pd.Series) -> float:
        """
        Calculate correlation with another asset.
        
        Args:
            other_returns (pd.Series): Series of returns for another asset
            
        Returns:
            float: Correlation coefficient
        """
        return self.returns.corr(other_returns)
    
    def generate_risk_report(self, market_returns: Optional[pd.Series] = None) -> Dict:
        """
        Generate a comprehensive risk report.
        
        Args:
            market_returns (pd.Series, optional): Series of market returns for beta calculation
            
        Returns:
            Dict: Dictionary containing all risk metrics
        """
        report = {
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'volatility': self.calculate_volatility(),
            'value_at_risk_95': self.calculate_var(0.95),
            'max_drawdown': self.calculate_max_drawdown(),
            'correlation_with_market': None
        }
        
        if market_returns is not None:
            report['beta'] = self.calculate_beta(market_returns)
            report['correlation_with_market'] = self.calculate_correlation(market_returns)
            
        return report
    
    def check_risk_alerts(self, thresholds: Dict) -> Dict:
        """
        Check for risk alerts based on thresholds.
        
        Args:
            thresholds (Dict): Dictionary of threshold values
            
        Returns:
            Dict: Dictionary of triggered alerts
        """
        alerts = {}
        
        # Check volatility alert
        volatility = self.calculate_volatility()
        if volatility > thresholds.get('volatility_threshold', 0.3):
            alerts['high_volatility'] = {
                'value': volatility,
                'threshold': thresholds['volatility_threshold']
            }
            
        # Check drawdown alert
        max_drawdown = self.calculate_max_drawdown()
        if abs(max_drawdown) > thresholds.get('drawdown_threshold', 0.2):
            alerts['significant_drawdown'] = {
                'value': max_drawdown,
                'threshold': thresholds['drawdown_threshold']
            }
            
        # Check VaR alert
        var = self.calculate_var()
        if abs(var) > thresholds.get('var_threshold', 0.05):
            alerts['high_var'] = {
                'value': var,
                'threshold': thresholds['var_threshold']
            }
            
        return alerts 