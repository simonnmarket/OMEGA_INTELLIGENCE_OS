//+------------------------------------------------------------------+
//| ModuleRegistry.mqh - Registro de Módulos da EA Numeia           |
//+------------------------------------------------------------------+
#ifndef __MODULE_REGISTRY_MQH__
#define __MODULE_REGISTRY_MQH__

#include "../Utils/Log.mqh"

class ModuleRegistry {
private:
   bool tradingAgentEnabled;
   bool riskAgentEnabled;
   bool patternAgentEnabled;
   bool marketAnalysisAgentEnabled;

public:
   // Construtor - habilita os módulos padrão
   ModuleRegistry() {
      tradingAgentEnabled         = true;
      riskAgentEnabled            = true;
      patternAgentEnabled         = true;
      marketAnalysisAgentEnabled  = true;
   }

   // Setters para ativar/desativar módulos dinamicamente
   void EnableTradingAgent(bool state)         { tradingAgentEnabled = state; }
   void EnableRiskAgent(bool state)            { riskAgentEnabled = state; }
   void EnablePatternAgent(bool state)         { patternAgentEnabled = state; }
   void EnableMarketAnalysisAgent(bool state)  { marketAnalysisAgentEnabled = state; }

   // Getters para checar o status dos módulos
   bool IsTradingAgentEnabled()         { return tradingAgentEnabled; }
   bool IsRiskAgentEnabled()            { return riskAgentEnabled; }
   bool IsPatternAgentEnabled()         { return patternAgentEnabled; }
   bool IsMarketAnalysisAgentEnabled()  { return marketAnalysisAgentEnabled; }

   // Logging da configuração atual
   void LogModuleStatus() {
      Log("=== Módulos Ativos ===");
      Log("- TradingAgent: " + (string)tradingAgentEnabled);
      Log("- RiskAgent: " + (string)riskAgentEnabled);
      Log("- PatternRecognitionAgent: " + (string)patternAgentEnabled);
      Log("- MarketAnalysisAgent: " + (string)marketAnalysisAgentEnabled);
   }
};

#endif // __MODULE_REGISTRY_MQH__
