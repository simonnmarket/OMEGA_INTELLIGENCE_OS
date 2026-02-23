#property copyright "Daniel Jose"
#property version "1.01"
#property description "Nano Expert Advisor"
#property description "Ajuste o nível de alavancagem desejado."
#property description "Para facilitar TakeProfit e StopLoss são valores financeiros."
#property description "Pressione SHIFT para comprar usando o mouse."
#property description "Pressione CTRL para vender usando o mouse."
#property link      "https://www.mql5.com/en/users/FMIC"
#property strict
//+------------------------------------------------------------------+
class C_NanoEA
  {
protected:
   enum eTypeSymbolFast {WIN, WDO, OTHER};
   string            m_szSymbol;
   double            m_VolMinimal;
   MqlTradeRequest   TradeRequest;
   MqlTradeResult    TradeResult;
private  :
   //+------------------------------------------------------------------+
   struct st
     {
      long              Id;
      int               nDigits;
      string            szHLinePrice,
                        szHLineTake,
                        szHLineStop;
      eTypeSymbolFast   TypeSymbol;
      double            Volume,
                        StopLoss,
                        TakeProfit;
      bool              IsDayTrade;
      color             cPrice,
                        cTake,
                        cStop;
     } m_Infos;
   //+------------------------------------------------------------------+
   void              CreateHLine(string &sz0, const color arg)
     {
      if(sz0 != NULL)
         return;
      sz0 = "HLine" + (string)ObjectsTotal(m_Infos.Id, -1, OBJ_HLINE);
      ObjectCreate(m_Infos.Id, sz0, OBJ_HLINE, 0, 0, 0);
      ObjectSetString(m_Infos.Id, sz0, OBJPROP_TOOLTIP, "\n");
      ObjectSetInteger(m_Infos.Id, sz0, OBJPROP_COLOR, arg);
     };
   //+------------------------------------------------------------------+
   double            AdjustPrice(const double arg)
     {
      double v0, v1;
      if(m_Infos.TypeSymbol == OTHER)
         return arg;
      v0 = (m_Infos.TypeSymbol == WDO ? round(arg * 10.0) : round(arg));
      v1 = fmod(round(v0), 5.0);
      v0 -= ((v1 != 0) || (v1 != 5) ? v1 : 0);
      return (m_Infos.TypeSymbol == WDO ? v0 / 10.0 : v0);
     };
   //+------------------------------------------------------------------+
   ulong             CreateOrderPendent(const bool IsBuy, const double Volume, const double Price, const double Take, const double Stop, const bool DayTrade = true)
     {
      double last = SymbolInfoDouble(m_szSymbol, SYMBOL_LAST);
      ZeroMemory(TradeRequest);
      ZeroMemory(TradeResult);
      TradeRequest.action        = TRADE_ACTION_PENDING;
      TradeRequest.symbol        = m_szSymbol;
      TradeRequest.volume        = Volume;
      TradeRequest.type          = (IsBuy ? (last >= Price ? ORDER_TYPE_BUY_LIMIT : ORDER_TYPE_BUY_STOP) : (last < Price ? ORDER_TYPE_SELL_LIMIT : ORDER_TYPE_SELL_STOP));
      TradeRequest.price         = NormalizeDouble(Price, m_Infos.nDigits);
      TradeRequest.sl            = NormalizeDouble(Stop, m_Infos.nDigits);
      TradeRequest.tp            = NormalizeDouble(Take, m_Infos.nDigits);
      TradeRequest.type_time     = (DayTrade ? ORDER_TIME_DAY : ORDER_TIME_GTC);
      TradeRequest.stoplimit     = 0;
      TradeRequest.expiration    = 0;
      TradeRequest.type_filling  = ORDER_FILLING_RETURN;
      TradeRequest.deviation     = 1000;
      TradeRequest.comment       = "Ordem Gerada pelo Expert Advisor.";
      if(!OrderSend(TradeRequest, TradeResult))
        {
         MessageBox(StringFormat("Erro Número: %d", TradeResult.retcode), "Nano EA");
         return 0;
        };
      return TradeResult.order;
     };
   //+------------------------------------------------------------------+
public   :
   //+------------------------------------------------------------------+
                     C_NanoEA()
     {
      m_Infos.szHLinePrice = m_Infos.szHLineTake = m_Infos.szHLineStop = NULL;
      m_Infos.TypeSymbol = OTHER;
      ChartSetInteger(m_Infos.Id, CHART_EVENT_MOUSE_MOVE, true);
     };
   //+------------------------------------------------------------------+
                    ~C_NanoEA()
     {
      ChartSetInteger(m_Infos.Id, CHART_EVENT_MOUSE_MOVE, false);
      if(m_Infos.szHLinePrice == NULL)
         return;
      ObjectDelete(m_Infos.Id, m_Infos.szHLinePrice);
      ObjectDelete(m_Infos.Id, m_Infos.szHLineTake);
      ObjectDelete(m_Infos.Id, m_Infos.szHLineStop);
     };
   //+------------------------------------------------------------------+
   void              Initilize(int nContracts, int FinanceTake, int FinanceStop, color cp, color ct, color cs, bool b1)
     {
      string sz0 = StringSubstr(m_szSymbol = _Symbol, 0, 3);
      double v1 = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE) / SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      m_Infos.Id = ChartID();
      m_Infos.TypeSymbol = ((sz0 == "WDO") || (sz0 == "DOL") ? WDO : ((sz0 == "WIN") || (sz0 == "IND") ? WIN : OTHER));
      m_Infos.nDigits = (int) SymbolInfoInteger(m_szSymbol, SYMBOL_DIGITS);
      m_Infos.Volume = nContracts * (m_VolMinimal = SymbolInfoDouble(m_szSymbol, SYMBOL_VOLUME_MIN));
      m_Infos.TakeProfit = AdjustPrice(FinanceTake * v1 / m_Infos.Volume);
      m_Infos.StopLoss = AdjustPrice(FinanceStop * v1 / m_Infos.Volume);
      m_Infos.IsDayTrade = b1;
      CreateHLine(m_Infos.szHLinePrice, m_Infos.cPrice = cp);
      CreateHLine(m_Infos.szHLineTake, m_Infos.cTake = ct);
      CreateHLine(m_Infos.szHLineStop, m_Infos.cStop = cs);
      ChartSetInteger(m_Infos.Id, CHART_COLOR_VOLUME, m_Infos.cPrice);
      ChartSetInteger(m_Infos.Id, CHART_COLOR_STOP_LEVEL, m_Infos.cStop);
     }
   //+------------------------------------------------------------------+
   inline void       MoveTo(int X, int Y, uint Key)
     {
      int w = 0;
      datetime dt;
      bool bEClick, bKeyBuy, bKeySell;
      double take = 0, stop = 0, price;
      bEClick  = (Key & 0x01) == 0x01;    //Clique esquerdo
      bKeyBuy  = (Key & 0x04) == 0x04;    //SHIFT Pressionada
      bKeySell = (Key & 0x08) == 0x08;    //CTRL Pressionada
      ChartXYToTimePrice(m_Infos.Id, X, Y, w, dt, price);
      ObjectMove(m_Infos.Id, m_Infos.szHLinePrice, 0, 0, price = (bKeyBuy != bKeySell ? AdjustPrice(price) : 0));
      ObjectMove(m_Infos.Id, m_Infos.szHLineTake, 0, 0, take = price + (m_Infos.TakeProfit * (bKeyBuy ? 1 : -1)));
      ObjectMove(m_Infos.Id, m_Infos.szHLineStop, 0, 0, stop = price + (m_Infos.StopLoss * (bKeyBuy ? -1 : 1)));
      if((bEClick) && (bKeyBuy != bKeySell))
         CreateOrderPendent(bKeyBuy, m_Infos.Volume, price, take, stop, m_Infos.IsDayTrade);
      ObjectSetInteger(m_Infos.Id, m_Infos.szHLinePrice, OBJPROP_COLOR, (bKeyBuy != bKeySell ? m_Infos.cPrice : clrNONE));
      ObjectSetInteger(m_Infos.Id, m_Infos.szHLineTake, OBJPROP_COLOR, (take > 0 ? m_Infos.cTake : clrNONE));
      ObjectSetInteger(m_Infos.Id, m_Infos.szHLineStop, OBJPROP_COLOR, (stop > 0 ? m_Infos.cStop : clrNONE));
     };
   //+------------------------------------------------------------------+
  };
