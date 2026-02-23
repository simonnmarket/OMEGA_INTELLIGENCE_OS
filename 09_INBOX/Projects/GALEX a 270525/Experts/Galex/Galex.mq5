//+------------------------------------------------------------------+
//|                                                      Galex.mq5 |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de módulos
#include "..\..\Include\Core\MarketSignal\MarketSignal.mqh"
#include "..\..\Include\Core\TradeExecutor\TradeExecutor.mqh"
#include "..\..\Include\Core\DataUpdater\DataUpdater.mqh"
#include "..\..\Include\Physics\PhysicsEngine\PhysicsEngine.mqh"
#include "..\..\Include\Analysis\MarketAnalyzer\MarketAnalyzer.mqh"
#include "..\..\Include\Analysis\TrajectoryAnalyzer\TrajectoryAnalyzer.mqh"
#include "..\..\Include\Risk\RiskManager\RiskManager.mqh"
#include "..\..\Include\Utils\Statistics\Statistics.mqh"
#include "..\..\Include\Utils\Logger\Logger.mqh"
#include "..\..\Include\Detectors\InstitutionalRadar\InstitutionalRadar.mqh"

// Parâmetros de entrada
input group "=== Parâmetros Gerais ==="
input double InitialLots = 0.01;                // Tamanho inicial do lote
input double MaxLots = 1.0;                     // Tamanho máximo do lote
input double RiskPercent = 1.0;                 // Percentual de risco por operação
input int StopLossPoints = 150;                 // Stop Loss em pontos (se não usar ATR)
input int TakeProfitPoints = 300;               // Take Profit em pontos (se não usar ATR)
input bool UseATRStopLoss = true;               // Usar ATR para Stop Loss
input double ATRStopLossMultiplier = 2.0;       // Multiplicador do ATR para Stop Loss
input bool UseATRTakeProfit = true;             // Usar ATR para Take Profit
input double ATRTakeProfitMultiplier = 3.0;     // Multiplicador do ATR para Take Profit
input bool UseTrailingStop = true;              // Usar Trailing Stop
input int TrailingStop = 50;                    // Trailing Stop em pontos
input int TrailingStep = 10;                    // Trailing Step em pontos
input bool UseBreakEven = true;                 // Usar Break Even
input int BreakEvenPoints = 30;                 // Pontos para ativar Break Even
input int BreakEvenProfit = 10;                 // Pontos de lucro após Break Even
input int MagicNumber = 11041982;               // Número mágico para identificação de ordens

// Variáveis globais
CMarketSignal g_market_signal;
CTradeExecutor g_trade_executor;
CDataUpdater g_data_updater;
CPhysicsEngine g_physics_engine;
CMarketAnalyzer g_market_analyzer;
CTrajectoryAnalyzer g_trajectory_analyzer;
CRiskManager g_risk_manager;
CLogger g_logger;
CInstitutionalRadar g_institutional_radar;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Inicializar logger
   if(!g_logger.Init("GALEX_Log.txt", true, true, LOG_LEVEL_INFO))
   {
      Print("Erro ao inicializar logger");
      return INIT_FAILED;
   }
   
   g_logger.Info("Inicializando GALEX Trading System...");
   
   // Inicializar módulos
   if(!InitializeModules())
   {
      g_logger.Error("Erro ao inicializar módulos");
      return INIT_FAILED;
   }
   
   g_logger.Info("GALEX Trading System inicializado com sucesso");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   g_logger.Info("Finalizando GALEX Trading System...");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Atualizar dados de mercado
   if(!g_data_updater.UpdateMarketData())
   {
      g_logger.Error("Erro ao atualizar dados de mercado");
      return;
   }
   
   // Obter arrays de dados
   const double &price_array[] = g_data_updater.GetPriceArray();
   const double &volume_array[] = g_data_updater.GetVolumeArray();
   int period = g_data_updater.GetPeriod();
   
   // Atualizar análise de mercado
   g_market_analyzer.Update(price_array, volume_array, period);
   
   // Atualizar análise de trajetória
   g_trajectory_analyzer.Update(price_array, volume_array, period);
   
   // Atualizar física
   g_physics_engine.CalculateExhaustVelocity(price_array, volume_array, period);
   g_physics_engine.CalculateDrag(price_array, volume_array, period);
   g_physics_engine.CalculateAcceleration(price_array, volume_array, period);
   g_physics_engine.GetPotentialEnergy(price_array, volume_array, period);
   
   // Atualizar radar institucional
   g_institutional_radar.Update(price_array, volume_array, period);
   
   // Atualizar sinal de mercado
   g_market_signal.UpdateSignal(price_array, volume_array, period);
   
   // Atualizar gestão de risco
   g_risk_manager.Update();
   
   // Verificar condições de entrada
   if(CheckForSignal())
   {
      // Executar sinal
      ExecuteSignal();
   }
}

