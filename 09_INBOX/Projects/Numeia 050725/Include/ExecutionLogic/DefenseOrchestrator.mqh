//+------------------------------------------------------------------+
//| Include/ExecutionLogic/DefenseOrchestrator.mqh                   |
//| Camada de Orquestração de Defesa Institucional – Nível BlackRock|
//| Atualizado para integração com DefenseDashboard e IA            |
//+------------------------------------------------------------------+
#ifndef __EXECUTIONLOGIC_DEFENSE_ORCHESTRATOR_MQH__
#define __EXECUTIONLOGIC_DEFENSE_ORCHESTRATOR_MQH__

#include <Trade/Trade.mqh>
#include <Modules/DefenseAgent.mqh>
#include <Logs/AuditManager.mqh>
#include <Visuals/DefenseDashboard.mq5>   // Acesso à função GetLastDefenseSignal()

CTrade trade;

//--- Configurações táticas
input bool   EnableAutoTrade     = true;
input bool   EnableAuditLogging  = true;
input bool   EnableAlerting      = true;
input double RiskPerTrade        = 0.01;
input double SlippagePips        = 2;
input int    MaxOpenTrades       = 3;

//+------------------------------------------------------------------+
//| Função principal de avaliação e execução                         |
//+------------------------------------------------------------------+
void EvaluateDefenseSignalAndExecute()
{
   string symbol = _Symbol;
   int lastSignal = GetLastDefenseSignal(); // ← leitura direta da dashboard
   double price = SymbolInfoDouble(symbol, SYMBOL_BID);

   //--- Log institucional
   if (EnableAuditLogging)
   {
      AuditLog("DefenseOrchestrator", symbol,
               StringFormat("Último sinal detectado: %d | Preço Atual: %.5f", lastSignal, price));
   }

   //--- Alertas visuais / sonoros
   if (EnableAlerting && lastSignal != DEFENSE_NONE)
   {
      string msg = StringFormat("%s ⚔️ SINAL DE DEFESA: %s\nPreço: %.5f",
                                symbol, EnumToString(lastSignal), price);
      Alert(msg);
      SendNotification(msg);
   }

   //--- Execução automática
   if (EnableAutoTrade && PositionsTotal() < MaxOpenTrades)
   {
      double lotSize = CalculateLotSize(RiskPerTrade);

      if (lastSignal == DEFENSE_BUY_ZONE && CheckNoOpenOrder(POSITION_TYPE_BUY))
      {
         trade.Buy(lotSize, symbol, price,
                   price - 1.5 * _Point,  // SL
                   price + 2.0 * _Point,  // TP
                   NULL);
      }
      else if (lastSignal == DEFENSE_SELL_ZONE && CheckNoOpenOrder(POSITION_TYPE_SELL))
      {
         trade.Sell(lotSize, symbol, price,
                    price + 1.5 * _Point,  // SL
                    price - 2.0 * _Point,  // TP
                    NULL);
      }
   }
}

//+------------------------------------------------------------------+
//| Cálculo de lote baseado em risco por operação                    |
//+------------------------------------------------------------------+
double CalculateLotSize(double riskPercent)
{
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double atr = iATR(NULL, 0, 14, 0);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double stopDistance = atr * 1.5;
   double valuePerPoint = tickValue / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double riskAmount = balance * riskPercent;
   double lot = NormalizeDouble(riskAmount / (stopDistance * valuePerPoint), 2);
   return lot;
}

//+------------------------------------------------------------------+
//| Verifica se já há ordem aberta do mesmo tipo                    |
//+------------------------------------------------------------------+
bool CheckNoOpenOrder(int type)
{
   for (int i = 0; i < PositionsTotal(); i++)
   {
      if (PositionGetInteger(POSITION_TYPE) == type)
         return false;
   }
   return true;
}

#endif // __EXECUTIONLOGIC_DEFENSE_ORCHESTRATOR_MQH__
