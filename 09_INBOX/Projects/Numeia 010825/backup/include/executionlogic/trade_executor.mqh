// ============================================================================
// ID: include/executionlogic
// Name: trade_executor.mqh
// Projeto: QuantumOmegaGodMode
// Versão: v1.1 Blindada + Retry + Spread Check + Timestamp
// Função: Executar ordens com base em sinais institucionais
// Criado em: 2025-07-13
// Atualizado: 2025-07-13
// Classificação: TIER-0 | Execução Institucional + Logger + Segurança
// ============================================================================

#ifndef __TRADE_EXECUTOR_MQH__
#define __TRADE_EXECUTOR_MQH__

#include "../../types/trade_signal_enum.mqh"
#include "../../utils/logger_institutional.mqh"

class trade_executor
{
private:
   logger_institutional &m_logger;

public:
   trade_executor(logger_institutional &logger) : m_logger(logger) {}

   void initialize()
   {
      m_logger.log_info("[trade_executor] Módulo de execução pronto.");
   }

   double CalculateDynamicDeviation()
   {
      double atr = iATR(_Symbol, PERIOD_M15, 14, 0);
      return NormalizeDouble(atr / _Point, 0);
   }

   bool execute_order(trade_signal signal, double volume)
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[trade_executor] Terminal desconectado.");
         return false;
      }

      if(volume <= 0.0)
      {
         m_logger.log_error("[trade_executor] Volume inválido.");
         return false;
      }

      RefreshRates();

      double spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(spread > 50)
      {
         m_logger.log_warning("[trade_executor] Spread anormal detectado: " + DoubleToString(spread));
         return false;
      }

      ENUM_ORDER_TYPE type = (signal == SIGNAL_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
      double price = (type == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                                              : SymbolInfoDouble(_Symbol, SYMBOL_BID);

      if(price <= 0)
      {
         m_logger.log_error("[trade_executor] Preço inválido.");
         return false;
      }

      price = NormalizeDouble(price, _Digits);
      datetime now = TimeCurrent();
      m_logger.log_info("Ordem enviada às " + TimeToString(now, TIME_MINUTES));

      MqlTradeRequest request;
      MqlTradeResult  result;
      ZeroMemory(request);
      ZeroMemory(result);

      request.action       = TRADE_ACTION_DEAL;
      request.symbol       = _Symbol;
      request.volume       = volume;
      request.type         = type;
      request.price        = price;
      request.deviation    = CalculateDynamicDeviation();
      request.type_filling = ORDER_FILLING_IOC;
      request.magic        = 123456;

      int attempts = 0;
      while(attempts < 3)
      {
         if(OrderSend(request, result) && result.retcode == TRADE_RETCODE_DONE)
         {
            m_logger.log_info("[trade_executor] Ordem executada com sucesso. Ticket: " + IntegerToString(result.order));
            return true;
         }
         m_logger.log_warning("[trade_executor] Tentativa " + IntegerToString(attempts+1) + " falhou: " + result.comment);
         Sleep(200);
         attempts++;
      }

      m_logger.log_error("[trade_executor] Falha total na execução após 3 tentativas.");
      return false;
   }
};

#endif // __TRADE_EXECUTOR_MQH__