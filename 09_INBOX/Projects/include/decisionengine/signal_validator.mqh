// include/decisionengine/signal_validator.mqh

#ifndef __SIGNAL_VALIDATOR_MQH__
#define __SIGNAL_VALIDATOR_MQH__

#include <Trade\SymbolInfo.mqh>

class signal_validator {
public:
   bool is_spoofing_detected() {
      double mfi = iBWMFI(_Symbol, PERIOD_M1, 0);
      double vol = iVolume(_Symbol, PERIOD_M1, 0);
      double avg = iMA(_Symbol, PERIOD_M1, 14, 0, MODE_SMA, PRICE_VOLUME, 0);
      if(avg <= 0) return false;
      return (mfi > 80.0 && vol < 0.5 * avg);
   }

   bool is_volume_valid(double minVolume = 10000.0) {
      double volume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME);
      return (volume >= minVolume);
   }

   bool is_atr_within_range(double maxATR = 0.0020) {
      double atr = iATR(_Symbol, PERIOD_M15, 14, 0);
      return (atr < maxATR);
   }

   bool validate_signal() {
      return (!is_spoofing_detected() && is_volume_valid() && is_atr_within_range());
   }
};

#endif