//+------------------------------------------------------------------+
//|                                           InstitutionalRadar.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Constantes do radar institucional
#define MIN_VOLUME_THRESHOLD 1000000
#define MIN_PRICE_CHANGE 0.001
#define MAX_SPREAD 0.0002

// Classe principal do radar institucional
class CInstitutionalRadar : public IDataAnalyzer
{
private:
   double m_institutional_volume;
   double m_price_impact;
   double m_market_depth;
   double m_spread;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CInstitutionalRadar()
   {
      m_institutional_volume = 0.0;
      m_price_impact = 0.0;
      m_market_depth = 0.0;
      m_spread = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_institutional_volume = 0.0;
      m_price_impact = 0.0;
      m_market_depth = 0.0;
      m_spread = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      
      // Atualizar spread
      UpdateSpread();
      
      // Atualizar profundidade do mercado
      UpdateMarketDepth();
      
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_spread >= 0.0 && m_market_depth >= 0.0;
   }
   
   void Cleanup() override
   {
      m_institutional_volume = 0.0;
      m_price_impact = 0.0;
      m_market_depth = 0.0;
      m_spread = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "InstitutionalRadar"; }
   
   // Implementação de IDataAnalyzer
   bool AnalyzeData(const MqlRates &rates[], const double &volume[]) override
   {
      if(!m_is_initialized || ArraySize(rates) == 0 || ArraySize(volume) == 0) return false;
      
      // Analisar volume institucional
      AnalyzeInstitutionalVolume(rates, volume);
      
      // Analisar impacto no preço
      AnalyzePriceImpact(rates);
      
      return true;
   }
   
   bool GetAnalysisResults(double &institutional_volume, double &price_impact, double &market_depth, double &spread) override
   {
      if(!m_is_initialized) return false;
      
      institutional_volume = m_institutional_volume;
      price_impact = m_price_impact;
      market_depth = m_market_depth;
      spread = m_spread;
      
      return true;
   }
   
   // Métodos específicos do InstitutionalRadar
   bool DetectInstitutionalActivity(const MqlRates &rates[], const double &volume[])
   {
      if(!m_is_initialized || ArraySize(rates) == 0 || ArraySize(volume) == 0) return false;
      
      // Verificar volume
      if(volume[0] < MIN_VOLUME_THRESHOLD)
         return false;
      
      // Verificar mudança de preço
      double price_change = MathAbs(rates[0].close - rates[1].close) / rates[1].close;
      if(price_change < MIN_PRICE_CHANGE)
         return false;
      
      // Verificar spread
      if(m_spread > MAX_SPREAD)
         return false;
      
      return true;
   }
   
   // Getters
   double GetInstitutionalVolume() const { return m_institutional_volume; }
   double GetPriceImpact() const { return m_price_impact; }
   double GetMarketDepth() const { return m_market_depth; }
   double GetSpread() const { return m_spread; }
   
private:
   void UpdateSpread()
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      
      m_spread = (ask - bid) / ask;
   }
   
   void UpdateMarketDepth()
   {
      // Implementar lógica de atualização da profundidade do mercado
      m_market_depth = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_REAL);
   }
   
   void AnalyzeInstitutionalVolume(const MqlRates &rates[], const double &volume[])
   {
      double total_volume = 0.0;
      double large_trades = 0.0;
      
      for(int i = 0; i < ArraySize(volume); i++)
      {
         total_volume += volume[i];
         
         if(volume[i] > MIN_VOLUME_THRESHOLD)
            large_trades += volume[i];
      }
      
      if(total_volume > 0.0)
         m_institutional_volume = large_trades / total_volume;
      else
         m_institutional_volume = 0.0;
   }
   
   void AnalyzePriceImpact(const MqlRates &rates[])
   {
      double price_change = 0.0;
      double volume_change = 0.0;
      
      for(int i = 1; i < ArraySize(rates); i++)
      {
         price_change += MathAbs(rates[i].close - rates[i-1].close);
         volume_change += MathAbs(rates[i].tick_volume - rates[i-1].tick_volume);
      }
      
      if(volume_change > 0.0)
         m_price_impact = price_change / volume_change;
      else
         m_price_impact = 0.0;
   }
}; 