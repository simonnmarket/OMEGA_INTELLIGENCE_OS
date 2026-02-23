//+------------------------------------------------------------------+
//|  SessionManager.mqh                                              |
//|  Gerencia sessões de operação com base em horário e região.     |
//+------------------------------------------------------------------+
#pragma once

class SessionManager
{
private:
   datetime sessionStartTime;
   datetime sessionEndTime;
   bool enableLondonSession;
   bool enableNYSession;
   bool enableAsiaSession;
   int maxTradeDurationMinutes;
   datetime lastTradeTime;

public:
   // Inicialização da sessão
   void Init(datetime start, datetime end, bool london, bool ny, bool asia, int maxDurationMinutes)
   {
      sessionStartTime      = start;
      sessionEndTime        = end;
      enableLondonSession   = london;
      enableNYSession       = ny;
      enableAsiaSession     = asia;
      maxTradeDurationMinutes = maxDurationMinutes;
      lastTradeTime         = 0;
   }

   // Verifica se está dentro do horário permitido
   bool IsWithinTimeWindow()
   {
      datetime now = TimeCurrent();
      int currentHour = TimeHour(now);
      return (currentHour >= TimeHour(sessionStartTime) && currentHour <= TimeHour(sessionEndTime));
   }

   // Verifica se está em alguma das sessões ativas
   bool IsInActiveSession()
   {
      int hour = TimeHour(TimeCurrent());

      bool isLondon = (hour >= 8 && hour < 17);    // 08:00–17:00 GMT+0
      bool isNY     = (hour >= 13 && hour < 22);   // 13:00–22:00 GMT+0
      bool isAsia   = (hour >= 0 && hour < 8);     // 00:00–08:00 GMT+0

      return (enableLondonSession && isLondon) ||
             (enableNYSession && isNY) ||
             (enableAsiaSession && isAsia);
   }

   // Verifica se está tudo liberado para operar
   bool IsWithinSession()
   {
      return IsWithinTimeWindow() && IsInActiveSession();
   }

   // Marca o horário da última operação
   void MarkTradeTime()
   {
      lastTradeTime = TimeCurrent();
   }

   // Verifica se tempo máximo da operação foi excedido
   bool IsTradeDurationExceeded()
   {
      if (lastTradeTime == 0)
         return false;

      int elapsed = (int)((TimeCurrent() - lastTradeTime) / 60);
      return elapsed > maxTradeDurationMinutes;
   }
}; 