//+------------------------------------------------------------------+
class C_Protection : public C_NanoEA
  {
protected:
private  :
   ulong             m_Ticket;
   bool              m_IsBuy;
   double            m_Take, m_Stop, m_Volume;
   //+------------------------------------------------------------------+
   bool              ClosePosition(const int arg = 0)
     {
      double v1 = arg * m_VolMinimal;
      if(!PositionSelectByTicket(m_Ticket))
         return false;
      ZeroMemory(TradeRequest);
      ZeroMemory(TradeResult);
      TradeRequest.action     = TRADE_ACTION_DEAL;
      TradeRequest.type       = (m_IsBuy ? ORDER_TYPE_SELL : ORDER_TYPE_BUY);
      TradeRequest.price      = SymbolInfoDouble(m_szSymbol, (m_IsBuy ? SYMBOL_BID : SYMBOL_ASK));
      TradeRequest.position   = m_Ticket;
      TradeRequest.symbol     = m_szSymbol;
      TradeRequest.volume     = ((v1 == 0) || (v1 > m_Volume) ? m_Volume : v1);
      TradeRequest.deviation  = 1000;
      if(!OrderSend(TradeRequest, TradeResult))
        {
         MessageBox(StringFormat("Erro Número: %d", TradeResult.retcode), "Nano EA");
         return false;
        }
      else
         m_Ticket = 0;
      return true;
     };
   //+------------------------------------------------------------------+
public   :
                     C_Protection() : m_Ticket(0), m_IsBuy(true), m_Take(0.0), m_Stop(0.0), m_Volume(0.0) {};
   //+------------------------------------------------------------------+
   void              UpdatePosition(void)
     {
      for(int i0 = PositionsTotal() - 1; i0 >= 0; i0--)
         if(PositionGetSymbol(i0) == m_szSymbol)
           {
            m_Take      = PositionGetDouble(POSITION_TP);
            m_Stop      = PositionGetDouble(POSITION_SL);
            m_IsBuy     = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
            m_Volume    = PositionGetDouble(POSITION_VOLUME);
            m_Ticket    = PositionGetInteger(POSITION_TICKET);
           }
     };
   //+------------------------------------------------------------------+
   inline bool       CheckPosition(const double price = 0, const int factor = 0)
     {
      //+------------------------------------------------------------------+
      //|   Se você indicar um valor para o preço, poderá efeturar parcial |
      //|com um fator de desalavancagem indicada pela variavel factor      |
      //+------------------------------------------------------------------+
      double last;
      if(m_Ticket == 0)
         return false;
      last = SymbolInfoDouble(m_szSymbol, SYMBOL_LAST);
      if(m_IsBuy)
        {
         if((last > m_Take) || (last < m_Stop))
            return ClosePosition();
         if((price > 0) && (price >= last))
            return ClosePosition(factor);
        }
      else
        {
         if((last < m_Take) || (last > m_Stop))
            return ClosePosition();
         if((price > 0) && (price <= last))
            return ClosePosition(factor);
        }
      return false;
     };
   //+------------------------------------------------------------------+
  } EA_Nano;
