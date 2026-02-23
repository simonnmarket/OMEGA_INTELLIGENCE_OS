//+------------------------------------------------------------------+
//| VectorDisplay.mqh - Sistema de Visualização Vetorial                |
//| Mostra magnitude e direção do campo financeiro                    |
//+------------------------------------------------------------------+

class VectorDisplay {
private:
   string m_name;
   int    m_x;
   int    m_y;

public:
   VectorDisplay(string name = "label", int x = 0, int y = 0) {
      m_name = name;
      m_x = x;
      m_y = y;
   }

   // Cria label gráfico
   bool Create(long chart_id = 0, int window = 0, int x = 0, int y = 0) {
      if(ObjectFind(chart_id, m_name) != -1)
         ObjectDelete(chart_id, m_name);

      ObjectCreate(chart_id, m_name, OBJ_LABEL, window, 0, 0);
      ObjectSetInteger(chart_id, m_name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(chart_id, m_name, OBJPROP_YDISTANCE, y);
      ObjectSetText(chart_id, m_name, m_name, 12, "Arial", clrWhite);
      return true;
   }

   // Atualiza texto do display com cor baseada no tipo de sinal
   void Update(const string new_text) {
      color clr = (StringFind(new_text, "🔺") >= 0) ? clrGreen :
                 (StringFind(new_text, "🔻") >= 0) ? clrRed : clrWhite;

      ObjectSetText(0, m_name, new_text, 12, "Arial", clr);
   }
};