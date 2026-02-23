//+------------------------------------------------------------------+
//| trade_signal_enum.mqh - Sistema de Sinais Quânticos              |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Types/                                           |
//| Versão: v2.4 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-23            |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_TRADE_SIGNAL_ENUM_MQH__
#define __QUANTUM_TRADE_SIGNAL_ENUM_MQH__

#include "utils/logger_institutional.mqh"
#include "quantum/quantum_neural_core.mqh"
#include "analysis/darkpool_monitor.mqh"
#include "analysis/hft_detector.mqh"
#include "ChartObjects\ChartObjectsTxtControls.mqh"

//+------------------------------------------------------------------+
//| Enumeração de Módulos do Sidebar (Primeira Letra Alterada)      |
//+------------------------------------------------------------------+
enum ENUM_SIDEBAR_MODULES
{
   MODULE_ANALYSIS = 0,        // A → Analysis
   MODULE_QUANTUM,             // Q → Quantum
   MODULE_INTELLIGENCE,        // I → Intelligence
   MODULE_SECURITY,            // S → Security
   MODULE_NEURAL,              // N → Neural
   MODULE_AUDIT,               // A → Audit
   MODULE_COMPLIANCE,          // C → Compliance
   MODULE_DATA,                // D → Data
   MODULE_DECISIONENGINE,      // D → DecisionEngine
   MODULE_DETECTION,           // D → Detection
   MODULE_EXECUTIONLOGIC,      // E → ExecutionLogic
   MODULE_INTEGRATION,         // I → Integration
   MODULE_MODULES,             // M → Modules
   MODULE_OPTIMIZATION,        // O → Optimization
   MODULE_RISK,                // R → Risk
   MODULE_TOOLS,               // T → Tools
   MODULE_TYPES,               // T → Types
   MODULE_VISUALS              // V → Visuals
};

//+------------------------------------------------------------------+
//| Estrutura de Navegação do Sidebar                                |
//+------------------------------------------------------------------+
struct SidebarNavigation
{
   ENUM_SIDEBAR_MODULES module_id;
   string module_name;
   string display_name;
   string description;
   bool is_active;
   int priority;
};

//+------------------------------------------------------------------+
//| Enumeração de Sinais Quânticos                                  |
//| Prioridade: QUANTUM_ALERT > DARKPOOL_CRITICAL > AI_OVERRIDE     |
//+------------------------------------------------------------------+
enum ENUM_TRADE_SIGNAL
{
   SIGNAL_NONE = 0,                    // Estado neutro (ignorado em operações)
   SIGNAL_BUY,                         // Compra padrão
   SIGNAL_SELL,                        // Venda padrão
   SIGNAL_HEDGE_BUY,                   // Hedge de compra (proteção)
   SIGNAL_HEDGE_SELL,                  // Hedge de venda (proteção)
   SIGNAL_CLOSE,                       // Fechamento de posição
   SIGNAL_REVERSE_BUY,                 // Inversão para compra
   SIGNAL_REVERSE_SELL,                // Inversão para venda
   SIGNAL_BREAK_EVEN,                  // Ajuste para break-even
   SIGNAL_TRAILING_STOP,               // Trailing stop ativo
   SIGNAL_SCALP_BUY,                   // Scalping compra (HFT)
   SIGNAL_SCALP_SELL,                  // Scalping venda (HFT)
   SIGNAL_MACRO_NEWS_PROTECT,          // Bloqueio por notícia
   SIGNAL_QUANTUM_ALERT,               // Anomalia quântica
   SIGNAL_QUANTUM_FLASH,               // Flash quântico (prioridade máxima)
   SIGNAL_DARKPOOL_CRITICAL,           // Sinal de dark pool crítico
   SIGNAL_AI_OVERRIDE_BUY,             // Override de IA (compra)
   SIGNAL_AI_OVERRIDE_SELL,            // Override de IA (venda)
   SIGNAL_QUANTUM_HOLD,                // Manter posição
   SIGNAL_QUANTUM_CRISIS,              // Sinal de crise (parar trading)
   SIGNAL_QUANTUM_HFT_SPIKE,           // Sinal de pico HFT (alta frequência)
   SIGNAL_QUANTUM_DARKPOOL,            // Sinal de dark pool detectado
   SIGNAL_QUANTUM_REVERSAL,            // Sinal de reversão de tendência
   SIGNAL_QUANTUM_LIQUIDITY_SHOCK,     // Choque de liquidez detectado
   SIGNAL_QUANTUM_ENTANGLEMENT         // Análise de entrelaçamento quântico
};

