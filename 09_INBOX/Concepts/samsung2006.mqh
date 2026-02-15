// MetaTrader 5 (MT5) Expert Advisor Example Code
#include <Trade\Trade.mqh>

input int rsi_period = 14;          // RSI Period
input double lot_size = 0.1;        // Lot Size
input double risk_percentage = 1;  // Risk Percentage per Trade
input double take_profit = 2;       // Take-profit in percentage
input double stop_loss = 1;         // Stop-loss in percentage

CTrade trade;

double CalculateLotSize(double risk, double stop_loss_points) {
    double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = account_balance * (risk / 100);
    double lot = NormalizeDouble(risk_amount / stop_loss_points, 2);
    return lot;
}

int OnInit() {
    Print("RSI Strategy EA Initialized.");
    return(INIT_SUCCEEDED);
}

void OnTick() {
    double rsi = iRSI(_Symbol, PERIOD_CURRENT, rsi_period, PRICE_CLOSE, 0);

    if (rsi < 30) {
        double entry_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl = entry_price - (entry_price * stop_loss / 100);
        double tp = entry_price + (entry_price * take_profit / 100);
        double stop_loss_points = entry_price - sl;
        double lot = CalculateLotSize(risk_percentage, stop_loss_points);

        if (trade.PositionTotal() == 0) {
            if (trade.Buy(lot, _Symbol, entry_price, sl, tp)) {
                Print("Buy Order Placed at ", entry_price, " | TP: ", tp, " | SL: ", sl);
            } else {
                Print("Buy Order Failed: ", GetLastError());
            }
        }
    }
}
