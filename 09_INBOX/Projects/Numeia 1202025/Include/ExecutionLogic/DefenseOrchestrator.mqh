//+------------------------------------------------------------------+
//| DefenseOrchestrator.mqh - Orquestrador de Defesa Institucional  |
//| Projeto: EA Numeia - Sistema de Proteção Avançada               |
//+------------------------------------------------------------------+
#ifndef __DEFENSE_ORCHESTRATOR_MQH__
#define __DEFENSE_ORCHESTRATOR_MQH__

#include <Trade/Trade.mqh>
#include "../../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Constantes de Defesa                                             |
//+------------------------------------------------------------------+
#define DEFENSE_NONE      0
#define DEFENSE_BUY_ZONE  1
#define DEFENSE_SELL_ZONE 2

class DefenseOrchestrator {
private:
   CTrade m_trade;

public:
   DefenseOrchestrator() {
      m_trade.SetDeviationInPoints(20);
   }

   bool Init() {
      AuditLog("[DefenseOrchestrator] Inicializando orquestrador de defesa...", LOG_LEVEL_INFO);
      return true;
   }

   void OnDeinit() {
      AuditLog("[DefenseOrchestrator] Encerrando orquestrador de defesa...", LOG_LEVEL_INFO);
   }

   void OrchestrateDefense(string symbol) {
      AuditLog("[DefenseOrchestrator] Executando defesa para " + symbol, LOG_LEVEL_INFO);
   }

   int GetLastDefenseSignal() {
      // Implementação simplificada - retorna DEFENSE_NONE por padrão
      return DEFENSE_NONE;
   }

   // Método público para acessar trade
   CTrade* GetTrade() {
      return &m_trade;
   }
};

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
   DefenseOrchestrator defense;
   int lastSignal = defense.GetLastDefenseSignal();
   double price = SymbolInfoDouble(symbol, SYMBOL_BID);

   //--- Log institucional
   if (EnableAuditLogging)
   {
      AuditLog("[DefenseOrchestrator] Último sinal detectado: " + IntegerToString(lastSignal) + " | Preço Atual: " + DoubleToString(price, 5), LOG_LEVEL_INFO);
   }

   //--- Alertas visuais / sonoros
   if (EnableAlerting && lastSignal != DEFENSE_NONE)
   {
      string msg = StringFormat("%s ⚔️ SINAL DE DEFESA: %d\nPreço: %.5f",
                                symbol, lastSignal, price);
      Alert(msg);
   }

   //--- Execução automática
   if (EnableAutoTrade && PositionsTotal() < MaxOpenTrades)
   {
      double lotSize = CalculateLotSize(RiskPerTrade);
      CTrade* trade = defense.GetTrade();

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
   double atr = iATR(_Symbol, PERIOD_CURRENT, 14);
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

#endif // __DEFENSE_ORCHESTRATOR_MQH__ 