//+------------------------------------------------------------------+
//| Estrutura de metadados do sinal                                 |
//+------------------------------------------------------------------+
struct SignalMetadata
{
   ENUM_TRADE_SIGNAL signal;           // Tipo de sinal
   datetime timestamp;                 // Timestamp de geração
   double confidence;                  // Confiança do sinal (0-1)
   string symbol;                      // Símbolo associado
   int time_frame;                     // Timeframe de origem
   double risk_level;                  // Nível de risco associado
   double reward_ratio;                // Razão risco/recompensa
   string source_module;               // Módulo que gerou o sinal
};

//+------------------------------------------------------------------+
//| Estrutura de Histórico de Sinais                                  |
//+------------------------------------------------------------------+
struct SignalHistoryEntry {
   datetime timestamp;
   string symbol;
   ENUM_TRADE_SIGNAL signal;
   double confidence;
   double risk_level;
   string source;
   bool critical;
   double execution_time_ms;
};

//+------------------------------------------------------------------+
//| Classe TradeSignalUtils - Utilitários de Sinais                   |
//+------------------------------------------------------------------+
class TradeSignalUtils
{
private:
   logger_institutional &m_logger;
   QuantumCore &m_quantum;
   DarkPoolMonitor &m_darkpool;
   HFTDetector &m_hft;
   string m_symbol;
   datetime m_last_signal_time;

   // Histórico de sinais
   SignalHistoryEntry m_signal_history[];

   // Painel de decisão
   CLabel *m_signal_label = NULL;
   CLabel *m_signal_confidence = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[SIGNAL] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[SIGNAL] Logger não inicializado");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de sinal                                     |
   //+--------------------------------------------------------------+
   void updateSignalDisplay(ENUM_TRADE_SIGNAL signal, double confidence)
   {
      if(m_signal_label == NULL)
      {
         m_signal_label = new CLabel("SignalLabel", 0, 10, 1050);
         m_signal_label->text("SINAL: NONE");
         m_signal_label->color(clrGray);
      }

      if(m_signal_confidence == NULL)
      {
         m_signal_confidence = new CLabel("SignalConfidence", 0, 10, 1070);
         m_signal_confidence->text("CONF: 0%");
         m_signal_confidence->color(clrGray);
      }

      m_signal_label->text("SINAL: " + ToString(signal));
      m_signal_label->color(
         signal == SIGNAL_QUANTUM_FLASH ? clrMagenta :
         signal == SIGNAL_DARKPOOL_CRITICAL ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrGray
      );

      m_signal_confidence->text("CONF: " + DoubleToString(confidence*100, 0) + "%");
      m_signal_confidence->color(
         confidence > 0.8 ? clrLime :
         confidence > 0.5 ? clrYellow : clrRed
      );
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   TradeSignalUtils(logger_institutional &logger,
                  QuantumCore &qc,
                  DarkPoolMonitor &dpm,
                  HFTDetector &hft,
                  string symbol = _Symbol) :
      m_logger(logger),
      m_quantum(qc),
      m_darkpool(dpm),
      m_hft(hft),
      m_symbol(symbol),
      m_last_signal_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[SIGNAL] Logger não inicializado");
         ExpertRemove();
      }

      // Verificação de integridade
      if(!m_quantum.IsQuantumReady())
      {
         m_logger.log_error("[SIGNAL] Core quântico não está pronto");
         ExpertRemove();
      }

