from typing import Optional, Dict, List
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from ..core.database import Database

class RiskGuardian:
    """Risk management agent."""
    
    def __init__(self, database: Database, max_risk_per_trade: float = 0.02,
                 max_daily_risk: float = 0.05, max_drawdown: float = 0.1):
        """Initialize RiskGuardian with risk parameters."""
        self.db = database
        self.logger = logging.getLogger(__name__)
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_risk = max_daily_risk
        self.max_drawdown = max_drawdown
        
    def assess_trade_risk(self, symbol: str, action: str, volume: float,
                         entry_price: float, stop_loss: float) -> Dict:
        """Assess risk for a potential trade."""
        try:
            # Calculate position risk
            position_risk = abs(stop_loss - entry_price) * volume
            account_balance = self._get_account_balance()
            
            if account_balance <= 0:
                return {'approved': False, 'reason': 'Insufficient account balance'}
                
            # Calculate risk metrics
            risk_percentage = position_risk / account_balance
            daily_risk = self._calculate_daily_risk()
            drawdown = self._calculate_current_drawdown()
            
            # Risk assessment
            if risk_percentage > self.max_risk_per_trade:
                return {
                    'approved': False,
                    'reason': f'Risk per trade ({risk_percentage:.2%}) exceeds maximum ({self.max_risk_per_trade:.2%})'
                }
                
            if daily_risk + risk_percentage > self.max_daily_risk:
                return {
                    'approved': False,
                    'reason': f'Daily risk ({daily_risk + risk_percentage:.2%}) would exceed maximum ({self.max_daily_risk:.2%})'
                }
                
            if drawdown > self.max_drawdown:
                return {
                    'approved': False,
                    'reason': f'Current drawdown ({drawdown:.2%}) exceeds maximum ({self.max_drawdown:.2%})'
                }
                
            # Additional risk factors
            volatility = self._calculate_volatility(symbol)
            correlation = self._calculate_correlation(symbol)
            
            return {
                'approved': True,
                'risk_metrics': {
                    'position_risk': position_risk,
                    'risk_percentage': risk_percentage,
                    'daily_risk': daily_risk,
                    'drawdown': drawdown,
                    'volatility': volatility,
                    'correlation': correlation
                }
            }
        except Exception as e:
            self.logger.error(f"Error assessing trade risk: {str(e)}")
            return {'approved': False, 'reason': 'Error in risk assessment'}
            
    def monitor_positions(self) -> Dict:
        """Monitor and assess risk of open positions."""
        try:
            # Get open positions
            positions = self.db.get_transactions({'status': 'open'})
            if not positions:
                return {'status': 'safe', 'risk_level': 'low'}
                
            # Calculate position metrics
            total_exposure = sum(p.risk for p in positions)
            account_balance = self._get_account_balance()
            exposure_percentage = total_exposure / account_balance if account_balance > 0 else 0
            
            # Calculate portfolio metrics
            returns = [p.profit for p in positions]
            volatility = np.std(returns) if returns else 0
            correlation = self._calculate_portfolio_correlation(positions)
            
            # Risk assessment
            risk_level = self._determine_risk_level(
                exposure_percentage,
                volatility,
                correlation
            )
            
            return {
                'status': 'safe' if risk_level == 'low' else 'warning' if risk_level == 'medium' else 'danger',
                'risk_level': risk_level,
                'metrics': {
                    'total_exposure': total_exposure,
                    'exposure_percentage': exposure_percentage,
                    'volatility': volatility,
                    'correlation': correlation
                }
            }
        except Exception as e:
            self.logger.error(f"Error monitoring positions: {str(e)}")
            return {'status': 'error', 'risk_level': 'unknown'}
            
    def calculate_position_size(self, symbol: str, entry_price: float,
                              stop_loss: float, risk_amount: float) -> float:
        """Calculate appropriate position size based on risk parameters."""
        try:
            account_balance = self._get_account_balance()
            if account_balance <= 0:
                return 0.0
                
            # Calculate risk per unit
            risk_per_unit = abs(stop_loss - entry_price)
            if risk_per_unit <= 0:
                return 0.0
                
            # Calculate position size
            position_size = risk_amount / risk_per_unit
            
            # Apply position size limits
            max_position = account_balance * self.max_risk_per_trade / risk_per_unit
            position_size = min(position_size, max_position)
            
            return position_size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
            
    def _get_account_balance(self) -> float:
        """Get current account balance."""
        try:
            account = self.db.get_account_info()
            return account.balance if account else 0.0
        except Exception as e:
            self.logger.error(f"Error getting account balance: {str(e)}")
            return 0.0
            
    def _calculate_daily_risk(self) -> float:
        """Calculate current daily risk exposure."""
        try:
            today = datetime.now().date()
            today_trades = self.db.get_transactions({
                'timestamp': {'$gte': datetime.combine(today, datetime.min.time())}
            })
            
            if not today_trades:
                return 0.0
                
            return sum(t.risk for t in today_trades) / self._get_account_balance()
        except Exception as e:
            self.logger.error(f"Error calculating daily risk: {str(e)}")
            return 0.0
            
    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown."""
        try:
            account = self.db.get_account_info()
            if not account:
                return 0.0
                
            peak_balance = self._get_peak_balance()
            if peak_balance <= 0:
                return 0.0
                
            return (peak_balance - account.balance) / peak_balance
        except Exception as e:
            self.logger.error(f"Error calculating drawdown: {str(e)}")
            return 0.0
            
    def _get_peak_balance(self) -> float:
        """Get peak account balance."""
        try:
            transactions = self.db.get_transactions()
            if not transactions:
                return self._get_account_balance()
                
            balances = []
            current_balance = self._get_account_balance()
            
            for t in transactions:
                current_balance += t.profit
                balances.append(current_balance)
                
            return max(balances) if balances else current_balance
        except Exception as e:
            self.logger.error(f"Error getting peak balance: {str(e)}")
            return self._get_account_balance()
            
    def _calculate_volatility(self, symbol: str) -> float:
        """Calculate symbol volatility."""
        try:
            market_data = self.db.get_market_data(symbol, 'D1', 30)
            if not market_data:
                return 0.0
                
            returns = [m.close_price / m.open_price - 1 for m in market_data]
            return np.std(returns) * np.sqrt(252)  # Annualized volatility
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.0
            
    def _calculate_correlation(self, symbol: str) -> float:
        """Calculate correlation with other positions."""
        try:
            positions = self.db.get_transactions({'status': 'open'})
            if not positions:
                return 0.0
                
            # Get returns for all positions
            returns = {}
            for p in positions:
                market_data = self.db.get_market_data(p.symbol, 'D1', 30)
                if market_data:
                    returns[p.symbol] = [m.close_price / m.open_price - 1 for m in market_data]
                    
            if not returns:
                return 0.0
                
            # Calculate average correlation
            correlations = []
            for other_symbol in returns:
                if other_symbol != symbol:
                    corr = np.corrcoef(returns[symbol], returns[other_symbol])[0, 1]
                    correlations.append(corr)
                    
            return np.mean(correlations) if correlations else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {str(e)}")
            return 0.0
            
    def _calculate_portfolio_correlation(self, positions: List) -> float:
        """Calculate portfolio correlation."""
        try:
            if len(positions) < 2:
                return 0.0
                
            # Get returns for all positions
            returns = {}
            for p in positions:
                market_data = self.db.get_market_data(p.symbol, 'D1', 30)
                if market_data:
                    returns[p.symbol] = [m.close_price / m.open_price - 1 for m in market_data]
                    
            if len(returns) < 2:
                return 0.0
                
            # Calculate average correlation
            correlations = []
            symbols = list(returns.keys())
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    corr = np.corrcoef(returns[symbols[i]], returns[symbols[j]])[0, 1]
                    correlations.append(corr)
                    
            return np.mean(correlations) if correlations else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating portfolio correlation: {str(e)}")
            return 0.0
            
    def _determine_risk_level(self, exposure: float, volatility: float,
                            correlation: float) -> str:
        """Determine overall risk level."""
        risk_score = 0
        
        # Exposure risk
        if exposure > self.max_risk_per_trade * 2:
            risk_score += 2
        elif exposure > self.max_risk_per_trade:
            risk_score += 1
            
        # Volatility risk
        if volatility > 0.3:  # High volatility
            risk_score += 2
        elif volatility > 0.2:  # Medium volatility
            risk_score += 1
            
        # Correlation risk
        if correlation > 0.7:  # High correlation
            risk_score += 2
        elif correlation > 0.5:  # Medium correlation
            risk_score += 1
            
        # Determine risk level
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        return 'low' 