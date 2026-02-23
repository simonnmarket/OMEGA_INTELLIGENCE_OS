//+------------------------------------------------------------------+
//|                                                RiskAgent.mqh     |
//|                Parte do projeto Numeia EA - SKY LAB              |
//+------------------------------------------------------------------+
#pragma once
#include "../Config/GlobalConfig.mqh"
#include "../Config/RiskConfig.mqh"
#include "../Utils/Log.mqh"
#include "../Core/types.mqh"

class RiskAgent {
private:
   double maxDrawdown;
   double dailyLossLimit;
   double accountInitialBalance;
   datetime tradingDayStart;

public:
   RiskAgent() {
      accountInitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      maxDrawdown           = RISK_MAX_DRAWDOWN;
      dailyLossLimit        = RISK_DAILY_LOSS_LIMIT;
      tradingDayStart       = TimeCurrent();
   }

   bool CheckRiskExposure() {
      double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      double drawdown      = (accountInitialBalance - currentEquity) / accountInitialBalance;

      if(drawdown >= maxDrawdown) {
         Log::Warn("Drawdown máximo atingido: "+DoubleToString(drawdown * 100, 2)+"%");
         return false;
      }

      double dayProfit = CalculateDailyProfit();
      if(dayProfit < -dailyLossLimit) {
         Log::Warn("Limite de perda diária atingido: "+DoubleToString(dayProfit, 2));
         return false;
      }

      return true;
   }

   double CalculateDailyProfit() {
      HistorySelect(tradingDayStart, TimeCurrent());
      double profitToday = 0.0;

      for(int i = HistoryDealsTotal() - 1; i >= 0; i--) {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0 && HistoryDealGetInteger(ticket, DEAL_TIME) >= tradingDayStart) {
            profitToday += HistoryDealGetDouble(ticket, DEAL_PROFIT);
         }
      }

      return profitToday;
   }

   void ResetDayStart() {
      tradingDayStart = TimeCurrent();
      accountInitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   }
};
