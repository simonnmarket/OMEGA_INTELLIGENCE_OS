//+------------------------------------------------------------------+
//|                                                 PhysicsEngine.mqh |
//|                                  Copyright 2024, GALEX Trading System |
//|                                                                     |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property link      "https://www.galex.com"
#property version   "1.00"
#property strict

// Inclusão de bibliotecas necessárias
#include <Arrays\ArrayDouble.mqh>
#include <Math\Stat\Math.mqh>

// Constantes físicas
#define GRAVITY 9.81
#define AIR_DENSITY 1.225
#define PI 3.14159265358979323846

// Classe principal de física
class CPhysicsEngine
{
private:
   double m_exhaust_velocity;
   double m_drag_coefficient;
   double m_acceleration;
   double m_potential_energy;
   
public:
   // Construtor
   CPhysicsEngine()
   {
      m_exhaust_velocity = 0.0;
      m_drag_coefficient = 0.0;
      m_acceleration = 0.0;
      m_potential_energy = 0.0;
   }
   
   // Inicialização
   bool Init()
   {
      m_exhaust_velocity = 0.0;
      m_drag_coefficient = 0.0;
      m_acceleration = 0.0;
      m_potential_energy = 0.0;
      
      return true;
   }
   
   // Calcular velocidade de exaustão
   double CalculateExhaustVelocity(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < 2 || ArraySize(volume) < 2) return 0.0;
      
      double price_change = price[0] - price[1];
      double volume_change = volume[0] - volume[1];
      
      m_exhaust_velocity = (volume_change != 0.0) ? price_change / volume_change : 0.0;
      
      return m_exhaust_velocity;
   }
   
   // Calcular arrasto
   double CalculateDrag(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < 2 || ArraySize(volume) < 2) return 0.0;
      
      double avg_price = 0.0;
      double avg_volume = 0.0;
      
      for(int i = 0; i < period && i < ArraySize(price) && i < ArraySize(volume); i++)
      {
         avg_price += price[i];
         avg_volume += volume[i];
      }
      
      avg_price /= period;
      avg_volume /= period;
      
      double price_deviation = MathAbs(price[0] - avg_price);
      double volume_deviation = MathAbs(volume[0] - avg_volume);
      
      m_drag_coefficient = (volume_deviation != 0.0) ? price_deviation / volume_deviation : 0.0;
      
      return m_drag_coefficient;
   }
   
   // Calcular aceleração
   double CalculateAcceleration(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < 3 || ArraySize(volume) < 3) return 0.0;
      
      double price_change1 = price[0] - price[1];
      double price_change2 = price[1] - price[2];
      double volume_change1 = volume[0] - volume[1];
      double volume_change2 = volume[1] - volume[2];
      
      double acceleration_price = price_change1 - price_change2;
      double acceleration_volume = volume_change1 - volume_change2;
      
      m_acceleration = (acceleration_volume != 0.0) ? acceleration_price / acceleration_volume : 0.0;
      
      return m_acceleration;
   }
   
   // Calcular energia potencial
   double GetPotentialEnergy(const double &price[], const double &volume[], int period)
   {
      if(ArraySize(price) < 2 || ArraySize(volume) < 2) return 0.0;
      
      double max_price = price[0];
      double min_price = price[0];
      
      for(int i = 1; i < period && i < ArraySize(price); i++)
      {
         if(price[i] > max_price) max_price = price[i];
         if(price[i] < min_price) min_price = price[i];
      }
      
      double height = max_price - min_price;
      double mass = ArraySum(volume, period);
      
      m_potential_energy = mass * GRAVITY * height;
      
      return m_potential_energy;
   }
   
   // Getters
   double GetExhaustVelocity() const { return m_exhaust_velocity; }
   double GetDragCoefficient() const { return m_drag_coefficient; }
   double GetAcceleration() const { return m_acceleration; }
   double GetPotentialEnergy() const { return m_potential_energy; }
   
private:
   // Função auxiliar para somar array
   double ArraySum(const double &array[], int count)
   {
      double sum = 0.0;
      
      for(int i = 0; i < count && i < ArraySize(array); i++)
      {
         sum += array[i];
      }
      
      return sum;
   }
}; 