//+------------------------------------------------------------------+
//|                                         CGUIManager.mqh           |
//|                  Copyright 2024, MetaQuotes Ltd.                  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.0"
#property strict

#include "..\\Utils\\CLogger.mqh"

//+------------------------------------------------------------------+
//| Classe para gerenciamento de interface gráfica                    |
//+------------------------------------------------------------------+
class CGUIManager
{
private:
   CLogger* m_logger;
   string m_chart_name;
   int m_chart_id;
   datetime m_last_update_time;
   
public:
   // Construtor
   CGUIManager(CLogger* logger)
   {
      m_logger = logger;
      m_chart_name = _Symbol;
      m_chart_id = ChartID();
      m_last_update_time = TimeCurrent();
   }
   
   // Define nome do gráfico
   void SetChartName(string chart_name)
   {
      m_chart_name = chart_name;
      m_logger.Info("Nome do gráfico atualizado: " + m_chart_name);
   }
   
   // Atualiza interface
   void Update()
   {
      // Atualiza informações do gráfico
      ChartRedraw(m_chart_id);
      m_last_update_time = TimeCurrent();
   }
   
   // Obtém nome do gráfico
   string GetChartName()
   {
      return m_chart_name;
   }
   
   // Obtém ID do gráfico
   int GetChartID()
   {
      return m_chart_id;
   }
   
   // Obtém tempo da última atualização
   datetime GetLastUpdateTime()
   {
      return m_last_update_time;
   }
}; 