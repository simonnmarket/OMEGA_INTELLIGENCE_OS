//+------------------------------------------------------------------+
//|                                                     TextObject.h |
//+------------------------------------------------------------------+

#include "ChartObjectText.mqh"

class CTextLabel : public CChartObjectText
{
public:
   CTextLabel(void);
   ~CTextLabel(void);
   bool Create(long chart_id,const string name,int window,int x,int y);
};

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CTextLabel::CTextLabel(void)
{
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CTextLabel::~CTextLabel(void)
{
}

//+------------------------------------------------------------------+
//| Create object                                                    |
//+------------------------------------------------------------------+
bool CTextLabel::Create(long chart_id,const string name,int window,int x,int y)
{
   if(!CChartObjectText::Create(chart_id, name, window, x, y))
      return(false);

   Text("New Label");
   Color(clrRed);
   FontSize(10);
   return(true);
}