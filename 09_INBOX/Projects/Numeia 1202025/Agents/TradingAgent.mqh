//+------------------------------------------------------------------+
//| TradingAgent.mqh - Agente de Execução de Trades Institucional   |
//| Projeto: EA Numeia - Sistema de Execução Avançada               |
//+------------------------------------------------------------------+
#ifndef __TRADING_AGENT_MQH__
#define __TRADING_AGENT_MQH__

#include <Trade\Trade.mqh>
#include "../Utils/Log.mqh"
#include "../Core/types.mqh"

// Estruturas avançadas para trading institucional
struct TradeSignal {
   string symbol;
   ENUM_ORDER_TYPE orderType;
   double volume;
   double price;
   double stopLoss;
   double takeProfit;
   string strategy;
   double confidence;
   datetime timestamp;
   bool isHighPriority;
};

struct PositionMetrics {
   double unrealizedPnL;
   double realizedPnL;
   double drawdown;
   double sharpeRatio;
   double maxDrawdown;
   int consecutiveWins;
   int consecutiveLosses;
   double winRate;
};

class TradingAgent {
private:
   CTrade trade;
   string agentName;
   bool initialized;
   
   // Métricas de performance institucional
   PositionMetrics metrics;
   TradeSignal lastSignal;
   
   // Configurações avançadas
   double maxPositionSize;
   double riskPerTrade;
   double maxDailyLoss;
   double targetDailyProfit;
   int maxConcurrentPositions;
   
   // Controle de risco dinâmico
   double currentRiskExposure;
   double portfolioBeta;
   double volatilityAdjustment;
   
   // Estratégias institucionais
   bool enableScalping;
   bool enableSwingTrading;
   bool enableArbitrage;
   bool enableHedging;

public:
   TradingAgent() {
      agentName = "TradingAgent";
      initialized = false;
      
      // Configurações padrão institucionais
      maxPositionSize = 100.0; // Lotes
      riskPerTrade = 0.02; // 2% por trade
      maxDailyLoss = 0.05; // 5% máximo diário
      targetDailyProfit = 0.03; // 3% alvo diário
      maxConcurrentPositions = 10;
      
      // Inicializar métricas
      ResetMetrics();
   }

   void Initialize() {
      if (initialized) return;
      
      // Configurar parâmetros de trading
      trade.SetDeviationInPoints(10);
      trade.SetTypeFilling(ORDER_FILLING_FOK);
      trade.SetMarginMode();
      trade.LogLevel(LOG_LEVEL_ALL);
      
      initialized = true;
      Log("TradingAgent institucional inicializado", agentName);
   }

   // Execução de sinal com lógica institucional
   bool ExecuteSignal(TradeSignal &signal) {
      if (!initialized) Initialize();
      
      // Validações institucionais
      if (!ValidateSignal(signal)) {
         Log("Sinal rejeitado - validação institucional falhou", agentName);
         return false;
      }
      
      // Cálculo de volume dinâmico
      double calculatedVolume = CalculateDynamicVolume(signal);
      
      // Execução com proteções
      bool success = ExecuteOrder(signal, calculatedVolume);
      
      if (success) {
         UpdateMetrics(signal);
         Log(StringFormat("Ordem executada: %s %.2f lotes @ %.5f", 
                         signal.symbol, calculatedVolume, signal.price), agentName);
      }
      
      return success;
   }

   // Validação institucional de sinais
   bool ValidateSignal(TradeSignal &signal) {
      // Verificar limites de risco
      if (currentRiskExposure > maxDailyLoss) {
         Log("Risco diário excedido", agentName);
         return false;
      }
      
      // Verificar posições simultâneas
      if (PositionsTotal() >= maxConcurrentPositions) {
         Log("Limite de posições simultâneas atingido", agentName);
         return false;
      }
      
      // Verificar confiança mínima
      if (signal.confidence < 0.7) {
         Log("Confiança insuficiente para execução", agentName);
         return false;
      }
      
      return true;
   }

