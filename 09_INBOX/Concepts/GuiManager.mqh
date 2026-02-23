//+------------------------------------------------------------------+
//| GuiManager.mqh - Gerenciador de Interface Gráfica                |
//+------------------------------------------------------------------+
#include <Objects/TextObject.mqh>

class GuiManager
{
private:
   CTextLabel label_title;
   CTextLabel label_header;
   CTextLabel labels[3]; // Para até 3 ativos

public:
   void Init()
   {
      label_title.Create(0, "title", 0, 50, 30);
      label_title.Text("Robô Multiativos - Modo Operacional");
      label_title.FontSize(14);
      label_title.Color(clrWhite);
      label_title.Background(true);
      label_title.BackColor(clrDarkSlateGray);

      label_header.Create(0, "header", 0, 50, 50);
      label_header.Text("Símbolo      Sinal        Status");
      label_header.FontSize(12);
      label_header.Color(clrYellow);

      for(int i=0; i<3; i++)
      {
         labels[i].Create(0, "label_"+IntegerToString(i), 0, 50, 70 + i*20);
         labels[i].FontSize(12);
         labels[i].Color(clrLightBlue);
      }
   }

   void Update(string symbol, int signal, string status)
   {
      string arrow = (signal == 1) ? "🔺 Compra" : (signal == -1) ? "🔻 Venda" : "⬤ Nenhum";
      string line = StringFormat("%-8s   %-10s   %s", symbol, arrow, status);

      if(symbol == "EURUSD") labels[0].Text(line);
      if(symbol == "GBPUSD") labels[1].Text(line);
      if(symbol == "USDJPY") labels[2].Text(line);
   }

   void Destroy()
   {
      label_title.Delete(0, "title");
      label_header.Delete(0, "header");
      for(int i=0; i<3; i++) labels[i].Delete(0, "label_"+IntegerToString(i));
   }
}; 