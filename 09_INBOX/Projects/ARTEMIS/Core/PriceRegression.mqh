//+------------------------------------------------------------------+
//| PriceRegression.mqh - Análise de Regressão e Previsão de Preços  |
//| Inspirado em: Box-Jenkins, ARIMA, GARCH                           |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>

class PriceRegression
{
private:
   // Parâmetros do modelo
   int m_ar_order;      // Ordem do modelo AR
   int m_ma_order;      // Ordem do modelo MA
   int m_diff_order;    // Ordem da diferenciação
   
   // Dados históricos
   struct PriceData {
      double prices[];
      double returns[];
      double volatility[];
      double residuals[];
   };
   
   PriceData m_data;
   
   // Coeficientes do modelo
   double m_ar_coeffs[];
   double m_ma_coeffs[];
   
   // Métricas de qualidade
   struct ModelMetrics {
      double aic;       // Critério de Informação de Akaike
      double bic;       // Critério de Informação Bayesiano
      double rmse;      // Raiz do Erro Quadrático Médio
   };
   
   ModelMetrics m_metrics;
   
public:
   PriceRegression(int ar_order = 2, int ma_order = 2, int diff_order = 1)
   {
      m_ar_order = ar_order;
      m_ma_order = ma_order;
      m_diff_order = diff_order;
      
      ArrayResize(m_ar_coeffs, ar_order);
      ArrayResize(m_ma_coeffs, ma_order);
      ArrayResize(m_data.prices, 1000);
      ArrayResize(m_data.returns, 1000);
      ArrayResize(m_data.volatility, 1000);
      ArrayResize(m_data.residuals, 1000);
   }
   
   // Atualização de dados
   void UpdateData(string symbol)
   {
      for(int i = 0; i < ArraySize(m_data.prices); i++)
      {
         m_data.prices[i] = iClose(symbol, PERIOD_M1, i);
      }
      
      CalculateReturns();
      CalculateVolatility();
      FitModel();
   }
   
   // Previsão de preço
   double PredictPrice(string symbol, int steps_ahead = 1)
   {
      double last_price = iClose(symbol, PERIOD_M1, 0);
      double prediction = last_price;
      
      for(int i = 0; i < steps_ahead; i++)
      {
         prediction = PredictNextPrice(prediction);
      }
      
      return prediction;
   }
   
   // Obter intervalo de confiança
   void GetConfidenceInterval(double &lower, double &upper, double confidence = 0.95)
   {
      double std_dev = CalculateStandardDeviation();
      double z_score = NormalQuantile((1.0 + confidence) / 2.0);
      
      lower = m_data.prices[0] - z_score * std_dev;
      upper = m_data.prices[0] + z_score * std_dev;
   }
   
   // Verificar qualidade do modelo
   bool IsModelValid()
   {
      return m_metrics.rmse < 0.1 && m_metrics.aic < 0.0;
   }
   
private:
   // Cálculo de retornos
   void CalculateReturns()
   {
      for(int i = 1; i < ArraySize(m_data.prices); i++)
      {
         m_data.returns[i-1] = (m_data.prices[i-1] - m_data.prices[i]) / m_data.prices[i];
      }
   }
   
   // Cálculo de volatilidade
   void CalculateVolatility()
   {
      int window = 20;
      for(int i = window; i < ArraySize(m_data.returns); i++)
      {
         double sum = 0.0;
         double sum_sq = 0.0;
         
         for(int j = 0; j < window; j++)
         {
            sum += m_data.returns[i-j];
            sum_sq += m_data.returns[i-j] * m_data.returns[i-j];
         }
         
         double mean = sum / window;
         m_data.volatility[i] = MathSqrt((sum_sq / window) - (mean * mean));
      }
   }
   
