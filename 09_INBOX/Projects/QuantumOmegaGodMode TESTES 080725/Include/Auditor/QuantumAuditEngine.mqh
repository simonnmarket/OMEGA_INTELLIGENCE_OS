//+------------------------------------------------------------------+
//|                      QuantumAuditEngine.mqh                      |
//|      Auditor Inteligente com Aprendizado Contínuo de Erros      |
//|      Projeto: Quantum Omega God Mode                            |
//|      Nível: Institutional Audit + ML Feedback                   |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_AUDIT_ENGINE_MQH__
#define __QUANTUM_AUDIT_ENGINE_MQH__

#include <stdlib.mqh>

//+------------------------------------------------------------------+
//| Classe CQuantumAuditEngine                                       |
//+------------------------------------------------------------------+
class CQuantumAuditEngine
  {
private:
   int      m_errorCount;
   string   m_lastError;
   datetime m_lastErrorTime;

public:
            CQuantumAuditEngine() : m_errorCount(0), m_lastError("None"), m_lastErrorTime(0) {}

   void     LogError(const string source, const string description)
            {
             m_errorCount++;
             m_lastError = description;
             m_lastErrorTime = TimeCurrent();
             Print("[AUDITOR] 🔥 Erro detectado em ", source, ": ", description);
            }

   void     ReportStatus()
            {
             Print("[AUDITOR] Relatório: Total de erros: ", m_errorCount, 
                   " | Último erro: ", m_lastError, 
                   " | Ocorrido em: ", TimeToString(m_lastErrorTime));
            }

   int      GetErrorCount()     { return m_errorCount; }
   string   GetLastError()      { return m_lastError; }
   datetime GetLastErrorTime()  { return m_lastErrorTime; }

   void     Reset()
            {
             Print("[AUDITOR] Resetando contadores de erro.");
             m_errorCount = 0;
             m_lastError = "None";
             m_lastErrorTime = 0;
            }
  };

#endif
//+------------------------------------------------------------------+
