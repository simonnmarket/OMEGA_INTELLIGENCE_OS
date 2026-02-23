//+------------------------------------------------------------------+
//|                                             DefenseOrchestrator.mqh |
//| Camada de Orquestração de Defesa Institucional - Nível BlackRock  |
//+------------------------------------------------------------------+
#ifndef __DEFENSE_ORCHESTRATOR_MQH__
#define __DEFENSE_ORCHESTRATOR_MQH__

#include <Trade\Trade.mqh>
#include <Modules\DefenseAgent.mqh>
#include <Logs\AuditManager.mqh>

CTrade trade;

//--- Configurações táticas
input bool EnableAutoTrade     = true;
input bool EnableAuditLogging  = true;
input bool EnableAlerting      = true;
input double RiskPerTrade      = 0.01;
input double SlippagePips      = 2;
input int MaxOpenTrades        = 3;

//+------------------------------------------------------------------+
//| Função para execução de ações com base no status de defesa       |
//+------------------------------------------------------------------+
void EvaluateDefenseAndExecute(const int barIndex,
                               const double &close[],
                               const double &high[],
                               const double &low[],
                               const long &volume[])
{
   DefenseStatus ds = GetDefenseStatus(barIndex, close, high, low, volume);
   string symbol = _Symbol;
   double price = close[barIndex];

   //--- Log institucional
   if (EnableAuditLogging)
   {
      AuditLog("DefenseStatus", symbol,
               StringFormat("Status: %d | Hurst: %.2f | Liquidity: %.2f | Price: %.5f | DefenseLine: %.5f",
                            ds.signal, ds.hurst, ds.liquidity, price, ds.defenseLine));
   }

   //--- Alertas visuais / sonoros
   if (EnableAlerting && ds.signal != DEFENSE_NONE)
   {
      string msg = StringFormat("%s ⚔️ DEFENSE SIGNAL: %s\nPrice: %.5f | Hurst: %.2f | Liquidity: %.2f",
                                symbol,
                                EnumToString(ds.signal), price, ds.hurst, ds.liquidity);
      Alert(msg);
      SendNotification(msg);
   }

   //--- Execução automática
   if (EnableAutoTrade && PositionsTotal() < MaxOpenTrades)
   {
      double lotSize = CalculateLotSize(RiskPerTrade);
      if (ds.signal == DEFENSE_BUY_ZONE && CheckNoOpenOrder(POSITION_TYPE_BUY))
      {
         trade.Buy(lotSize, symbol, price, price - 1.5 * SymbolInfoDouble(symbol, SYMBOL_POINT),
                   price + 2.0 * SymbolInfoDouble(symbol, SYMBOL_POINT), NULL);
      }
      else if (ds.signal == DEFENSE_SELL_ZONE && CheckNoOpenOrder(POSITION_TYPE_SELL))
      {
         trade.Sell(lotSize, symbol, price, price + 1.5 * SymbolInfoDouble(symbol, SYMBOL_POINT),
                    price - 2.0 * SymbolInfoDouble(symbol, SYMBOL_POINT), NULL);
      }
   }
}

//+------------------------------------------------------------------+
//| Cálculo de lote baseado em risco por operação                   |
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
      ulong ticket = PositionGetTicket(i);
      if (PositionGetInteger(POSITION_TYPE) == type)
         return false;
   }
   return true;
}

#endif // __DEFENSE_ORCHESTRATOR_MQH__