   // Ajuste do modelo
   void FitModel()
   {
      // Implementação simplificada do ajuste ARIMA
      // Em um sistema real, usar biblioteca especializada
      
      // Ajuste AR
      for(int i = 0; i < m_ar_order; i++)
      {
         m_ar_coeffs[i] = CalculateARCoef(i+1);
      }
      
      // Ajuste MA
      for(int i = 0; i < m_ma_order; i++)
      {
         m_ma_coeffs[i] = CalculateMACoef(i+1);
      }
      
      // Calcular resíduos
      CalculateResiduals();
      
      // Atualizar métricas
      UpdateMetrics();
   }
   
   // Cálculo de coeficiente AR
   double CalculateARCoef(int lag)
   {
      double sum_xy = 0.0;
      double sum_x2 = 0.0;
      
      for(int i = lag; i < ArraySize(m_data.returns); i++)
      {
         sum_xy += m_data.returns[i] * m_data.returns[i-lag];
         sum_x2 += m_data.returns[i-lag] * m_data.returns[i-lag];
      }
      
      return sum_xy / sum_x2;
   }
   
   // Cálculo de coeficiente MA
   double CalculateMACoef(int lag)
   {
      double sum_xy = 0.0;
      double sum_x2 = 0.0;
      
      for(int i = lag; i < ArraySize(m_data.residuals); i++)
      {
         sum_xy += m_data.residuals[i] * m_data.residuals[i-lag];
         sum_x2 += m_data.residuals[i-lag] * m_data.residuals[i-lag];
      }
      
      return sum_xy / sum_x2;
   }
   
   // Cálculo de resíduos
   void CalculateResiduals()
   {
      for(int i = m_ar_order; i < ArraySize(m_data.returns); i++)
      {
         double predicted = 0.0;
         
         // Componente AR
         for(int j = 0; j < m_ar_order; j++)
         {
            predicted += m_ar_coeffs[j] * m_data.returns[i-j-1];
         }
         
         // Componente MA
         for(int j = 0; j < m_ma_order; j++)
         {
            predicted += m_ma_coeffs[j] * m_data.residuals[i-j-1];
         }
         
         m_data.residuals[i] = m_data.returns[i] - predicted;
      }
   }
   
   // Previsão do próximo preço
   double PredictNextPrice(double last_price)
   {
      double predicted_return = 0.0;
      
      // Componente AR
      for(int i = 0; i < m_ar_order; i++)
      {
         predicted_return += m_ar_coeffs[i] * m_data.returns[i];
      }
      
      // Componente MA
      for(int i = 0; i < m_ma_order; i++)
      {
         predicted_return += m_ma_coeffs[i] * m_data.residuals[i];
      }
      
      return last_price * (1.0 + predicted_return);
   }
   
   // Atualização de métricas
   void UpdateMetrics()
   {
      int n = ArraySize(m_data.residuals);
      double sum_sq_error = 0.0;
      
      for(int i = 0; i < n; i++)
      {
         sum_sq_error += m_data.residuals[i] * m_data.residuals[i];
      }
      
      m_metrics.rmse = MathSqrt(sum_sq_error / n);
      m_metrics.aic = n * MathLog(sum_sq_error / n) + 2 * (m_ar_order + m_ma_order);
      m_metrics.bic = n * MathLog(sum_sq_error / n) + (m_ar_order + m_ma_order) * MathLog(n);
   }
   
   // Cálculo do desvio padrão
   double CalculateStandardDeviation()
   {
      double sum = 0.0;
      double sum_sq = 0.0;
      int n = ArraySize(m_data.residuals);
      
      for(int i = 0; i < n; i++)
      {
         sum += m_data.residuals[i];
         sum_sq += m_data.residuals[i] * m_data.residuals[i];
      }
      
      double mean = sum / n;
      return MathSqrt((sum_sq / n) - (mean * mean));
   }
   
   // Função quantil da distribuição normal
   double NormalQuantile(double p)
   {
      // Implementação simplificada
      // Em um sistema real, usar biblioteca especializada
      return 1.96; // Aproximação para 95% de confiança
   }
}; 