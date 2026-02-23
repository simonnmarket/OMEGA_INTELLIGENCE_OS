//+------------------------------------------------------------------+
//| File: Include/ExecutionLogic/SignalExecutionAgent.mqh           |
//| Purpose: Executar ordens com base na convicção do sinal         |
//| Requisitos: Integrado ao SignalConsensusEngine                  |
//+------------------------------------------------------------------+
#ifndef __SIGNAL_EXECUTION_AGENT_MQH__
#define __SIGNAL_EXECUTION_AGENT_MQH__

#include "..\Core\TradeExecutor.mqh"
#include "..\DecisionEngine\SignalConsensusEngine.mqh"
#include "..\Log\Log.mqh"

// Níveis mínimos para execução real
#define MIN_CONVICTION_TO_TRADE   CONVICTION_STRONG_BUY
#define MAX_CONVICTION_ALLOWED    CONVICTION_VERY_STRONG_SELL

// Configuração de volume adaptável
input double BaseLotSize = 0.10;
input double MaxLotSize  = 10.0;

//+------------------------------------------------------------------+
//| Executa a ordem com base na convicção estratégica                |
//+------------------------------------------------------------------+
void ExecuteSignalIfConvictionStrong(const string symbol, ENUM_TIMEFRAMES tf)
{
   SignalConviction sc = GetSignalConviction(symbol, tf);

   Log("🧠 [SignalExecutionAgent] Conviction Level: " + EnumToString(sc.level));
   if (sc.level < MIN_CONVICTION_TO_TRADE || sc.level > MAX_CONVICTION_ALLOWED)
   {
      Log("⚠️ Conviction insuficiente para operar (" + EnumToString(sc.level) + ")");
      return;
   }

   double volume = CalculateLotByConviction(sc.level);
   bool success = false;

   if (sc.direction == DIRECTION_BUY)
      success = ExecuteBuyOrder(symbol, volume, "SignalExec");
   else if (sc.direction == DIRECTION_SELL)
      success = ExecuteSellOrder(symbol, volume, "SignalExec");

   if (success)
      Log("✅ Ordem executada com sucesso para " + symbol + " (" + EnumToString(sc.direction) + ", Vol: " + DoubleToString(volume, 2) + ")");
   else
      Log("❌ Falha na execução da ordem para " + symbol);
}

//+------------------------------------------------------------------+
//| Converte nível de convicção em volume proporcional               |
//+------------------------------------------------------------------+
double CalculateLotByConviction(ENUM_CONVICTION_LEVEL level)
{
   double factor = 1.0;
   switch (level)
   {
      case CONVICTION_STRONG_BUY:
      case CONVICTION_STRONG_SELL: factor = 1.0; break;

      case CONVICTION_VERY_STRONG_BUY:
      case CONVICTION_VERY_STRONG_SELL: factor = 2.0; break;

      case CONVICTION_EXTREME_BUY:
      case CONVICTION_EXTREME_SELL: factor = 3.0; break;

      default: factor = 0.0; break;
   }

   double lot = BaseLotSize * factor;
   return MathMin(lot, MaxLotSize);
}

//+------------------------------------------------------------------+
//| Função auxiliar para converter enum em string                    |
//+------------------------------------------------------------------+
string GetConvictionName(SignalConvictionLevel level)
{
   switch (level)
   {
      case NO_SIGNAL:     return "NO_SIGNAL";
      case AVOID:         return "AVOID";
      case NEUTRAL:       return "NEUTRAL";
      case WEAK_BUY:      return "WEAK_BUY";
      case STRONG_BUY:    return "STRONG_BUY";
      case WEAK_SELL:     return "WEAK_SELL";
      case STRONG_SELL:   return "STRONG_SELL";
      default:            return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Função auxiliar para converter tipo de ordem em string           |
//+------------------------------------------------------------------+
string GetOrderTypeName(ENUM_ORDER_TYPE orderType)
{
   switch (orderType)
   {
      case ORDER_TYPE_BUY:   return "BUY";
      case ORDER_TYPE_SELL:  return "SELL";
      default:               return "UNKNOWN";
   }
}

#endif // __SIGNAL_EXECUTION_AGENT_MQH__ 