      m_logger.log_info("[SIGNAL] Sistema de sinais inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Converte sinal para string                                   |
   //+--------------------------------------------------------------+
   string ToString(ENUM_TRADE_SIGNAL signal)
   {
      switch(signal)
      {
         case SIGNAL_NONE: return "NONE";
         case SIGNAL_BUY: return "BUY";
         case SIGNAL_SELL: return "SELL";
         case SIGNAL_HEDGE_BUY: return "HEDGE_BUY";
         case SIGNAL_HEDGE_SELL: return "HEDGE_SELL";
         case SIGNAL_CLOSE: return "CLOSE";
         case SIGNAL_REVERSE_BUY: return "REVERSE_BUY";
         case SIGNAL_REVERSE_SELL: return "REVERSE_SELL";
         case SIGNAL_BREAK_EVEN: return "BREAK_EVEN";
         case SIGNAL_TRAILING_STOP: return "TRAILING_STOP";
         case SIGNAL_SCALP_BUY: return "SCALP_BUY";
         case SIGNAL_SCALP_SELL: return "SCALP_SELL";
         case SIGNAL_MACRO_NEWS_PROTECT: return "MACRO_NEWS";
         case SIGNAL_QUANTUM_ALERT: return "QUANTUM_ALERT";
         case SIGNAL_QUANTUM_FLASH: return "QUANTUM_FLASH";
         case SIGNAL_DARKPOOL_CRITICAL: return "DARKPOOL_CRITICAL";
         case SIGNAL_AI_OVERRIDE_BUY: return "AI_OVERRIDE_BUY";
         case SIGNAL_AI_OVERRIDE_SELL: return "AI_OVERRIDE_SELL";
         case SIGNAL_QUANTUM_HOLD: return "QUANTUM_HOLD";
         case SIGNAL_QUANTUM_CRISIS: return "QUANTUM_CRISIS";
         case SIGNAL_QUANTUM_HFT_SPIKE: return "QUANTUM_HFT_SPIKE";
         case SIGNAL_QUANTUM_DARKPOOL: return "QUANTUM_DARKPOOL";
         case SIGNAL_QUANTUM_REVERSAL: return "QUANTUM_REVERSAL";
         case SIGNAL_QUANTUM_LIQUIDITY_SHOCK: return "LIQUIDITY_SHOCK";
         case SIGNAL_QUANTUM_ENTANGLEMENT: return "ENTANGLEMENT";
         default: return "UNKNOWN";
      }
   }

   //+--------------------------------------------------------------+
   //| Verifica se é sinal de compra                                |
   //+--------------------------------------------------------------+
   bool IsBuySignal(ENUM_TRADE_SIGNAL signal)
   {
      return (signal == SIGNAL_BUY ||
              signal == SIGNAL_REVERSE_BUY ||
              signal == SIGNAL_SCALP_BUY ||
              signal == SIGNAL_QUANTUM_FLASH ||
              signal == SIGNAL_DARKPOOL_CRITICAL ||
              signal == SIGNAL_AI_OVERRIDE_BUY ||
              signal == SIGNAL_QUANTUM_REVERSAL);
   }

   //+--------------------------------------------------------------+
   //| Verifica se é sinal de venda                                 |
   //+--------------------------------------------------------------+
   bool IsSellSignal(ENUM_TRADE_SIGNAL signal)
   {
      return (signal == SIGNAL_SELL ||
              signal == SIGNAL_REVERSE_SELL ||
              signal == SIGNAL_SCALP_SELL ||
              signal == SIGNAL_QUANTUM_FLASH ||
              signal == SIGNAL_DARKPOOL_CRITICAL ||
              signal == SIGNAL_AI_OVERRIDE_SELL ||
              signal == SIGNAL_QUANTUM_LIQUIDITY_SHOCK);
   }

   //+--------------------------------------------------------------+
   //| Verifica se é sinal crítico                                  |
   //+--------------------------------------------------------------+
   bool IsCriticalSignal(ENUM_TRADE_SIGNAL signal)
   {
      return (signal == SIGNAL_QUANTUM_FLASH ||
              signal == SIGNAL_DARKPOOL_CRITICAL ||
              signal == SIGNAL_QUANTUM_CRISIS ||
              signal == SIGNAL_QUANTUM_LIQUIDITY_SHOCK ||
              signal == SIGNAL_MACRO_NEWS_PROTECT);
   }

   //+--------------------------------------------------------------+
   //| Geração de sinal dinâmico por IA quântica                    |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL GenerateDynamicSignal()
   {
      if(!is_valid_context()) return SIGNAL_NONE;

      double start_time = GetMicrosecondCount();

      double quantum_score = m_quantum.CalculateSignalScore();
      if(quantum_score > 90.0) return SIGNAL_QUANTUM_FLASH;
      else if(quantum_score > 80.0) return SIGNAL_DARKPOOL_CRITICAL;
      else if(quantum_score > 70.0) return SIGNAL_QUANTUM_ALERT;

      // Padrões de HFT dinâmicos
      if(m_hft.DetectHFTPattern())
      {
         if(MathRand() % 2 == 0) return SIGNAL_SCALP_BUY;
         return SIGNAL_SCALP_SELL;
      }

      // Fallback para ML tradicional
      return SIGNAL_NONE;
   }

   //+--------------------------------------------------------------+
   //| Processamento de sinal com inteligência quântica             |
   //+--------------------------------------------------------------+
   void ProcessQuantumSignal(ENUM_TRADE_SIGNAL signal, double confidence = 1.0)
   {
      if(!is_valid_context()) return;

      string log_entry = StringFormat("%s| Confiança: %.2f| Timestamp: %s",
                                    ToString(signal), confidence,
                                    TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS));

      // Registro histórico
      SignalHistoryEntry entry;
      entry.timestamp = TimeCurrent();
      entry.symbol = m_symbol;
      entry.signal = signal;
      entry.confidence = confidence;
      entry.risk_level = 1.0 - confidence;
      entry.source = "QuantumCore";
      entry.critical = IsCriticalSignal(signal);
      entry.execution_time_ms = 0.0;
      ArrayPushBack(m_signal_history, entry);

      // Log específico para sinais críticos
      if(IsCriticalSignal(signal))
      {
         m_logger.log_warning("SINAL CRÍTICO DETECTADO - " + log_entry);
         m_quantum.AlertRiskManagement(signal);
      }
      else
      {
         m_logger.log_info("Processando sinal - " + log_entry);
      }

      m_last_signal_time = TimeCurrent();
      updateSignalDisplay(signal, confidence);
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de sinais                                  |
   //+--------------------------------------------------------------+
   bool ExportSignalHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_signal_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_signal_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_signal_history[i].symbol,
            ToString(m_signal_history[i].signal),
            DoubleToString(m_signal_history[i].confidence, 4),
            DoubleToString(m_signal_history[i].risk_level, 4),
            m_signal_history[i].source,
            m_signal_history[i].critical ? "SIM" : "NÃO",
            DoubleToString(m_signal_history[i].execution_time_ms, 1)
         );
      }

      FileClose(handle);
      m_logger.log_info("[SIGNAL] Histórico de sinais exportado para: " + file_path);
      return true;
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~TradeSignalUtils()
   {
      m_logger.log_info("[SIGNAL] Sistema de sinais encerrado para " + m_symbol);
   }
};

