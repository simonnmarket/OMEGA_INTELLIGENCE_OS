//+------------------------------------------------------------------+
//| VolumeSurgeAgent.mqh - Agente Institucional de Volume            |
//| v10.0 - Detecção Híbrida de Fluxo de Ordens                      |
//+------------------------------------------------------------------+

#include "AgentBase.mqh"
#include <Math\Alglib\alglib.mqh>

class VolumeSurgeAgent : public AgentBase {
private:
   int m_lookback_periods[3];     // Períodos [curto, médio, longo]
   double m_thresholds[2];        // Limiares [compra, venda]
   double m_volume_profile[24];   // Perfil de volume por hora
   double m_flow_imbalance;       // Desequilíbrio de fluxo
   bool m_news_filter;            // Filtro de notícias
   
   // Calcula perfil de volume histórico
   void CalculateVolumeProfile(string symbol) {
      MqlDateTime time;
      TimeCurrent(time);
      int current_hour = time.hour;
      
      for(int i=0; i<24; i++) {
         double sum = 0;
         int count = 0;
         for(int j=1; j<=30; j++) { // 30 dias históricos
            if(iVolume(symbol, PERIOD_H1, j*24 + current_hour) > 0) {
               sum += iVolume(symbol, PERIOD_H1, j*24 + current_hour);
               count++;
            }
         }
         m_volume_profile[i] = count > 0 ? sum/count : 0;
      }
   }
   
   // Calcula desequilíbrio de fluxo
   double CalculateFlowImbalance(string symbol) {
      double buy_vol = 0, sell_vol = 0;
      for(int i=1; i<=m_lookback_periods[1]; i++) {
         double delta = iClose(symbol, PERIOD_M1, i) - iClose(symbol, PERIOD_M1, i+1);
         if(delta > 0) buy_vol += iVolume(symbol, PERIOD_M1, i);
         else sell_vol += iVolume(symbol, PERIOD_M1, i);
      }
      return (buy_vol - sell_vol)/(buy_vol + sell_vol + 1e-8);
   }

public:
   VolumeSurgeAgent() : AgentBase("InstitutionalVolumeHunter") {
      m_lookback_periods[0] = 5;    // Curto prazo
      m_lookback_periods[1] = 20;   // Médio prazo
      m_lookback_periods[2] = 100;  // Longo prazo
      m_thresholds[0] = 1.8;        // Limiar de compra 
      m_thresholds[1] = 1.8;        // Limiar de venda
      m_news_filter = true;
      ArrayInitialize(m_volume_profile, 0);
   }

   int Analyze(string symbol) override {
      // 1. Atualizar perfil de volume
      CalculateVolumeProfile(symbol);
      
      // 2. Calcular métricas de volume
      MqlDateTime time;
      TimeCurrent(time);
      int current_hour = time.hour;
      
      double current_vol = iVolume(symbol, PERIOD_M1, 0);
      double avg_vol_short = iMA(symbol, PERIOD_M1, m_lookback_periods[0], 0, MODE_SMA, PRICE_VOLUME, 0);
      double avg_vol_profile = m_volume_profile[current_hour];
      
      // 3. Calcular desequilíbrio de fluxo
      m_flow_imbalance = CalculateFlowImbalance(symbol);
      
      // 4. Detecção de anomalia
      double vol_ratio_short = current_vol / (avg_vol_short + 1e-8);
      double vol_ratio_profile = current_vol / (avg_vol_profile + 1e-8);
      
      // 5. Filtro de notícias (simplificado)
      bool is_news_event = m_news_filter ? IsNewsTime() : false;
      
      // 6. Lógica de decisão
      if(!is_news_event && (vol_ratio_short > m_thresholds[0] || vol_ratio_profile > 2.5)) {
         if(m_flow_imbalance > 0.2) {
            m_confidence = MathMin(1.0, 0.3 + 0.7 * m_flow_imbalance);
            return 1;
         }
         else if(m_flow_imbalance < -0.2) {
            m_confidence = MathMin(1.0, 0.3 - 0.7 * m_flow_imbalance);
            return -1;
         }
      }
      
      m_confidence = 0.0;
      return 0;
   }

   // Clone especializado
   VolumeSurgeAgent* Clone() const override {
      VolumeSurgeAgent* clone = new VolumeSurgeAgent();
      clone.m_lookback_periods = this.m_lookback_periods;
      clone.m_thresholds = this.m_thresholds;
      clone.m_volume_profile = this.m_volume_profile;
      clone.m_flow_imbalance = this.m_flow_imbalance;
      clone.m_news_filter = this.m_news_filter;
      clone.m_confidence = this.m_confidence;
      clone.m_nash_weight = this.m_nash_weight;
      return clone;
   }

private:
   // Detecção simplificada de período de notícias
   bool IsNewsTime() const {
      MqlDateTime time;
      TimeCurrent(time);
      // Exemplo: filtrar 15 minutos antes/após grandes notícias
      return (time.hour == 14 && time.min >= 45) || // NFP
             (time.hour == 15 && time.min <= 15);   // FOMC
   }
};