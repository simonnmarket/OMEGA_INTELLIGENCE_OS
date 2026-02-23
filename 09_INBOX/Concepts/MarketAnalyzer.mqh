//+------------------------------------------------------------------+
//|                                                    MarketAnalyzer.mqh |
//|             Núcleo Institucional de Análise de Mercado - EA Numeia |
//+------------------------------------------------------------------+
#property strict

#include <Utils/Log.mqh>
#include <Utils/IndicatorUtils.mqh>

class MarketAnalyzer {
private:
   double volume_threshold;
   double price_energy_sensitivity;
   int    trend_lookback;

public:
   // Resultados
   bool   is_uptrend;
   bool   is_downtrend;
   double current_volume;
   double vwap_price;
   double energy_index;
   bool   wyckoff_phase_detected;

   // Construtor
   MarketAnalyzer(double volumeThreshold = 100000, double sensitivity = 1.2, int lookback = 20) {
      volume_threshold         = volumeThreshold;
      price_energy_sensitivity = sensitivity;
      trend_lookback           = lookback;
      Reset();
   }

   void Reset() {
      is_uptrend            = false;
      is_downtrend          = false;
      current_volume        = 0.0;
      vwap_price            = 0.0;
      energy_index          = 0.0;
      wyckoff_phase_detected = false;
   }

   // Atualiza todos os cálculos com base nos dados mais recentes
   void Analyze(string symbol, ENUM_TIMEFRAMES tf) {
      Reset();

      // 1. Volume atual
      current_volume = iVolume(symbol, tf, 0);

      // 2. VWAP (usando preço médio ponderado por volume)
      double total_volume = 0;
      double volume_price_sum = 0;
      for (int i = 0; i < trend_lookback; i++) {
         double vol = iVolume(symbol, tf, i);
         double typical = (iHigh(symbol, tf, i) + iLow(symbol, tf, i) + iClose(symbol, tf, i)) / 3.0;
         volume_price_sum += vol * typical;
         total_volume += vol;
      }
      if (total_volume > 0) {
         vwap_price = volume_price_sum / total_volume;
      }

      // 3. Energia do preço (variação relativa com peso de volume)
      double energy = 0;
      for (int i = 1; i <= trend_lookback; i++) {
         double vol = iVolume(symbol, tf, i);
         double delta = iClose(symbol, tf, i - 1) - iClose(symbol, tf, i);
         energy += MathAbs(delta * vol);
      }
      energy_index = energy / trend_lookback;

      // 4. Direção de tendência (simplificada)
      double price_now = iClose(symbol, tf, 0);
      double price_past = iClose(symbol, tf, trend_lookback);
      if (price_now > price_past) is_uptrend = true;
      else if (price_now < price_past) is_downtrend = true;

      // 5. Fase Wyckoff (protótipo simples)
      if (energy_index > volume_threshold && is_uptrend)
         wyckoff_phase_detected = true;

      Log::Info("Análise de Mercado [" + symbol + "] TF: " + EnumToString(tf) +
                " | Volume: " + DoubleToString(current_volume, 2) +
                " | VWAP: " + DoubleToString(vwap_price, 5) +
                " | Energia: " + DoubleToString(energy_index, 2) +
                " | Tendência: " + (is_uptrend ? "Alta" : (is_downtrend ? "Baixa" : "Neutra")));
   }
}; 