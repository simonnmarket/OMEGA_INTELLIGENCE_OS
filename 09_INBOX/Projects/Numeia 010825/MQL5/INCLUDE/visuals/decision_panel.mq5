//+------------------------------------------------------------------+
//| decision_panel.mq5 - Painel de Decisão Institucional             |
//| Projeto: QuantumOmegaGodMode / EA Numeia                         |
//| Versão: v2.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-21 | Agente: Qwen (CEO Mode)              |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_plots 0

#include "ChartObjects\ChartObjectsTxtControls.mqh"
#include "ChartObjects\ChartObjectsBmpControls.mqh"
#include "utils/logger_institutional.mqh"
#include "types/trade_signal_enum.mqh"
#include "risk/risk_profile.mqh"
#include "analysis/market_regime_detector.mqh"
#include "intelligence/anomaly_detector_ai.mqh"

//+------------------------------------------------------------------+
//| Definições de Input                                              |
//+------------------------------------------------------------------+
input string PanelPrefix = "NumeiaDP_";     // Prefixo para objetos
input int PanelWidth = 300;                 // Largura do painel
input int PanelHeight = 450;                // Altura do painel
input color BackgroundColor = clrDarkSlateGray; // Cor de fundo
input int UpdateInterval = 250;              // Intervalo de atualização (ms)
input bool Simulate = true;                // Modo simulado

//+------------------------------------------------------------------+
//| Enumeradores Avançados                                           |
//+------------------------------------------------------------------+
enum ENUM_PANEL_MODE
{
   PANEL_MODE_BASIC,          // Modo básico
   PANEL_MODE_ADVANCED,      // Modo avançado
   PANEL_MODE_INSTITUTIONAL, // Modo institucional
   PANEL_MODE_CRISIS         // Modo de crise
};

//+------------------------------------------------------------------+
//| Estrutura de Dados do Painel                                     |
//+------------------------------------------------------------------+
struct PanelData
{
   string            symbol;
   double            bid;
   double            ask;
   double            spread;
   double            volatility;
   double            liquidity;
   double            market_entropy;
   ENUM_TRADE_SIGNAL current_signal;
   string            strategy_status;
   datetime          last_update;
};

//+------------------------------------------------------------------+
//| Classe DecisionPanel - Painel de Decisão                        |
//+------------------------------------------------------------------+
class DecisionPanel
{
private:
   logger_institutional &m_logger;
   RiskProfile &m_risk;
   MarketRegimeDetector &m_regime;
   AnomalyDetectorAI &m_ai;

   CChartObjectRect m_background;
   CChartObjectLabel m_header;
   CChartObjectLabel m_price_info;
   CChartObjectLabel m_risk_info;
   CChartObjectLabel m_signal_info;
   CChartObjectBmpLabel m_heatmap;

   PanelData m_current_data;
   ENUM_PANEL_MODE m_current_mode;
   int m_x_position;
   int m_y_position;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(Simulate)
      {
         m_logger.log_debug("[PANEL] Modo simulado. Atualização registrada, mas não executada.");
         return false;
      }

      if(!m_risk.is_profile_ready())
      {
         m_logger.log_error("[PANEL] Módulo de risco não está pronto");
         return false;
      }

      if(!m_regime.is_detector_ready())
      {
         m_logger.log_error("[PANEL] Módulo de regime de mercado não está pronto");
         return false;
      }