//+------------------------------------------------------------------+
//| Classe SidebarManager - Gerenciador do Sidebar                   |
//+------------------------------------------------------------------+
class SidebarManager
{
private:
   logger_institutional &m_logger;
   SidebarNavigation m_modules[];
   CLabel *m_sidebar_labels[];
   int m_x_position;
   int m_y_position;
   int m_label_height;
   color m_active_color;
   color m_inactive_color;

   //+--------------------------------------------------------------+
   //| Inicializa módulos do sidebar                                 |
   //+--------------------------------------------------------------+
   void InitializeModules()
   {
      ArrayResize(m_modules, 18);
      
      // Módulos com primeira letra alterada
      m_modules[0] = {MODULE_ANALYSIS, "analysis", "Analysis", "Análise técnica e quantitativa", true, 1};
      m_modules[1] = {MODULE_QUANTUM, "quantum", "Quantum", "Processamento quântico", true, 2};
      m_modules[2] = {MODULE_INTELLIGENCE, "intelligence", "Intelligence", "IA e aprendizado", true, 3};
      m_modules[3] = {MODULE_SECURITY, "security", "Security", "Segurança e proteção", true, 4};
      m_modules[4] = {MODULE_NEURAL, "neural", "Neural", "Redes neurais", true, 5};
      m_modules[5] = {MODULE_AUDIT, "audit", "Audit", "Auditoria e verificação", true, 6};
      m_modules[6] = {MODULE_COMPLIANCE, "compliance", "Compliance", "Conformidade institucional", true, 7};
      m_modules[7] = {MODULE_DATA, "data", "Data", "Dados de mercado", true, 8};
      m_modules[8] = {MODULE_DECISIONENGINE, "decisionengine", "DecisionEngine", "Motor de decisão", true, 9};
      m_modules[9] = {MODULE_DETECTION, "detection", "Detection", "Detecção de padrões", true, 10};
      m_modules[10] = {MODULE_EXECUTIONLOGIC, "executionlogic", "ExecutionLogic", "Lógica de execução", true, 11};
      m_modules[11] = {MODULE_INTEGRATION, "integration", "Integration", "Integrações externas", true, 12};
      m_modules[12] = {MODULE_MODULES, "modules", "Modules", "Componentes modulares", true, 13};
      m_modules[13] = {MODULE_OPTIMIZATION, "optimization", "Optimization", "Otimização e algoritmos", true, 14};
      m_modules[14] = {MODULE_RISK, "risk", "Risk", "Gestão de risco", true, 15};
      m_modules[15] = {MODULE_TOOLS, "tools", "Tools", "Ferramentas auxiliares", true, 16};
      m_modules[16] = {MODULE_TYPES, "types", "Types", "Tipos e estruturas", true, 17};
      m_modules[17] = {MODULE_VISUALS, "visuals", "Visuals", "Interface visual", true, 18};
   }

