//+------------------------------------------------------------------+
//| Converter sinal para string                                       |
//+------------------------------------------------------------------+
string SignalToString(ENUM_APOLLO11_SIGNAL signal)
{
   switch(signal)
   {
      case SIGNAL_BUY:  return "BUY";
      case SIGNAL_SELL: return "SELL";
      default:          return "NONE";
   }
}
