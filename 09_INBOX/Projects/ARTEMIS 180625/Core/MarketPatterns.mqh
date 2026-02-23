//+------------------------------------------------------------------+
//| MarketPatterns.mqh - Análise de Padrões de Mercado               |
//| Inspirado em: Technical Analysis, Chart Patterns                  |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>

class MarketPatterns
{
private:
   // Estrutura para dados de preço
   struct PriceData {
      double open[];
      double high[];
      double low[];
      double close[];
      double volume[];
   };
   
   PriceData m_data;
   
   // Estrutura para padrões
   struct Pattern
   {
      string name;
      double probability;
      double strength;
   };
   
   Pattern m_patterns[];
   int m_pattern_count;
   
   // Parâmetros de análise
   int m_lookback_period;
   double m_pattern_threshold;
   
public:
   MarketPatterns(int lookback_period = 100, double pattern_threshold = 0.7)
   {
      m_lookback_period = lookback_period;
      m_pattern_threshold = pattern_threshold;
      
      m_pattern_count = 0;
      ArrayResize(m_patterns, 0);
      
      ArrayResize(m_data.open, lookback_period);
      ArrayResize(m_data.high, lookback_period);
      ArrayResize(m_data.low, lookback_period);
      ArrayResize(m_data.close, lookback_period);
      ArrayResize(m_data.volume, lookback_period);
   }
   
   // Atualização de dados
   void UpdateData(string symbol)
   {
      for(int i = 0; i < m_lookback_period; i++)
      {
         m_data.open[i] = iOpen(symbol, PERIOD_M1, i);
         m_data.high[i] = iHigh(symbol, PERIOD_M1, i);
         m_data.low[i] = iLow(symbol, PERIOD_M1, i);
         m_data.close[i] = iClose(symbol, PERIOD_M1, i);
         m_data.volume[i] = iVolume(symbol, PERIOD_M1, i);
      }
      
      DetectPatterns();
   }
   
   // Detecção de padrões
   void DetectPatterns()
   {
      ArrayResize(m_patterns, 0);
      
      // Verificar padrões de reversão
      CheckDoubleTop();
      CheckDoubleBottom();
      CheckHeadAndShoulders();
      CheckInverseHeadAndShoulders();
      
      // Verificar padrões de continuação
      CheckTriangle();
      CheckRectangle();
      CheckFlag();
      CheckPennant();
      
      // Verificar padrões de candlestick
      CheckDoji();
      CheckEngulfing();
      CheckHammer();
      CheckShootingStar();
   }
   
   // Obter padrões detectados
   int GetPatterns(Pattern &patterns[])
   {
      ArrayResize(patterns, ArraySize(m_patterns));
      ArrayCopy(patterns, m_patterns);
      return ArraySize(patterns);
   }
   
   // Verificar se há padrões válidos
   bool HasValidPatterns()
   {
      return ArraySize(m_patterns) > 0;
   }
   
   // Obter melhor padrão
   bool GetBestPattern(Pattern &pattern)
   {
      if(!HasValidPatterns())
         return false;
      
      int best_idx = 0;
      double best_prob = m_patterns[0].probability;
      
      for(int i = 1; i < ArraySize(m_patterns); i++)
      {
         if(m_patterns[i].probability > best_prob)
         {
            best_idx = i;
            best_prob = m_patterns[i].probability;
         }
      }
      
      pattern = m_patterns[best_idx];
      return true;
   }
   
   // Adicionar padrão
   bool AddPattern(const string name, const double probability, const double strength)
   {
      if(name == "") return false;
      
      int new_size = m_pattern_count + 1;
      ArrayResize(m_patterns, new_size);
      
      m_patterns[m_pattern_count].name = name;
      m_patterns[m_pattern_count].probability = probability;
      m_patterns[m_pattern_count].strength = strength;
      
      m_pattern_count++;
      return true;
   }
   
   // Obter padrão
   bool GetPattern(const int index, string &name, double &probability, double &strength)
   {
      if(index < 0 || index >= m_pattern_count)
         return false;
         
      name = m_patterns[index].name;
      probability = m_patterns[index].probability;
      strength = m_patterns[index].strength;
      
      return true;
   }
   
   // Obter contagem de padrões
   int GetPatternCount() const
   {
      return m_pattern_count;
   }
   
   // Limpar padrões
   void Clear()
   {
      m_pattern_count = 0;
      ArrayResize(m_patterns, 0);
   }
   