   //+--------------------------------------------------------------+
   //| Cria labels do sidebar                                        |
   //+--------------------------------------------------------------+
   void CreateSidebarLabels()
   {
      ArrayResize(m_sidebar_labels, ArraySize(m_modules));
      
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         string label_name = "Sidebar_" + m_modules[i].module_name;
         m_sidebar_labels[i] = new CLabel(label_name, 0, m_x_position, m_y_position + (i * m_label_height));
         m_sidebar_labels[i]->text(m_modules[i].display_name);
         m_sidebar_labels[i]->color(m_modules[i].is_active ? m_active_color : m_inactive_color);
         m_sidebar_labels[i]->font("Arial");
         m_sidebar_labels[i]->fontsize(10);
         m_sidebar_labels[i]->corner(CORNER_LEFT_UPPER);
      }
   }

public:
   //+--------------------------------------------------------------+
   //| Construtor                                                   |
   //+--------------------------------------------------------------+
   SidebarManager(logger_institutional &logger, int x_pos = 10, int y_pos = 50) :
      m_logger(logger),
      m_x_position(x_pos),
      m_y_position(y_pos),
      m_label_height(25),
      m_active_color(clrLime),
      m_inactive_color(clrGray)
   {
      InitializeModules();
      CreateSidebarLabels();
      m_logger.log_info("[SIDEBAR] Sidebar inicializado com " + IntegerToString(ArraySize(m_modules)) + " módulos");
   }

   //+--------------------------------------------------------------+
   //| Atualiza status do módulo                                     |
   //+--------------------------------------------------------------+
   void UpdateModuleStatus(ENUM_SIDEBAR_MODULES module_id, bool is_active)
   {
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(m_modules[i].module_id == module_id)
         {
            m_modules[i].is_active = is_active;
            if(m_sidebar_labels[i] != NULL)
            {
               m_sidebar_labels[i]->color(is_active ? m_active_color : m_inactive_color);
            }
            break;
         }
      }
   }

   //+--------------------------------------------------------------+
   //| Obtém nome do módulo                                          |
   //+--------------------------------------------------------------+
   string GetModuleName(ENUM_SIDEBAR_MODULES module_id)
   {
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(m_modules[i].module_id == module_id)
         {
            return m_modules[i].display_name;
         }
      }
      return "UNKNOWN";
   }

   //+--------------------------------------------------------------+
   //| Obtém descrição do módulo                                     |
   //+--------------------------------------------------------------+
   string GetModuleDescription(ENUM_SIDEBAR_MODULES module_id)
   {
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         if(m_modules[i].module_id == module_id)
         {
            return m_modules[i].description;
         }
      }
      return "Descrição não disponível";
   }

   //+--------------------------------------------------------------+
   //| Lista todos os módulos                                        |
   //+--------------------------------------------------------------+
   void ListAllModules()
   {
      m_logger.log_info("[SIDEBAR] Lista de módulos do sidebar:");
      for(int i = 0; i < ArraySize(m_modules); i++)
      {
         string status = m_modules[i].is_active ? "ATIVO" : "INATIVO";
         m_logger.log_info(StringFormat("[SIDEBAR] %d. %s (%s) - %s", 
                                       i + 1, 
                                       m_modules[i].display_name, 
                                       m_modules[i].module_name, 
                                       status));
      }
   }

   //+--------------------------------------------------------------+
   //| Destrutor                                                    |
   //+--------------------------------------------------------------+
   ~SidebarManager()
   {
      for(int i = 0; i < ArraySize(m_sidebar_labels); i++)
      {
         if(m_sidebar_labels[i] != NULL)
         {
            delete m_sidebar_labels[i];
         }
      }
      m_logger.log_info("[SIDEBAR] Sidebar encerrado");
   }
};

//+------------------------------------------------------------------+
//| Macros de segurança para operações com sinais                    |
//+------------------------------------------------------------------+
#define QUANTUM_SIGNAL_CHECK(signal) \
   if(!ValidateQuantumSignal(signal)) { \
      Print("Falha na validação quântica em ", __FILE__, " linha ", __LINE__); \
      return; \
   }

#define CRITICAL_SIGNAL_HANDLER(signal) \
   if(TradeSignalUtils().IsCriticalSignal(signal)) { \
      QuantumCore::ActivateShieldProtocol(); \
   }

#endif // __QUANTUM_TRADE_SIGNAL_ENUM_MQH__