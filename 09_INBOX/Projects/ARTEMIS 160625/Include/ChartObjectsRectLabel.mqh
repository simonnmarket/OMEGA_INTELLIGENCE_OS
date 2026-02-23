//+------------------------------------------------------------------+
//|                                                    ChartObjectsRectLabel.mqh |
//|                             Copyright 2009-2021, MetaQuotes Software Corp. |
//|                                       https://www.mql5.com                    |
//+------------------------------------------------------------------+

#include <ChartObjects\ChartObject.mqh>
#include <ChartObjects\ChartObjectsCoordinates.mqh>

//--- Includes from Standard library
#include <Arrays\ArrayObj.mqh>

//+------------------------------------------------------------------+
//| Class CChartObjectRectangle                                        |
//| Purpose: Describes functionality of rectangle object               |
//+------------------------------------------------------------------+
class CChartObjectRectangle : public CChartObject
  {
protected:
   double            m_x1;
   double            m_y1;
   double            m_x2;
   double            m_y2;
   color             m_color;
   uint              m_border_type;
   color             m_border_color;
   int               m_border_width;
   bool              m_filled;
   color             m_fill_color;

public:
                     CChartObjectRectangle(void);
                    ~CChartObjectRectangle(void);

   bool              Create(long chart_id,const string name,int window,double x1,double y1,double x2,double y2);
   void              Delete(void);

   virtual bool      ChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam);

   //--- Set methods
   bool              Coordinates(double x1,double y1,double x2,double y2);
   bool              Color(color clr);
   bool              BorderType(uint type);
   bool              BorderColor(color clr);
   bool              BorderWidth(int width);
   bool              Filled(bool filled);
   bool              FillColor(color clr);

   //--- Get methods
   double            X1(void) const { return(m_x1); }
   double            Y1(void) const { return(m_y1); }
   double            X2(void) const { return(m_x2); }
   double            Y2(void) const { return(m_y2); }
   color             Color(void) const { return(m_color); }
   uint              BorderType(void) const { return(m_border_type); }
   color             BorderColor(void) const { return(m_border_color); }
   int               BorderWidth(void) const { return(m_border_width); }
   bool              Filled(void) const { return(m_filled); }
   color             FillColor(void) const { return(m_fill_color); }

private:
   bool              Load(void);
   bool              Save(void);
  }; 