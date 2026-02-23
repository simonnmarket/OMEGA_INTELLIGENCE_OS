//+------------------------------------------------------------------+
//|                                           TrajectoryAnalyzer.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include "..\Core\Interfaces\IModule.mqh"

// Constantes de análise de trajetória
#define MIN_TRAJECTORY_POINTS 10
#define MAX_TRAJECTORY_DEVIATION 0.002
#define MIN_TRAJECTORY_MOMENTUM 0.001

// Classe principal de análise de trajetória
class CTrajectoryAnalyzer : public IDataAnalyzer
{
private:
   double m_trajectory_angle;
   double m_trajectory_momentum;
   double m_trajectory_deviation;
   double m_trajectory_curvature;
   string m_version;
   string m_status;
   bool m_is_initialized;
   
public:
   // Construtor
   CTrajectoryAnalyzer()
   {
      m_trajectory_angle = 0.0;
      m_trajectory_momentum = 0.0;
      m_trajectory_deviation = 0.0;
      m_trajectory_curvature = 0.0;
      m_version = "1.0.0";
      m_status = "Not Initialized";
      m_is_initialized = false;
   }
   
   // Implementação de IModule
   bool Init() override
   {
      m_trajectory_angle = 0.0;
      m_trajectory_momentum = 0.0;
      m_trajectory_deviation = 0.0;
      m_trajectory_curvature = 0.0;
      m_status = "Initialized";
      m_is_initialized = true;
      
      return true;
   }
   
   void Update() override
   {
      if(!m_is_initialized) return;
      m_status = "Updated";
   }
   
   bool Validate() override
   {
      if(!m_is_initialized) return false;
      return m_trajectory_deviation >= 0.0 && m_trajectory_momentum >= 0.0;
   }
   
   void Cleanup() override
   {
      m_trajectory_angle = 0.0;
      m_trajectory_momentum = 0.0;
      m_trajectory_deviation = 0.0;
      m_trajectory_curvature = 0.0;
      m_status = "Cleaned";
      m_is_initialized = false;
   }
   
   string GetStatus() const override { return m_status; }
   string GetVersion() const override { return m_version; }
   string GetName() const override { return "TrajectoryAnalyzer"; }
   
   // Implementação de IDataAnalyzer
   bool AnalyzeData(const MqlRates &rates[], const double &volume[]) override
   {
      if(!m_is_initialized || ArraySize(rates) < MIN_TRAJECTORY_POINTS || ArraySize(volume) < MIN_TRAJECTORY_POINTS) return false;
      
      // Analisar ângulo da trajetória
      AnalyzeTrajectoryAngle(rates);
      
      // Analisar momento da trajetória
      AnalyzeTrajectoryMomentum(rates);
      
      // Analisar desvio da trajetória
      AnalyzeTrajectoryDeviation(rates);
      
      // Analisar curvatura da trajetória
      AnalyzeTrajectoryCurvature(rates);
      
      return true;
   }
   
   bool GetAnalysisResults(double &trajectory_angle, double &trajectory_momentum, double &trajectory_deviation, double &trajectory_curvature) override
   {
      if(!m_is_initialized) return false;
      
      trajectory_angle = m_trajectory_angle;
      trajectory_momentum = m_trajectory_momentum;
      trajectory_deviation = m_trajectory_deviation;
      trajectory_curvature = m_trajectory_curvature;
      
      return true;
   }
   
   // Métodos específicos do TrajectoryAnalyzer
   bool IsValidTrajectory(const MqlRates &rates[])
   {
      if(!m_is_initialized || ArraySize(rates) < MIN_TRAJECTORY_POINTS) return false;
      
      // Verificar desvio
      if(m_trajectory_deviation > MAX_TRAJECTORY_DEVIATION)
         return false;
      
      // Verificar momento
      if(m_trajectory_momentum < MIN_TRAJECTORY_MOMENTUM)
         return false;
      
      return true;
   }
   
   // Getters
   double GetTrajectoryAngle() const { return m_trajectory_angle; }
   double GetTrajectoryMomentum() const { return m_trajectory_momentum; }
   double GetTrajectoryDeviation() const { return m_trajectory_deviation; }
   double GetTrajectoryCurvature() const { return m_trajectory_curvature; }
   
private:
   void AnalyzeTrajectoryAngle(const MqlRates &rates[])
   {
      double start_price = rates[ArraySize(rates)-1].close;
      double end_price = rates[0].close;
      double time_span = rates[0].time - rates[ArraySize(rates)-1].time;
      
      if(time_span > 0.0)
         m_trajectory_angle = MathArctan((end_price - start_price) / time_span);
      else
         m_trajectory_angle = 0.0;
   }
   
   void AnalyzeTrajectoryMomentum(const MqlRates &rates[])
   {
      double total_momentum = 0.0;
      
      for(int i = 1; i < ArraySize(rates); i++)
      {
         double price_change = rates[i].close - rates[i-1].close;
         double time_change = rates[i].time - rates[i-1].time;
         
         if(time_change > 0.0)
            total_momentum += price_change / time_change;
      }
      
      m_trajectory_momentum = total_momentum / (ArraySize(rates) - 1);
   }
   
   void AnalyzeTrajectoryDeviation(const MqlRates &rates[])
   {
      double sum_squared_diff = 0.0;
      double start_price = rates[ArraySize(rates)-1].close;
      double end_price = rates[0].close;
      double time_span = rates[0].time - rates[ArraySize(rates)-1].time;
      
      if(time_span > 0.0)
      {
         double expected_price;
         
         for(int i = 0; i < ArraySize(rates); i++)
         {
            double time_ratio = (rates[i].time - rates[ArraySize(rates)-1].time) / time_span;
            expected_price = start_price + (end_price - start_price) * time_ratio;
            
            sum_squared_diff += MathPow(rates[i].close - expected_price, 2);
         }
         
         m_trajectory_deviation = MathSqrt(sum_squared_diff / ArraySize(rates));
      }
      else
         m_trajectory_deviation = 0.0;
   }
   
   void AnalyzeTrajectoryCurvature(const MqlRates &rates[])
   {
      if(ArraySize(rates) < 3) return;
      
      double total_curvature = 0.0;
      
      for(int i = 1; i < ArraySize(rates)-1; i++)
      {
         double prev_price = rates[i-1].close;
         double curr_price = rates[i].close;
         double next_price = rates[i+1].close;
         
         double prev_time = rates[i-1].time;
         double curr_time = rates[i].time;
         double next_time = rates[i+1].time;
         
         double time_diff1 = curr_time - prev_time;
         double time_diff2 = next_time - curr_time;
         
         if(time_diff1 > 0.0 && time_diff2 > 0.0)
         {
            double slope1 = (curr_price - prev_price) / time_diff1;
            double slope2 = (next_price - curr_price) / time_diff2;
            
            total_curvature += MathAbs(slope2 - slope1);
         }
      }
      
      m_trajectory_curvature = total_curvature / (ArraySize(rates) - 2);
   }
}; 