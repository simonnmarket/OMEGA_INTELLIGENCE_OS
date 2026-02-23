//+------------------------------------------------------------------+
//| AdvancedRiskManager.mqh - Gerenciamento de Risco Avançado        |
//| Inspirado em: Black-Scholes, Markowitz, Kelly                     |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>
#include <Trade\Trade.mqh>
#include "..\Core\VolatilityAnalysis.mqh"
#include <Object.mqh>
#include <StdLibErr.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>
#include <Math\Stat\stat.mqh>

#property copyright "Copyright 2025, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict

// Enum para códigos de erro personalizados
enum RiskErrorCodes {
    RISK_OK = 0,
    RISK_INVALID_SYMBOL = 1,
    RISK_INVALID_PARAMS = 2,
    RISK_CALCULATION_ERROR = 3,
    RISK_API_TIMEOUT = 4
};

// Estruturas para análise avançada
struct StressScenario {
   string name;
   double market_shock;      // Choque de mercado em %
   double volatility_shock;  // Choque de volatilidade em %
   double correlation_shock; // Choque de correlação em %
   double liquidity_shock;   // Choque de liquidez em %
};

struct LiquidityMetrics {
   double bid_ask_spread;
   double market_depth;
   double volume_profile;
   double slippage_estimate;
};

struct RiskAttribution {
   double market_risk;
   double credit_risk;
   double liquidity_risk;
   double operational_risk;
   double model_risk;
};

struct ModelValidation {
   double backtest_accuracy;
   double out_of_sample_performance;
   double model_stability;
   double parameter_sensitivity;
};

struct RegulatoryMetrics {
   double var_99;
   double expected_shortfall;
   double leverage_ratio;
   double liquidity_coverage_ratio;
   double net_stable_funding_ratio;
};

// Estrutura para grupos de exposição
struct ExposureGroup {
   string name;
   double max_risk_percent;
   double current_exposure;
};

class AdvancedRiskManager
{
private:
   // Parâmetros de risco
   string m_symbols[];
   double m_risk_per_trade;
   int m_max_orders;
   double m_max_daily_risk;
   double m_max_drawdown;
   double m_kelly_fraction;
   long m_magic_number;
   double m_risk_free_rate;
   double m_stress_factor;
   string m_log_file;
   bool m_use_ewma;              // Flag para usar EWMA em vez de GARCH
   double m_ewma_lambda;         // Parâmetro lambda para EWMA

   // Grupos de exposição
   ExposureGroup m_groups[];

   // Métricas de risco
   struct RiskMetrics {
      double var_95;
      double var_99;
      double cvar_95;
      double cvar_99;
      double sharpe_ratio;
      double sortino_ratio;
      double calmar_ratio;
      double max_drawdown;
      double current_drawdown;
      double daily_pnl;
      double monthly_pnl;
      double win_rate;
      double profit_factor;
      double ewma_volatility;    // Volatilidade EWMA
   };
   
   RiskMetrics m_metrics;
   
   // Histórico de trades
   struct TradeHistory {
      datetime time;
      double profit;
      double risk;
      double reward;
      string symbol;
   };
   
   TradeHistory m_trades[];
   CMatrixDouble m_correlation_matrix;
   int m_monte_carlo_paths;
   double m_garch_alpha;
   double m_garch_beta;
   double m_garch_omega;

   // Arrays para cenários de stress
   StressScenario m_scenarios[];
   
