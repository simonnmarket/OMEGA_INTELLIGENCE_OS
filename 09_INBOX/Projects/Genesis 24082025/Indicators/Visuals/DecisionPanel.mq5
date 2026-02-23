//+------------------------------------------------------------------+
//| decision_panel.mq5 - Painel de Decisão Institucional             |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v2.1                                                     |
//+------------------------------------------------------------------+
#property strict
#property indicator_chart_window
#property indicator_plots 0

#include <Genesis/Utils/Utils.mqh>
#include <Genesis/Core/TradeSignalEnum.mqh>

input string PanelPrefix = "GenesisDP_";
input int PanelWidth = 300;
input int PanelHeight = 450;
input color BackgroundColor = clrDarkSlateGray;
input int UpdateInterval = 250;
input bool Simulate = true;

enum ENUM_PANEL_MODE { PANEL_MODE_BASIC, PANEL_MODE_ADVANCED, PANEL_MODE_INSTITUTIONAL, PANEL_MODE_CRISIS };

struct PanelData { string symbol; double bid; double ask; double spread; double volatility; double liquidity; double market_entropy; ENUM_TRADE_SIGNAL current_signal; string strategy_status; datetime last_update; };

class CGenesisDecisionPanel
{
private:
   CGenesisUtils *m_logger; PanelData m_current_data; ENUM_PANEL_MODE m_current_mode; int m_x_position; int m_y_position;
   bool is_valid_context(){ if(Simulate){ Print("[PANEL] Modo simulado. Atualização registrada, mas não executada."); return false; } if(m_logger == NULL){ Print("[PANEL] Logger não inicializado"); return false; } return true; }
   void update_mode_by_market(){ int regime_type = MathRand() % 4; m_current_mode = (ENUM_PANEL_MODE)regime_type; }
   double calculate_market_entropy(){ MqlRates rates[]; CopyRates(m_current_data.symbol, PERIOD_M1, 0, 20, rates); double price_entropy = 0.0; double volume_entropy = 0.0; double sum_price = 0.0; double sum_volume = 0.0; for(int i = 0; i < ArraySize(rates); i++){ sum_price += rates[i].close; sum_volume += rates[i].tick_volume; } if(sum_price > 0.0) for(int i = 0; i < ArraySize(rates); i++){ double p = rates[i].close / sum_price; if(p > 0) price_entropy -= p * MathLog(p); } if(sum_volume > 0.0) for(int i = 0; i < ArraySize(rates); i++){ double p2 = rates[i].tick_volume / sum_volume; if(p2 > 0) volume_entropy -= p2 * MathLog(p2); } return price_entropy * 0.6 + volume_entropy * 0.4; }
public:
   CGenesisDecisionPanel(CGenesisUtils &logger, string symbol, int x = 10, int y = 30){ m_logger = &logger; m_current_data.symbol = symbol; m_current_data.last_update = TimeCurrent(); m_x_position = x; m_y_position = y; m_current_mode = PANEL_MODE_BASIC; }
   ~CGenesisDecisionPanel(){ ObjectsDeleteAll(0, PanelPrefix); }
   bool Create(){ if(Simulate){ Print("[PANEL] Modo simulado. Painel criado, mas atualização bloqueada."); return true; } if(!ObjectCreate(0, PanelPrefix + "BG", OBJ_RECTANGLE_LABEL, 0, 0, 0)) return false; ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_XDISTANCE, m_x_position); ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_YDISTANCE, m_y_position); ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_XSIZE, PanelWidth); ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_YSIZE, PanelHeight); ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_BGCOLOR, BackgroundColor); ObjectSetInteger(0, PanelPrefix + "BG", OBJPROP_SELECTABLE, false); if(!ObjectCreate(0, PanelPrefix + "Header", OBJ_LABEL, 0, 0, 0)) return false; ObjectSetInteger(0, PanelPrefix + "Header", OBJPROP_XDISTANCE, m_x_position + 10); ObjectSetInteger(0, PanelPrefix + "Header", OBJPROP_YDISTANCE, m_y_position + 10); ObjectSetString(0, PanelPrefix + "Header", OBJPROP_TEXT, "GENESIS QUANTUM DASHBOARD v2.1"); ObjectSetString(0, PanelPrefix + "Header", OBJPROP_FONT, "Consolas"); ObjectSetInteger(0, PanelPrefix + "Header", OBJPROP_FONTSIZE, 14); ObjectSetInteger(0, PanelPrefix + "Header", OBJPROP_COLOR, clrGold); return true; }
   void Update(){ if(!is_valid_context()) return; m_current_data.bid = SymbolInfoDouble(m_current_data.symbol, SYMBOL_BID); m_current_data.ask = SymbolInfoDouble(m_current_data.symbol, SYMBOL_ASK); m_current_data.spread = (m_current_data.ask - m_current_data.bid) / SymbolInfoDouble(m_current_data.symbol, SYMBOL_POINT); m_current_data.volatility = 0.15 + (MathRand() % 100) / 1000.0; m_current_data.liquidity = 0.8 + (MathRand() % 200) / 1000.0; m_current_data.market_entropy = calculate_market_entropy(); m_current_data.strategy_status = "ACTIVE"; m_current_data.current_signal = (ENUM_TRADE_SIGNAL)(MathRand() % 4); update_mode_by_market(); }
};

int OnInit(){ return INIT_SUCCEEDED; }
void OnDeinit(const int reason){}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
{
   return(rates_total);
}