//+------------------------------------------------------------------+
input int   user01   = 1;                 //Fator de alavancagem
input int   user02   = 100;               //Take Profit ( FINANCEIRO )
input int   user03   = 75;                //Stop Loss ( FINANCEIRO )
input color user04   = clrBlue;           //Cor da linha de Preço
input color user05   = clrForestGreen;    //Cor da linha Take Profit
input color user06   = clrFireBrick;      //Cor da linha Stop
input bool  user07   = true;              //Day Trade ?
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Funções de análise de liquidez                                    |
//+------------------------------------------------------------------+
class C_LiquidityAnalysis
  {
private:
   double            m_volumeThreshold;
   string            m_szSymbol;
   ENUM_TIMEFRAMES   m_timeframe;
   
public:
   C_LiquidityAnalysis(string symbol = NULL, ENUM_TIMEFRAMES timeframe = PERIOD_CURRENT)
     {
      m_szSymbol = (symbol == NULL ? _Symbol : symbol);
      m_timeframe = timeframe;
      m_volumeThreshold = 1000;
     }
   
   //+------------------------------------------------------------------+
   void              IdentifyLiquidityZones()
     {
      double priceLevel;
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      if(CopyRates(m_szSymbol, m_timeframe, 0, 100, rates) <= 0)
         return;
         
      for(int i = 1; i < 100; i++)
        {
         priceLevel = rates[i].close;
         if(rates[i].tick_volume > m_volumeThreshold)
           {
            Print("Zona de Liquidez Identificada em: ", priceLevel, " com volume: ", rates[i].tick_volume);
            DrawLiquidityZone(priceLevel);
           }
        }
     }
   
   //+------------------------------------------------------------------+
   bool              CheckRejection(double priceLevel)
     {
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      if(CopyRates(m_szSymbol, m_timeframe, 0, 2, rates) <= 0)
         return false;
         
      if(priceLevel >= rates[1].low && priceLevel <= rates[1].high)
         return true;
         
      return false;
     }
   
   //+------------------------------------------------------------------+
   bool              CheckLiquiditySweep(double priceLevel)
     {
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      if(CopyRates(m_szSymbol, m_timeframe, 0, 2, rates) <= 0)
         return false;
         
      if(MathAbs(rates[0].close - rates[1].close) > SymbolInfoDouble(m_szSymbol, SYMBOL_POINT))
         return true;
         
      return false;
     }
   
   //+------------------------------------------------------------------+
   bool              CheckTrap(double priceLevel)
     {
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      if(CopyRates(m_szSymbol, m_timeframe, 0, 2, rates) <= 0)
         return false;
         
      if(rates[0].close > rates[1].high && rates[1].close < rates[1].high)
        {
         Print("Armadilha detectada acima de: ", rates[1].high);
         return true;
        }
      else if(rates[0].close < rates[1].low && rates[1].close > rates[1].low)
        {
         Print("Armadilha detectada abaixo de: ", rates[1].low);
         return true;
        }
         
      return false;
     }
   
   //+------------------------------------------------------------------+
private:
   void              DrawLiquidityZone(double priceLevel)
     {
      string name = "LiquidityZone_" + TimeToString(TimeCurrent());
      ObjectCreate(0, name, OBJ_HLINE, 0, 0, priceLevel);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
     }
  };