   // Métodos de análise avançada
   double CalculateCorrelationImpact(double correlation_shock) {
      double impact = 0;
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         for(int j = i + 1; j < ArraySize(m_symbols); j++) {
            double current_corr = m_correlation_matrix[i][j];
            double shocked_corr = current_corr * (1 + correlation_shock);
            impact += MathAbs(shocked_corr - current_corr);
         }
      }
      return impact;
   }
   
   double CalculateLiquidityImpact(double liquidity_shock) {
      double impact = 0;
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         LiquidityMetrics metrics = CalculateLiquidityMetrics(m_symbols[i]);
         impact += metrics.slippage_estimate * (1 + liquidity_shock);
      }
      return impact;
   }
   
   double CalculateHistoricalSlippage(string symbol) {
      double slippage = 0;
      int count = 0;
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         if(m_trades[i].symbol == symbol) {
            double expected_price = m_trades[i].profit / m_trades[i].risk;
            double actual_price = m_trades[i].reward / m_trades[i].risk;
            slippage += MathAbs(expected_price - actual_price) / expected_price;
            count++;
         }
      }
      
      return count > 0 ? slippage / count : 0;
   }
   
   double CalculateVolumeProfile(string symbol) {
      double volume_profile[];
      ArraySetAsSeries(volume_profile, true);
      int copied = CopyTickVolume(symbol, PERIOD_M1, 0, 100, volume_profile);
      
      if(copied > 0) {
         double avg_volume = 0;
         for(int i = 0; i < copied; i++) {
            avg_volume += volume_profile[i];
         }
         return avg_volume / copied;
      }
      return 0;
   }
   
   double CalculateMarketDepth(string symbol) {
      double volume = SymbolInfoDouble(symbol, SYMBOL_VOLUME_REAL);
      double tick_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      return volume * tick_size;
   }
   
   double CalculateBidAskSpread(string symbol) {
      double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
      return (ask - bid) / bid * 100;
   }
   
   double CalculateMarketRiskContribution(double &returns[]) {
      double contribution = 0;
      double portfolio_variance = 0;
      
      for(int i = 0; i < ArraySize(returns); i++) {
         portfolio_variance += returns[i] * returns[i];
      }
      
      for(int i = 0; i < ArraySize(returns); i++) {
         contribution += returns[i] * returns[i] / portfolio_variance;
      }
      
      return contribution;
   }
   
   double CalculateCreditRiskContribution() {
      double contribution = 0;
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         double spread = SymbolInfoDouble(m_symbols[i], SYMBOL_ASK) - 
                        SymbolInfoDouble(m_symbols[i], SYMBOL_BID);
         double counterparty_risk = 0.01; // 1% de risco de contraparte
         contribution += spread * m_risk_per_trade * (1 + counterparty_risk);
      }
      return contribution;
   }
   
   double CalculateLiquidityRiskContribution() {
      double contribution = 0;
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         LiquidityMetrics metrics = CalculateLiquidityMetrics(m_symbols[i]);
         double liquidity_score = (metrics.bid_ask_spread * 0.3) + 
                                (1 / metrics.market_depth * 0.3) + 
                                (metrics.slippage_estimate * 0.4);
         contribution += liquidity_score * m_risk_per_trade;
      }
      return contribution;
   }
   
   double CalculateOperationalRiskContribution() {
      double gross_income = 0;
      for(int i = 0; i < ArraySize(m_trades); i++) {
         gross_income += MathAbs(m_trades[i].profit);
      }
      
      double alpha = 0.15;
      return gross_income * alpha;
   }
   
   double CalculateModelRiskContribution() {
      ModelValidation validation = ValidateRiskModels();
      
      double model_risk = (1 - validation.backtest_accuracy) * 0.4 +
                         (1 - validation.out_of_sample_performance) * 0.3 +
                         (1 - validation.model_stability) * 0.2 +
                         (1 - validation.parameter_sensitivity) * 0.1;
      
      return model_risk * m_risk_per_trade;
   }
   
   double CalculateBacktestAccuracy() {
      double accuracy = 0;
      int correct_predictions = 0;
      int total_predictions = 0;
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         if(i > 0) { // Precisa de pelo menos um trade anterior para previsão
            double predicted_risk = m_trades[i-1].risk;
            double actual_risk = m_trades[i].risk;
            
            // Considera a previsão correta se estiver dentro de 10% do valor real
            if(MathAbs(predicted_risk - actual_risk) / actual_risk <= 0.1) {
               correct_predictions++;
            }
            total_predictions++;
         }
      }
      
      return total_predictions > 0 ? (double)correct_predictions / total_predictions : 0;
   }
   
   double CalculateOutOfSamplePerformance() {
      // Divide os dados em treino (70%) e teste (30%)
      int split_point = (int)(ArraySize(m_trades) * 0.7);
      
      double in_sample_sharpe = CalculateSharpeRatio(0, split_point);
      double out_of_sample_sharpe = CalculateSharpeRatio(split_point, ArraySize(m_trades));
      
      // Compara o desempenho fora da amostra com o desempenho dentro da amostra
      return out_of_sample_sharpe / in_sample_sharpe;
   }
   
   double CalculateModelStability() {
      double stability = 0;
      int periods = 10; // Número de períodos para análise
      
      if(ArraySize(m_trades) >= periods) {
         double var_values[];
         ArrayResize(var_values, periods);
         
         // Calcula VaR para diferentes períodos
         for(int i = 0; i < periods; i++) {
            int start_idx = i * (ArraySize(m_trades) / periods);
            int end_idx = (i + 1) * (ArraySize(m_trades) / periods);
            var_values[i] = CalculateValueAtRisk(start_idx, end_idx);
         }
         
         // Calcula o coeficiente de variação (menor = mais estável)
         double mean = 0, variance = 0;
         for(int i = 0; i < periods; i++) {
            mean += var_values[i];
         }
         mean /= periods;
         
         for(int i = 0; i < periods; i++) {
            variance += MathPow(var_values[i] - mean, 2);
         }
         variance /= periods;
         
         stability = 1 / (1 + MathSqrt(variance) / mean);
      }
      
      return stability;
   }
   
   double CalculateParameterSensitivity() {
      double base_risk = m_risk_per_trade;
      double sensitivity = 0;
      
      // Testa sensibilidade a variações de 10% nos parâmetros principais
      double parameters[] = {m_kelly_fraction, m_ewma_lambda};
      double variations[] = {0.1, 0.1}; // 10% de variação
      
      for(int i = 0; i < ArraySize(parameters); i++) {
         double original_value = parameters[i];
         double varied_value = original_value * (1 + variations[i]);
         
         // Simula risco com parâmetro variado
         double varied_risk = SimulateRiskWithParameter(varied_value);
         
         // Calcula sensibilidade como mudança percentual no risco
         sensitivity += MathAbs(varied_risk - base_risk) / base_risk;
      }
      
      return 1 / (1 + sensitivity); // Normaliza para [0,1]
   }
   
   double SimulateRiskWithParameter(double parameter_value) {
      // Implementação simplificada - simula risco com parâmetro variado
      return m_risk_per_trade * (1 + parameter_value);
   }

   // Log com timestamp e nível de severidade
   void Log(string message, string severity = "INFO") {
      int handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT|FILE_COMMON, ';');
      if(handle != INVALID_HANDLE) {
         string log_entry = StringFormat("[%s][%s] %s", 
            TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), 
            severity, 
            message);
         FileWrite(handle, log_entry);
         FileClose(handle);
      } else {
         Print("[ERROR] Falha ao abrir arquivo de log: ", GetLastError());
      }
   }
   
   // Validação robusta de inputs
   RiskErrorCodes ValidateInputs() {
      if(ArraySize(m_symbols) == 0) {
         Log("Nenhum símbolo configurado", "ERROR");
         return RISK_INVALID_PARAMS;
      }
      
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         if(!SymbolInfoDouble(m_symbols[i], SYMBOL_TRADE_TICK_VALUE) || 
            !SymbolInfoDouble(m_symbols[i], SYMBOL_TRADE_TICK_SIZE)) {
            Log("Dados do símbolo inválidos: " + m_symbols[i], "ERROR");
            return RISK_INVALID_SYMBOL;
         }
      }
      
      if(m_risk_per_trade <= 0 || m_max_orders <= 0 || m_kelly_fraction <= 0) {
         Log("Parâmetros de risco inválidos", "ERROR");
         return RISK_INVALID_PARAMS;
      }
      return RISK_OK;
   }
   
   // Cálculo de volatilidade com EWMA
   double CalculateEWMAVolatility() {
      double prices[];
      int copied = CopyClose(m_symbols[0], PERIOD_M1, 0, 101, prices);
      if(copied < 101) {
         Log("Erro ao copiar dados históricos", "ERROR");
         return 0.0;
      }
      ArraySetAsSeries(prices, true);

      double returns[];
      ArrayResize(returns, 100);

      for(int i = 0; i < 100; i++) {
         returns[i] = MathLog(prices[i] / prices[i+1]); // Log-retorno
      }

      double variance = returns[0] * returns[0];
      for(int i = 1; i < 100; i++) {
         variance = m_ewma_lambda * variance + (1 - m_ewma_lambda) * returns[i] * returns[i];
      }

      m_metrics.ewma_volatility = MathSqrt(variance * 252); // Anualizado
      return m_metrics.ewma_volatility;
   }

   // Gera um número mágico único
   long GenerateUniqueMagicNumber() {
      return (long)(GetTickCount() + MathRand());
   }

   // Métodos de métricas regulatórias
   double CalculateValueAtRisk99() {
      double returns[];
      ArrayResize(returns, ArraySize(m_trades));
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         returns[i] = m_trades[i].profit;
      }
      
      // Ordena retornos
      ArraySort(returns);
      
      // Calcula VaR 99%
      int var_index = (int)(ArraySize(returns) * 0.01);
      return -returns[var_index];
   }
   
   double CalculateExpectedShortfall() {
      double returns[];
      ArrayResize(returns, ArraySize(m_trades));
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         returns[i] = m_trades[i].profit;
      }
      
      // Ordena retornos
      ArraySort(returns);
      
      // Calcula ES (média das perdas além do VaR)
      int var_index = (int)(ArraySize(returns) * 0.01);
      double es = 0;
      
      for(int i = 0; i < var_index; i++) {
         es += returns[i];
      }
      
      return -es / var_index;
   }
   
   double CalculateLeverageRatio() {
      double total_assets = 0;
      double total_equity = 0;
      
      for(int i = 0; i < PositionsTotal(); i++) {
         ulong ticket = PositionGetTicket(i);
         if(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_MAGIC) == m_magic_number) {
            total_assets += PositionGetDouble(POSITION_VOLUME) * 
                          PositionGetDouble(POSITION_PRICE_OPEN);
         }
      }
      
      // Assume equity como 10% dos ativos totais (ajuste conforme necessário)
      total_equity = total_assets * 0.1;
      
      return total_assets / total_equity;
   }
   
   double CalculateLiquidityCoverageRatio() {
      double hqla = 0; // High Quality Liquid Assets
      double net_outflow = 0;
      
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         LiquidityMetrics metrics = CalculateLiquidityMetrics(m_symbols[i]);
         
         // Considera ativos com alta liquidez como HQLA
         if(metrics.bid_ask_spread < 0.05 && metrics.market_depth > 1000000) {
            hqla += PositionGetDouble(POSITION_VOLUME) * 
                   PositionGetDouble(POSITION_PRICE_OPEN);
         }
         
         // Estima saída líquida baseada no histórico de trades
         net_outflow += CalculateNetOutflow(m_symbols[i]);
      }
      
      return net_outflow > 0 ? hqla / net_outflow : 1.0;
   }
   
   double CalculateNetStableFundingRatio() {
      double available_stable_funding = 0;
      double required_stable_funding = 0;
      
      for(int i = 0; i < ArraySize(m_symbols); i++) {
         double position_value = PositionGetDouble(POSITION_VOLUME) * 
                               PositionGetDouble(POSITION_PRICE_OPEN);
         
         // Calcula funding disponível (assume 100% de funding estável)
         available_stable_funding += position_value;
         
         // Calcula funding requerido baseado no tipo de ativo
         double asf_factor = CalculateASFFactor(m_symbols[i]);
         required_stable_funding += position_value * asf_factor;
      }
      
      return required_stable_funding > 0 ? available_stable_funding / required_stable_funding : 1.0;
   }
   
   double CalculateASFFactor(string symbol) {
      // Implementação simplificada dos fatores ASF do Basel III
      // Valores reais devem ser ajustados conforme regulamentação específica
      return 0.85; // Fator padrão para a maioria dos ativos
   }
   
   double CalculateNetOutflow(string symbol) {
      double outflow = 0;
      int lookback = 30; // 30 dias de histórico
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         if(m_trades[i].symbol == symbol && i < lookback) {
            outflow += MathAbs(m_trades[i].profit);
         }
      }
      
      return outflow / lookback;
   }

   // Métodos de Stress Testing
   void InitializeStressScenarios() {
      ArrayResize(m_scenarios, 5);
      
      // Cenário 1: Crise de Mercado
      m_scenarios[0].name = "Crise de Mercado";
      m_scenarios[0].market_shock = -0.15;      // -15% choque de mercado
      m_scenarios[0].volatility_shock = 0.50;   // +50% choque de volatilidade
      m_scenarios[0].correlation_shock = 0.30;  // +30% choque de correlação
      m_scenarios[0].liquidity_shock = 0.40;    // +40% choque de liquidez
      
      // Cenário 2: Crise de Liquidez
      m_scenarios[1].name = "Crise de Liquidez";
      m_scenarios[1].market_shock = -0.05;      // -5% choque de mercado
      m_scenarios[1].volatility_shock = 0.20;   // +20% choque de volatilidade
      m_scenarios[1].correlation_shock = 0.10;  // +10% choque de correlação
      m_scenarios[1].liquidity_shock = 0.80;    // +80% choque de liquidez
      
      // Cenário 3: Crise de Correlação
      m_scenarios[2].name = "Crise de Correlação";
      m_scenarios[2].market_shock = -0.10;      // -10% choque de mercado
      m_scenarios[2].volatility_shock = 0.30;   // +30% choque de volatilidade
      m_scenarios[2].correlation_shock = 0.50;  // +50% choque de correlação
      m_scenarios[2].liquidity_shock = 0.20;    // +20% choque de liquidez
      
      // Cenário 4: Crise de Volatilidade
      m_scenarios[3].name = "Crise de Volatilidade";
      m_scenarios[3].market_shock = -0.08;      // -8% choque de mercado
      m_scenarios[3].volatility_shock = 0.70;   // +70% choque de volatilidade
      m_scenarios[3].correlation_shock = 0.20;  // +20% choque de correlação
      m_scenarios[3].liquidity_shock = 0.30;    // +30% choque de liquidez
      
      // Cenário 5: Crise Sistêmica
      m_scenarios[4].name = "Crise Sistêmica";
      m_scenarios[4].market_shock = -0.20;      // -20% choque de mercado
      m_scenarios[4].volatility_shock = 0.60;   // +60% choque de volatilidade
      m_scenarios[4].correlation_shock = 0.40;  // +40% choque de correlação
      m_scenarios[4].liquidity_shock = 0.60;    // +60% choque de liquidez
   }
   
   double CalculatePortfolioImpact(const StressScenario &scenario) {
      double total_impact = 0;
      double portfolio_value = 0;
      
      for(int i = 0; i < PositionsTotal(); i++) {
         ulong ticket = PositionGetTicket(i);
         if(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_MAGIC) == m_magic_number) {
            string symbol = PositionGetString(POSITION_SYMBOL);
            double position_value = PositionGetDouble(POSITION_VOLUME) * 
                                  PositionGetDouble(POSITION_PRICE_OPEN);
            
            // Impacto direto do choque de mercado
            double market_impact = position_value * scenario.market_shock;
            
            // Impacto da volatilidade
            double current_vol = CalculateEWMAVolatility();
            double vol_impact = position_value * (current_vol * scenario.volatility_shock);
            
            // Impacto da correlação
            double corr_impact = CalculateCorrelationImpact(scenario.correlation_shock);
            
            // Impacto da liquidez
            LiquidityMetrics metrics = CalculateLiquidityMetrics(symbol);
            double liquidity_impact = position_value * 
                                    (metrics.slippage_estimate * scenario.liquidity_shock);
            
            // Soma todos os impactos
            total_impact += market_impact + vol_impact + corr_impact + liquidity_impact;
            portfolio_value += position_value;
         }
      }
      
      return portfolio_value > 0 ? (total_impact / portfolio_value) * 100 : 0;
   }

   // Métodos auxiliares para cálculos estatísticos
   double ArrayMean(const double &array[]) {
      double sum = 0;
      for(int i = 0; i < ArraySize(array); i++) {
         sum += array[i];
      }
      return ArraySize(array) > 0 ? sum / ArraySize(array) : 0;
   }
   
   double ArrayStdDev(const double &array[]) {
      double mean = ArrayMean(array);
      double sum = 0;
      
      for(int i = 0; i < ArraySize(array); i++) {
         sum += MathPow(array[i] - mean, 2);
      }
      
      return ArraySize(array) > 1 ? MathSqrt(sum / (ArraySize(array) - 1)) : 0;
   }
   
   // Carrega retornos diários
   bool LoadDailyReturns(double &returns[]) {
      double equity[];
      if(!HistorySelect(TimeCurrent() - 365 * 86400, TimeCurrent(), equity)) {
         Log("Erro ao carregar histórico de equity", "ERROR");
         return false;
      }
      
      ArraySetAsSeries(equity, true);
      int size = ArraySize(equity);
      if(size < 2) {
         Log("Dados insuficientes para cálculo de retornos", "WARNING");
         return false;
      }
      
      ArrayResize(returns, size - 1);
      for(int i = 0; i < size - 1; i++) {
         returns[i] = (equity[i] - equity[i + 1]) / MathMax(equity[i + 1], 1e-7);
      }
      return true;
   }

   // Cálculo de volatilidade GARCH
   double CalculateGARCHVolatility() {
      double returns[];
      if(!LoadDailyReturns(returns)) {
         Log("Erro ao carregar retornos para GARCH", "ERROR");
         return 0.0;
      }

      alglib::real_1d_array r;
      r.setcontent(ArraySize(returns), returns);

      double mu, alpha0, alpha1, beta1;
      alglib::garchreport report;

      // Ajuste do modelo GARCH(1,1)
      alglib::garchfit(r, r.length(), 1, 1, mu, alpha0, alpha1, beta1, report);

      // Previsão da variância condicional
      double h = alpha0 + alpha1 * r[r.length()-1]*r[r.length()-1] + beta1 * 0.01;

      double volatility = MathSqrt(h);
      Log(StringFormat("Volatilidade GARCH calculada: %.4f%%", volatility * 100));
      return volatility;
   }

   // Método auxiliar para VaR com volatilidade customizada
   double CalculateVaRWithVolatility(double custom_volatility, double confidence_level = 0.95) {
      double returns[];
      ArrayResize(returns, m_monte_carlo_paths);

      MathSrand((int)(TimeCurrent() * TimeGMT()));
      for(int i = 0; i < m_monte_carlo_paths; i++) {
         double z = MathRand() / 32767.0;
         z = MathSqrt(-2.0 * MathLog(z)) * MathCos(2.0 * M_PI * MathRand() / 32767.0);
         returns[i] = custom_volatility * z;
      }

      ArraySort(returns);
      int index = (int)MathFloor(m_monte_carlo_paths * (1 - confidence_level));
      return -returns[index];
   }

   // Associa símbolos a grupos
   string GetSymbolGroup(string symbol) {
      if(StringFind(symbol, "XAUUSD") != -1 || StringFind(symbol, "XAGUSD") != -1)
         return "Commodities";
      if(StringFind(symbol, "BTCUSD") != -1 || StringFind(symbol, "ETHUSD") != -1)
         return "Crypto";
      return "Forex";
   }

