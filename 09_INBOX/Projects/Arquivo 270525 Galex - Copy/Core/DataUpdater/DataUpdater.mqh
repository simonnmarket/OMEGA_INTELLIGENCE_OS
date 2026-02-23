//+------------------------------------------------------------------+
//|                                                   DataUpdater.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include "..\Interfaces\IModule.mqh"

// Classe principal de atualização de dados
class CDataUpdater : public IDataProcessor
{
private:
   MqlRates m_rates[];
   double m_volume[];
   datetime m_last_update;
   int m_timeframe;
   int m_bars_to_process;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CDataUpdater()
   {
      m_last_update = 0;
      m_timeframe = PERIOD_CURRENT;
      m_bars_to_process = 100;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_last_update = 0;
      m_timeframe = PERIOD_CURRENT;
      m_bars_to_process = 100;
      m_status = "Initialized";
      m_is_initialized = true;
      
      ArrayResize(m_rates, m_bars_to_process);
      ArrayResize(m_volume, m_bars_to_process);
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      
      datetime current_time = TimeCurrent();
      if(current_time - m_last_update >= PeriodSeconds(m_timeframe))
      {
         ProcessData();
         m_last_update = current_time;
         m_status = "Updated";
      }
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_bars_to_process > 0 && m_timeframe > 0;
   }
   
   void Cleanup() override
   {
      ArrayFree(m_rates);
      ArrayFree(m_volume);
      m_last_update = 0;
      m_timeframe = PERIOD_CURRENT;
      m_bars_to_process = 100;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "DataUpdater"; }
   
   // Implementação de IDataProcessor
   bool ProcessData() override
   {
      if(!m_is_initialized) return false;
      
      int copied = CopyRates(_Symbol, m_timeframe, 0, m_bars_to_process, m_rates);
      if(copied != m_bars_to_process) return false;
      
      for(int i = 0; i < m_bars_to_process; i++)
      {
         m_volume[i] = m_rates[i].tick_volume;
      }
      
      return true;
   }
   
   bool GetProcessedData(MqlRates &rates[], double &volume[]) override
   {
      if(!m_is_initialized) return false;
      
      ArrayResize(rates, m_bars_to_process);
      ArrayResize(volume, m_bars_to_process);
      
      ArrayCopy(rates, m_rates);
      ArrayCopy(volume, m_volume);
      
      return true;
   }
   
   // Métodos específicos do DataUpdater
   bool Init(int timeframe, int bars_to_process)
   {
      m_timeframe = timeframe;
      m_bars_to_process = bars_to_process;
      
      ArrayResize(m_rates, m_bars_to_process);
      ArrayResize(m_volume, m_bars_to_process);
      
      return true;
   }
   
   bool UpdateData()
   {
      if(!m_is_initialized) return false;
      
      int copied = CopyRates(_Symbol, m_timeframe, 0, m_bars_to_process, m_rates);
      if(copied != m_bars_to_process) return false;
      
      for(int i = 0; i < m_bars_to_process; i++)
      {
         m_volume[i] = m_rates[i].tick_volume;
      }
      
      m_last_update = TimeCurrent();
      return true;
   }
   
   // Getters
   datetime GetLastUpdate() const { return m_last_update; }
   int GetTimeframe() const { return m_timeframe; }
   int GetBarsToProcess() const { return m_bars_to_process; }
}; 