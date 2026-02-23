//+------------------------------------------------------------------+
//| CVolatilityAnalysis.mqh - Advanced Volatility Analysis            |
//| Version 3.0 - Unified and Enhanced (2025)                        |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include <Object.mqh>
#include "..\\Utils\\CLogger.mqh"
#include "..\\Core\\CStatistics.mqh"

//===========================================
// ENUMS
//===========================================
enum VolatilityMethod {
   METHOD_ATR = 0,
   METHOD_EWMA = 1,
   METHOD_GARCH = 2,
   METHOD_HYBRID = 3
};

//===========================================
// CLASS: VOLATILITY ANALYSIS
//===========================================
class CVolatilityAnalysis : public CObject {
private:
   CLogger* m_logger;                    // Logger
   CStatistics* m_statistics;            // Módulo de estatísticas
   
   string m_symbol;                      // Símbolo
   double m_volatility;                  // Volatilidade atual
   double m_volatility_ma;               // Média móvel da volatilidade
   double m_volatility_std;              // Desvio padrão da volatilidade
   bool m_is_initialized;                // Se está inicializado
   
   // Arrays para armazenar dados
   double m_returns[];                   // Array de retornos
   double m_volatilities[];              // Array de volatilidades
   int m_data_count;                     // Contador de dados
   
   // Configuração
   ENUM_TIMEFRAMES m_timeframe;
   int m_atr_period;
   int m_atr_handle;
   double m_volatility_threshold;
   
   // Parâmetros EWMA
   double m_ewma_lambda;                 // Parâmetro de suavização
   double m_ewma_volatility;             // Volatilidade EWMA
   
   // Validações
   bool ValidateSymbol(string symbol) {
      return (symbol != NULL && symbol != "");
   }
   
   bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe) {
      return (timeframe > 0);
   }
   
   bool ValidatePeriod(int period) {
      return (period > 0);
   }
   
   bool ValidateThreshold(double threshold) {
      return (threshold > 0);
   }
   
   bool ValidateParameters() {
      if(!ValidateSymbol(m_symbol)) {
         Print("Símbolo inválido: ", m_symbol);
         return false;
      }
      
      if(!ValidateTimeframe(m_timeframe)) {
         Print("Timeframe inválido: ", m_timeframe);
         return false;
      }
      
      if(!ValidatePeriod(m_atr_period)) {
         Print("Período ATR inválido: ", m_atr_period);
         return false;
      }
      
      if(!ValidateThreshold(m_volatility_threshold)) {
         Print("Limite de volatilidade inválido: ", m_volatility_threshold);
         return false;
      }
      
      return true;
   }
   
   // Cálculos
   bool CalculateReturns(double &returns[]) {
      if(!ValidateParameters()) return false;
      
      ArraySetAsSeries(returns, true);
      ArrayResize(returns, m_data_count);
      
      double prices[];
      ArraySetAsSeries(prices, true);
      ArrayResize(prices, m_data_count + 1);
      
      // Obtém preços de fechamento
      for(int i = 0; i < m_data_count + 1; i++) {
         prices[i] = iClose(m_symbol, m_timeframe, i);
      }
      
      // Calcula retornos logarítmicos
      for(int i = 0; i < m_data_count; i++) {
         if(prices[i+1] > 0) {
            returns[i] = MathLog(prices[i] / prices[i+1]);
         } else {
            returns[i] = 0;
         }
      }
      
      return true;
   }
   
   double CalculateEWMAVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      double variance = returns[0] * returns[0];
      for(int i = 1; i < m_data_count; i++) {
         variance = m_ewma_lambda * variance + (1 - m_ewma_lambda) * returns[i] * returns[i];
      }
      
      return MathSqrt(variance * 252); // Anualizado
   }
   
   double CalculateGARCHVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      double variance = 0;
      CAlglib::GARCHFit(returns, variance);
      return MathSqrt(variance * 252); // Anualizado
   }
   
   double CalculateATRVolatility() {
      if(!m_is_initialized || m_atr_handle == INVALID_HANDLE) return 0;
      
      double buffer[];
      if(CopyBuffer(m_atr_handle, 0, 0, 1, buffer) <= 0) return 0;
      
      double close = iClose(m_symbol, m_timeframe, 0);
      if(close == 0) return 0;
      
      return buffer[0] / close;
   }

