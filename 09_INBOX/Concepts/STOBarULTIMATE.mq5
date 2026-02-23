//+------------------------------------------------------------------+
//|                                               SatosBarULTIMATE.mq5|
//|                     Indicador profissional de detecção de big players |
//+------------------------------------------------------------------+

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   1

#plot_Color_Candles
#property indicator_type1 DRAW_COLOR_CANDLES
#property indicator_color1 clrBlue,clrWhite,clrYellow,clrOrange,clrRed
#property indicator_style1 STYLE_SOLID
#property indicator_width1 1

input int VolumePeriod = 20;           // Período para cálculo estatístico
input double AlertLevel = 2.0;         // Limiar para alerta institucional
input bool UseDeltaFilter = true;      // Usar delta como filtro adicional
input bool PlayAlertSound = true;      // Tocar som quando há presença institucional

double ExtColorBuffer[];
double ExtVolumeBuffer[];

//--- Índices das cores
#define COLOR_BLUE    0
#define COLOR_WHITE   1
#define COLOR_YELLOW  2
#define COLOR_ORANGE  3
#define COLOR_RED     4

int OnInit()
{
   SetIndexBuffer(0, ExtColorBuffer, INDICATOR_COLOR_INDEX);
   SetIndexBuffer(1, ExtVolumeBuffer);

   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_COLOR_CANDLES);
   PlotIndexSetInteger(0, PLOT_COLOR, clrBlue);
   PlotIndexSetInteger(0, PLOT_COLOR, clrWhite, 1);
   PlotIndexSetInteger(0, PLOT_COLOR, clrYellow, 2);
   PlotIndexSetInteger(0, PLOT_COLOR, clrOrange, 3);
   PlotIndexSetInteger(0, PLOT_COLOR, clrRed, 4);

   EventSetTimer(60); // Atualização a cada minuto
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   EventKillTimer();
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   int start = prev_calculated == 0 ? VolumePeriod : prev_calculated - 1;

   for(int i = start; i < rates_total; i++)
   {
      if(i < VolumePeriod) {
         ExtColorBuffer[i] = COLOR_BLUE;
         continue;
      }

      // Cálculo da média e desvio padrão do volume
      double sumVol = 0, sumSq = 0;
      for(int j = 1; j <= VolumePeriod; j++) {
          double v = volume[i - j];
          sumVol += v;
          sumSq += v * v;
      }

      double avgVol = sumVol / VolumePeriod;
      double varVol = sumSq / VolumePeriod - avgVol * avgVol;
      double stdVol = MathSqrt(varVol);
      double zscore = (volume[i] - avgVol) / stdVol;

      // Delta como filtro
      double delta = UseDeltaFilter ?
                     (close[i] > open[i] ? tick_volume[i] : -tick_volume[i]) : 0;

      // Classificação por cor
      int colorIndex = COLOR_BLUE;

      if(zscore < 0.5)
         colorIndex = COLOR_BLUE;
      else if(zscore < 1.0)
         colorIndex = COLOR_WHITE;
      else if(zscore < 1.5)
         colorIndex = COLOR_YELLOW;
      else if(zscore < AlertLevel)
         colorIndex = COLOR_ORANGE;
      else {
         colorIndex = COLOR_RED;
         if(PlayAlertSound && MathAbs(delta) > 1000) {
            PlaySound("bigplayer_alert.wav");
            SendNotification("🔴 Big Player detectado em " + Symbol());
         }
      }

      ExtColorBuffer[i] = colorIndex;
      ExtVolumeBuffer[i] = zscore;
   }

   return(rates_total);
}

void OnTimer()
{
   string fileName = "SatosLog.csv";
   int handle = FileOpen(fileName, FILE_WRITE | FILE_CSV);
   if(handle != INVALID_HANDLE)
   {
      for(int i = 0; i < BarsCalculated; i++)
         FileWrite(handle, TimeToString(Time[i]), ExtVolumeBuffer[i], ExtColorBuffer[i]);
      FileClose(handle);
   }
}