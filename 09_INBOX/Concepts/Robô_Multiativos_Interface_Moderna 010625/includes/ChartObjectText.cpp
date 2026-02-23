#include <ChartObjects/ChartObject.mqh>

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