public:
   // Construtor
   CVolatilityAnalysis(string symbol, CLogger* logger)
   {
      m_symbol = symbol;
      m_logger = logger;
      m_is_initialized = false;
      m_data_count = 0;
      m_ewma_lambda = 0.94;              // Valor padrão para EWMA
      m_ewma_volatility = 0.0;
      
      // Inicializa módulos
      m_statistics = new CStatistics(m_logger);
      
      if(m_logger != NULL && m_statistics != NULL)
      {
         m_logger.Info("Análise de volatilidade inicializada");
         m_is_initialized = true;
      }
      
      m_timeframe = PERIOD_CURRENT;
      m_atr_period = 14;
      m_atr_handle = INVALID_HANDLE;
      m_volatility_threshold = 0.002;
   }
   
   // Destrutor
   ~CVolatilityAnalysis()
   {
      if(m_statistics != NULL)
         delete m_statistics;
         
      if(m_logger != NULL)
         m_logger.Info("Análise de volatilidade finalizada");
      
      Release();
   }
   
   // Atualiza análise
   void Update()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Atualiza estatísticas
      if(m_statistics != NULL)
      {
         m_volatility = m_statistics.GetVolatility(m_symbol);
         m_volatility_ma = m_statistics.GetVolatilityMA(m_symbol);
         m_volatility_std = m_statistics.GetVolatilityStd(m_symbol);
         
         // Atualiza EWMA
         if(m_data_count > 0)
         {
            double current_return = m_returns[m_data_count - 1];
            m_ewma_volatility = m_ewma_lambda * m_ewma_volatility + 
                              (1 - m_ewma_lambda) * current_return * current_return;
         }
      }
   }
   
   // Adiciona retorno
   bool AddReturn(double ret)
   {
      if(!m_is_initialized)
         return false;
         
      int new_size = m_data_count + 1;
      
      if(!ArrayResize(m_returns, new_size))
         return false;
         
      m_returns[m_data_count] = ret;
      m_data_count++;
      
      return true;
   }
   
   // Calcula volatilidade
   double CalculateVolatility()
   {
      if(m_data_count < 2)
         return 0.0;
         
      double sum = 0.0;
      double sum_sq = 0.0;
      
      for(int i = 0; i < m_data_count; i++)
      {
         sum += m_returns[i];
         sum_sq += m_returns[i] * m_returns[i];
      }
      
      double mean = sum / m_data_count;
      double variance = (sum_sq / m_data_count) - (mean * mean);
      
      return MathSqrt(variance);
   }
   
   // Calcula volatilidade exponencial
   double CalculateExponentialVolatility()
   {
      return MathSqrt(m_ewma_volatility);
   }
   
   // Calcula volatilidade de Parkinson
   double CalculateParkinsonVolatility()
   {
      if(m_data_count < 2)
         return 0.0;
         
      double sum = 0.0;
      
      for(int i = 0; i < m_data_count; i++)
      {
         double high = m_returns[i] + MathAbs(m_returns[i] * 0.1);
         double low = m_returns[i] - MathAbs(m_returns[i] * 0.1);
         sum += MathLog(high / low) * MathLog(high / low);
      }
      
      return MathSqrt(sum / (4.0 * m_data_count * MathLog(2.0)));
   }
   
   // Calcula volatilidade de Garman-Klass
   double CalculateGarmanKlassVolatility()
   {
      if(m_data_count < 2)
         return 0.0;
         
      double sum = 0.0;
      
      for(int i = 0; i < m_data_count; i++)
      {
         double high = m_returns[i] + MathAbs(m_returns[i] * 0.1);
         double low = m_returns[i] - MathAbs(m_returns[i] * 0.1);
         double close = m_returns[i];
         double open = m_returns[i] * 0.5;
         
         sum += 0.5 * MathLog(high / low) * MathLog(high / low) -
                0.386 * MathLog(close / open) * MathLog(close / open);
      }
      
      return MathSqrt(sum / m_data_count);
   }
   
   // Calcula volatilidade de Rogers-Satchell
   double CalculateRogersSatchellVolatility()
   {
      if(m_data_count < 2)
         return 0.0;
         
      double sum = 0.0;
      
      for(int i = 0; i < m_data_count; i++)
      {
         double high = m_returns[i] + MathAbs(m_returns[i] * 0.1);
         double low = m_returns[i] - MathAbs(m_returns[i] * 0.1);
         double close = m_returns[i];
         double open = m_returns[i] * 0.5;
         
         sum += MathLog(high / close) * MathLog(high / open) +
                MathLog(low / close) * MathLog(low / open);
      }
      
      return MathSqrt(sum / m_data_count);
   }
   
   // Calcula volatilidade de Yang-Zhang
   double CalculateYangZhangVolatility()
   {
      if(m_data_count < 2)
         return 0.0;
         
      double sum = 0.0;
      double sum_overnight = 0.0;
      double sum_intraday = 0.0;
      
      for(int i = 0; i < m_data_count; i++)
      {
         double high = m_returns[i] + MathAbs(m_returns[i] * 0.1);
         double low = m_returns[i] - MathAbs(m_returns[i] * 0.1);
         double close = m_returns[i];
         double open = m_returns[i] * 0.5;
         
         double overnight = MathLog(open / close);
         double intraday = MathLog(high / low);
         
         sum_overnight += overnight * overnight;
         sum_intraday += intraday * intraday;
      }
      
      double k = 0.34 / (1.34 + (m_data_count + 1) / (m_data_count - 1));
      
      return MathSqrt(k * sum_overnight / m_data_count +
                     (1 - k) * sum_intraday / m_data_count);
   }
   
   // Obtém volatilidade atual
   double GetVolatility()
   {
      return m_volatility;
   }
   
   // Obtém média móvel da volatilidade
   double GetVolatilityMA()
   {
      return m_volatility_ma;
   }
   
   // Obtém desvio padrão da volatilidade
   double GetVolatilityStd()
   {
      return m_volatility_std;
   }
   
   // Obtém volatilidade EWMA
   double GetEWMAVolatility()
   {
      return MathSqrt(m_ewma_volatility);
   }
   
   // Define parâmetro EWMA
   void SetEWMAParameter(double lambda)
   {
      if(lambda > 0.0 && lambda < 1.0)
         m_ewma_lambda = lambda;
   }
   
   // Limpa dados
   void ClearData()
   {
      ArrayResize(m_returns, 0);
      ArrayResize(m_volatilities, 0);
      m_data_count = 0;
      m_ewma_volatility = 0.0;
   }
   
   bool Initialize(string symbol, ENUM_TIMEFRAMES timeframe, int atr_period = 14, 
                  double volatility_threshold = 0.002) {
      if(m_is_initialized) {
         Print("CVolatilityAnalysis já inicializado");
         return false;
      }
      
      m_symbol = symbol;
      m_timeframe = timeframe;
      m_atr_period = atr_period;
      m_volatility_threshold = volatility_threshold;
      
      if(!ValidateParameters()) return false;
      
      // Inicializar ATR
      m_atr_handle = iATR(m_symbol, m_timeframe, m_atr_period);
      if(m_atr_handle == INVALID_HANDLE) {
         Print("Erro ao criar ATR: ", GetLastError());
         return false;
      }
      
      m_is_initialized = true;
      return true;
   }
   
   void Release() {
      if(!m_is_initialized) return;
      
      if(m_atr_handle != INVALID_HANDLE) {
         IndicatorRelease(m_atr_handle);
         m_atr_handle = INVALID_HANDLE;
      }
      
      m_is_initialized = false;
   }
   
   bool IsInitialized() const {
      return m_is_initialized;
   }
   
   double GetHistoricalVolatility() {
      double returns[];
      if(!CalculateReturns(returns)) return 0.0;
      
      double sum = 0;
      double sum_squared = 0;
      
      for(int i = 0; i < m_data_count; i++) {
         sum += returns[i];
         sum_squared += returns[i] * returns[i];
      }
      
      double mean = sum / m_data_count;
      double variance = (sum_squared / m_data_count) - (mean * mean);
      
      return MathSqrt(variance * 252); // Anualizado
   }
};