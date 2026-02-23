//+------------------------------------------------------------------+
//|              ExecutionLoopController.mqh                         |
//|      Controlador do loop principal de execução                   |
//|      Orquestra agentes e executores de forma sequencial          |
//+------------------------------------------------------------------+
#property strict

#include "TradeExecutor.mqh"
#include "PositionManager.mqh"
#include "..\\Agents\\RiskAgent.mqh"
#include "..\\Agents\\TradingAgent.mqh"
#include "..\\Agents\\PatternRecognitionAgent.mqh"
#include "..\\Analysis\\SignalValidator.mqh"
#include "..\\Utils\\Log.mqh"

class CExecutionLoopController {
private:
   CTradingAgent           tradingAgent;
   CRiskAgent              riskAgent;
   CPatternRecognitionAgent patternAgent;
   CSignalValidator        signalValidator;
   CTradeExecutor          executor;
   CPositionManager        positionManager;

public:
   CExecutionLoopController() {
      Log::Info("⏳ ExecutionLoopController inicializado");
   }

   void Execute() {
      if (!IsTradeTime()) {
         Log::Info("⏸ Fora do horário de negociação.");
         return;
      }

      // 1. Verificar condições de risco
      if (!riskAgent.ValidateRiskConditions()) {
         Log::Warn("⚠️ Risco elevado. Execução bloqueada.");
         return;
      }

      // 2. Detectar padrões e gerar sinais
      trade_signal signal = patternAgent.DetectSignal();
      if (!signal.is_valid) {
         Log::Info("❌ Nenhum padrão válido identificado.");
         return;
      }

      // 3. Validar com análise de contexto
      if (!signalValidator.IsSignalAligned(signal)) {
         Log::Info("❌ Sinal não está alinhado com o contexto de mercado.");
         return;
      }

      // 4. Executar operação
      bool orderSent = tradingAgent.ExecuteSignal(signal);
      if (!orderSent) {
         Log::Error("Erro ao executar ordem baseada no sinal.");
         return;
      }

      // 5. Gerenciar posição aberta
      positionManager.ManageOpenPositions();
   }

   bool IsTradeTime() {
      datetime now = TimeCurrent();
      int hour = TimeHour(now);
      return (hour >= GlobalConfig::StartHour && hour <= GlobalConfig::EndHour);
   }
};
