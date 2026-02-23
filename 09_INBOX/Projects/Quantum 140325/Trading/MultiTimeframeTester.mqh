#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

//+------------------------------------------------------------------+
//| Classe para gerenciamento de testes multi-timeframe                |
//+------------------------------------------------------------------+
class C_MultiTimeframeTester
  {
private:
   struct TimeframeData
     {
      ENUM_TIMEFRAMES timeframe;
      datetime       lastBarTime;
      double         lastClose;
      double         lastHigh;
      double         lastLow;
      double         lastVolume;
      bool           isNewBar;
     };
   
   TimeframeData    m_timeframes[];
   string           m_symbol;
   bool             m_isInitialized;
   
   //+------------------------------------------------------------------+
   void              InitializeTimeframes()
     {
      ArrayResize(m_timeframes, 7); // M1, M5, M15, H1, H4, H12, D1
      
      m_timeframes[0].timeframe = PERIOD_M1;
      m_timeframes[1].timeframe = PERIOD_M5;
      m_timeframes[2].timeframe = PERIOD_M15;
      m_timeframes[3].timeframe = PERIOD_H1;
      m_timeframes[4].timeframe = PERIOD_H4;
      m_timeframes[5].timeframe = PERIOD_H12;
      m_timeframes[6].timeframe = PERIOD_D1;
      
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         m_timeframes[i].lastBarTime = 0;
         m_timeframes[i].lastClose = 0;
         m_timeframes[i].lastHigh = 0;
         m_timeframes[i].lastLow = 0;
         m_timeframes[i].lastVolume = 0;
         m_timeframes[i].isNewBar = false;
        }
     }
   
   //+------------------------------------------------------------------+
   bool              UpdateTimeframeData(TimeframeData &tf)
     {
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      if(CopyRates(m_symbol, tf.timeframe, 0, 1, rates) <= 0)
         return false;
         
      if(rates[0].time != tf.lastBarTime)
        {
         tf.lastBarTime = rates[0].time;
         tf.lastClose = rates[0].close;
         tf.lastHigh = rates[0].high;
         tf.lastLow = rates[0].low;
         tf.lastVolume = rates[0].tick_volume;
         tf.isNewBar = true;
         return true;
        }
      
      tf.isNewBar = false;
      return false;
     }
   
   //+------------------------------------------------------------------+
   void              AnalyzeCorrelation()
     {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         for(int j = i + 1; j < ArraySize(m_timeframes); j++)
           {
            if(m_timeframes[i].isNewBar && m_timeframes[j].isNewBar)
              {
               double correlation = CalculateCorrelation(i, j);
               Print("Correlação entre ", EnumToString(m_timeframes[i].timeframe), 
                     " e ", EnumToString(m_timeframes[j].timeframe), ": ", correlation);
              }
           }
        }
     }
   
   //+------------------------------------------------------------------+
   double            CalculateCorrelation(int tf1, int tf2)
     {
      MqlRates rates1[], rates2[];
      ArraySetAsSeries(rates1, true);
      ArraySetAsSeries(rates2, true);
      
      if(CopyRates(m_symbol, m_timeframes[tf1].timeframe, 0, 100, rates1) <= 0)
         return 0;
         
      if(CopyRates(m_symbol, m_timeframes[tf2].timeframe, 0, 100, rates2) <= 0)
         return 0;
         
      double sum1 = 0, sum2 = 0, sum12 = 0;
      double sum1Squared = 0, sum2Squared = 0;
      int n = MathMin(ArraySize(rates1), ArraySize(rates2));
      
      for(int i = 0; i < n; i++)
        {
         sum1 += rates1[i].close;
         sum2 += rates2[i].close;
         sum12 += rates1[i].close * rates2[i].close;
         sum1Squared += rates1[i].close * rates1[i].close;
         sum2Squared += rates2[i].close * rates2[i].close;
        }
      
      double numerator = n * sum12 - sum1 * sum2;
      double denominator = MathSqrt((n * sum1Squared - sum1 * sum1) * (n * sum2Squared - sum2 * sum2));
      
      return denominator != 0 ? numerator / denominator : 0;
     }
   
   //+------------------------------------------------------------------+
   void              GeneratePerformanceReport()
     {
      string report = "Relatório de Performance por Timeframe\n";
      report += "=====================================\n\n";
      
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         report += "Timeframe: " + EnumToString(m_timeframes[i].timeframe) + "\n";
         report += "Último Preço: " + DoubleToString(m_timeframes[i].lastClose, _Digits) + "\n";
         report += "Volume: " + DoubleToString(m_timeframes[i].lastVolume, 0) + "\n";
         report += "Nova Barra: " + (m_timeframes[i].isNewBar ? "Sim" : "Não") + "\n";
         report += "-------------------------------------\n";
        }
      
      Print(report);
     }
   
public:
   //+------------------------------------------------------------------+
                     C_MultiTimeframeTester(string symbol = NULL)
     {
      m_symbol = (symbol == NULL ? _Symbol : symbol);
      m_isInitialized = false;
     }
   
   //+------------------------------------------------------------------+
   bool              Initialize()
     {
      if(m_isInitialized)
         return true;
         
      InitializeTimeframes();
      m_isInitialized = true;
      return true;
     }
   
   //+------------------------------------------------------------------+
   void              Update()
     {
      if(!m_isInitialized)
         return;
         
      bool anyNewBar = false;
      
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         if(UpdateTimeframeData(m_timeframes[i]))
            anyNewBar = true;
        }
      
      if(anyNewBar)
        {
         AnalyzeCorrelation();
         GeneratePerformanceReport();
        }
     }
   
   //+------------------------------------------------------------------+
   bool              IsNewBar(ENUM_TIMEFRAMES timeframe)
     {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         if(m_timeframes[i].timeframe == timeframe)
            return m_timeframes[i].isNewBar;
        }
      return false;
     }
   
   //+------------------------------------------------------------------+
   double            GetLastClose(ENUM_TIMEFRAMES timeframe)
     {
      for(int i = 0; i < ArraySize(m_timeframes); i++)
        {
         if(m_timeframes[i].timeframe == timeframe)
            return m_timeframes[i].lastClose;
        }
      return 0;
     }
  }; 