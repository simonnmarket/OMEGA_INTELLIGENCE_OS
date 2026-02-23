//+------------------------------------------------------------------+
//|                        TimeUtils.mqh                             |
//|    Funções auxiliares para tempo, datas e comparação temporal    |
//+------------------------------------------------------------------+
#ifndef __TIME_UTILS_MQH__
#define __TIME_UTILS_MQH__

// Retorna o timestamp atual
datetime Now() {
   return TimeCurrent();
}

// Converte datetime em string formatada
string FormatDateTime(datetime dt) {
   return TimeToString(dt, TIME_DATE | TIME_MINUTES);
}

// Verifica se um timestamp está dentro de uma faixa horária
bool IsWithinTimeRange(datetime time, int hour_start, int hour_end) {
   MqlDateTime dt;
   TimeToStruct(time, dt);
   return (dt.hour >= hour_start && dt.hour < hour_end);
}

// Verifica se está dentro do horário de operação
bool IsTradingHours(int start_hour = 8, int end_hour = 17) {
   return IsWithinTimeRange(TimeCurrent(), start_hour, end_hour);
}

// Diferença em minutos entre dois tempos
int MinutesBetween(datetime t1, datetime t2) {
   return int(MathAbs(t2 - t1) / 60);
}

#endif // __TIME_UTILS_MQH__ 