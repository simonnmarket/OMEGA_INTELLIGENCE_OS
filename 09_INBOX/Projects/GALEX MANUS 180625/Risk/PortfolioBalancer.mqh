//+------------------------------------------------------------------+
//| PortfolioBalancer.mqh - Sistema de Alocação Quântica Avançado    |
//| v14.0 - Integração com Física de Mercado e Controle Tensorial    |
//+------------------------------------------------------------------+

#include "..\Math\QuantumMath.mqh"
#include "..\Core\MarketField.mqh"
#include <Math\Alglib\alglib.mqh>
#include <Genetic\GeneticAlgorithm.mqh>

class PortfolioBalancer {
private:
   MarketField* m_market_field;
   double m_max_total_risk;
   double m_risk_parity_weights[];
   CMatrixDouble m_correlation_matrix;
   double m_entropy_threshold;
   double m_quantum_coherence;
   double m_sector_exposure[10]; // 10 setores principais
   double m_liquidity_factors[];
   CMatrixDouble m_covariance_matrix;
   double m_value_at_risk;
   
   // Estrutura para estados quânticos do portfólio
   struct QuantumPortfolioState {
      complex wave_function;
      double probability;
      double phase_coherence;
   } m_qstate;

   // Calcula a matriz de covariância quântica
   void CalculateQuantumCovariance(string &symbols[], int count) {
      m_covariance_matrix.Resize(count, count);
      
      for(int i=0; i<count; i++) {
         for(int j=0; j<count; j++) {
            if(i == j) {
               double volatility = iATR(symbols[i], PERIOD_D1, 14, 0);
               m_covariance_matrix[i][j] = MathPow(volatility, 2);
            } else {
               // Usando o produto interno quântico para covariância
               complex psi_i = m_market_field->GetQuantumState(i).GetWaveFunction();
               complex psi_j = m_market_field->GetQuantumState(j).GetWaveFunction();
               m_covariance_matrix[i][j] = (psi_i * psi_j).re;
            }
         }
      }
   }

   // Calcula o Value at Risk quântico
   double CalculateQuantumVaR(string &symbols[], int count) {
      double portfolio_variance = 0;
      double total_weight = 0;
      
      for(int i=0; i<count; i++) {
         for(int j=0; j<count; j++) {
            portfolio_variance += m_risk_parity_weights[i] * 
                                 m_risk_parity_weights[j] * 
                                 m_covariance_matrix[i][j];
         }
         total_weight += m_risk_parity_weights[i];
      }
      
      // Fator de correção quântica
      double qfactor = 1.0 - m_qstate.phase_coherence;
      return MathSqrt(portfolio_variance) * NormalQuantile(0.95) * qfactor;
   }

   // Atualiza o estado quântico do portfólio
   void UpdateQuantumState(string &symbols[], int count) {
      complex total_wave;
      double total_prob = 0;
      
      for(int i=0; i<count; i++) {
         QuantumState state = m_market_field->GetQuantumState(i);
         total_wave += state.GetWaveFunction() * m_risk_parity_weights[i];
         total_prob += state.Probability() * m_risk_parity_weights[i];
      }
      
      m_qstate.wave_function = total_wave;
      m_qstate.probability = total_prob;
      m_qstate.phase_coherence = MathCos(total_wave.im);
   }

public:
   PortfolioBalancer(MarketField* field, double max_total_risk = 25.0) {
      m_market_field = field;
      m_max_total_risk = max_total_risk;
      m_entropy_threshold = 1.5;
      m_quantum_coherence = 1.0;
      m_value_at_risk = 0.0;
      ArrayInitialize(m_sector_exposure, 0);
      ArrayResize(m_risk_parity_weights, 0);
      ArrayResize(m_liquidity_factors, 0);
      m_qstate.wave_function = complex(0,0);
      m_qstate.probability = 0;
      m_qstate.phase_coherence = 0;
   }

   // Interface principal atualizada com mecânica quântica
   bool CanOpenNewPosition(string symbol, double risk_per_position, string &portfolio_symbols[]) {
      // 1. Verificação de coerência quântica
      if(m_qstate.phase_coherence < 0.3) {
         Print("Alerta: Baixa coerência quântica no portfólio - bloqueando novas posições");
         return false;
      }
      
      // 2. Verificação de risco tradicional
      double current_risk = TotalPortfolioRisk(portfolio_symbols);
      double new_var = CalculateQuantumVaR(portfolio_symbols, ArraySize(portfolio_symbols));
      
      if((current_risk + risk_per_position) > m_max_total_risk || new_var > m_max_total_risk * 0.8) {
         return false;
      }
      
      // 3. Verificação de entropia setorial
      string sector = GetAssetSector(symbol);
      if(GetSectorExposure(sector) + risk_per_position > m_max_total_risk * 0.3) {
         return false;
      }
      
      return true;
   }

   // Cálculo de risco com integração quântica
   double TotalPortfolioRisk(string &symbols[]) {
      int count = ArraySize(symbols);
      if(count == 0) return 0;
      
      CalculateQuantumCovariance(symbols, count);
      UpdateQuantumState(symbols, count);
      
      // Cálculo tradicional modificado por fatores quânticos
      double classical_risk = 0;
      for(int i=0; i<count; i++) {
         for(int j=0; j<count; j++) {
            classical_risk += m_risk_parity_weights[i] * 
                            m_risk_parity_weights[j] * 
                            m_covariance_matrix[i][j];
         }
      }
      
      m_value_at_risk = CalculateQuantumVaR(symbols, count);
      return MathSqrt(classical_risk) * (1.0 + m_qstate.phase_coherence) * 100;
   }