   // Cálculo de volume dinâmico baseado em risco
   double CalculateDynamicVolume(TradeSignal &signal) {
      double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      double riskAmount = accountBalance * riskPerTrade;
      
      // Ajuste por volatilidade
      double volatility = GetSymbolVolatility(signal.symbol);
      double adjustedRisk = riskAmount * (1.0 - volatilityAdjustment);
      
      // Cálculo de volume baseado em stop loss
      double stopDistance = MathAbs(signal.price - signal.stopLoss);
      double tickValue = SymbolInfoDouble(signal.symbol, SYMBOL_TRADE_TICK_VALUE);
      
      if (stopDistance == 0 || tickValue == 0) return 0.01;
      
      double volume = adjustedRisk / (stopDistance * tickValue);
      volume = MathMin(volume, maxPositionSize);
      
      return NormalizeDouble(volume, 2);
   }

   // Execução de ordem com proteções
   bool ExecuteOrder(TradeSignal &signal, double volume) {
      if (signal.orderType == ORDER_TYPE_BUY) {
         return trade.Buy(volume, signal.symbol, signal.price, signal.stopLoss, signal.takeProfit, signal.strategy);
      } else if (signal.orderType == ORDER_TYPE_SELL) {
         return trade.Sell(volume, signal.symbol, signal.price, signal.stopLoss, signal.takeProfit, signal.strategy);
      }
      
      return false;
   }

   // Atualização de métricas de performance
   void UpdateMetrics(TradeSignal &signal) {
      lastSignal = signal;
      
      // Calcular P&L atual
      CalculateCurrentPnL();
      
      // Atualizar drawdown
      UpdateDrawdown();
      
      // Calcular Sharpe Ratio
      CalculateSharpeRatio();
   }

   // Cálculo de volatilidade do símbolo
   double GetSymbolVolatility(string symbol) {
      int atrHandle = iATR(symbol, PERIOD_D1, 14);
      if (atrHandle == INVALID_HANDLE) return 0.0;
      
      double atrValues[1];
      if (CopyBuffer(atrHandle, 0, 0, 1, atrValues) > 0) {
         return atrValues[0];
      }
      
      return 0.0;
   }

   // Cálculo de P&L atual
   void CalculateCurrentPnL() {
      metrics.unrealizedPnL = 0.0;
      
      for (int i = 0; i < PositionsTotal(); i++) {
         if (PositionSelectByTicket(PositionGetTicket(i))) {
            metrics.unrealizedPnL += PositionGetDouble(POSITION_PROFIT);
         }
      }
   }

   // Atualização de drawdown
   void UpdateDrawdown() {
      double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      double peakEquity = AccountInfoDouble(ACCOUNT_BALANCE); // Simplificado
      
      double currentDrawdown = (peakEquity - currentEquity) / peakEquity;
      metrics.drawdown = currentDrawdown;
      
      if (currentDrawdown > metrics.maxDrawdown) {
         metrics.maxDrawdown = currentDrawdown;
      }
   }

   // Cálculo de Sharpe Ratio
   void CalculateSharpeRatio() {
      // Implementação simplificada - em produção seria mais complexa
      if (metrics.unrealizedPnL > 0) {
         metrics.sharpeRatio = metrics.unrealizedPnL / MathMax(metrics.drawdown, 0.001);
      } else {
         metrics.sharpeRatio = 0.0;
      }
   }

   // Reset de métricas
   void ResetMetrics() {
      metrics.unrealizedPnL = 0.0;
      metrics.realizedPnL = 0.0;
      metrics.drawdown = 0.0;
      metrics.sharpeRatio = 0.0;
      metrics.maxDrawdown = 0.0;
      metrics.consecutiveWins = 0;
      metrics.consecutiveLosses = 0;
      metrics.winRate = 0.0;
   }

   // Getters para métricas
   PositionMetrics GetMetrics() { return metrics; }
   TradeSignal GetLastSignal() { return lastSignal; }
   
   // Configurações avançadas
   void SetRiskParameters(double maxRisk, double dailyLoss, double targetProfit) {
      riskPerTrade = maxRisk;
      maxDailyLoss = dailyLoss;
      targetDailyProfit = targetProfit;
   }
   
   void EnableStrategies(bool scalping, bool swing, bool arbitrage, bool hedging) {
      enableScalping = scalping;
      enableSwingTrading = swing;
      enableArbitrage = arbitrage;
      enableHedging = hedging;
   }
};

#endif // __TRADING_AGENT_MQH__ 