//+------------------------------------------------------------------+
//| TestSkyIntelDecisionSimulator.mq5                                |
//| Script de Teste Estratégico do SKYINTEL - Numeia EA              |
//| Executa decisões em lote para múltiplos ativos e registra logs   |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include <Core/CoreBrainManager.mqh>
#include <Integration/SkyIntelBridge.mqh>
#include <DecisionEngine/SignalController.mqh>
#include <Logs/AuditManager.mqh>

input string AssetList     = "EURUSD,US500,BTCUSD,XAUUSD,WIN$";
input ENUM_TIMEFRAMES TF   = PERIOD_M15;
input int DelayBetweenTests = 2; // segundos entre ativos

//+------------------------------------------------------------------+
//| Função Principal                                                 |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("===== [SKYINTEL] Simulação Estratégica Iniciada =====");
   string assets[];
   StringSplit(AssetList, ',', assets);

   for (int i = 0; i < ArraySize(assets); i++)
   {
      string symbol = StringTrim(assets[i]);
      if (!SymbolSelect(symbol, true))
      {
         Print("❌ Ativo inválido ou não disponível: ", symbol);
         continue;
      }

      PrintFormat("\n🛰️ [%s | %s] Testando decisão estratégica...", symbol, EnumToString(TF));
      ENUM_SIGNAL_TYPE intel = SkyIntelBridge::EvaluateSkyIntelSignal(symbol);
      SignalController::STRATEGIC_DECISION decision = SignalController::ConsolidatedDecision(symbol);

      string result = SignalController::DescribeSignal(intel);
      string recommendation = DecisionToString(decision);

      AuditLog("SkyIntelSimulator", symbol,
               StringFormat("🔎 Resultado: %s | Recomendação: %s",
                            result, recommendation));

      PrintFormat("📘 [%s] Sinal SKYINTEL: %s | Ação Recomendada: %s",
                  symbol, result, recommendation);

      Sleep(DelayBetweenTests * 1000); // pequena pausa entre ativos
   }

   Print("===== [SKYINTEL] Simulação Concluída =====");
}

//+------------------------------------------------------------------+
//| Conversão da decisão estratégica para texto                      |
//+------------------------------------------------------------------+
string DecisionToString(SignalController::STRATEGIC_DECISION d)
{
   switch (d)
   {
      case STRATEGIC_BUY:  return "BUY";
      case STRATEGIC_SELL: return "SELL";
      default:             return "IGNORAR";
   }
}
