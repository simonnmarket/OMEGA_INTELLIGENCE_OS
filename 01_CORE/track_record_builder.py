import os
import csv
from datetime import datetime
import pandas as pd

class TrackRecordBuilder:
    """
    O ÚNICO código que importa agora para validação Institucional.
    Registra Estado -> Ação -> Recompensa (PnL) para o verdadeiro RL.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.start_date = datetime.now()
        self.trades = []
        self.initial_capital = initial_capital
        self.equity_curve = [initial_capital]
        self.log_file = f"01_CORE/track_record_audited_{self.start_date.strftime('%Y%m%d')}.csv"
        
        # Inicializa o arquivo de auditoria
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Ticket", "Symbol", "Action", "Entry_Time", "Entry_Price", "SL", "TP", "Close_Time", "Close_Price", "PnL", "Accumulated_Equity"])

    def registrar_trade(self, ticket: str, symbol: str, action: str, entry_time: str, entry_price: float, sl: float, tp: float, close_time: str, close_price: float, pnl: float):
        """Registra cada trade encerrado e atualiza a curva de capital"""
        new_equity = self.equity_curve[-1] + pnl
        self.equity_curve.append(new_equity)
        
        trade_data = [ticket, symbol, action, entry_time, entry_price, sl, tp, close_time, close_price, pnl, new_equity]
        self.trades.append(trade_data)
        
        with open(self.log_file, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(trade_data)
            
        print(f"[AUDIT] Trade {ticket} fechado. PnL: ${pnl:.2f} | Equity: ${new_equity:.2f}")

    def calcular_win_rate(self):
        if not self.trades: return 0.0
        wins = sum(1 for t in self.trades if t[9] > 0)
        return (wins / len(self.trades)) * 100

    def calcular_max_drawdown(self):
        if len(self.equity_curve) < 2: return 0.0
        
        peak = self.equity_curve[0]
        max_dd = 0.0
        
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak
            if dd > max_dd:
                max_dd = dd
                
        return max_dd * 100

    def calcular_sharpe(self):
        # Simplificacao estatística para o relatório inicial (assumindo risk-free = 0)
        if len(self.trades) < 2: return 0.0
        
        df = pd.DataFrame(self.trades, columns=["Ticket", "Symbol", "Action", "Entry_Time", "Entry_Price", "SL", "TP", "Close_Time", "Close_Price", "PnL", "Equity"])
        returns = df["PnL"] / self.initial_capital
        
        if returns.std() == 0: return 0.0
        
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5) # Annualized
        return round(sharpe, 2)

    def gerar_relatorio_semanal(self):
        """Produz relatorio auditavel para investidor"""
        dias_operacionais = max(1, (datetime.now() - self.start_date).days)
        
        relatorio = {
            "dias_operacionais": dias_operacionais,
            "total_trades": len(self.trades),
            "win_rate_pct": f"{self.calcular_win_rate():.2f}%",
            "pnl_total_usd": self.equity_curve[-1] - self.initial_capital,
            "sharpe_ratio_estimado": self.calcular_sharpe(),
            "max_drawdown_pct": f"{self.calcular_max_drawdown():.2f}%",
            "trades_por_dia": round(len(self.trades) / dias_operacionais, 2)
        }
        
        print("\n" + "="*50)
        print(" OMEGA OS - RELATÓRIO DE TRACK RECORD (AUDITORIA)")
        print("="*50)
        for k, v in relatorio.items():
            print(f"{k.upper()}: {v}")
        print("="*50 + "\n")
        
        return relatorio

if __name__ == "__main__":
    # Teste unitario do builder
    builder = TrackRecordBuilder(initial_capital=10000.0)
    print("Track Record Builder Inicializado. Cofre criado.")