//+------------------------------------------------------------------+
//| Inicializar módulos                                              |
//+------------------------------------------------------------------+
bool InitializeModules()
{
   // Inicializar executor de ordens
   if(!g_trade_executor.Init(InitialLots, MagicNumber))
   {
      g_logger.Error("Erro ao inicializar executor de ordens");
      return false;
   }
   
   // Inicializar atualizador de dados
   if(!g_data_updater.Init(100))
   {
      g_logger.Error("Erro ao inicializar atualizador de dados");
      return false;
   }
   
   // Inicializar física
   if(!g_physics_engine.Init())
   {
      g_logger.Error("Erro ao inicializar física");
      return false;
   }
   
   // Inicializar analisador de mercado
   if(!g_market_analyzer.Init())
   {
      g_logger.Error("Erro ao inicializar analisador de mercado");
      return false;
   }
   
   // Inicializar analisador de trajetória
   if(!g_trajectory_analyzer.Init())
   {
      g_logger.Error("Erro ao inicializar analisador de trajetória");
      return false;
   }
   
   // Inicializar gestor de risco
   if(!g_risk_manager.Init(InitialLots, MaxLots, RiskPercent,
                          StopLossPoints, TakeProfitPoints,
                          UseATRStopLoss, ATRStopLossMultiplier,
                          UseATRTakeProfit, ATRTakeProfitMultiplier,
                          UseTrailingStop, TrailingStop, TrailingStep,
                          UseBreakEven, BreakEvenPoints, BreakEvenProfit))
   {
      g_logger.Error("Erro ao inicializar gestor de risco");
      return false;
   }
   
   // Inicializar radar institucional
   if(!g_institutional_radar.Init())
   {
      g_logger.Error("Erro ao inicializar radar institucional");
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Verificar condições de entrada                                   |
//+------------------------------------------------------------------+
bool CheckForSignal()
{
   // Obter sinal do analisador de mercado
   ENUM_MARKET_SIGNAL market_signal = g_market_analyzer.AnalyzeMarket();
   
   // Verificar atividade institucional
   bool institutional_activity = g_institutional_radar.DetectInstitutionalActivity();
   
   // Verificar força gravitacional
   double gravitational_force = g_trajectory_analyzer.GetGravitationalForce();
   
   // Verificar energia potencial
   double potential_energy = g_physics_engine.GetPotentialEnergy();
   
   // Verificar aceleração
   double acceleration = g_physics_engine.GetAcceleration();
   
   // Verificar arrasto
   double drag = g_physics_engine.GetDragCoefficient();
   
   // Verificar velocidade de exaustão
   double exhaust_velocity = g_physics_engine.GetExhaustVelocity();
   
   // Registrar informações de debug
   g_logger.Debug(StringFormat("Sinal de Mercado: %d", market_signal));
   g_logger.Debug(StringFormat("Atividade Institucional: %s", institutional_activity ? "Sim" : "Não"));
   g_logger.Debug(StringFormat("Força Gravitacional: %.5f", gravitational_force));
   g_logger.Debug(StringFormat("Energia Potencial: %.5f", potential_energy));
   g_logger.Debug(StringFormat("Aceleração: %.5f", acceleration));
   g_logger.Debug(StringFormat("Arrasto: %.5f", drag));
   g_logger.Debug(StringFormat("Velocidade de Exaustão: %.5f", exhaust_velocity));
   
   // Verificar condições de entrada
   if(market_signal != SIGNAL_NONE && institutional_activity)
   {
      if(market_signal == SIGNAL_BUY)
      {
         return gravitational_force > 0.0 && potential_energy > 0.0 && acceleration > 0.0;
      }
      else if(market_signal == SIGNAL_SELL)
      {
         return gravitational_force < 0.0 && potential_energy < 0.0 && acceleration < 0.0;
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Executar sinal                                                   |
//+------------------------------------------------------------------+
void ExecuteSignal()
{
   // Obter sinal do analisador de mercado
   ENUM_MARKET_SIGNAL market_signal = g_market_analyzer.AnalyzeMarket();
   
   // Obter stop loss e take profit
   double stop_loss = g_risk_manager.GetStopLoss(market_signal);
   double take_profit = g_risk_manager.GetTakeProfit(market_signal);
   
   // Obter tamanho do lote
   double lot_size = g_risk_manager.GetPositionSize(stop_loss);
   
   // Executar ordem
   if(g_trade_executor.ExecuteTrade(market_signal, stop_loss, take_profit))
   {
      g_logger.Info(StringFormat("Ordem executada: %s, Lote: %.2f, SL: %.5f, TP: %.5f",
                                market_signal == SIGNAL_BUY ? "Compra" : "Venda",
                                lot_size, stop_loss, take_profit));
   }
   else
   {
      g_logger.Error("Erro ao executar ordem");
   }
} 