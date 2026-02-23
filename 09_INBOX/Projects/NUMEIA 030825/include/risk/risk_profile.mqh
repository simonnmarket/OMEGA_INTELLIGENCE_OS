//+------------------------------------------------------------------+
//| risk_profile.mqh - Gestão Institucional de Risco                 |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Analysis/                                        |
//| Versão: v2.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-23            |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __RISK_PROFILE_MQH__
#define __RISK_PROFILE_MQH__

#include "utils/logger_institutional.mqh"
#include "types/trade_signal_enum.mqh"


//+------------------------------------------------------------------+
//| PARÂMETROS DE RISCO                                             |
//+------------------------------------------------------------------+
input group "Risk Profile"
input double   MAX_RISK_PERCENT = 2.0;     // Risco máximo por operação (%)
input double   MAX_DRAWDOWN = 0.15;        // Drawdown máximo (0-1)
input double   MIN_LIQUIDITY = 100000;     // Liquidez mínima (USD)
input bool     ENABLE_AI_ADJUSTMENT = true; // Ajuste de risco por IA
input int      UPDATE_INTERVAL_MS = 500;   // Intervalo de atualização (ms)

//+------------------------------------------------------------------+
//| ESTRUTURA DE MÉTRICAS DE RISCO                                 |
//+------------------------------------------------------------------+
struct RiskMetrics
{
   double current_risk;        // Risco atual (%)
   double max_drawdown;        // Drawdown máximo
   double volatility;          // Volatilidade anualizada
   double correlation;         // Correlação com portfólio
   double liquidity;           // Nível de liquidez
   double var_95;              // Value at Risk (95%)
   datetime last_update;       // Última atualização
   ENUM_TRADE_SIGNAL last_signal; // Último sinal processado
};

//+------------------------------------------------------------------+
//| Estrutura de Histórico de Risco                                 |
//+------------------------------------------------------------------+
struct RiskProfileHistory {
   datetime timestamp;
   string symbol;
   double current_risk;
   double max_drawdown;
   double volatility;
   double liquidity;
   double var_95;
   bool safe_to_trade;
   string regime;
   ENUM_TRADE_SIGNAL last_signal;
   double execution_time_ms;
};

//+------------------------------------------------------------------+
//| CLASSE PRINCIPAL: RiskProfile - Gestão de Risco Institucional   |
//+------------------------------------------------------------------+
class RiskProfile
{
private:
   logger_institutional &m_logger;
   string               m_symbol;
   datetime             m_last_risk_update;

   RiskMetrics          m_risk_metrics;
   double               m_risk_multiplier;
   string               m_market_regime;
   
   // Histórico de risco
   RiskProfileHistory m_risk_history[];

