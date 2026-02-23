//+------------------------------------------------------------------+
//|                                           SkyIntelBridge.mqh      |
//|              Ponte de Integração com Sistema SkyIntel            |
//+------------------------------------------------------------------+
#ifndef __SKY_INTEL_BRIDGE_MQH__
#define __SKY_INTEL_BRIDGE_MQH__

#include "../../Utils/Log.mqh"

//+------------------------------------------------------------------+
//| Constantes de Sinais                                             |
//+------------------------------------------------------------------+
#define SIGNAL_NONE        0
#define SIGNAL_SPIKE_LONG  1
#define SIGNAL_SPIKE_SHORT 2
#define SIGNAL_UNCERTAIN   3

//+------------------------------------------------------------------+
//| Classe: SkyIntelBridge                                           |
//+------------------------------------------------------------------+
class SkyIntelBridge
{
private:
   bool m_isInitialized;
   bool m_skyIntelEnabled;

public:
   // Construtor
   SkyIntelBridge() : m_isInitialized(false), m_skyIntelEnabled(true) {}
   
   // Destrutor
   ~SkyIntelBridge() {}

   // Inicialização
   bool Init()
   {
      AuditLog("[SkyIntelBridge] Inicializando ponte de integração...", LOG_LEVEL_INFO);
      m_isInitialized = true;
      AuditLog("[SkyIntelBridge] Ponte inicializada com sucesso", LOG_LEVEL_INFO);
      return true;
   }

   // Verificar se está inicializado
   bool IsInitialized() const { return m_isInitialized; }

   // Habilitar/Desabilitar SkyIntel
   void EnableSkyIntel(bool enable) { m_skyIntelEnabled = enable; }
   bool IsSkyIntelEnabled() const { return m_skyIntelEnabled; }

   // Processar sinais do SkyIntel
   void ProcessSkyIntelSignals()
   {
      if(!m_isInitialized || !m_skyIntelEnabled)
         return;

      AuditLog("[SkyIntelBridge] Processando sinais do SkyIntel...", LOG_LEVEL_DEBUG);
   }

   // Obter status do SkyIntel
   string GetSkyIntelStatus()
   {
      if(!m_isInitialized)
         return "NÃO_INICIALIZADO";
      
      if(!m_skyIntelEnabled)
         return "DESABILITADO";
      
      return "ATIVO";
   }

   // Encerramento
   void OnDeinit()
   {
      AuditLog("[SkyIntelBridge] Encerrando ponte de integração...", LOG_LEVEL_INFO);
      m_isInitialized = false;
   }

   int GetStrategicSignal(string symbol) {
      // Verificar se SkyIntel está ativo
      if (!m_skyIntelEnabled) {
         AuditLog("[SkyIntelBridge] SkyIntel desativado pelo operador.");
         return SIGNAL_NONE;
      }

      // Obter sinal estratégico
      int signal = SIGNAL_NONE;
      
      if (m_skyIntelEnabled) {
         signal = EvaluateSkyIntelSignal(symbol);
         
         if (signal != SIGNAL_NONE) {
            AuditLog("[SkyIntelBridge] Sinal SkyIntel detectado: " + GetSignalName(signal));
         }
      } else {
         AuditLog("[SkyIntelBridge] Sinal SkyIntel bloqueado por compliance", LOG_LEVEL_WARN);
      }

      return signal;
   }

private:
   int EvaluateSkyIntelSignal(string symbol) {
      // Implementação simplificada de avaliação de sinais
      return SIGNAL_NONE;
   }

   string GetSignalName(int signal) {
      switch (signal) {
         case SIGNAL_SPIKE_LONG:  return "SPIKE_LONG";
         case SIGNAL_SPIKE_SHORT: return "SPIKE_SHORT";
         case SIGNAL_UNCERTAIN:   return "UNCERTAIN";
         default:                 return "NONE";
      }
   }
};

#endif // __SKY_INTEL_BRIDGE_MQH__ 