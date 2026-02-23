// File: Include/Integration/PythonBridge.mqh
#ifndef INTEGRATION_PYTHONBRIDGE_MQH
#define INTEGRATION_PYTHONBRIDGE_MQH

//+------------------------------------------------------------------+
//| PythonBridge - Integração MT5 <--> Python via Socket TCP        |
//| Certificações: Apollo / Brookfield / DWS                        |
//| Finalidade: Comunicação com modelos externos (ML, GARCH, NLP)   |
//| Compatibilidade: MetaTrader 5 (Build ≥ 3045)                    |
//| Última atualização: 2025-07-02                                  |
//+------------------------------------------------------------------+

class PythonBridge
  {
private:
   int socket;
   string server_ip;
   int server_port;

public:
   PythonBridge(string ip = "127.0.0.1", int port = 9001)
     {
      server_ip   = ip;
      server_port = port;
     }

   bool Connect()
     {
      socket = SocketCreate();
      if(socket == INVALID_HANDLE)
        {
         Print("[PYTHON-BRIDGE] Erro ao criar socket");
         return false;
        }

      if(!SocketConnect(socket, server_ip, server_port))
        {
         Print("[PYTHON-BRIDGE] Conexão falhou: ", GetLastError());
         return false;
        }

      Print("[PYTHON-BRIDGE] Conectado com sucesso: ", server_ip, ":", server_port);
      return true;
     }

   bool SendRequest(string payload)
     {
      if(socket == INVALID_HANDLE)
         return false;
      return SocketSend(socket, payload);
     }

   string ReadResponse()
     {
      char buffer[2048];
      int bytes = SocketRead(socket, buffer, sizeof(buffer));
      if(bytes <= 0)
         return "";
      return CharArrayToString(buffer, bytes);
     }

   void Close()
     {
      if(socket != INVALID_HANDLE)
         SocketClose(socket);
     }
  };

#endif // INTEGRATION_PYTHONBRIDGE_MQH