//+------------------------------------------------------------------+
//| Variáveis globais                                                  |
//+------------------------------------------------------------------+
C_LiquidityAnalysis LiquidityAnalysis;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
  {
   EA_Nano.Initilize(user01, user02, user03, user04, user05, user06, user07);
   OnTrade();
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Limpeza dos objetos gráficos
   ObjectsDeleteAll(0, "LiquidityZone_");
  }

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
  {
   // Verificar a existência de uma nova barra
   static datetime dtBarraCorrente   = WRONG_VALUE;
   datetime dtBarraPrecedente = dtBarraCorrente;
   dtBarraCorrente   = iTime(_Symbol, _Period, 0);
   bool     bEventoBarraNova  = (dtBarraCorrente != dtBarraPrecedente);
   
   // Análise de liquidez
   LiquidityAnalysis.IdentifyLiquidityZones();
   
   // Reagir ao evento de uma barra nova
   if(bEventoBarraNova)
     {
      // Detectar se é o primeiro tick recebido
      if(dtBarraPrecedente == WRONG_VALUE)
        {
         Print("Primeiro tick recebido - Inicializando EA");
        }
      else
        {
         Print("Nova barra detectada - Processando sinais");
         EA_Nano.CheckPosition();
        }
     }
   else
     {
      EA_Nano.CheckPosition();
     }
   
   // Atualização de posições
   EA_Nano.UpdatePosition();
  }

//+------------------------------------------------------------------+
void OnTrade()
  {
   EA_Nano.UpdatePosition();
  }

//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
  {
   switch(id)
     {
      case CHARTEVENT_MOUSE_MOVE:
         EA_Nano.MoveTo((int)lparam, (int)dparam, (uint)sparam);
         ChartRedraw();
         break;
     };
  }
//+------------------------------------------------------------------+ 