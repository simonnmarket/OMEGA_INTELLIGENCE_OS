//+------------------------------------------------------------------+
//|                                               ChartObjectText.cpp|
//+------------------------------------------------------------------+

#include <ChartObject.mqh>

class CChartObjectText : public CChartObject
{
protected:
   double            m_angle;
   int               m_z_order;
   color             m_color;
   int               m_font_size;
   string            m_font;
   ENUM_TEXT_ALIGN   m_align;
   bool              m_background;
   bool              m_selection;

public:
   CChartObjectText(void);
   virtual ~CChartObjectText(void);

   virtual bool      Create(long chart_id,const string name,int window,int x,int y);
   bool              Text(const string text);
   string            Text(void) const;
   bool              Color(color clr);
   color             Color(void) const;
   bool              FontSize(int size);
   int               FontSize(void) const;
   bool              Font(const string font);
   string            Font(void) const;
   bool              Align(ENUM_TEXT_ALIGN align);
   ENUM_TEXT_ALIGN   Align(void) const;
   bool              Background(bool enable);
   bool              Background(void) const;
   bool              Selectable(bool select);
   bool              Selectable(void) const;
};

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CChartObjectText::CChartObjectText(void) :
   m_angle(0.0),
   m_z_order(0),
   m_color(clrBlack),
   m_font_size(10),
   m_font("Arial"),
   m_align(ALIGN_LEFT),
   m_background(false),
   m_selection(true)
{
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CChartObjectText::~CChartObjectText(void)
{
}

//+------------------------------------------------------------------+
//| Create object                                                    |
//+------------------------------------------------------------------+
bool CChartObjectText::Create(long chart_id,const string name,int window,int x,int y)
{
   if(!ObjectCreate(chart_id, name, OBJ_LABEL, window, x, y))
      return(false);

   ObjectSetInteger(chart_id, name, OBJPROP_COLOR, m_color);
   ObjectSetInteger(chart_id, name, OBJPROP_FONTSIZE, m_font_size);
   ObjectSetString(chart_id, name, OBJPROP_FONT, m_font);
   ObjectSetInteger(chart_id, name, OBJPROP_ALIGN, (int)m_align);
   ObjectSetInteger(chart_id, name, OBJPROP_BACK, m_background);
   ObjectSetInteger(chart_id, name, OBJPROP_SELECTABLE, m_selection);

   Text("Text");
   return(true);
}

//+------------------------------------------------------------------+
//| Set text                                                         |
//+------------------------------------------------------------------+
bool CChartObjectText::Text(const string text)
{
   return(ObjectSetString(ChartID(), Name(), OBJPROP_TEXT, text));
}

//+------------------------------------------------------------------+
//| Get text                                                         |
//+------------------------------------------------------------------+
string CChartObjectText::Text(void) const
{
   string result;
   ObjectGetString(ChartID(), Name(), OBJPROP_TEXT, result);
   return(result);
}

//+------------------------------------------------------------------+
//| Set color                                                        |
//+------------------------------------------------------------------+
bool CChartObjectText::Color(color clr)
{
   m_color = clr;
   return(ObjectSetInteger(ChartID(), Name(), OBJPROP_COLOR, clr));
}

//+------------------------------------------------------------------+
//| Get color                                                        |
//+------------------------------------------------------------------+
color CChartObjectText::Color(void) const
{
   return((color)ObjectGetInteger(ChartID(), Name(), OBJPROP_COLOR));
}

//+------------------------------------------------------------------+
//| Set font size                                                    |
//+------------------------------------------------------------------+
bool CChartObjectText::FontSize(int size)
{
   m_font_size = size;
   return(ObjectSetInteger(ChartID(), Name(), OBJPROP_FONTSIZE, size));
}

//+------------------------------------------------------------------+
//| Get font size                                                    |
//+------------------------------------------------------------------+
int CChartObjectText::FontSize(void) const
{
   return((int)ObjectGetInteger(ChartID(), Name(), OBJPROP_FONTSIZE));
}

//+------------------------------------------------------------------+
//| Set font                                                         |
//+------------------------------------------------------------------+
bool CChartObjectText::Font(const string font)
{
   m_font = font;
   return(ObjectSetString(ChartID(), Name(), OBJPROP_FONT, font));
}

//+------------------------------------------------------------------+
//| Get font                                                         |
//+------------------------------------------------------------------+
string CChartObjectText::Font(void) const
{
   string result;
   ObjectGetString(ChartID(), Name(), OBJPROP_FONT, result);
   return(result);
}

//+------------------------------------------------------------------+
//| Set alignment                                                    |
//+------------------------------------------------------------------+
bool CChartObjectText::Align(ENUM_TEXT_ALIGN align)
{
   m_align = align;
   return(ObjectSetInteger(ChartID(), Name(), OBJPROP_ALIGN, (int)align));
}

//+------------------------------------------------------------------+
//| Get alignment                                                    |
//+------------------------------------------------------------------+
ENUM_TEXT_ALIGN CChartObjectText::Align(void) const
{
   return((ENUM_TEXT_ALIGN)ObjectGetInteger(ChartID(), Name(), OBJPROP_ALIGN));
}

//+------------------------------------------------------------------+
//| Enable background                                                |
//+------------------------------------------------------------------+
bool CChartObjectText::Background(bool enable)
{
   m_background = enable;
   return(ObjectSetInteger(ChartID(), Name(), OBJPROP_BACK, enable));
}

//+------------------------------------------------------------------+
//| Is background enabled                                            |
//+------------------------------------------------------------------+
bool CChartObjectText::Background(void) const
{
   return((bool)ObjectGetInteger(ChartID(), Name(), OBJPROP_BACK));
}

//+------------------------------------------------------------------+
//| Make object selectable                                           |
//+------------------------------------------------------------------+
bool CChartObjectText::Selectable(bool select)
{
   m_selection = select;
   return(ObjectSetInteger(ChartID(), Name(), OBJPROP_SELECTABLE, select));
}

//+------------------------------------------------------------------+
//| Is object selectable                                             |
//+------------------------------------------------------------------+
bool CChartObjectText::Selectable(void) const
{
   return((bool)ObjectGetInteger(ChartID(), Name(), OBJPROP_SELECTABLE));
}