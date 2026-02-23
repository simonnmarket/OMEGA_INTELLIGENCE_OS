//+------------------------------------------------------------------+
//|                                                RiskManager.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Constantes de risco
#define MAX_RISK_PERCENT 2.0
#define MAX_DRAWDOWN_PERCENT 10.0
#define MIN_RISK_REWARD_RATIO 2.0

// Classe principal de gerenciamento de risco
class CRiskManager : public IRiskManager
{
private:
   double m_account_balance;
   double m_max_risk_percent;
   double m_max_drawdown_percent;
   double m_min_risk_reward_ratio;
   double m_current_drawdown;
   double m_total_profit;
   double m_total_loss;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CRiskManager()
   {
      m_account_balance = 0.0;
      m_max_risk_percent = MAX_RISK_PERCENT;
      m_max_drawdown_percent = MAX_DRAWDOWN_PERCENT;
      m_min_risk_reward_ratio = MIN_RISK_REWARD_RATIO;
      m_current_drawdown = 0.0;
      m_total_profit = 0.0;
      m_total_loss = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      m_max_risk_percent = MAX_RISK_PERCENT;
      m_max_drawdown_percent = MAX_DRAWDOWN_PERCENT;
      m_min_risk_reward_ratio = MIN_RISK_REWARD_RATIO;
      m_current_drawdown = 0.0;
      m_total_profit = 0.0;
      m_total_loss = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      
      // Atualizar saldo da conta
      m_account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
      
      // Atualizar drawdown atual
      UpdateDrawdown();
      
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_account_balance > 0.0 && m_max_risk_percent > 0.0 && m_max_drawdown_percent > 0.0 && m_min_risk_reward_ratio > 0.0;
   }
   
   void Cleanup() override
   {
      m_account_balance = 0.0;
      m_max_risk_percent = MAX_RISK_PERCENT;
      m_max_drawdown_percent = MAX_DRAWDOWN_PERCENT;
      m_min_risk_reward_ratio = MIN_RISK_REWARD_RATIO;
      m_current_drawdown = 0.0;
      m_total_profit = 0.0;
      m_total_loss = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "RiskManager"; }
   
   // Implementação de IRiskManager
   bool CheckRisk(const double lot_size, const double stop_loss, const double take_profit) override
   {
      if(!m_is_initialized) return false;
      
      // Verificar se o tamanho do lote está dentro do limite de risco
      double risk_amount = lot_size * stop_loss * _Point;
      double risk_percent = (risk_amount / m_account_balance) * 100.0;
      
      if(risk_percent > m_max_risk_percent)
         return false;
      
      // Verificar se o drawdown atual está dentro do limite
      if(m_current_drawdown > m_max_drawdown_percent)
         return false;
      
      // Verificar se a relação risco/recompensa está dentro do limite
      double reward_amount = lot_size * take_profit * _Point;
      double risk_reward_ratio = reward_amount / risk_amount;
      
      if(risk_reward_ratio < m_min_risk_reward_ratio)
         return false;
      
      return true;
   }
   
   bool UpdateRiskMetrics(const double profit_loss) override
   {
      if(!m_is_initialized) return false;
      
      if(profit_loss > 0.0)
         m_total_profit += profit_loss;
      else
         m_total_loss += MathAbs(profit_loss);
      
      UpdateDrawdown();
      
      return true;
   }
   
   // Métodos específicos do RiskManager
   bool Init(double max_risk_percent, double max_drawdown_percent, double min_risk_reward_ratio)
   {
      m_max_risk_percent = max_risk_percent;
      m_max_drawdown_percent = max_drawdown_percent;
      m_min_risk_reward_ratio = min_risk_reward_ratio;
      
      return true;
   }
   
   // Getters
   double GetAccountBalance() const { return m_account_balance; }
   double GetMaxRiskPercent() const { return m_max_risk_percent; }
   double GetMaxDrawdownPercent() const { return m_max_drawdown_percent; }
   double GetMinRiskRewardRatio() const { return m_min_risk_reward_ratio; }
   double GetCurrentDrawdown() const { return m_current_drawdown; }
   double GetTotalProfit() const { return m_total_profit; }
   double GetTotalLoss() const { return m_total_loss; }
   
private:
   void UpdateDrawdown()
   {
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      
      if(balance > 0.0)
         m_current_drawdown = ((balance - equity) / balance) * 100.0;
      else
         m_current_drawdown = 0.0;
   }
}; 