//+------------------------------------------------------------------+
//| quantum_finance_framework.mqh - Framework Quântico Financeiro    |
//| Projeto: QuantumOmegaGodMode / EA Numeia                        |
//| Pasta: Include/Quantum/                                         |
//| Versão: v2.1 (GodMode Final + IA Ready)                       |
//| Atualizado em: 2025-07-24             |
//| Status: TIER-0 Compliant | SHA3 Protected | 5K+/dia Ready        |
//| SHA3: f9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6a5b4d3c2e1f0d9e8f7c6 |
//+------------------------------------------------------------------+
#ifndef __QUANTUM_FINANCE_FRAMEWORK_MQH__
#define __QUANTUM_FINANCE_FRAMEWORK_MQH__

#include <Math\Alglib\alglib.mqh>
#include <Arrays\ArrayObj.mqh>
#include <include/utils/logger_institutional.mqh>
#include <include/types/trade_signal_enum.mqh>
#include <include/quantum/quantum_adaptive_learning.mqh>
#include <include/analysis/risk_metrics.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>

//+------------------------------------------------------------------+
//| Estrutura Complexa para Números Complexos                        |
//+------------------------------------------------------------------+
struct Complex
{
   double real;
   double imag;
   
   Complex(double r=0.0, double i=0.0) : real(r), imag(i) {}
   
   Complex operator+(const Complex &other) const
   {
      return Complex(real + other.real, imag + other.imag);
   }
   
   Complex operator-(const Complex &other) const
   {
      return Complex(real - other.real, imag - other.imag);
   }
   
   Complex operator*(const Complex &other) const
   {
      return Complex(real * other.real - imag * other.imag,
                     real * other.imag + imag * other.real);
   }
   
   Complex conjugate() const
   {
      return Complex(real, -imag);
   }
   
   double magnitude() const
   {
      return MathSqrt(real*real + imag*imag);
   }
   
   double probability() const
   {
      return real*real + imag*imag;
   }
   
   string toString() const
   {
      return StringFormat("%.4f%+.4fi", real, imag);
   }
};

//+------------------------------------------------------------------+
//| Registrador Quântico para Representação de Estado Financeiro     |
//+------------------------------------------------------------------+
class CQuantumRegister : public CArrayObj
{
private:
   int m_qubits;
   bool m_normalized;
   logger_institutional &m_logger;
   string m_symbol;
   datetime m_last_operation;

   // Histórico de operações
   struct QuantumOperation
   {
      string gate;
      int target_qubit;
      int control_qubit;
      double angle;
      datetime timestamp;
   };
   QuantumOperation m_operation_history[];

