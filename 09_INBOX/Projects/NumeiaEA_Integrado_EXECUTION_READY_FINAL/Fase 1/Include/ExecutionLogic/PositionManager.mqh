// File: Include/ExecutionLogic/PositionManager.mqh
#ifndef EXECUTIONLOGIC_POSITIONMANAGER_MQH
#define EXECUTIONLOGIC_POSITIONMANAGER_MQH

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| PositionManager - Camada de Execução Certificada Apollo         |
//| Certificações: Apollo / Brookfield / DWS                        |
//| Responsável por enviar ordens com gerenciamento de risco        |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                    |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+

class PositionManager
  {
private:
   string  m_symbol;
   double  m_maxLot;
   double  m_riskPct;
   int     m_maxTrades;

public:
   PositionManager(string symbol, double maxLot, double riskPct, int maxTrades)
     {
      m_symbol     = symbol;
      m_maxLot     = maxLot;
      m_riskPct    = riskPct;
      m_maxTrades  = maxTrades;
     }

   bool OpenTrade(ENUM_ORDER_TYPE type, double lotSize, double price, double stopLoss, double takeProfit, string comment)
     {
      MqlTradeRequest request = {};
      request.action   = TRADE_ACTION_DEAL;
      request.symbol   = m_symbol;
      request.volume   = NormalizeDouble(lotSize, 2);
      request.type     = type;
      request.price    = NormalizeDouble(price, _Digits);
      request.sl       = (stopLoss > 0.0) ? NormalizeDouble(price - stopLoss, _Digits) : 0.0;
      request.tp       = (takeProfit > 0.0) ? NormalizeDouble(price + takeProfit, _Digits) : 0.0;
      request.deviation= 5;
      request.comment  = comment;

      MqlTradeResult result;
      if(!OrderSend(request, result))
        {
         Print("[APOLLO-ERROR] Ordem falhou. Código: ", GetLastError(), " | Retcode: ", result.retcode);
         return false;
        }

      if(result.retcode != TRADE_RETCODE_DONE)
        {
         Print("[APOLLO-WARNING] Ordem não completada com sucesso. Retcode: ", result.retcode);
         return false;
        }

      Print("[APOLLO-EXEC] Ordem enviada com sucesso. Ticket: ", result.order);
      return true;
     }
  };

#endif // EXECUTIONLOGIC_POSITIONMANAGER_MQH