   // Validar padrões
   bool ValidatePatterns() const
   {
      if(m_pattern_count == 0) return false;
      
      for(int i = 0; i < m_pattern_count; i++)
      {
         if(m_patterns[i].name == "" ||
            m_patterns[i].probability < 0.0 || m_patterns[i].probability > 1.0 ||
            m_patterns[i].strength < 0.0 || m_patterns[i].strength > 1.0)
            return false;
      }
      
      return true;
   }
   
private:
   // Verificar padrão Double Top
   void CheckDoubleTop()
   {
      for(int i = 2; i < m_lookback_period - 2; i++)
      {
         if(m_data.high[i] > m_data.high[i-1] &&
            m_data.high[i] > m_data.high[i+1] &&
            MathAbs(m_data.high[i] - m_data.high[i-2]) < m_data.high[i] * 0.001)
         {
            Pattern pattern;
            pattern.name = "Double Top";
            pattern.probability = CalculatePatternProbability(i, "Double Top");
            pattern.strength = CalculatePatternStrength(i, "Double Top");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Double Bottom
   void CheckDoubleBottom()
   {
      for(int i = 2; i < m_lookback_period - 2; i++)
      {
         if(m_data.low[i] < m_data.low[i-1] &&
            m_data.low[i] < m_data.low[i+1] &&
            MathAbs(m_data.low[i] - m_data.low[i-2]) < m_data.low[i] * 0.001)
         {
            Pattern pattern;
            pattern.name = "Double Bottom";
            pattern.probability = CalculatePatternProbability(i, "Double Bottom");
            pattern.strength = CalculatePatternStrength(i, "Double Bottom");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Head and Shoulders
   void CheckHeadAndShoulders()
   {
      for(int i = 3; i < m_lookback_period - 3; i++)
      {
         if(m_data.high[i] > m_data.high[i-1] &&
            m_data.high[i] > m_data.high[i+1] &&
            m_data.high[i-2] < m_data.high[i-1] &&
            m_data.high[i+2] < m_data.high[i+1])
         {
            Pattern pattern;
            pattern.name = "Head and Shoulders";
            pattern.probability = CalculatePatternProbability(i, "Head and Shoulders");
            pattern.strength = CalculatePatternStrength(i, "Head and Shoulders");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Inverse Head and Shoulders
   void CheckInverseHeadAndShoulders()
   {
      for(int i = 3; i < m_lookback_period - 3; i++)
      {
         if(m_data.low[i] < m_data.low[i-1] &&
            m_data.low[i] < m_data.low[i+1] &&
            m_data.low[i-2] > m_data.low[i-1] &&
            m_data.low[i+2] > m_data.low[i+1])
         {
            Pattern pattern;
            pattern.name = "Inverse Head and Shoulders";
            pattern.probability = CalculatePatternProbability(i, "Inverse Head and Shoulders");
            pattern.strength = CalculatePatternStrength(i, "Inverse Head and Shoulders");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Triangle
   void CheckTriangle()
   {
      for(int i = 5; i < m_lookback_period - 5; i++)
      {
         bool is_triangle = true;
         double upper_slope = 0.0;
         double lower_slope = 0.0;
         
         // Calcular inclinações
         for(int j = 0; j < 5; j++)
         {
            upper_slope += (m_data.high[i-j] - m_data.high[i-j-1]);
            lower_slope += (m_data.low[i-j] - m_data.low[i-j-1]);
         }
         
         upper_slope /= 5.0;
         lower_slope /= 5.0;
         
         // Verificar convergência
         if(upper_slope < 0 && lower_slope > 0)
         {
            Pattern pattern;
            pattern.name = "Triangle";
            pattern.probability = CalculatePatternProbability(i, "Triangle");
            pattern.strength = CalculatePatternStrength(i, "Triangle");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Rectangle
   void CheckRectangle()
   {
      for(int i = 5; i < m_lookback_period - 5; i++)
      {
         bool is_rectangle = true;
         double upper = m_data.high[i];
         double lower = m_data.low[i];
         
         // Verificar níveis
         for(int j = 1; j < 5; j++)
         {
            if(MathAbs(m_data.high[i-j] - upper) > upper * 0.001 ||
               MathAbs(m_data.low[i-j] - lower) > lower * 0.001)
            {
               is_rectangle = false;
               break;
            }
         }
         
         if(is_rectangle)
         {
            Pattern pattern;
            pattern.name = "Rectangle";
            pattern.probability = CalculatePatternProbability(i, "Rectangle");
            pattern.strength = CalculatePatternStrength(i, "Rectangle");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Flag
   void CheckFlag()
   {
      for(int i = 5; i < m_lookback_period - 5; i++)
      {
         bool is_flag = true;
         double upper_slope = 0.0;
         double lower_slope = 0.0;
         
         // Calcular inclinações
         for(int j = 0; j < 5; j++)
         {
            upper_slope += (m_data.high[i-j] - m_data.high[i-j-1]);
            lower_slope += (m_data.low[i-j] - m_data.low[i-j-1]);
         }
         
         upper_slope /= 5.0;
         lower_slope /= 5.0;
         
         // Verificar paralelismo
         if(MathAbs(upper_slope - lower_slope) < 0.0001)
         {
            Pattern pattern;
            pattern.name = "Flag";
            pattern.probability = CalculatePatternProbability(i, "Flag");
            pattern.strength = CalculatePatternStrength(i, "Flag");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Pennant
   void CheckPennant()
   {
      for(int i = 5; i < m_lookback_period - 5; i++)
      {
         bool is_pennant = true;
         double upper_slope = 0.0;
         double lower_slope = 0.0;
         
         // Calcular inclinações
         for(int j = 0; j < 5; j++)
         {
            upper_slope += (m_data.high[i-j] - m_data.high[i-j-1]);
            lower_slope += (m_data.low[i-j] - m_data.low[i-j-1]);
         }
         
         upper_slope /= 5.0;
         lower_slope /= 5.0;
         
         // Verificar convergência
         if(upper_slope < 0 && lower_slope > 0)
         {
            Pattern pattern;
            pattern.name = "Pennant";
            pattern.probability = CalculatePatternProbability(i, "Pennant");
            pattern.strength = CalculatePatternStrength(i, "Pennant");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Doji
   void CheckDoji()
   {
      for(int i = 0; i < m_lookback_period; i++)
      {
         double body = MathAbs(m_data.close[i] - m_data.open[i]);
         double shadow = m_data.high[i] - m_data.low[i];
         
         if(body < shadow * 0.1)
         {
            Pattern pattern;
            pattern.name = "Doji";
            pattern.probability = CalculatePatternProbability(i, "Doji");
            pattern.strength = CalculatePatternStrength(i, "Doji");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Engulfing
   void CheckEngulfing()
   {
      for(int i = 1; i < m_lookback_period; i++)
      {
         if((m_data.close[i] > m_data.open[i] &&
             m_data.close[i-1] < m_data.open[i-1] &&
             m_data.close[i] > m_data.open[i-1] &&
             m_data.open[i] < m_data.close[i-1]) ||
            (m_data.close[i] < m_data.open[i] &&
             m_data.close[i-1] > m_data.open[i-1] &&
             m_data.close[i] < m_data.open[i-1] &&
             m_data.open[i] > m_data.close[i-1]))
         {
            Pattern pattern;
            pattern.name = "Engulfing";
            pattern.probability = CalculatePatternProbability(i, "Engulfing");
            pattern.strength = CalculatePatternStrength(i, "Engulfing");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Hammer
   void CheckHammer()
   {
      for(int i = 0; i < m_lookback_period; i++)
      {
         double body = MathAbs(m_data.close[i] - m_data.open[i]);
         double upper_shadow = m_data.high[i] - MathMax(m_data.open[i], m_data.close[i]);
         double lower_shadow = MathMin(m_data.open[i], m_data.close[i]) - m_data.low[i];
         
         if(lower_shadow > body * 2 && upper_shadow < body * 0.1)
         {
            Pattern pattern;
            pattern.name = "Hammer";
            pattern.probability = CalculatePatternProbability(i, "Hammer");
            pattern.strength = CalculatePatternStrength(i, "Hammer");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Verificar padrão Shooting Star
   void CheckShootingStar()
   {
      for(int i = 0; i < m_lookback_period; i++)
      {
         double body = MathAbs(m_data.close[i] - m_data.open[i]);
         double upper_shadow = m_data.high[i] - MathMax(m_data.open[i], m_data.close[i]);
         double lower_shadow = MathMin(m_data.open[i], m_data.close[i]) - m_data.low[i];
         
         if(upper_shadow > body * 2 && lower_shadow < body * 0.1)
         {
            Pattern pattern;
            pattern.name = "Shooting Star";
            pattern.probability = CalculatePatternProbability(i, "Shooting Star");
            pattern.strength = CalculatePatternStrength(i, "Shooting Star");
            
            if(pattern.probability >= m_pattern_threshold)
            {
               ArrayResize(m_patterns, ArraySize(m_patterns) + 1);
               m_patterns[ArraySize(m_patterns) - 1] = pattern;
            }
         }
      }
   }
   
   // Cálculo de probabilidade do padrão
   double CalculatePatternProbability(int index, string pattern_name)
   {
      // Implementação simplificada
      // Em um sistema real, usar análise estatística mais sofisticada
      return 0.8;
   }
   
   // Cálculo de força do padrão
   double CalculatePatternStrength(int index, string pattern_name)
   {
      // Implementação simplificada
      // Em um sistema real, usar análise estatística mais sofisticada
      return 0.8;
   }
}; 