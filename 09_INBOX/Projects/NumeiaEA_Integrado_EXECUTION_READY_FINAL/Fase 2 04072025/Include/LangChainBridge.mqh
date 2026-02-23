// File: Include/Integration/LangChainBridge.mqh
#ifndef INTEGRATION_LANGCHAINBRIDGE_MQH
#define INTEGRATION_LANGCHAINBRIDGE_MQH

#include "PythonBridge.mqh"
#include "BridgeDiagnostics.mqh"

//+------------------------------------------------------------------+
//| LangChainBridge - Integração com LangChain                      |
//| Certificações: Apollo / Brookfield                              |
//| Função: Enviar contextos e receber respostas LLM via Python     |
//| Requisitos: Backend Python com endpoint /langchain              |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                    |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+

class LangChainBridge
  {
private:
   PythonBridge *bridge;

public:
   LangChainBridge()
     {
      bridge = new PythonBridge();
     }

   bool Connect()
     {
      bool status = bridge.Connect("127.0.0.1", 5051);  // Porta reservada LangChain API
      BridgeDiagnostics::LogConnectionStatus(status, "LangChainBridge");
      return status;
     }

   string SendPrompt(string context)
     {
      if(bridge == NULL)
         return "ERROR: Bridge não inicializado.";

      bridge.Send(context);
      BridgeDiagnostics::LogMessageSent(context, "LangChainBridge");

      string response = bridge.Receive();
      BridgeDiagnostics::LogMessageReceived(response, "LangChainBridge");
      return response;
     }

   void Disconnect()
     {
      if(bridge != NULL)
        {
         delete bridge;
         bridge = NULL;
        }
     }
  };

#endif // INTEGRATION_LANGCHAINBRIDGE_MQH