public:
   AdvancedRiskManager(string symbols[], double risk_per_trade = 1.0, int max_orders = 10, 
                       long magic_number = 123456, double risk_free_rate = 0.02, 
                       bool use_ewma = false, double ewma_lambda = 0.94) 
      : m_risk_per_trade(risk_per_trade), m_max_orders(max_orders), 
        m_magic_number(GenerateUniqueMagicNumber()), m_risk_free_rate(risk_free_rate),
        m_use_ewma(use_ewma), m_ewma_lambda(ewma_lambda) {
      
      ArrayCopy(m_symbols, symbols);
      m_max_daily_risk = risk_per_trade * 2.5;
      m_max_drawdown = risk_per_trade * 7.5;
      m_kelly_fraction = 0.5;
      m_monte_carlo_paths = 10000;
      m_garch_alpha = 0.1;
      m_garch_beta = 0.8;
      m_garch_omega = 0.0001;
      m_log_file = "RiskManager_Log_" + IntegerToString(GetTickCount()) + ".txt";
      m_stress_factor = 2.0;
      
      ZeroMemory(m_metrics);
      m_correlation_matrix.Resize(ArraySize(m_symbols), ArraySize(m_symbols));
      m_correlation_matrix.Fill(0);
      
      Log("Inicialização concluída. Símbolos: " + IntegerToString(ArraySize(m_symbols)));
   }
   
   // Cálculo de Kelly com validação robusta
   double CalculateKellyPosition(string symbol, double win_rate, double avg_win, double avg_loss) {
      if(ValidateInputs() != RISK_OK) return 0.0;
      
      if(avg_loss == 0 || avg_win == 0) {
         Log("Erro: avg_win ou avg_loss zerados em CalculateKellyPosition", "ERROR");
         return 0.0;
      }
      
      double reward_ratio = avg_win / MathAbs(avg_loss);
      double kelly = win_rate - ((1 - win_rate) / reward_ratio);
      double adjusted_kelly = MathMin(kelly * m_kelly_fraction, 0.99); // Limita a 99% do capital
      
      Log(StringFormat("Kelly Calculado: %.2f% (Símbolo: %s)", adjusted_kelly * 100, symbol));
      return adjusted_kelly;
   }
   
   // Cálculo de VaR com fallback para EWMA
   double CalculateVaR(double confidence_level) {
      if(ValidateInputs() != RISK_OK) return 0.0;
      
      double volatility = m_use_ewma ? CalculateEWMAVolatility() : CalculateGARCHVolatility();
      double returns[];
      ArrayResize(returns, m_monte_carlo_paths);
      double last_price = iClose(m_symbols[0], PERIOD_M1, 1);
      
      MathSrand(GetTickCount()); // Seed mais robusta
      for(int i = 0; i < m_monte_carlo_paths; i++) {
         double z = MathRand() / 32767.0;
         z = MathSqrt(-2.0 * MathLog(z)) * MathCos(2.0 * M_PI * MathRand() / 32767.0);
         returns[i] = volatility * z;
      }
      
      ArraySort(returns);
      int index = (int)MathFloor(m_monte_carlo_paths * (1 - confidence_level));
      double var = -returns[index] * last_price;
      
      Log(StringFormat("VaR %.0f%% calculado: %.2f (Método: %s)", 
          confidence_level * 100, var, m_use_ewma ? "EWMA" : "GARCH"));
      return var;
   }

   // Kill Switch com confirmação
   void TriggerKillSwitch() {
      int closed_positions = 0;
      for(int i = PositionsTotal() - 1; i >= 0; i--) {
         ulong ticket = PositionGetTicket(i);
         if(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_MAGIC) == m_magic_number) {
            CTrade trade;
            if(trade.PositionClose(ticket)) {
               closed_positions++;
               Log("Posição fechada via Kill Switch. Ticket: " + IntegerToString(ticket));
            }
         }
      }
      SendNotification("Kill Switch acionado. Posições fechadas: " + IntegerToString(closed_positions));
   }

   // Relatório em formato CSV para integração
   string GenerateRegulatoryReportCSV() {
      string csv = "Metrica,Valor\n";
      csv += StringFormat("VaR 95%%,%.4f\n", m_metrics.var_95);
      csv += StringFormat("CVaR 95%%,%.4f\n", m_metrics.cvar_95);
      csv += StringFormat("Drawdown Atual,%.2f%%\n", m_metrics.current_drawdown * 100);
      csv += StringFormat("Volatilidade (%s),%.2f%%\n", m_use_ewma ? "EWMA" : "GARCH", 
             (m_use_ewma ? m_metrics.ewma_volatility : CalculateGARCHVolatility()) * 100);
      csv += StringFormat("Sharpe Ratio,%.2f\n", m_metrics.sharpe_ratio);
      csv += StringFormat("Sortino Ratio,%.2f\n", m_metrics.sortino_ratio);
      csv += StringFormat("Calmar Ratio,%.2f\n", m_metrics.calmar_ratio);

      // Adiciona informações de exposição por grupo
      csv += "\nGrupo,Exposição Atual,Limite Máximo\n";
      for(int i = 0; i < ArraySize(m_groups); i++) {
         csv += StringFormat("%s,%.2f%%,%.2f%%\n", 
            m_groups[i].name, 
            m_groups[i].current_exposure,
            m_groups[i].max_risk_percent);
      }

      string filename = "RiskReport_" + TimeToString(TimeCurrent(), TIME_DATE) + ".csv";
      int handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_COMMON);
      if(handle != INVALID_HANDLE) {
         FileWrite(handle, csv);
         FileClose(handle);
      }
      return csv;
   }

   // Novos métodos públicos
   double RunStressTest(const StressScenario &scenario) {
      double portfolio_value = 0;
      double max_loss = 0;
      
      for(int i = 0; i < PositionsTotal(); i++) {
         ulong ticket = PositionGetTicket(i);
         if(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_MAGIC) == m_magic_number) {
            double position_value = PositionGetDouble(POSITION_VOLUME) * 
                                  PositionGetDouble(POSITION_PRICE_OPEN);
            double shock_value = position_value * scenario.market_shock;
            
            double current_vol = CalculateEWMAVolatility();
            double shocked_vol = current_vol * (1 + scenario.volatility_shock);
            
            double correlation_impact = CalculateCorrelationImpact(scenario.correlation_shock);
            double liquidity_impact = CalculateLiquidityImpact(scenario.liquidity_shock);
            
            double total_impact = shock_value + correlation_impact + liquidity_impact;
            max_loss = MathMin(max_loss, total_impact);
            portfolio_value += position_value;
         }
      }
      
      return (max_loss / portfolio_value) * 100;
   }
   
   LiquidityMetrics CalculateLiquidityMetrics(string symbol) {
      LiquidityMetrics metrics;
      
      // Calcula spread bid-ask
      metrics.bid_ask_spread = CalculateBidAskSpread(symbol);
      
      // Calcula profundidade de mercado
      metrics.market_depth = CalculateMarketDepth(symbol);
      
      // Calcula perfil de volume
      metrics.volume_profile = CalculateVolumeProfile(symbol);
      
      // Estima slippage baseado no histórico
      metrics.slippage_estimate = CalculateHistoricalSlippage(symbol);
      
      // Log das métricas de liquidez
      Log(StringFormat("Métricas de Liquidez para %s: Spread=%.4f%%, Profundidade=%.2f, Volume=%.2f, Slippage=%.4f%%",
          symbol, metrics.bid_ask_spread, metrics.market_depth, metrics.volume_profile, metrics.slippage_estimate * 100));
      
      return metrics;
   }
   
   RiskAttribution CalculateRiskAttribution() {
      RiskAttribution attribution;
      
      double returns[];
      ArrayResize(returns, ArraySize(m_trades));
      
      for(int i = 0; i < ArraySize(m_trades); i++) {
         returns[i] = m_trades[i].profit;
      }
      
      attribution.market_risk = CalculateMarketRiskContribution(returns);
      attribution.credit_risk = CalculateCreditRiskContribution();
      attribution.liquidity_risk = CalculateLiquidityRiskContribution();
      attribution.operational_risk = CalculateOperationalRiskContribution();
      attribution.model_risk = CalculateModelRiskContribution();
      
      Log(StringFormat("Atribuição de Risco: Mercado=%.2f%%, Crédito=%.2f%%, Liquidez=%.2f%%, Operacional=%.2f%%, Modelo=%.2f%%",
          attribution.market_risk * 100,
          attribution.credit_risk * 100,
          attribution.liquidity_risk * 100,
          attribution.operational_risk * 100,
          attribution.model_risk * 100));
      
      return attribution;
   }
   
   ModelValidation ValidateRiskModels() {
      ModelValidation validation;
      
      validation.backtest_accuracy = CalculateBacktestAccuracy();
      validation.out_of_sample_performance = CalculateOutOfSamplePerformance();
      validation.model_stability = CalculateModelStability();
      validation.parameter_sensitivity = CalculateParameterSensitivity();
      
      // Log dos resultados da validação
      Log(StringFormat("Validação de Modelos: Backtest=%.2f%%, Out-of-Sample=%.2f%%, Estabilidade=%.2f%%, Sensibilidade=%.2f%%",
          validation.backtest_accuracy * 100,
          validation.out_of_sample_performance * 100,
          validation.model_stability * 100,
          validation.parameter_sensitivity * 100));
      
      return validation;
   }
   
   RegulatoryMetrics CalculateRegulatoryMetrics() {
      RegulatoryMetrics metrics;
      
      metrics.var_99 = CalculateValueAtRisk99();
      metrics.expected_shortfall = CalculateExpectedShortfall();
      metrics.leverage_ratio = CalculateLeverageRatio();
      metrics.liquidity_coverage_ratio = CalculateLiquidityCoverageRatio();
      metrics.net_stable_funding_ratio = CalculateNetStableFundingRatio();
      
      // Log das métricas regulatórias
      Log(StringFormat("Métricas Regulatórias: VaR99=%.2f, ES=%.2f, Alavancagem=%.2f, LCR=%.2f, NSFR=%.2f",
          metrics.var_99,
          metrics.expected_shortfall,
          metrics.leverage_ratio,
          metrics.liquidity_coverage_ratio,
          metrics.net_stable_funding_ratio));
      
      return metrics;
   }

   // Método para verificar liquidez antes de uma operação
   bool CheckLiquidityBeforeTrade(string symbol, double volume) {
      LiquidityMetrics metrics = CalculateLiquidityMetrics(symbol);
      
      // Verifica se o volume da operação é menor que 10% do volume médio
      if(volume > metrics.volume_profile * 0.1) {
         Log(StringFormat("Aviso: Volume da operação (%.2f) excede 10%% do volume médio (%.2f)", 
             volume, metrics.volume_profile * 0.1), "WARNING");
         return false;
      }
      
      // Verifica se o spread está dentro de limites aceitáveis
      if(metrics.bid_ask_spread > 0.1) { // 0.1% de spread máximo
         Log(StringFormat("Aviso: Spread muito alto (%.4f%%)", metrics.bid_ask_spread), "WARNING");
         return false;
      }
      
      // Verifica se há profundidade de mercado suficiente
      if(metrics.market_depth < volume * 10) { // Profundidade deve ser 10x o volume da operação
         Log(StringFormat("Aviso: Profundidade de mercado insuficiente (%.2f < %.2f)", 
             metrics.market_depth, volume * 10), "WARNING");
         return false;
      }
      
      return true;
   }

   // Método para gerar relatório de atribuição de risco
   string GenerateRiskAttributionReport() {
      RiskAttribution attribution = CalculateRiskAttribution();
      
      string report = "=== Relatório de Atribuição de Risco ===\n";
      report += StringFormat("Risco de Mercado: %.2f%%\n", attribution.market_risk * 100);
      report += StringFormat("Risco de Crédito: %.2f%%\n", attribution.credit_risk * 100);
      report += StringFormat("Risco de Liquidez: %.2f%%\n", attribution.liquidity_risk * 100);
      report += StringFormat("Risco Operacional: %.2f%%\n", attribution.operational_risk * 100);
      report += StringFormat("Risco de Modelo: %.2f%%\n", attribution.model_risk * 100);
      
      double total_risk = attribution.market_risk + 
                         attribution.credit_risk + 
                         attribution.liquidity_risk + 
                         attribution.operational_risk + 
                         attribution.model_risk;
      
      report += StringFormat("\nRisco Total: %.2f%%\n", total_risk * 100);
      
      return report;
   }

   // Método para gerar relatório de validação
   string GenerateValidationReport() {
      ModelValidation validation = ValidateRiskModels();
      
      string report = "=== Relatório de Validação de Modelos ===\n";
      report += StringFormat("Precisão do Backtest: %.2f%%\n", validation.backtest_accuracy * 100);
      report += StringFormat("Desempenho Fora da Amostra: %.2f%%\n", validation.out_of_sample_performance * 100);
      report += StringFormat("Estabilidade do Modelo: %.2f%%\n", validation.model_stability * 100);
      report += StringFormat("Sensibilidade a Parâmetros: %.2f%%\n", validation.parameter_sensitivity * 100);
      
      // Avaliação geral
      double overall_score = (validation.backtest_accuracy * 0.3 +
                            validation.out_of_sample_performance * 0.3 +
                            validation.model_stability * 0.2 +
                            validation.parameter_sensitivity * 0.2) * 100;
      
      report += StringFormat("\nPontuação Geral: %.2f%%\n", overall_score);
      
      // Recomendações baseadas na pontuação
      if(overall_score >= 80) {
         report += "\nStatus: Modelo Robusto - Aprovado para uso\n";
      } else if(overall_score >= 60) {
         report += "\nStatus: Modelo Aceitável - Monitoramento Recomendado\n";
      } else {
         report += "\nStatus: Modelo Precisa de Revisão - Não Recomendado para Uso\n";
      }
      
      return report;
   }

   // Método para gerar relatório regulatório
   string GenerateRegulatoryReport() {
      RegulatoryMetrics metrics = CalculateRegulatoryMetrics();
      
      string report = "=== Relatório de Métricas Regulatórias ===\n";
      report += StringFormat("Value at Risk (99%%): %.2f\n", metrics.var_99);
      report += StringFormat("Expected Shortfall: %.2f\n", metrics.expected_shortfall);
      report += StringFormat("Razão de Alavancagem: %.2f\n", metrics.leverage_ratio);
      report += StringFormat("Razão de Cobertura de Liquidez (LCR): %.2f\n", metrics.liquidity_coverage_ratio);
      report += StringFormat("Razão de Funding Estável Líquido (NSFR): %.2f\n", metrics.net_stable_funding_ratio);
      
      // Avaliação de conformidade
      report += "\nAvaliação de Conformidade:\n";
      
      // Verifica LCR (mínimo 100%)
      if(metrics.liquidity_coverage_ratio >= 1.0) {
         report += "✓ LCR: Conforme (>= 100%)\n";
      } else {
         report += "✗ LCR: Não Conforme (< 100%)\n";
      }
      
      // Verifica NSFR (mínimo 100%)
      if(metrics.net_stable_funding_ratio >= 1.0) {
         report += "✓ NSFR: Conforme (>= 100%)\n";
      } else {
         report += "✗ NSFR: Não Conforme (< 100%)\n";
      }
      
      // Verifica Alavancagem (máximo 33x)
      if(metrics.leverage_ratio <= 33.0) {
         report += "✓ Alavancagem: Conforme (<= 33x)\n";
      } else {
         report += "✗ Alavancagem: Não Conforme (> 33x)\n";
      }
      
      return report;
   }

   // Método público para Stress Testing
   string RunStressTests() {
      InitializeStressScenarios();
      
      string report = "=== Relatório de Stress Testing ===\n\n";
      double max_impact = 0;
      string worst_scenario = "";
      
      for(int i = 0; i < ArraySize(m_scenarios); i++) {
         double impact = CalculatePortfolioImpact(m_scenarios[i]);
         
         report += StringFormat("Cenário: %s\n", m_scenarios[i].name);
         report += StringFormat("Impacto no Portfólio: %.2f%%\n", impact);
         report += StringFormat("Choque de Mercado: %.1f%%\n", m_scenarios[i].market_shock * 100);
         report += StringFormat("Choque de Volatilidade: %.1f%%\n", m_scenarios[i].volatility_shock * 100);
         report += StringFormat("Choque de Correlação: %.1f%%\n", m_scenarios[i].correlation_shock * 100);
         report += StringFormat("Choque de Liquidez: %.1f%%\n", m_scenarios[i].liquidity_shock * 100);
         report += "----------------------------------------\n";
         
         if(impact < max_impact) {
            max_impact = impact;
            worst_scenario = m_scenarios[i].name;
         }
      }
      
      report += StringFormat("\nPior Cenário: %s (Impacto: %.2f%%)\n", worst_scenario, max_impact);
      
      // Recomendações baseadas no stress testing
      report += "\nRecomendações:\n";
      if(max_impact > -20) {
         report += "✓ Portfólio resiliente a cenários de stress\n";
      } else if(max_impact > -30) {
         report += "⚠ Portfólio moderadamente vulnerável - considere ajustes\n";
      } else {
         report += "✗ Portfólio altamente vulnerável - ações corretivas necessárias\n";
      }
      
      return report;
   }
   
   // Método para verificar limites de stress
   bool CheckStressLimits() {
      InitializeStressScenarios();
      bool within_limits = true;
      
      for(int i = 0; i < ArraySize(m_scenarios); i++) {
         double impact = CalculatePortfolioImpact(m_scenarios[i]);
         
         // Limite de perda máxima de 25% em qualquer cenário
         if(impact < -25) {
            Log(StringFormat("Aviso: Cenário '%s' excede limite de perda (%.2f%%)", 
                m_scenarios[i].name, impact), "WARNING");
            within_limits = false;
         }
      }
      
      return within_limits;
   }

   // Métricas de Risco
   double CalculateSharpeRatio(double risk_free_rate = 0.02) {
      double returns[];
      if(!LoadDailyReturns(returns)) return 0.0;
      
      double mean = ArrayMean(returns);
      double std = ArrayStdDev(returns);
      if(std == 0) return 0.0;
      
      double sharpe = (mean - risk_free_rate / 252) / std * MathSqrt(252);
      
      // Atualiza métricas
      m_metrics.sharpe_ratio = sharpe;
      
      Log(StringFormat("Sharpe Ratio calculado: %.2f", sharpe));
      return sharpe;
   }
   
   double CalculateSortinoRatio(double risk_free_rate = 0.02) {
      double returns[];
      if(!LoadDailyReturns(returns)) return 0.0;
      
      double target_return = risk_free_rate / 252;
      double downside_deviation = 0;
      int count = 0;
      
      for(int i = 0; i < ArraySize(returns); i++) {
         double diff = returns[i] - target_return;
         if(diff < 0) {
            downside_deviation += diff * diff;
            count++;
         }
      }
      
      if(count == 0) return 0.0;
      downside_deviation = MathSqrt(downside_deviation / count);
      
      double excess_return = ArrayMean(returns) - target_return;
      double sortino = excess_return / downside_deviation * MathSqrt(252);
      
      // Atualiza métricas
      m_metrics.sortino_ratio = sortino;
      
      Log(StringFormat("Sortino Ratio calculado: %.2f", sortino));
      return sortino;
   }
   
   double CalculateCalmarRatio() {
      double max_dd = m_metrics.max_drawdown;
      if(max_dd <= 0) return 0.0;
      
      double annual_return = AccountInfoDouble(ACCOUNT_BALANCE) / 
                           AccountInfoDouble(ACCOUNT_EQUITY) - 1;
      annual_return *= 252;
      
      double calmar = annual_return / max_dd;
      
      // Atualiza métricas
      m_metrics.calmar_ratio = calmar;
      
      Log(StringFormat("Calmar Ratio calculado: %.2f", calmar));
      return calmar;
   }

   // Histórico de Trades
   bool SaveTradeHistory(string filename = "trade_history.csv") {
      int handle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_COMMON);
      if(handle == INVALID_HANDLE) {
         Log("Erro ao abrir arquivo para salvar histórico: " + filename, "ERROR");
         return false;
      }

      // Cabeçalho
      FileWrite(handle, "Time,Symbol,Profit,Risk,Reward");

      // Dados
      for(int i = 0; i < ArraySize(m_trades); i++) {
         string line = TimeToString(m_trades[i].time, TIME_DATE|TIME_MINUTES) + "," +
                      m_trades[i].symbol + "," +
                      DoubleToString(m_trades[i].profit, 2) + "," +
                      DoubleToString(m_trades[i].risk, 2) + "," +
                      DoubleToString(m_trades[i].reward, 2);
         FileWrite(handle, line);
      }

      FileClose(handle);
      Log("Histórico de trades salvo com sucesso: " + filename);
      return true;
   }

   bool LoadTradeHistory(string filename = "trade_history.csv") {
      int handle = FileOpen(filename, FILE_READ | FILE_CSV | FILE_COMMON);
      if(handle == INVALID_HANDLE) {
         Log("Arquivo de histórico não encontrado: " + filename, "WARNING");
         return false;
      }

      int count = 0;
      while(!FileIsEnding(handle)) {
         string row = FileReadString(handle);
         if(row == "" || StringFind(row, "Time,Symbol") != -1) continue;

         string values[];
         StringSplit(row, ',', values);

         if(ArraySize(values) >= 5) {
            TradeHistory trade;
            trade.time = StringToTime(values[0]);
            trade.symbol = values[1];
            trade.profit = StringToDouble(values[2]);
            trade.risk = StringToDouble(values[3]);
            trade.reward = StringToDouble(values[4]);

            ArrayResize(m_trades, ArraySize(m_trades) + 1);
            m_trades[ArraySize(m_trades) - 1] = trade;
            count++;
         }
      }

      FileClose(handle);
      Log(StringFormat("Histórico carregado: %d trades", count));
      return count > 0;
   }

   // Stress Testing
   double SimulateStressScenario(double stress_factor = 3.0) {
      double volatility = m_use_ewma ? CalculateEWMAVolatility() : CalculateGARCHVolatility();
      double stressed_volatility = volatility * stress_factor;

      Log(StringFormat("Volatilidade sob estresse (%.1fx): %.4f%%", 
          stress_factor, stressed_volatility * 100));
      return stressed_volatility;
   }

   bool IsPortfolioResilient(double max_allowed_var = 0.05) {
      double stressed_var = CalculateVaRWithVolatility(SimulateStressScenario());
      return stressed_var <= max_allowed_var;
   }

   // Configura grupos de exposição
   void SetupExposureGroups() {
      ExposureGroup forex, commodities, crypto;
      forex.name = "Forex";
      forex.max_risk_percent = 40.0;
      forex.current_exposure = 0.0;

      commodities.name = "Commodities";
      commodities.max_risk_percent = 30.0;
      commodities.current_exposure = 0.0;

      crypto.name = "Crypto";
      crypto.max_risk_percent = 20.0;
      crypto.current_exposure = 0.0;

      ArrayResize(m_groups, 3);
      m_groups[0] = forex;
      m_groups[1] = commodities;
      m_groups[2] = crypto;
      
      Log("Grupos de exposição configurados");
   }

   // Verifica limite de exposição antes de operar
   bool CheckExposureLimit(string symbol, double risk_amount) {
      string group_name = GetSymbolGroup(symbol);
      for(int i = 0; i < ArraySize(m_groups); i++) {
         if(m_groups[i].name == group_name) {
            if(m_groups[i].current_exposure + risk_amount > m_groups[i].max_risk_percent) {
               Log("Limite de exposição excedido para grupo: " + group_name, "WARNING");
               return false;
            }
            m_groups[i].current_exposure += risk_amount;
            return true;
         }
      }
      return false;
   }
}; 