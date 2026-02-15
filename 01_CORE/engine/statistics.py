import numpy as np

class TradingStatistics:
    """
    Engine para análise estatística de trading.
    Baseado em métricas de finanças quantitativas.
    """

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """
        Calcula o Sharpe Ratio.
        """
        if not returns or len(returns) < 2:
            return 0
        
        avg_return = np.mean(returns)
        std_dev = np.std(returns)
        
        if std_dev == 0:
            return 0
            
        sharpe = (avg_return - (risk_free_rate / 252)) / std_dev
        # Anualizar (assumindo retornos diários)
        return round(sharpe * np.sqrt(252), 2)

    @staticmethod
    def calculate_max_drawdown(equity_curve):
        """
        Calcula o Drawdown Máximo.
        """
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak != 0 else 0
            if dd > max_dd:
                max_dd = dd
                
        return round(max_dd * 100, 2)

    @staticmethod
    def calculate_win_rate(trades):
        """
        Calcula a Taxa de Acerto.
        """
        if not trades:
            return 0
        
        wins = sum(1 for t in trades if t > 0)
        return round((wins / len(trades)) * 100, 2)

    @staticmethod
    def calculate_p_value(returns):
        """
        Calcula o P-Value simplificado (t-test contra 0).
        H0: A estratégia não tem borda (média = 0)
        """
        from scipy import stats
        if len(returns) < 2:
            return 1.0
            
        t_stat, p_val = stats.ttest_1samp(returns, 0)
        return round(p_val, 4)
