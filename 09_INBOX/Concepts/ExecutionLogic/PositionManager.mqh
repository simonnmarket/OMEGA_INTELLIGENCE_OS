
//+------------------------------------------------------------------+
//| PositionManager.mqh - ExecutionLogic                            |
//| Atualizado para suportar construtor personalizado               |
//+------------------------------------------------------------------+
#pragma once
#include <Trade/Trade.mqh>

class PositionManager {
private:
    string m_name;
    double m_lotMin;
    double m_lotMax;
    int    m_magic;

public:
    PositionManager(string name = "PM", double lotMin = 0.01, double lotMax = 100.0, int magic = 123456) {
        m_name   = name;
        m_lotMin = lotMin;
        m_lotMax = lotMax;
        m_magic  = magic;
    }

    bool OpenTrade(ENUM_ORDER_TYPE type, double lotSize, double price, double stopLoss, double takeProfit, string comment) {
        MqlTradeRequest request = {0};
        MqlTradeResult result;

        request.action   = TRADE_ACTION_DEAL;
        request.symbol   = _Symbol;
        request.volume   = NormalizeDouble(MathMax(m_lotMin, MathMin(lotSize, m_lotMax)), 2);
        request.magic    = m_magic;
        request.type     = type;
        request.price    = NormalizeDouble(price, _Digits);
        request.sl       = (stopLoss > 0) ? NormalizeDouble(price + (type == ORDER_TYPE_BUY ? -stopLoss : stopLoss), _Digits) : 0.0;
        request.tp       = (takeProfit > 0) ? NormalizeDouble(price + (type == ORDER_TYPE_BUY ? takeProfit : -takeProfit), _Digits) : 0.0;
        request.deviation = 10;
        request.comment   = comment;

        if (!OrderSend(request, result)) {
            Print("[PositionManager-ERROR] Falha ao enviar ordem: ", GetLastError(), " | Retcode: ", result.retcode);
            return false;
        }

        if (result.retcode != TRADE_RETCODE_DONE) {
            Print("[PositionManager-FAIL] Retcode: ", result.retcode, " | Ordem não executada corretamente.");
            return false;
        }

        Print("[PositionManager-OK] Ordem executada com sucesso | Ticket: ", result.order);
        return true;
    }
};
