//+------------------------------------------------------------------+
//|                                                      ChartObjectsLblControls.mqh |
//|                             Copyright 2009-2021, MetaQuotes Software Corp. |
//|                                       https://www.mql5.com                    |
//+------------------------------------------------------------------+

#include <ChartObjects\ChartObject.mqh>
#include <ChartObjects\ChartObjectsCoordinates.mqh>

//--- Includes from Standard library
#include <Arrays\ArrayObj.mqh>

//+------------------------------------------------------------------+
//| Class CChartObjectLabel                                          |
//| Purpose: Describes functionality of label object                 |
//+------------------------------------------------------------------+
class CChartObjectLabel : public CChartObject
  {
protected:
   double            m_x;
   double            m_y;
   string            m_text;
   int               m_font_size;
   string            m_font;
   color             m_color;
   ENUM_BASE_CORNER  m_anchor;

public:
                     CChartObjectLabel(void);
                    ~CChartObjectLabel(void);

   bool              Create(long chart_id,const string name,int window,double x,double y);
   void              Delete(void);

   virtual bool      ChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam);

   //--- Set methods
   bool              Text(const string text);
   bool              FontSize(int size);
   bool              Font(const string font);
   bool              Color(color clr);
   bool              Anchor(ENUM_BASE_CORNER anchor);

   //--- Get methods
   string            Text(void) const { return(m_text); }
   int               FontSize(void) const { return(m_font_size); }
   string            Font(void) const { return(m_font); }
   color             Color(void) const { return(m_color); }
   ENUM_BASE_CORNER  Anchor(void) const { return(m_anchor); }

private:
   bool              Load(void);
   bool              Save(void);
  }; 