   // Rebalanceamento com física quântica
   void QuantumRebalance(string &symbols[], int count) {
      // 1. Atualizar estados quânticos
      m_market_field->AnalyzeAll(symbols, count);
      
      // 2. Calcular nova matriz de covariância
      CalculateQuantumCovariance(symbols, count);
      
      // 3. Otimizar pesos com algoritmo genético quântico
      OptimizeWeightsWithGA(symbols, count);
      
      // 4. Aplicar limites de coerência
      if(m_qstate.phase_coherence < 0.2) {
         ForceDecoherenceRebalance(symbols, count);
      }
      
      // 5. Atualizar perfil de liquidez
      UpdateLiquidityProfile(symbols, count);
   }

private:
   // Otimização com algoritmo genético quântico
   void OptimizeWeightsWithGA(string &symbols[], int count) {
      CGeneticalAlgorithm ga;
      ga.SetQuantumMode(true); // Ativa modo quântico
      ga.SetPopulationSize(150);
      ga.SetGenerationsNumber(100);
      
      // Função de fitness multi-objetivo
      ga.FitnessFunction([&](double &weights[]) {
         double sharpe = CalculatePortfolioSharpe(weights, symbols);
         double coherence = CalculatePortfolioCoherence(weights, symbols);
         return sharpe * coherence;
      });
      
      // Executa otimização
      double optimized_weights[];
      ga.Optimize(optimized_weights);
      
      // Aplica pesos com normalização quântica
      double sum = 0;
      for(int i=0; i<count; i++) sum += optimized_weights[i];
      for(int i=0; i<count; i++) m_risk_parity_weights[i] = optimized_weights[i] / sum;
   }

   // Rebalanceamento forçado por decoerência
   void ForceDecoherenceRebalance(string &symbols[], int count) {
      // 1. Fechar posições mais correlacionadas
      for(int i=PositionsTotal()-1; i>=0; i--) {
         string sym = PositionGetString(POSITION_SYMBOL);
         if(GetQuantumCorrelation(sym, symbols) > 0.7) {
            trade.PositionClose(sym);
         }
      }
      
      // 2. Resetar pesos para estado base
      double base_weight = 1.0 / count;
      for(int i=0; i<count; i++) {
         m_risk_parity_weights[i] = base_weight;
      }
      
      // 3. Resetar estado quântico
      m_qstate.phase_coherence = 1.0;
      m_qstate.wave_function = complex(base_weight, 0);
   }

   // Atualiza perfil de liquidez
   void UpdateLiquidityProfile(string &symbols[], int count) {
      ArrayResize(m_liquidity_factors, count);
      
      for(int i=0; i<count; i++) {
         double volume = iVolume(symbols[i], PERIOD_D1, 0);
         double spread = SymbolInfoDouble(symbols[i], SYMBOL_ASK) - 
                        SymbolInfoDouble(symbols[i], SYMBOL_BID);
         
         m_liquidity_factors[i] = volume / (spread + 1e-8);
      }
   }

   // Métodos auxiliares avançados
   double GetQuantumCorrelation(string symbol, string &portfolio_symbols[]) {
      int index = -1;
      for(int i=0; i<ArraySize(portfolio_symbols); i++) {
         if(portfolio_symbols[i] == symbol) {
            index = i;
            break;
         }
      }
      
      if(index == -1) return 0;
      
      double max_corr = 0;
      for(int i=0; i<ArraySize(portfolio_symbols); i++) {
         if(i != index) {
            max_corr = MathMax(max_corr, MathAbs(m_covariance_matrix[index][i]));
         }
      }
      
      return max_corr;
   }

   string GetAssetSector(string symbol) {
      // Mapeamento simplificado - implementação real requer base de dados
      string currency = StringSubstr(symbol, 0, 3);
      if(currency == "XAU") return "METAL";
      if(currency == "BTC") return "CRYPTO";
      return "FOREX";
   }

   double GetSectorExposure(string sector) {
      // Implementação simplificada
      if(sector == "FOREX") return m_sector_exposure[0];
      if(sector == "METAL") return m_sector_exposure[1];
      if(sector == "CRYPTO") return m_sector_exposure[2];
      return 0;
   }

public:
   // Métricas avançadas de análise
   double GetPortfolioCoherence() const { return m_qstate.phase_coherence; }
   double GetQuantumProbability() const { return m_qstate.probability; }
   double GetValueAtRisk() const { return m_value_at_risk; }
   
   // Controle de parâmetros dinâmicos
   void SetEntropyThreshold(double threshold) { m_entropy_threshold = threshold; }
   void SetMaxSectorExposure(double exposure) { 
      for(int i=0; i<10; i++) m_sector_exposure[i] = exposure; 
   }
   
   // Geração de relatório quântico
   string GenerateQuantumReport() const {
      string report = "=== RELATÓRIO QUÂNTICO DO PORTFÓLIO ===\n";
      report += "Coerência: " + DoubleToString(m_qstate.phase_coherence, 3) + "\n";
      report += "Probabilidade: " + DoubleToString(m_qstate.probability, 3) + "\n";
      report += "Value at Risk: " + DoubleToString(m_value_at_risk, 2) + "%\n";
      report += "Entropia: " + DoubleToString(PortfolioEntropy(), 3) + "\n";
      report += "Estado: " + (m_qstate.phase_coherence > 0.6 ? "COERENTE" : "DECOERENTE");
      return report;
   }
};