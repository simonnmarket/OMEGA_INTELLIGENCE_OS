//+------------------------------------------------------------------+
//| QuantumMath.mqh - Funções matemáticas quânticas                  |
//+------------------------------------------------------------------+
#ifndef QUANTUM_MATH_MQH
#define QUANTUM_MATH_MQH

class Complex {
public:
   double re;
   double im;
   
   Complex(double r=0, double i=0) : re(r), im(i) {}
   
   Complex operator*(const Complex &other) const {
      return Complex(re*other.re - im*other.im, re*other.im + im*other.re);
   }
   
   double Norm() const { return sqrt(re*re + im*im); }
   double Arg() const { return atan2(im, re); }
};

class QuantumMath {
public:
   static double Entropy(double p) {
      return p > 0 ? -p * log(p) : 0;
   }
   
   static double NormalizedWave(double x, double sigma) {
      return exp(-x*x/(2*sigma*sigma));
   }
};

#endif