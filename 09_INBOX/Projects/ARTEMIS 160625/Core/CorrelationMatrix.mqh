#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.6"
#property strict

#include "..\\Utils\\CLogger.mqh"
#include "..\\Core\\CStatistics.mqh"

//+------------------------------------------------------------------+
//| CCorrelationMatrix.mqh - Correlation Matrix Analysis             |
//| Inspirado em: Markowitz, Sharpe, Lintner                         |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>
#include <Trade\Trade.mqh>
#include "..\Math\CStatistics.mqh"

class CCorrelationMatrix : public CObject
{
private:
   CLogger* m_logger;                    // Logger
   CStatistics* m_statistics;            // Módulo de estatísticas
   double m_matrix[];                    // Matriz de correlação
   string m_symbols[];                   // Símbolos
   int m_size;                           // Tamanho da matriz
   bool m_is_initialized;                // Se está inicializado
   
public:
   // Construtor
   CCorrelationMatrix(string symbols[], CLogger* logger)
   {
      m_logger = logger;
      m_is_initialized = false;
      
      // Inicializa módulos
      m_statistics = new CStatistics(m_logger);
      
      // Inicializa matriz
      m_size = ArraySize(symbols);
      if(m_size > 0)
      {
         ArrayResize(m_symbols, m_size);
         ArrayCopy(m_symbols, symbols);
         ArrayResize(m_matrix, m_size * m_size);
         ArrayInitialize(m_matrix, 0.0);
         
         if(m_logger != NULL && m_statistics != NULL)
         {
            m_logger.Info("Matriz de correlação inicializada");
            m_is_initialized = true;
         }
      }
   }
   
   // Destrutor
   ~CCorrelationMatrix()
   {
      if(m_statistics != NULL)
         delete m_statistics;
         
      if(m_logger != NULL)
         m_logger.Info("Matriz de correlação finalizada");
   }
   
   // Atualiza matriz
   void Update()
   {
      if(!m_is_initialized || m_logger == NULL)
         return;
         
      // Calcula correlações
      for(int i = 0; i < m_size; i++)
      {
         for(int j = i; j < m_size; j++)
         {
            double correlation = CalculateCorrelation(m_symbols[i], m_symbols[j]);
            m_matrix[i * m_size + j] = correlation;
            m_matrix[j * m_size + i] = correlation;
         }
      }
   }
   
   // Obtém correlação
   double GetCorrelation(int i, int j)
   {
      if(!m_is_initialized || i < 0 || i >= m_size || j < 0 || j >= m_size)
         return 0.0;
         
      return m_matrix[i * m_size + j];
   }
   
   // Obtém tamanho
   int GetSize()
   {
      return m_size;
   }
   
   // Obtém símbolo
   string GetSymbol(int index)
   {
      if(!m_is_initialized || index < 0 || index >= m_size)
         return "";
         
      return m_symbols[index];
   }
   
   // Validar matriz
   bool ValidateMatrix() const
   {
      if(m_size == 0) return false;
      
      // Verificar simetria
      for(int i = 0; i < m_size; i++)
      {
         for(int j = 0; j < m_size; j++)
         {
            if(MathAbs(m_matrix[i * m_size + j] - m_matrix[j * m_size + i]) > 0.0001)
               return false;
         }
      }
      
      return true;
   }
   
private:
   // Calcula correlação entre dois símbolos
   double CalculateCorrelation(string symbol1, string symbol2)
   {
      if(!m_is_initialized || m_statistics == NULL)
         return 0.0;
         
      double returns1[];
      double returns2[];
      
      // Obtém retornos
      if(!GetReturns(symbol1, returns1) || !GetReturns(symbol2, returns2))
         return 0.0;
         
      // Calcula correlação
      return m_statistics.CalculateCorrelation(returns1, returns2);
   }
   
   // Obtém retornos de um símbolo
   bool GetReturns(string symbol, double& returns[])
   {
      if(!m_is_initialized)
         return false;
         
      double prices[];
      int count = 100; // Número de períodos
      
      // Obtém preços
      if(!GetPrices(symbol, prices, count))
         return false;
         
      // Calcula retornos
      ArrayResize(returns, count - 1);
      
      for(int i = 1; i < count; i++)
         returns[i - 1] = (prices[i] - prices[i - 1]) / prices[i - 1];
         
      return true;
   }
   
   // Obtém preços de um símbolo
   bool GetPrices(string symbol, double& prices[], int count)
   {
      if(!m_is_initialized)
         return false;
         
      ArrayResize(prices, count);
      
      for(int i = 0; i < count; i++)
      {
         double close = iClose(symbol, PERIOD_CURRENT, i);
         if(close <= 0)
            return false;
            
         prices[i] = close;
      }
      
      return true;
   }
}; 