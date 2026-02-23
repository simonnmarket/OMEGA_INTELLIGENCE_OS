//+------------------------------------------------------------------+
//|                                                     ChartObjectsBtnControls.mqh |
//|                             Copyright 2009-2021, MetaQuotes Software Corp. |
//|                                       https://www.mql5.com                    |
//+------------------------------------------------------------------+

#include <ChartObjects\ChartObject.mqh>
#include <ChartObjects\ChartObjectsCoordinates.mqh>

//--- Includes from Standard library
#include <Arrays\ArrayObj.mqh>

//+------------------------------------------------------------------+
//| Class CChartObjectButton                                         |
//| Purpose: Describes functionality of button object                |
//+------------------------------------------------------------------+
class CChartObjectButton : public CChartObject
  {
protected:
   double            m_x;
   double            m_y;
   double            m_width;
   double            m_height;
   string            m_caption;
   int               m_font_size;
   string            m_font;
   color             m_color;
   ENUM_BASE_CORNER  m_anchor;

public:
                     CChartObjectButton(void);
                    ~CChartObjectButton(void);

   bool              Create(long chart_id,const string name,int window,double x,double y,double width,double height);
   void              Delete(void);

   virtual bool      ChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam);

   //--- Set methods
   bool              Caption(const string caption);
   bool              Width(double width);
   bool              Height(double height);
   bool              FontSize(int size);
   bool              Font(const string font);
   bool              Color(color clr);
   bool              Anchor(ENUM_BASE_CORNER anchor);

   //--- Get methods
   string            Caption(void) const { return(m_caption); }
   double            Width(void) const { return(m_width); }
   double            Height(void) const { return(m_height); }
   int               FontSize(void) const { return(m_font_size); }
   string            Font(void) const { return(m_font); }
   color             Color(void) const { return(m_color); }
   ENUM_BASE_CORNER  Anchor(void) const { return(m_anchor); }

private:
   bool              Load(void);
   bool              Save(void);
  }; 