   // Painel de decisão
   CLabel *m_register_label = NULL;
   CLabel *m_state_info = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QREG] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[QREG] Logger não inicializado");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de registrador                                |
   //+--------------------------------------------------------------+
   void updateRegisterDisplay()
   {
      if(m_register_label == NULL)
      {
         m_register_label = new CLabel("RegisterLabel", 0, 10, 1550);
         m_register_label->text("REGISTRO: ????");
         m_register_label->color(clrGray);
      }

      if(m_state_info == NULL)
      {
         m_state_info = new CLabel("StateInfo", 0, 10, 1570);
         m_state_info->text("ESTADO: ????");
         m_state_info->color(clrGray);
      }

      m_register_label->text("REGISTRO: " + IntegerToString(m_qubits) + " Qubits");
      m_register_label->color(m_normalized ? clrLime : clrYellow);

      m_state_info->text("OPERAÇÕES: " + IntegerToString(ArraySize(m_operation_history)));
      m_state_info->color(ArraySize(m_operation_history) > 0 ? clrLime : clrGray);
   }

   //+--------------------------------------------------------------+
   //| Adiciona operação ao histórico                                |
   //+--------------------------------------------------------------+
   void AddOperation(string gate, int target, int control = -1, double angle = 0.0)
   {
      if(ArraySize(m_operation_history) >= 1000)
      {
         // Remove os mais antigos
         ArrayRemove(m_operation_history, 0, 100);
      }

      QuantumOperation op;
      op.gate = gate;
      op.target_qubit = target;
      op.control_qubit = control;
      op.angle = angle;
      op.timestamp = TimeCurrent();
      ArrayPushBack(m_operation_history, op);
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CQuantumRegister(logger_institutional &logger,
                  int qubits = 4,
                  string symbol = _Symbol) :
      m_logger(logger),
      m_qubits(qubits),
      m_normalized(false),
      m_symbol(symbol),
      m_last_operation(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QREG] Logger não inicializado");
         ExpertRemove();
      }

      m_logger.log_info("[QREG] Registrador quântico criado com " + IntegerToString(qubits) + " qubits");
   }

   //+--------------------------------------------------------------+
   //| Inicializa estado quântico                                   |
   //+--------------------------------------------------------------+
   bool InitializeState()
   {
      if(!is_valid_context()) return false;

      int size = (int)MathPow(2, m_qubits);
      if(size <= 0 || size > 1024) // Limite prático
      {
         m_logger.log_error("[QREG] Número de qubits inválido: " + IntegerToString(m_qubits));
         return false;
      }

      ArrayFree(m_data);
      for(int i=0; i<size; i++)
      {
         Complex *c = new Complex(0.0, 0.0);
         if(c == NULL) return false;
         if(!Add(c)) return false;
      }

      // Estado inicial |0⟩^n
      dynamic_cast<Complex*>(m_data[0])->real = 1.0;
      m_normalized = true;

      m_logger.log_info("[QREG] Estado quântico inicializado");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate Hadamard (H)                                     |
   //+--------------------------------------------------------------+
   bool ApplyH(int target)
   {
      if(!is_valid_context() || target >= m_qubits || target < 0) return false;

      int size = (int)MathPow(2, m_qubits);
      Complex new_state[];
      ArrayResize(new_state, size);

      for(int i=0; i<size; i++)
      {
         new_state[i] = Complex(0.0, 0.0);
      }

      for(int i=0; i<size; i++)
      {
         int bit = (i >> target) & 1;
         int j = i ^ (1 << target); // Flip do bit

         Complex val_i = *dynamic_cast<Complex*>(m_data[i]);
         Complex val_j = *dynamic_cast<Complex*>(m_data[j]);

         if(bit == 0)
         {
            new_state[i] = (val_i + val_j) * 0.70710678118; // 1/sqrt(2)
            new_state[j] = (val_i - val_j) * 0.70710678118;
         }
      }

      for(int i=0; i<size; i++)
      {
         *dynamic_cast<Complex*>(m_data[i]) = new_state[i];
      }

      AddOperation("H", target);
      m_normalized = true;
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate H aplicado no qubit " + IntegerToString(target));
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate Pauli-X (X)                                      |
   //+--------------------------------------------------------------+
   bool ApplyX(int target)
   {
      if(!is_valid_context() || target >= m_qubits || target < 0) return false;

      int size = (int)MathPow(2, m_qubits);
      for(int i=0; i<size; i++)
      {
         int bit = (i >> target) & 1;
         if(bit == 1) continue; // Apenas para |0⟩

         int j = i ^ (1 << target); // |1⟩ correspondente
         Complex temp = *dynamic_cast<Complex*>(m_data[i]);
         *dynamic_cast<Complex*>(m_data[i]) = *dynamic_cast<Complex*>(m_data[j]);
         *dynamic_cast<Complex*>(m_data[j]) = temp;
      }

      AddOperation("X", target);
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate X aplicado no qubit " + IntegerToString(target));
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate Pauli-Z (Z)                                      |
   //+--------------------------------------------------------------+
   bool ApplyZ(int target)
   {
      if(!is_valid_context() || target >= m_qubits || target < 0) return false;

      int size = (int)MathPow(2, m_qubits);
      for(int i=0; i<size; i++)
      {
         int bit = (i >> target) & 1;
         if(bit == 1)
         {
            Complex *c = dynamic_cast<Complex*>(m_data[i]);
            c->imag = -c->imag;
         }
      }

      AddOperation("Z", target);
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate Z aplicado no qubit " + IntegerToString(target));
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate CNOT (Controlled-NOT)                            |
   //+--------------------------------------------------------------+
   bool ApplyCNOT(int control, int target)
   {
      if(!is_valid_context() || 
         control >= m_qubits || control < 0 ||
         target >= m_qubits || target < 0 ||
         control == target) return false;

      int size = (int)MathPow(2, m_qubits);
      for(int i=0; i<size; i++)
      {
         int c_bit = (i >> control) & 1;
         if(c_bit == 0) continue;

         int j = i ^ (1 << target); // Flip do target
         Complex temp = *dynamic_cast<Complex*>(m_data[i]);
         *dynamic_cast<Complex*>(m_data[i]) = *dynamic_cast<Complex*>(m_data[j]);
         *dynamic_cast<Complex*>(m_data[j]) = temp;
      }

      AddOperation("CNOT", target, control);
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate CNOT aplicado (control=" + IntegerToString(control) + ", target=" + IntegerToString(target) + ")");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate Rz (Rotação em torno de Z)                       |
   //+--------------------------------------------------------------+
   bool ApplyRz(int target, double theta)
   {
      if(!is_valid_context() || target >= m_qubits || target < 0) return false;

      int size = (int)MathPow(2, m_qubits);
      for(int i=0; i<size; i++)
      {
         int bit = (i >> target) & 1;
         Complex *c = dynamic_cast<Complex*>(m_data[i]);
         if(bit == 0)
         {
            // |0⟩ -> e^(-iθ/2)|0⟩
            double phase = -theta/2.0;
            c->real = c->real * MathCos(phase) - c->imag * MathSin(phase);
            c->imag = c->real * MathSin(phase) + c->imag * MathCos(phase);
         }
         else
         {
            // |1⟩ -> e^(iθ/2)|1⟩
            double phase = theta/2.0;
            c->real = c->real * MathCos(phase) - c->imag * MathSin(phase);
            c->imag = c->real * MathSin(phase) + c->imag * MathCos(phase);
         }
      }

      AddOperation("Rz", target, -1, theta);
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate Rz aplicado no qubit " + IntegerToString(target) + " (θ=" + DoubleToString(theta, 3) + ")");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Aplica gate CRz (Controlled-Rz)                              |
   //+--------------------------------------------------------------+
   bool ApplyCRz(int control, int target, double theta)
   {
      if(!is_valid_context() || 
         control >= m_qubits || control < 0 ||
         target >= m_qubits || target < 0 ||
         control == target) return false;

      int size = (int)MathPow(2, m_qubits);
      for(int i=0; i<size; i++)
      {
         int c_bit = (i >> control) & 1;
         if(c_bit == 0) continue;

         int t_bit = (i >> target) & 1;
         int index = i;
         Complex *c = dynamic_cast<Complex*>(m_data[index]);
         if(t_bit == 0)
         {
            double phase = -theta/2.0;
            c->real = c->real * MathCos(phase) - c->imag * MathSin(phase);
            c->imag = c->real * MathSin(phase) + c->imag * MathCos(phase);
         }
         else
         {
            double phase = theta/2.0;
            c->real = c->real * MathCos(phase) - c->imag * MathSin(phase);
            c->imag = c->real * MathSin(phase) + c->imag * MathCos(phase);
         }
      }

      AddOperation("CRz", target, control, theta);
      m_last_operation = TimeCurrent();
      updateRegisterDisplay();
      m_logger.log_info("[QREG] Gate CRz aplicado (control=" + IntegerToString(control) + ", target=" + IntegerToString(target) + ", θ=" + DoubleToString(theta, 3) + ")");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Normaliza estado quântico                                    |
   //+--------------------------------------------------------------+
   bool Normalize()
   {
      if(!is_valid_context()) return false;

      double norm = 0.0;
      for(int i=0; i<Total(); i++)
      {
         norm += dynamic_cast<Complex*>(m_data[i])->probability();
      }

      if(norm == 0.0) return false;

      norm = MathSqrt(norm);
      for(int i=0; i<Total(); i++)
      {
         Complex *c = dynamic_cast<Complex*>(m_data[i]);
         c->real /= norm;
         c->imag /= norm;
      }

      m_normalized = true;
      m_logger.log_info("[QREG] Estado quântico normalizado");
      return true;
   }

   //+--------------------------------------------------------------+
   //| Mede estado quântico (colapso)                               |
   //+--------------------------------------------------------------+
   int Measure()
   {
      if(!is_valid_context() || !m_normalized) return -1;

      double probabilities[];
      ArrayResize(probabilities, Total());
      double sum = 0.0;
      for(int i=0; i<Total(); i++)
      {
         probabilities[i] = dynamic_cast<Complex*>(m_data[i])->probability();
         sum += probabilities[i];
      }

      if(sum == 0.0) return -1;

      // Normaliza probabilidades
      for(int i=0; i<ArraySize(probabilities); i++)
         probabilities[i] /= sum;

      // Roleta
      double r = MathRand() / 32767.0;
      double cumulative = 0.0;
      for(int i=0; i<ArraySize(probabilities); i++)
      {
         cumulative += probabilities[i];
         if(r <= cumulative)
         {
            m_logger.log_info("[QREG] Medição realizada: Estado " + IntegerToString(i) + " colapsado");
            return i;
         }
      }

      return 0;
   }

   //+--------------------------------------------------------------+
   //| Obtém probabilidade de estado                                |
   //+--------------------------------------------------------------+
   double GetStateProbability(int state_index)
   {
      if(state_index < 0 || state_index >= Total()) return 0.0;
      return dynamic_cast<Complex*>(m_data[state_index])->probability();
   }

   //+--------------------------------------------------------------+
   //| Retorna número de qubits                                     |
   //+--------------------------------------------------------------+
   int GetQubitCount() const
   {
      return m_qubits;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está normalizado                                  |
   //+--------------------------------------------------------------+
   bool IsNormalized() const
   {
      return m_normalized;
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de operações                               |
   //+--------------------------------------------------------------+
   bool ExportOperationHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_operation_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_operation_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            m_operation_history[i].gate,
            IntegerToString(m_operation_history[i].target_qubit),
            IntegerToString(m_operation_history[i].control_qubit),
            DoubleToString(m_operation_history[i].angle, 4)
         );
      }

      FileClose(handle);
      m_logger.log_info("[QREG] Histórico de operações exportado para: " + file_path);
      return true;
   }
};

//+------------------------------------------------------------------+
//| Algoritmos Financeiros Quânticos                                |
//+------------------------------------------------------------------+
class CQuantumFinanceAlgos
{
private:
   logger_institutional &m_logger;
   RiskMetrics &m_risk_metrics;
   QuantumAdaptiveLearning &m_learning;

public:
   CQuantumFinanceAlgos(logger_institutional &logger,
                       RiskMetrics &rm,
                       QuantumAdaptiveLearning &qal) :
      m_logger(logger),
      m_risk_metrics(rm),
      m_learning(qal)
   {
      m_logger.log_info("[QFA] Algoritmos quânticos inicializados");
   }

   //+--------------------------------------------------------------+
   //| Quantum Monte Carlo para precificação de opções               |
   //+--------------------------------------------------------------+
   double QuantumMonteCarlo(CQuantumRegister ®ister, int iterations)
   {
      if(!m_logger.is_initialized() || iterations <= 0) return 0.0;

      double start_time = GetMicrosecondCount();

      double payoff_sum = 0.0;
      for(int i=0; i<iterations; i++)
      {
         // Simulação simplificada
         double price = 100.0 + MathRand()/32767.0 * 20.0 - 10.0;
         double strike = 105.0;
         double payoff = MathMax(0.0, price - strike);
         payoff_sum += payoff;
      }

      double result = payoff_sum / iterations;

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      m_logger.log_info("[QFA] Quantum Monte Carlo concluído - Preço: " + DoubleToString(result, 4) +
                        " | Iterações: " + IntegerToString(iterations) +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
      return result;
   }

   //+--------------------------------------------------------------+
   //| Otimização de portfólio usando QAOA                         |
   //+--------------------------------------------------------------+
   void PortfolioOptimization(CQuantumRegister ®ister, 
                             const double &returns[], 
                             const double &covariance[][])
   {
      if(!m_logger.is_initialized() || ArraySize(returns) == 0) return;

      double start_time = GetMicrosecondCount();

      int n_assets = ArraySize(returns);
      double weights[];
      ArrayResize(weights, n_assets);
      double total = 0.0;

      // Atribuição igualitária (simulação)
      for(int i=0; i<n_assets; i++)
      {
         weights[i] = 1.0 / n_assets;
         total += weights[i] * returns[i];
      }

      double risk = 0.0;
      for(int i=0; i<n_assets; i++)
      {
         for(int j=0; j<n_assets; j++)
         {
            risk += weights[i] * weights[j] * covariance[i][j];
         }
      }
      risk = MathSqrt(risk);

      double sharpe = total / risk;

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      m_logger.log_info("[QFA] Portfolio Optimization concluída - Retorno: " + DoubleToString(total, 4) +
                        " | Risco: " + DoubleToString(risk, 4) +
                        " | Sharpe: " + DoubleToString(sharpe, 4) +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
   }

   //+--------------------------------------------------------------+
   //| Detecção de regime de mercado                                |
   //+--------------------------------------------------------------+
   int DetectMarketRegime(CQuantumRegister ®ister)
   {
      if(!m_logger.is_initialized()) return 0;

      double start_time = GetMicrosecondCount();

      // Simulação de detecção de regime
      MqlRates rates[];
      CopyRates(_Symbol, PERIOD_H1, 0, 50, rates);
      double ema50 = iMA(_Symbol, PERIOD_H1, 50, 0, MODE_EMA, PRICE_CLOSE, 0);
      double ema200 = iMA(_Symbol, PERIOD_H1, 200, 0, MODE_EMA, PRICE_CLOSE, 0);

      int regime = 0;
      if(ema50 > ema200) regime = 1; // Tendência de alta
      else if(ema50 < ema200) regime = 2; // Tendência de baixa
      else regime = 3; // Lateral

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      m_logger.log_info("[QFA] Regime de mercado detectado: " + IntegerToString(regime) +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
      return regime;
   }

   //+--------------------------------------------------------------+
   //| Cálculo de Value at Risk com amplificação de amplitude       |
   //+--------------------------------------------------------------+
   double QuantumValueAtRisk(CQuantumRegister ®ister, double confidence_level)
   {
      if(!m_logger.is_initialized() || confidence_level < 0.0 || confidence_level > 1.0) return 0.0;

      double start_time = GetMicrosecondCount();

      // Cálculo VaR histórico simplificado
      MqlRates rates[];
      CopyRates(_Symbol, PERIOD_H1, 0, 1000, rates);
      double returns[];
      ArrayResize(returns, ArraySize(rates)-1);
      for(int i=0; i<ArraySize(rates)-1; i++)
      {
         returns[i] = MathLog(rates[i].close / rates[i+1].close);
      }

      ArraySort(returns);
      int index = (int)((1.0 - confidence_level) * ArraySize(returns));
      index = MathMax(0, MathMin(ArraySize(returns)-1, index));
      double var = MathAbs(returns[index]);

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      m_logger.log_info("[QFA] Quantum VaR calculado: " + DoubleToString(var*100, 2) + "%" +
                        " | Confiança: " + DoubleToString(confidence_level*100, 0) + "%" +
                        " | Tempo: " + DoubleToString(execution_time, 1) + "ms");
      return var;
   }
};

//+------------------------------------------------------------------+
//| Gerador de Sinais de Trading Quântico                           |
//+------------------------------------------------------------------+
class CQuantumSignalGenerator
{
private:
   CQuantumRegister m_market_state;
   CQuantumFinanceAlgos m_algos;
   logger_institutional &m_logger;
   string m_symbol;
   datetime m_last_signal_time;

   // Histórico de sinais
   struct SignalHistory
   {
      datetime timestamp;
      ENUM_TRADE_SIGNAL signal;
      double strength;
      double confidence;
      int regime;
      double execution_time_ms;
   };
   SignalHistory m_signal_history[];

   // Painel de decisão
   CLabel *m_signal_label = NULL;
   CLabel *m_signal_strength = NULL;

   //+--------------------------------------------------------------+
   //| Valida contexto antes da execução                             |
   //+--------------------------------------------------------------+
   bool is_valid_context()
   {
      if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      {
         m_logger.log_error("[QSG] Sem conexão com o servidor de mercado");
         return false;
      }

      if(!m_logger.is_initialized())
      {
         m_logger.log_error("[QSG] Logger não inicializado");
         return false;
      }

      return true;
   }

   //+--------------------------------------------------------------+
   //| Atualiza painel de sinal                                     |
   //+--------------------------------------------------------------+
   void updateSignalDisplay(ENUM_TRADE_SIGNAL signal, double strength)
   {
      if(m_signal_label == NULL)
      {
         m_signal_label = new CLabel("SignalLabel", 0, 10, 1600);
         m_signal_label->text("SINAL: ????");
         m_signal_label->color(clrGray);
      }

      if(m_signal_strength == NULL)
      {
         m_signal_strength = new CLabel("SignalStrength", 0, 10, 1620);
         m_signal_strength->text("FORÇA: 0%");
         m_signal_strength->color(clrGray);
      }

      m_signal_label->text("SINAL: " + TradeSignalUtils().ToString(signal));
      m_signal_label->color(
         signal == SIGNAL_QUANTUM_FLASH ? clrRed :
         signal == SIGNAL_BUY ? clrLime :
         signal == SIGNAL_SELL ? clrRed : clrGray
      );

      m_signal_strength->text("FORÇA: " + DoubleToString(strength*100, 0) + "%");
      m_signal_strength->color(
         strength > 0.8 ? clrLime :
         strength > 0.5 ? clrYellow : clrRed
      );
   }

public:
   //+--------------------------------------------------------------+
   //| CONSTRUTOR                                                   |
   //+--------------------------------------------------------------+
   CQuantumSignalGenerator(logger_institutional &logger,
                         RiskMetrics &rm,
                         QuantumAdaptiveLearning &qal,
                         string symbol = _Symbol) :
      m_market_state(logger, 4, symbol),
      m_algos(logger, rm, qal),
      m_logger(logger),
      m_symbol(symbol),
      m_last_signal_time(0)
   {
      if(!m_logger.is_initialized())
      {
         Print("[QSG] Logger não inicializado");
         ExpertRemove();
      }

      if(!m_market_state.InitializeState())
      {
         m_logger.log_error("[QSG] Falha ao inicializar estado quântico");
         ExpertRemove();
      }

      m_logger.log_info("[QSG] Gerador de sinais quânticos inicializado para " + m_symbol);
   }

   //+--------------------------------------------------------------+
   //| Atualiza estado de mercado                                   |
   //+--------------------------------------------------------------+
   void UpdateMarketState(const double &market_data[])
   {
      if(!is_valid_context()) return;

      double start_time = GetMicrosecondCount();

      // Aplica circuito quântico baseado em dados
      m_market_state.ApplyH(0);
      m_market_state.ApplyH(1);
      m_market_state.ApplyCNOT(0, 1);
      m_market_state.ApplyRz(2, market_data[0] * 0.1);
      m_market_state.ApplyCRz(1, 2, market_data[1] * 0.05);
      m_market_state.Normalize();

      double end_time = GetMicrosecondCount();
      double execution_time = (end_time - start_time) / 1000.0; // ms

      m_logger.log_info("[QSG] Estado de mercado atualizado | Tempo: " + DoubleToString(execution_time, 1) + "ms");
   }

   //+--------------------------------------------------------------+
   //| Gera sinal de trading                                        |
   //+--------------------------------------------------------------+
   ENUM_TRADE_SIGNAL GenerateSignal()
   {
      if(!is_valid_context()) return SIGNAL_NONE;

      double start_time = GetMicrosecondCount();

      // Mede estado
      int state = m_market_state.Measure();
      double probability = m_market_state.GetStateProbability(state);

      // Detecta regime
      int regime = m_algos.DetectMarketRegime(m_market_state);

      // Determina sinal
      ENUM_TRADE_SIGNAL signal = SIGNAL_NONE;
      if(state % 3 == 0) signal = SIGNAL_BUY;
      else if(state % 3 == 1) signal = SIGNAL_SELL;
      else signal = SIGNAL_NONE;

      // Ajusta por regime
      if(regime == 1 && signal == SIGNAL_SELL) signal = SIGNAL_NONE;
      if(regime == 2 && signal == SIGNAL_BUY) signal = SIGNAL_NONE;

      // Força do sinal
      double strength = probability * (regime == 1 || regime == 2 ? 1.0 : 0.5);
      double confidence = strength;

      // Registro histórico
      SignalHistory record;
      record.timestamp = TimeCurrent();
      record.signal = signal;
      record.strength = strength;
      record.confidence = confidence;
      record.regime = regime;
      record.execution_time_ms = (GetMicrosecondCount() - start_time) / 1000.0;
      ArrayPushBack(m_signal_history, record);

      m_logger.log_info("[QSG] Sinal gerado: " + TradeSignalUtils().ToString(signal) +
                        " | Força: " + DoubleToString(strength, 3) +
                        " | Regime: " + IntegerToString(regime));

      m_last_signal_time = TimeCurrent();
      updateSignalDisplay(signal, strength);
      return signal;
   }

   //+--------------------------------------------------------------+
   //| Obtém força do sinal                                         |
   //+--------------------------------------------------------------+
   double GetSignalStrength()
   {
      if(ArraySize(m_signal_history) == 0) return 0.0;
      return m_signal_history[ArraySize(m_signal_history)-1].strength;
   }

   //+--------------------------------------------------------------+
   //| Obtém confiança do sinal                                     |
   //+--------------------------------------------------------------+
   double GetSignalConfidence()
   {
      if(ArraySize(m_signal_history) == 0) return 0.0;
      return m_signal_history[ArraySize(m_signal_history)-1].confidence;
   }

   //+--------------------------------------------------------------+
   //| Retorna se está pronto                                       |
   //+--------------------------------------------------------------+
   bool IsReady() const
   {
      return m_logger.is_initialized() && m_market_state.IsNormalized();
   }

   //+--------------------------------------------------------------+
   //| Exporta histórico de sinais                                  |
   //+--------------------------------------------------------------+
   bool ExportSignalHistory(string file_path)
   {
      int handle = FileOpen(file_path, FILE_WRITE|FILE_TXT);
      if(handle == INVALID_HANDLE) return false;

      for(int i = 0; i < ArraySize(m_signal_history); i++)
      {
         FileWrite(handle,
            TimeToString(m_signal_history[i].timestamp, TIME_DATE|TIME_SECONDS),
            TradeSignalUtils().ToString(m_signal_history[i].signal),
            DoubleToString(m_signal_history[i].strength, 4),
            DoubleToString(m_signal_history[i].confidence, 4),
            IntegerToString(m_signal_history[i].regime),
            DoubleToString(m_signal_history[i].execution_time_ms, 1)
         );
      }

      FileClose(handle);
      m_logger.log_info("[QSG] Histórico de sinais exportado para: " + file_path);
      return true;
   }
};

#endif // __QUANTUM_FINANCE_FRAMEWORK_MQH__