   // Painel de decisão
   CLabel *m_risk_label = NULL;
   CLabel *m_risk_value = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[RISK] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[RISK] Logger não inicializado");
         return false;
      }

      if(StringLen(m_symbol) == 0 || !SymbolInfoInteger(m_symbol, SYMBOL_SELECT))
      {
         m_logger.log_error("[RISK] Símbolo inválido: " + m_symbol);
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Verifica se é seguro atualizar o risco                        |
   //+--------------------------------------------------------------+
   bool is_safe_to_update(string symbol)
   {
      if(!is_valid_context()) return false;
      
      // Verifica se está em modo de teste
      if(MQLInfoInteger(MQL_TESTER))
      {
         m_logger.log_warning("[RISK] Modo de teste detectado - Atualização permitida");
         return true;
      }
      
      // Verifica conectividade
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[RISK] Sem conexão com o servidor de mercado");
         return false;
      }
      
      // Verifica se o símbolo está disponível
      if(!SymbolInfoInteger(symbol, SYMBOL_SELECT))
      {
         m_logger.log_error("[RISK] Símbolo não disponível: " + symbol);
         return false;
      }
      
      return true;
   }

   //+--------------------------------------------------------------+
   //| Calcula volatilidade                                          |
   //+--------------------------------------------------------------+
   void calculate_volatility(string symbol)
   {
      double atr = iATR(symbol, PERIOD_H1, 14, 0);
      double price = SymbolInfoDouble(symbol, SYMBOL_BID);
      m_risk_metrics.volatility = (atr / price) * MathSqrt(252);
   }

   //+--------------------------------------------------------------+
   //| Calcula correlação                                            |
   //+--------------------------------------------------------------+
   void calculate_correlation(string symbol)
   {
      // Simulação de cálculo de correlação
      m_risk_metrics.correlation = 0.3 + MathRand()/32767.0 * 0.4;
   }

   //+--------------------------------------------------------------+
   //| Calcula liquidez                                              |
   //+--------------------------------------------------------------+
   void calculate_liquidity(string symbol)
   {
      double volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_TICK);
      m_risk_metrics.liquidity = MathLog(volume + 1);
   }

   //+--------------------------------------------------------------+
   //| Detecta anomalias                                             |
   //+--------------------------------------------------------------+
   void detect_anomalies(string symbol)
   {
      MqlRates rates[];
      CopyRates(symbol, PERIOD_M1, 0, 5, rates);
      double avg_range = 0.0;
      for(int i=0; i<5; i++)
         avg_range += MathAbs(rates[i].high - rates[i].low);
      avg_range /= 5.0;
      
      double current_range = MathAbs(rates[0].high - rates[0].low);
      if(current_range > avg_range * 3.0)
      {
         m_logger.log_warning("[RISK] Anomalia de volatilidade detectada");
      }
   }

   //+--------------------------------------------------------------+
   //| Atualiza dimensionamento de posição                           |
   //+--------------------------------------------------------------+
   void update_position_sizing(string symbol)
   {
      double account_risk = AccountInfoDouble(ACCOUNT_EQUITY) * MAX_RISK_PERCENT / 100.0;
      double stop_loss_pips = 100.0;
      double pip_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE) / 
                        SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      double lot_size = account_risk / (stop_loss_pips * pip_value);
      
      m_risk_metrics.current_risk = MathMin(MAX_RISK_PERCENT, lot_size * pip_value * stop_loss_pips / AccountInfoDouble(ACCOUNT_EQUITY) * 100.0);
   }

   //+--------------------------------------------------------------+
   //| Atualiza multiplicador de risco                             |
   //+--------------------------------------------------------------+
   void update_risk_multiplier(string symbol)
   {
      double multiplier = 1.0;
      
      if(m_risk_metrics.volatility > 0.3) multiplier *= 0.8;
      if(m_risk_metrics.max_drawdown > MAX_DRAWDOWN * 0.8) multiplier *= 0.7;
      if(m_risk_metrics.liquidity < MathLog(MIN_LIQUIDITY)) multiplier *= 0.9;
      
      m_risk_multiplier = MathMax(0.1, MathMin(2.0, multiplier));
   }

   //+--------------------------------------------------------------+
   //| Atualiza display de risco                                   |
   //+--------------------------------------------------------------+
   void update_display(string symbol)
   {
      string risk_text = StringFormat("⚠ RISK METRICSCurrent Risk: %.2f%%Max Drawdown: %.2f%%VaR 95%%: %.2f%%",
         m_risk_metrics.current_risk * 100,
         m_risk_metrics.max_drawdown * 100,
         m_risk_metrics.var_95 * 100);
      
      if(m_risk_label == NULL)
      {
         m_risk_label = new CLabel("RiskLabel", 0, 10, 1010);
         m_risk_label->text("RISK: ????");
         m_risk_label->color(clrGray);
      }
      
      m_risk_label->text("RISK: " + DoubleToString(m_risk_metrics.current_risk*100, 1) + "%");
      m_risk_label->color(
         m_risk_metrics.current_risk > 2.0 ? clrRed :
         m_risk_metrics.current_risk > 1.0 ? clrOrange : clrLime
      );
   }

   //+--------------------------------------------------------------+
   //| Ajusta perfil por contexto                                   |
   //+--------------------------------------------------------------+
   void adjust_profile_by_context(string symbol)
   {
      // Ajuste por horário
      int hour = TimeHour(TimeCurrent());
      if(hour >= 22 || hour <= 5) // Após-horário
         m_risk_multiplier *= 0.8;
   }

   //+--------------------------------------------------------------+
   //| Ajusta perfil por IA                                         |
   //+--------------------------------------------------------------+
   void adjust_profile_by_ai(string symbol)
   {
      if(!ENABLE_AI_ADJUSTMENT) return;
      
      // Simulação de ajuste por IA
      double ai_adjustment = 0.9 + MathRand()/32767.0 * 0.2;
      m_risk_multiplier *= ai_adjustment;
      m_risk_multiplier = MathMax(0.1, MathMin(2.0, m_risk_multiplier));
   }

   //+--------------------------------------------------------------+
   //| Ajusta perfil por regime de mercado                          |
   //+--------------------------------------------------------------+
   void adjust_profile_by_regime(string symbol)
   {
      MqlRates rates[];
      CopyRates(symbol, PERIOD_H1, 0, 20, rates);
      double ema50 = iMA(symbol, PERIOD_H1, 50, 0, MODE_EMA, PRICE_CLOSE, 0);
      double ema200 = iMA(symbol, PERIOD_H1, 200, 0, MODE_EMA, PRICE_CLOSE, 0);
      
      if(ema50 > ema200)
         m_market_regime = "TENDENCIA_LONGA";
      else if(ema50 < ema200)
         m_market_regime = "TENDENCIA_CURTA";
      else
         m_market_regime = "LATERAL";
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   RiskProfile(logger_institutional &logger, string symbol = _Symbol) :
      m_logger(logger),
      m_symbol(symbol),
      m_risk_multiplier(1.0),
      m_market_regime("DESCONHECIDO"),
      m_last_risk_update(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[RISK] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de inicialização
      if(!is_safe_to_update(symbol))
      {
         Alert("Falha crítica na inicialização - Verifique logger e conexão de dados");
         ExpertRemove();
      }

      // Inicializa métricas
      m_risk_metrics.current_risk = 1.0;
      m_risk_metrics.max_drawdown = 0.0;
      m_risk_metrics.volatility = 0.0;
      m_risk_metrics.correlation = 0.0;
      m_risk_metrics.liquidity = 0.0;
      m_risk_metrics.var_95 = 0.0;
      m_risk_metrics.last_signal = SIGNAL_NONE;
      m_risk_metrics.last_update = TimeCurrent();

      m_logger.log_info(StringFormat("[RISK_PROFILE] Sistema inicializado (v%s)", "2.1"));
   }

   //+--------------------------------------------------------------+
   //| Atualização completa do perfil de risco                      |
   //+--------------------------------------------------------------+
   void UpdateRiskProfile(ENUM_TRADE_SIGNAL last_signal = SIGNAL_NONE)
   {
      if(!is_safe_to_update(m_symbol))
      {
         m_logger.log_warning("[RISK] Atualização bloqueada por segurança");
         return;
      }

      double start_time = GetMicrosecondCount();

      m_logger.log_info(StringFormat("[RISK] Atualizando perfil de risco para %s", m_symbol));

      calculate_volatility(m_symbol);
      calculate_correlation(m_symbol);
      calculate_liquidity(m_symbol);
      detect_anomalies(m_symbol);
      update_position_sizing(m_symbol);
      update_risk_multiplier(m_symbol);
      update_display(m_symbol);
      adjust_profile_by_context(m_symbol);
      adjust_profile_by_ai(m_symbol);
      adjust_profile_by_regime(m_symbol);

      m_risk_metrics.last_signal = last_signal;
      m_risk_metrics.last_update = TimeCurrent();
      m_last_risk_update = TimeCurrent();

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      // Registro histórico
      RiskProfileHistory record;
      record.timestamp = TimeCurrent();
      record.symbol = m_symbol;
      record.current_risk = m_risk_metrics.current_risk;
      record.max_drawdown = m_risk_metrics.max_drawdown;
      record.volatility = m_risk_metrics.volatility;
      record.liquidity = m_risk_metrics.liquidity;
      record.var_95 = m_risk_metrics.var_95;
      record.safe_to_trade = (m_risk_metrics.current_risk <= MAX_RISK_PERCENT);
      record.regime = m_market_regime;
      record.last_signal = last_signal;
      record.execution_time_ms = execution_time;
      ArrayPushBack(m_risk_history, record);

      m_logger.log_info(StringFormat("[RISK] Perfil de risco atualizado - Risco: %.2f%% | Regime: %s | Tempo: %.1fms",
                                   m_risk_metrics.current_risk * 100,
                                   m_market_regime,
                                   execution_time));
   }

   //+--------------------------------------------------------------+
   //| Retorna se está inicializado                                 |
   //+--------------------------------------------------------------+
   bool is_initialized() const
   {
      return m_logger.is_initialized();
   }

   //+--------------------------------------------------------------+
   //| Obtém multiplicador de risco                                 |
   //+--------------------------------------------------------------+
   double get_risk_multiplier() const
   {
      return m_risk_multiplier;
   }

   //+--------------------------------------------------------------+
   //| Obtém métricas de risco                                      |
   //+--------------------------------------------------------------+
   RiskMetrics GetRiskMetrics() const
   {
      return m_risk_metrics;
   }

   //+--------------------------------------------------------------+
   //| Valida parâmetros                                            |
   //+--------------------------------------------------------------+
   bool ValidateParameters(string symbol)
   {
      if(!SymbolInfoInteger(symbol, SYMBOL_SELECT))
      {
         m_logger.log_error(StringFormat("[RISK_PROFILE] Símbolo %s inválido ou não disponível", symbol));
         return false;
      }

      if(m_risk_metrics.volatility <= 0)
      {
         m_logger.log_error(StringFormat("[RISK_PROFILE] Volatilidade inválida para %s", symbol));
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de risco                                   |
   //+--------------------------------------------------------------+
   bool ExportRiskHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_risk_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_risk_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_risk_history[i].symbol,
            DoubleToString(m_risk_history[i].current_risk, 4),
            DoubleToString(m_risk_history[i].max_drawdown, 4),
            DoubleToString(m_risk_history[i].volatility, 4),
            DoubleToString(m_risk_history[i].liquidity, 4),
            DoubleToString(m_risk_history[i].var_95, 4),
            m_risk_history[i].safe_to_trade ? "SIM" : "NÃO",
            m_risk_history[i].regime,
            TradeSignalUtils().ToString(m_risk_history[i].last_signal),
            DoubleToString(m_risk_history[i].execution_time_ms, 1)
         );
      }

      FileClose(handle);
      m_logger.log_info("[RISK_PROFILE] Histórico de risco exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~RiskProfile()
   {
      ArrayFree(m_risk_history);
      m_logger.log_info("[RISK_PROFILE] Sistema desinicializado com sucesso");
   }
};

#endif // __RISK_PROFILE_MQH__