//+------------------------------------------------------------------+
//| Math.mqh - Statistical Functions                                  |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

// Forward declarations
class CLogger;
class CStatistics;

// Basic statistical functions
double Mean(const double &data[]) {
   if(ArraySize(data) == 0) return 0.0;
   double sum = 0.0;
   for(int i = 0; i < ArraySize(data); i++) {
      sum += data[i];
   }
   return sum / ArraySize(data);
}

double Variance(const double &data[]) {
   if(ArraySize(data) < 2) return 0.0;
   double mean = Mean(data);
   double sum = 0.0;
   for(int i = 0; i < ArraySize(data); i++) {
      sum += MathPow(data[i] - mean, 2);
   }
   return sum / (ArraySize(data) - 1);
}

double StandardDeviation(const double &data[]) {
   return MathSqrt(Variance(data));
}

double Skewness(const double &data[]) {
   if(ArraySize(data) < 3) return 0.0;
   double mean = Mean(data);
   double std = StandardDeviation(data);
   if(std == 0) return 0.0;
   
   double sum = 0.0;
   for(int i = 0; i < ArraySize(data); i++) {
      sum += MathPow((data[i] - mean) / std, 3);
   }
   return sum / ArraySize(data);
}

double Kurtosis(const double &data[]) {
   if(ArraySize(data) < 4) return 0.0;
   double mean = Mean(data);
   double std = StandardDeviation(data);
   if(std == 0) return 0.0;
   
   double sum = 0.0;
   for(int i = 0; i < ArraySize(data); i++) {
      sum += MathPow((data[i] - mean) / std, 4);
   }
   return sum / ArraySize(data) - 3.0;
}

// Advanced statistical functions
double Covariance(const double &data1[], const double &data2[]) {
   if(ArraySize(data1) != ArraySize(data2) || ArraySize(data1) < 2) return 0.0;
   
   double mean1 = Mean(data1);
   double mean2 = Mean(data2);
   double sum = 0.0;
   
   for(int i = 0; i < ArraySize(data1); i++) {
      sum += (data1[i] - mean1) * (data2[i] - mean2);
   }
   
   return sum / (ArraySize(data1) - 1);
}

double Correlation(const double &data1[], const double &data2[]) {
   double cov = Covariance(data1, data2);
   double std1 = StandardDeviation(data1);
   double std2 = StandardDeviation(data2);
   
   if(std1 == 0 || std2 == 0) return 0.0;
   return cov / (std1 * std2);
}

// Time series analysis
double Autocorrelation(const double &data[], int lag) {
   if(lag >= ArraySize(data) - 1) return 0.0;
   
   double mean = Mean(data);
   double variance = Variance(data);
   if(variance == 0) return 0.0;
   
   double sum = 0.0;
   for(int i = 0; i < ArraySize(data) - lag; i++) {
      sum += (data[i] - mean) * (data[i + lag] - mean);
   }
   
   return sum / ((ArraySize(data) - lag) * variance);
} 