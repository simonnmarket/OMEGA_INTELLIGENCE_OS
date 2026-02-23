
//+------------------------------------------------------------------+
//| QuantumDataFeed.mqh                                              |
//| Núcleo de Dados Institucional - Interface Padrão Goldman         |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_DATA_FEED_MQH__
#define __QUANTUM_DATA_FEED_MQH__

class QuantumDataFeed
{
private:
   bool m_isConnected;
   double m_dataQuality;

public:
   QuantumDataFeed()
   {
      m_isConnected = false;
      m_dataQuality = 0.0;
   }

   void Connect()
   {
      m_isConnected = CheckConnectivity();
   }

   bool IsAlive()
   {
      return m_isConnected;
   }

   double Fetch()
   {
      if (!m_isConnected)
         Connect();
      m_dataQuality = (MQLInfoInteger(MQL_TRADE_ALLOWED) ? 1.0 : 0.5);
      return m_dataQuality;
   }

   bool CheckConnectivity()
   {
      bool tradingAllowed = MQLInfoInteger(MQL_TRADE_ALLOWED);
      return tradingAllowed;
   }
};

#endif // __QUANTUM_DATA_FEED_MQH__
