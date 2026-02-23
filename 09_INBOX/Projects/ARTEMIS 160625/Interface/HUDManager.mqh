//+------------------------------------------------------------------+
//| HUDManager.mqh - Heads-Up Display Manager                        |
//+------------------------------------------------------------------+
#include <Objects\TextObject.mqh>

class HUDManager
{
private:
   CTextLabel* title_label;
   CTextLabel* status_label;
   CTextLabel* symbol_labels[];
   CTextLabel* signal_labels[];
   CTextLabel* performance_label;
   int max_symbols;
   
public:
   HUDManager()
   {
      max_symbols = 3;
      ArrayResize(symbol_labels, max_symbols);
      ArrayResize(signal_labels, max_symbols);
   }
   
   void Init()
   {
      // Create title label
      title_label = new CTextLabel();
      title_label.Create(0, "hud_title", 0, 10, 10);
      title_label.Text("ARTEMIS Trading System");
      title_label.FontSize(14);
      title_label.Color(clrWhite);
      title_label.Background(true);
      title_label.BackColor(clrDarkSlateGray);
      
      // Create status label
      status_label = new CTextLabel();
      status_label.Create(0, "status_label", 0, 10, 30);
      status_label.FontSize(12);
      status_label.Color(clrYellow);
      
      // Create symbol and signal labels
      for(int i = 0; i < max_symbols; i++)
      {
         symbol_labels[i] = new CTextLabel();
         symbol_labels[i].Create(0, "symbol_"+IntegerToString(i), 0, 10, 50 + i*20);
         symbol_labels[i].FontSize(10);
         symbol_labels[i].Color(clrLightBlue);
         
         signal_labels[i] = new CTextLabel();
         signal_labels[i].Create(0, "signal_"+IntegerToString(i), 0, 100, 50 + i*20);
         signal_labels[i].FontSize(10);
         signal_labels[i].Color(clrLightGreen);
      }
      
      // Create performance label
      performance_label = new CTextLabel();
      performance_label.Create(0, "performance_label", 0, 10, 110);
      performance_label.FontSize(10);
      performance_label.Color(clrOrange);
   }
   
   void Update(string symbol, int signal, double quantum_state)
   {
      // Update status label
      string status = StringFormat("Quantum State: %.4f", quantum_state);
      status_label.Text(status);
      
      // Update symbol and signal labels
      for(int i = 0; i < max_symbols; i++)
      {
         if(symbol_labels[i].Text() == "" || symbol_labels[i].Text() == symbol)
         {
            symbol_labels[i].Text(symbol);
            
            string signal_text = "";
            color signal_color = clrGray;
            
            switch(signal)
            {
               case 1:
                  signal_text = "🔺 BUY";
                  signal_color = clrLime;
                  break;
               case -1:
                  signal_text = "🔻 SELL";
                  signal_color = clrRed;
                  break;
               default:
                  signal_text = "⬤ NEUTRAL";
                  signal_color = clrGray;
            }
            
            signal_labels[i].Text(signal_text);
            signal_labels[i].Color(signal_color);
            break;
         }
      }
      
      // Update performance label
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double profit = equity - balance;
      string performance = StringFormat("Balance: %.2f | Equity: %.2f | P/L: %.2f", balance, equity, profit);
      performance_label.Text(performance);
   }
   
   void Destroy()
   {
      title_label.Delete(0, "hud_title");
      status_label.Delete(0, "status_label");
      performance_label.Delete(0, "performance_label");
      
      for(int i = 0; i < max_symbols; i++)
      {
         symbol_labels[i].Delete(0, "symbol_"+IntegerToString(i));
         signal_labels[i].Delete(0, "signal_"+IntegerToString(i));
      }
      
      delete title_label;
      delete status_label;
      delete performance_label;
      
      for(int i = 0; i < max_symbols; i++)
      {
         delete symbol_labels[i];
         delete signal_labels[i];
      }
   }
}; 