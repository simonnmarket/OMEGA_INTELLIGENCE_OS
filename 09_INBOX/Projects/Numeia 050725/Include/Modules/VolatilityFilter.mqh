//+------------------------------------------------------------------+
//| Include/Modules/VolatilityFilter.mqh                             |
//| Filtro Institucional de Volatilidade para Execução Precisa      |
//| SkyLab/Numeia - Versão aprimorada com segurança e auditoria      |
//+------------------------------------------------------------------+
#ifndef __VOLATILITY_FILTER__
#define __VOLATILITY_FILTER__

#include <Logs/AuditManager.mqh>  // Adicionado para logging institucional

//--- Parâmetros default configuráveis
input int    ATRPeriod       = 14;
input double MinVolatility   = 0.0008;
input double MaxVolatility   = 0.015;
input bool   EnableVolAudit  = false;  // Controla log via AuditManager

//+------------------------------------------------------------------+
//| Avalia se a volatilidade do ativo está dentro da zona ideal     |
//+------------------------------------------------------------------+
bool VolatilityIsAcceptable(string symbol,
                            ENUM_TIMEFRAMES tf,
                            int atrPeriod = ATRPeriod,
                            double minVol = MinVolatility,
                            double maxVol = MaxVolatility)
{
   if (!SymbolSelect(symbol, true))
   {
      if (EnableVolAudit)
         AuditLog("VolatilityFilter", symbol, "⛔ Symbol not available for selection");
      return false;
   }

   double atr = iATR(symbol, tf, atrPeriod, 0);
   if (atr <= 0.0)
   {
      if (EnableVolAudit)
         AuditLog("VolatilityFilter", symbol, StringFormat("⛔ ATR inválido: %.5f [TF=%s]", atr, EnumToString(tf)));
      return false;
   }

   bool accepted = (atr >= minVol && atr <= maxVol);

   if (EnableVolAudit)
   {
      string status = accepted ? "✅ Aceita" : "⛔ Rejeitada";
      string msg = StringFormat("ATR=%.5f | TF=%s | Status=%s", atr, EnumToString(tf), status);
      AuditLog("VolatilityFilter", symbol, msg);
   }

   return accepted;
}

//+------------------------------------------------------------------+
//| Versão simplificada para timeframe atual                         |
//+------------------------------------------------------------------+
bool VolatilityIsAcceptable(string symbol)
{
   return VolatilityIsAcceptable(symbol, Period(), ATRPeriod, MinVolatility, MaxVolatility);
}

#endif // __VOLATILITY_FILTER__
