//+------------------------------------------------------------------+
//|                  ACCOUNT INFO MODULE (EMBEDDED)                  |
//+------------------------------------------------------------------+
namespace AccountInfo {
    // Simula as funções padrão do MQL5
    double AccountBalance() {
        return AccountInfoDouble(ACCOUNT_BALANCE);
    }
    
    double AccountEquity() {
        return AccountInfoDouble(ACCOUNT_EQUITY);
    }
    
    double AccountFreeMargin() {
        return AccountInfoDouble(ACCOUNT_MARGIN_FREE);
    }
};
