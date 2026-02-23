// include/visuals/ai_feedback_panel.mq5

#property script_show_inputs
#include <ChartObjects\ChartObjectsTxtControls.mqh>

void OnStart() {
   string text =
      "🧠 AI FEEDBACK PANEL\n" +
      "====================\n" +
      "✅ Módulos Iniciados: core_brain_manager, decision_router\n" +
      "⚠️ Próximos passos: Integração neural\n";

   string name = "ai_feedback_panel";
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, 20);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 10);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
}