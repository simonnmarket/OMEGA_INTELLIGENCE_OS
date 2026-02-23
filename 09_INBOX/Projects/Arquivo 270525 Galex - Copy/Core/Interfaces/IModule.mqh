//+------------------------------------------------------------------+
//|                                                    IModule.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Interface base para todos os módulos
interface IModule
{
   // Inicialização do módulo
   bool Init();
   
   // Atualização do módulo
   void Update();
   
   // Validação do módulo
   bool Validate();
   
   // Limpeza do módulo
   void Cleanup();
   
   // Obter status do módulo
   string GetStatus() const;
   
   // Obter versão do módulo
   string GetVersion() const;
   
   // Obter nome do módulo
   string GetName() const;
};

// Interface para módulos que processam dados
interface IDataProcessor : public IModule
{
   // Processar dados
   bool ProcessData(const double &data[]);
   
   // Obter dados processados
   bool GetProcessedData(double &data[]);
};

// Interface para módulos que geram sinais
interface ISignalGenerator : public IModule
{
   // Gerar sinal
   ENUM_MARKET_SIGNAL GenerateSignal();
   
   // Obter força do sinal
   double GetSignalStrength() const;
};

// Interface para módulos que executam ações
interface IActionExecutor : public IModule
{
   // Executar ação
   bool ExecuteAction(const ENUM_MARKET_SIGNAL signal);
   
   // Verificar se ação pode ser executada
   bool CanExecuteAction(const ENUM_MARKET_SIGNAL signal);
};

// Interface para módulos que analisam dados
interface IDataAnalyzer : public IModule
{
   // Analisar dados
   bool AnalyzeData(const double &data[]);
   
   // Obter resultado da análise
   bool GetAnalysisResult(double &result[]);
};

// Interface para módulos que gerenciam risco
interface IRiskManager : public IModule
{
   // Calcular risco
   double CalculateRisk();
   
   // Verificar se risco está dentro dos limites
   bool IsRiskAcceptable();
   
   // Ajustar parâmetros de risco
   bool AdjustRiskParameters();
};

// Interface para módulos que registram logs
interface ILogger : public IModule
{
   // Registrar mensagem
   void Log(const string message, const ENUM_LOG_LEVEL level);
   
   // Obter histórico de logs
   bool GetLogHistory(string &history[]);
   
   // Limpar logs
   void ClearLogs();
}; 