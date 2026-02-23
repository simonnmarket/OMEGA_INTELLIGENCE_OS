//+------------------------------------------------------------------+
//|                                                       ChartObject.h |
//+------------------------------------------------------------------+

class CChartObject
{
protected:
   long              m_chart_id;
   string            m_name;
   int               m_window;

public:
   CChartObject(void);
   virtual ~CChartObject(void);

   virtual bool      Create(long chart_id,const string name,int window,int x,int y);
   virtual bool      Delete(void);

   long              ChartID(void) const { return(m_chart_id); }
   string            Name(void) const { return(m_name); }
   int               Window(void) const { return(m_window); }
};

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CChartObject::CChartObject(void) : m_chart_id(-1), m_name(""), m_window(0)
{
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CChartObject::~CChartObject(void)
{
}

//+------------------------------------------------------------------+
//| Create object                                                    |
//+------------------------------------------------------------------+
bool CChartObject::Create(long chart_id,const string name,int window,int x,int y)
{
   m_chart_id = chart_id;
   m_name = name;
   m_window = window;
   return(true);
}

//+------------------------------------------------------------------+
//| Delete object                                                    |
//+------------------------------------------------------------------+
bool CChartObject::Delete(void)
{
   if(m_chart_id != -1 && ObjectFind(m_chart_id, m_name) >= 0)
      ObjectDelete(m_chart_id, m_name);
   return(true);
}