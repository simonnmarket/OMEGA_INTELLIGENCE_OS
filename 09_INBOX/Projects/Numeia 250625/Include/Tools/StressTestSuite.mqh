//+------------------------------------------------------------------+
//| StressTestSuite.mqh - Suite de Testes de Estresse                |
//| Projeto: EA Numeia - Tools                                       |
//| Função: Testa a robustez do sistema em condições extremas        |
//+------------------------------------------------------------------+

#include <ExecutionLogic/DefenseAgent.mqh>
#include <Modules/VolatilityFilter.mqh>
#include <Utils/Log.mqh>

//--- Estrutura de resultado
struct StressResult {
   string symbol;
   ENUM_TIMEFRAMES timeframe;
   int totalZonas;
   double hurstMedia;
   double mediaFootprint;
   double percentualRupturas;
};

//--- Parâmetros configuráveis
input string AssetList = "EURUSD,US500,BTCUSD,WIN$,PETR4";
input ENUM_TIMEFRAMES TFList[] = { PERIOD_M5, PERIOD_M15, PERIOD_H1 };
input int LookbackBars = 500;
input double VolatilityThreshold = 0.0008;

//+------------------------------------------------------------------+
//| Varredura geral em todos os ativos/timeframes                    |
//+------------------------------------------------------------------+
void RunStressTest()
{
   string assets[];
   StringSplit(AssetList, ',', assets);

   for (int a = 0; a < ArraySize(assets); a++)
   {
      string sym = StringTrim(assets[a]);

      for (int t = 0; t < ArraySize(TFList); t++)
      {
         ENUM_TIMEFRAMES tf = TFList[t];

         StressResult r = RunTestFor(sym, tf);
         LogStressResult(r);
      }
   }
}

//+------------------------------------------------------------------+
//| Executa o teste para um par e timeframe específico               |
//+------------------------------------------------------------------+
StressResult RunTestFor(string symbol, ENUM_TIMEFRAMES tf)
{
   int zonas = 0;
   double hurstSum = 0, footprintSum = 0;
   int rupturas = 0;

   MqlRates rates[];
   if (CopyRates(symbol, tf, 0, LookbackBars, rates) <= 0)
      return (StressResult){"", tf, 0, 0, 0, 0};

   for (int i = LookbackBars - 1; i >= 0; i--)
   {
      if (!VolatilityIsAcceptable(symbol, tf, ATRPeriod, VolatilityThreshold, MaxVolatility))
         continue;

      DefenseStatus ds = GetDefenseStatus(symbol, tf, i);
      hurstSum += ds.hurst;
      footprintSum += (ds.footprint != EMPTY_VALUE ? 1 : 0);

      if (ds.signal != DEFENSE_NONE)
         zonas++;

      // Observação: rupturas reais dependem de outro mecanismo externo
      // Aqui interpretado como footprint ativo em zona sinal
      if (ds.signal != DEFENSE_NONE && ds.footprint != EMPTY_VALUE)
         rupturas++;
   }

   StressResult r;
   r.symbol = symbol;
   r.timeframe = tf;
   r.totalZonas = zonas;
   r.hurstMedia = hurstSum / LookbackBars;
   r.mediaFootprint = footprintSum / LookbackBars;
   r.percentualRupturas = (zonas > 0 ? (rupturas * 100.0 / zonas) : 0.0);

   return r;
}

//+------------------------------------------------------------------+
//| Log do resultado institucional                                   |
//+------------------------------------------------------------------+
void LogStressResult(const StressResult &r)
{
   string msg = StringFormat("[StressTest] %s [%s]: Zonas=%d | Hurst=%.2f | Footprint=%.2f | Rupturas=%.2f%%",
                             r.symbol, EnumToString(r.timeframe),
                             r.totalZonas, r.hurstMedia, r.mediaFootprint, r.percentualRupturas);

   Print(msg);
   AuditLog("StressTestSuite", r.symbol, msg);
} 