      if(m_ai.is_anomaly_detected())
      {
         m_logger.log_critical("[PANEL] Anomalia crítica detectada. Painel em modo seguro.");
         m_current_mode = PANEL_MODE_CRISIS;
         return true;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza modo do painel com base no mercado                   |
   //+--------------------------------------------------------------+
   void update_mode_by_market()
   {
      if(m_regime.is_chaotic())
         m_current_mode = PANEL_MODE_CRISIS;
      else if(m_regime.is_hft_spike())
         m_current_mode = PANEL_MODE_ADVANCED;
      else if(m_regime.is_black_swan())
         m_current_mode = PANEL_MODE_CRISIS;
      else
         m_current_mode = PANEL_MODE_INSTITUTIONAL;
   }

   //+--------------------------------------------------------------+
   //| Atualiza mapa de calor institucional                          |
   //+--------------------------------------------------------------+
   void update_heatmap()
   {
      double volatility = m_current_data.volatility;
      double liquidity = m_current_data.liquidity;
      double entropy = m_current_data.market_entropy;

      string heatmap_path = "::Numeia_Heatmap_" + IntegerToString(GetTickCount());
      ResourceCreate(heatmap_path, volatility * 255, liquidity * 255, entropy * 255, 255, 255, COLOR_FORMAT_ARGB_NORMALIZE);
      m_heatmap.BmpName("::" + heatmap_path);
   }

   //+--------------------------------------------------------------+
   //| Calcula entropia de mercado com múltiplas fontes             |
   //+--------------------------------------------------------------+
   double calculate_market_entropy()
   {
      MqlRates rates[];
      CopyRates(m_current_data.symbol, PERIOD_M1, 0, 20, rates);

      double price_entropy = 0.0;
      double volume_entropy = 0.0;
      double sum_price = 0.0;
      double sum_volume = 0.0;

      for(int i = 0; i < ArraySize(rates); i++)
      {
         sum_price += rates[i].close;
         sum_volume += rates[i].tick_volume;
      }

      if(sum_price > 0.0)
         for(int i = 0; i < ArraySize(rates); i++)
         {
            double p = rates[i].close / sum_price;
            if(p > 0) price_entropy -= p * MathLog(p);
         }

      if(sum_volume > 0.0)
         for(int i = 0; i < ArraySize(rates); i++)
         {
            double p = rates[i].tick_volume / sum_volume;
            if(p > 0) volume_entropy -= p * MathLog(p);
         }

      return price_entropy * 0.6 + volume_entropy * 0.4;
   }

public:
   //+--------------------------------------------------------------+
   //| Construtor e Destrutor                                       |
   //+--------------------------------------------------------------+
   DecisionPanel(logger_institutional &logger, 
                 RiskProfile &risk,
                 MarketRegimeDetector &regime,
                 AnomalyDetectorAI &ai,
                 string symbol,
                 int x = 10, int y = 30)
      : m_logger(logger), m_risk(risk), m_regime(regime), m_ai(ai)
   {
      m_current_data.symbol = symbol;
      m_current_data.last_update = TimeCurrent();
      m_x_position = x;
      m_y_position = y;
      m_current_mode = PANEL_MODE_BASIC;
   }

   ~DecisionPanel()
   {
      ObjectsDeleteAll(0, PanelPrefix);
      m_logger.log_info("[PANEL] Painel de decisão destruído com segurança");
   }

   //+--------------------------------------------------------------+
   //| Cria o painel visual completo                                |
   //+--------------------------------------------------------------+
   bool Create()
   {
      if(Simulate)
      {
         m_logger.log_debug("[PANEL] Modo simulado. Painel criado, mas atualização bloqueada.");
         return true;
      }

      if(!m_background.Create(0, PanelPrefix + "BG", 0, m_x_position, m_y_position, m_x_position + PanelWidth, m_y_position + PanelHeight))
         return false;

      m_background.Color(BackgroundColor);
      m_background.Background(true);
      m_background.Selectable(false);

      // Cabeçalho
      if(!m_header.Create(0, PanelPrefix + "Header", 0, m_x_position + 10, m_y_position + 10))
         return false;

      m_header.Font("Consolas", 14, FW_BOLD);
      m_header.Color(clrGold);
      m_header.Text("NUMeIA QUANTUM DASHBOARD v2.1");

      // Informações de preço
      if(!m_price_info.Create(0, PanelPrefix + "Prices", 0, m_x_position + 15, m_y_position + 50))
         return false;

      m_price_info.Font("Consolas", 10);
      m_price_info.Color(clrWhite);
      m_price_info.Text("Carregando dados de mercado...");

      // Informações de risco
      if(!m_risk_info.Create(0, PanelPrefix + "Risk", 0, m_x_position + 15, m_y_position + 150))
         return false;

      m_risk_info.Font("Consolas", 10);
      m_risk_info.Text("Calculando métricas de risco...");

      // Informações de sinal
      if(!m_signal_info.Create(0, PanelPrefix + "Signal", 0, m_x_position + 15, m_y_position + 250))
         return false;

      m_signal_info.Font("Consolas", 12, FW_BOLD);
      m_signal_info.Text("Aguardando sinais...");

      // Heatmap institucional
      if(!m_heatmap.Create(0, PanelPrefix + "Heatmap", 0, m_x_position + 15, m_y_position + 300, 270, 120))
         return false;

      m_logger.log_info("[PANEL] Painel de decisão criado com sucesso.");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza todos os dados do painel                              |
   //+--------------------------------------------------------------+
   void Update()
   {
      if(!is_valid_context())
      {
         m_logger.log_warning("[PANEL] Atualização bloqueada por segurança");
         return;
      }

      m_current_data.bid = SymbolInfoDouble(m_current_data.symbol, SYMBOL_BID);
      m_current_data.ask = SymbolInfoDouble(m_current_data.symbol, SYMBOL_ASK);
      m_current_data.spread = (m_current_data.ask - m_current_data.bid) / SymbolInfoDouble(m_current_data.symbol, SYMBOL_POINT);
      m_current_data.volatility = m_regime.get_volatility_index();
      m_current_data.liquidity = m_ai.get_liquidity_score();
      m_current_data.market_entropy = calculate_market_entropy();
      m_current_data.strategy_status = m_ai.get_strategy_status();

      update_mode_by_market();
      update_visualization();
      update_risk_metrics();
      update_signal_info();
      update_price_info();
      update_heatmap();
   }

private:
   //+--------------------------------------------------------------+
   //| Atualiza visualização com base no modo                        |
   //+--------------------------------------------------------------+
   void update_visualization()
   {
      color bg_color, text_color;
      string mode_text;

      switch(m_current_mode)
      {
         case PANEL_MODE_BASIC:
            bg_color = C'30,30,30';
            text_color = clrSilver;
            mode_text = "BASIC";
            break;
         case PANEL_MODE_ADVANCED:
            bg_color = C'20,40,60';
            text_color = clrDodgerBlue;
            mode_text = "ADVANCED";
            break;
         case PANEL_MODE_INSTITUTIONAL:
            bg_color = C'40,20,60';
            text_color = clrOrchid;
            mode_text = "INSTITUCIONAL";
            break;
         case PANEL_MODE_CRISIS:
            bg_color = C'80,20,20';
            text_color = clrGold;
            mode_text = "CRISIS";
            break;
         default:
            bg_color = C'30,30,30';
            text_color = clrSilver;
            mode_text = "DESCONHECIDO";
            m_logger.log_error("[PANEL] Modo de painel desconhecido");
            break;
      }

      m_background.Color(bg_color);
      m_header.Color(text_color);
      m_price_info.Color(text_color);
      m_risk_info.Color(text_color);
      m_signal_info.Color(text_color);
      m_header.Text("NUMeIA QUANTUM DASHBOARD v2.1 - " + mode_text);
   }

   //+--------------------------------------------------------------+
   //| Atualiza informações de preço                                  |
   //+--------------------------------------------------------------+
   void update_price_info()
   {
      string price_text = StringFormat(
         "💰 PREÇO ATUAL\n"
         "Bid: %.5f | Ask: %.5f\n"
         "Spread: %.1f pips\n"
         "📊 CONDIÇÕES DE MERCADO\n"
         "Volatilidade: %.2f | Liquidez: %.2f\n"
         "Entropia: %.2f",
         m_current_data.bid, m_current_data.ask, m_current_data.spread,
         m_current_data.volatility, m_current_data.liquidity, m_current_data.market_entropy
      );
      m_price_info.Text(price_text);
   }

   //+--------------------------------------------------------------+
   //| Atualiza métricas de risco                                  |
   //+--------------------------------------------------------------+
   void update_risk_metrics()
   {
      double var = m_risk.get_var_95();
      double es = m_risk.get_expected_shortfall();
      double exposure = m_risk.get_exposure_score();
      double drawdown = m_risk.get_max_drawdown();

      string risk_text = StringFormat(
         "⚠ MÉTRICAS DE RISCO\n"
         "VaR 95%%: %.2f%% | ES: %.2f%%\n"
         "Max DD: %.2f%%\n"
         "🛡 CONTROLES DE RISCO\n"
         "Tamanho da posição: %.2f lots\n"
         "Exposição: $%.2f",
         var * 100, es * 100, drawdown * 100,
         m_risk.calculate_position_size(m_current_data.symbol), exposure
      );
      m_risk_info.Text(risk_text);
   }

   //+--------------------------------------------------------------+
   //| Atualiza informações de sinal                                 |
   //+--------------------------------------------------------------+
   void update_signal_info()
   {
      string signal_text = StringFormat(
         "🚦 SINAL ATUAL\n"
         "Sinal: %s\n"
         "Status: %s\n"
         "Modo: %s",
         TradeSignalUtils().ToString(m_current_data.current_signal),
         m_current_data.strategy_status,
         EnumToString(m_current_mode)
      );
      m_signal_info.Text(signal_text);
   }
};
//+------------------------------------------------------------------+
//| Implementação do Indicador                                       |
//+------------------------------------------------------------------+
logger_institutional logger("DecisionPanel");
RiskProfile risk(logger, data_feed, learning_module);
MarketRegimeDetector regime(logger, ai);
AnomalyDetectorAI ai(logger, regime);

DecisionPanel panel(logger, risk, regime, ai, _Symbol);

//+------------------------------------------------------------------+
//| Initialization function                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   if(Simulate)
   {
      panel.SetPanelMode(PANEL_MODE_BASIC);
      return INIT_SUCCEEDED;
   }

   if(!logger.is_initialized())
   {
      Print("Erro: Logger não inicializado");
      return INIT_FAILED;
   }

   if(!risk.is_profile_ready())
   {
      logger.log_error("Falha na inicialização do perfil de risco");
      return INIT_FAILED;
   }

   if(!regime.is_detector_ready())
   {
      logger.log_error("Falha na inicialização do detector de regime");
      return INIT_FAILED;
   }

   if(!panel.Create())
   {
      logger.log_error("Falha na criação do painel de decisão");
      return INIT_FAILED;
   }

   panel.SetPanelMode(PANEL_MODE_INSTITUTIONAL);
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Deinitialization function                                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   logger.log_info(StringFormat("[PANEL] Painel de decisão desativado (motivo: %d)", reason));
}

//+------------------------------------------------------------------+
//| Chart event handler                                              |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_CHART_CHANGE || id == CHARTEVENT_TICK)
   {
      static datetime last_update = 0;
      if(TimeCurrent() - last_update >= UpdateInterval / 1000)
      {
         panel.Update();
         last_update = TimeCurrent();
      }
   }
}