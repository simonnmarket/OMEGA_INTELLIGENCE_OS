//+------------------------------------------------------------------+
//| SkyIntelStatusPanel.mq5 - Painel Estratégico SKYINTEL           |
//| Projeto: EA Numeia - Visualização Institucional                 |
//| Mostra status da IA, persona, sinal tático e recomendação       |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

#include <Integration/SkyIntelBridge.mqh>
#include <DecisionEngine/SignalController.mqh>

// Cores institucionais
#define COLOR_HEADER clrSteelBlue
#define COLOR_TEXT   clrWhite
#define COLOR_BUY    clrLimeGreen
#define COLOR_SELL   clrOrangeRed
#define COLOR_WAIT   clrLightGray

input string PanelPrefix      = "SkyIntelPanel";
input int    XOffset          = 20;
input int    YOffset          = 20;
input int    Corner           = 0;
input int    UpdateInterval   = 60;  // em segundos

int timer_id = 0;

//+------------------------------------------------------------------+
//| Inicialização                                                    |
//+------------------------------------------------------------------+
int OnInit()
{
   DrawSkyIntelPanel();
   EventSetTimer(UpdateInterval);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   EventKillTimer();
   DeleteSkyIntelPanel();
}

//+------------------------------------------------------------------+
//| Atualiza a cada X segundos                                       |
//+------------------------------------------------------------------+
void OnTimer()
{
   DeleteSkyIntelPanel();
   DrawSkyIntelPanel();
}

//+------------------------------------------------------------------+
//| Desenha o painel                                                 |
//+------------------------------------------------------------------+
void DrawSkyIntelPanel()
{
   string symbol = _Symbol;

   // Recuperar sinal estratégico e persona
   SignalController::StrategicSignal intel = SignalController::GetSkyIntelSignal(symbol);
   SignalController::STRATEGIC_DECISION decision = SignalController::ConsolidatedDecision(symbol);

   string title = "SKYINTEL STATUS";
   string persona = "Persona: " + intel.persona;
   string signal  = "Sinal: " + EnumToString(intel.intelSignal);
   string action  = "Recomendação: ";

   color actionColor = COLOR_WAIT;
   switch (decision)
   {
      case STRATEGIC_BUY:
         action += "BUY";
         actionColor = COLOR_BUY;
         break;
      case STRATEGIC_SELL:
         action += "SELL";
         actionColor = COLOR_SELL;
         break;
      default:
         action += "AGUARDAR";
         break;
   }

   int y = YOffset;

   DrawTextLabel(PanelPrefix + "_title",  title,       XOffset, y, COLOR_HEADER); y += 16;
   DrawTextLabel(PanelPrefix + "_persona", persona,    XOffset, y, COLOR_TEXT);   y += 16;
   DrawTextLabel(PanelPrefix + "_signal",  signal,     XOffset, y, COLOR_TEXT);   y += 16;
   DrawTextLabel(PanelPrefix + "_action",  action,     XOffset, y, actionColor);  y += 16;
}

//+------------------------------------------------------------------+
//| Função para desenhar rótulos                                     |
//+------------------------------------------------------------------+
void DrawTextLabel(string name, string text, int x, int y, color clr)
{
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER, Corner);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 10);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
}

//+------------------------------------------------------------------+
//| Limpa o painel                                                   |
//+------------------------------------------------------------------+
void DeleteSkyIntelPanel()
{
   string names[] = { "_title", "_persona", "_signal", "_action" };
   for (int i = 0; i < ArraySize(names); i++)
      ObjectDelete(0, PanelPrefix + names[i]);
} 