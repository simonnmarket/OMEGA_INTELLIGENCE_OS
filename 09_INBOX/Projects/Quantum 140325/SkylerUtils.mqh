#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Incluir arquivo de configuração
#include "SkylerConfig.mqh"

// Funções de cálculo de risco
double CalculatePositionSize(const double& accountBalance,
                           const double& riskPercentage,
                           const double& stopLossPips) {
    double riskAmount = accountBalance * riskPercentage;
    double pipValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE) * 10;
    double positionSize = riskAmount / (stopLossPips * pipValue);
    
    // Normalizar tamanho da posição
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    positionSize = MathRound(positionSize / lotStep) * lotStep;
    positionSize = MathMax(minLot, MathMin(maxLot, positionSize));
    
    return positionSize;
}

// Funções de cálculo de indicadores
double CalculateRSI(const double& prices[], const int& period) {
    if(ArraySize(prices) < period + 1) return 0.0;
    
    double gains = 0.0;
    double losses = 0.0;
    
    for(int i = 1; i <= period; i++) {
        double change = prices[i] - prices[i-1];
        if(change > 0) {
            gains += change;
        } else {
            losses -= change;
        }
    }
    
    double avgGain = gains / period;
    double avgLoss = losses / period;
    
    if(avgLoss == 0) return 100.0;
    
    double rs = avgGain / avgLoss;
    return 100.0 - (100.0 / (1.0 + rs));
}

void CalculateMACD(const double& prices[],
                   const int& fastPeriod,
                   const int& slowPeriod,
                   const int& signalPeriod,
                   double& macd[],
                   double& signal[],
                   double& hist[]) {
    if(ArraySize(prices) < slowPeriod + signalPeriod) return;
    
    // Calcular EMAs
    double fastEMA = CalculateEMA(prices, fastPeriod);
    double slowEMA = CalculateEMA(prices, slowPeriod);
    
    // Calcular MACD
    double macdValue = fastEMA - slowEMA;
    
    // Calcular sinal
    double signalValue = CalculateEMA(&macdValue, signalPeriod);
    
    // Calcular histograma
    double histValue = macdValue - signalValue;
    
    // Atualizar arrays
    ArrayResize(macd, 1);
    ArrayResize(signal, 1);
    ArrayResize(hist, 1);
    
    macd[0] = macdValue;
    signal[0] = signalValue;
    hist[0] = histValue;
}

double CalculateEMA(const double& prices[], const int& period) {
    if(ArraySize(prices) < period + 1) return 0.0;
    
    double multiplier = 2.0 / (period + 1);
    double ema = prices[0];
    
    for(int i = 1; i <= period; i++) {
        ema = (prices[i] - ema) * multiplier + ema;
    }
    
    return ema;
}

// Funções de cálculo de Bandas de Bollinger
void CalculateBollingerBands(const double& prices[],
                            const int& period,
                            const double& deviation,
                            double& upper[],
                            double& middle[],
                            double& lower[]) {
    if(ArraySize(prices) < period) return;
    
    // Calcular SMA
    double sma = 0.0;
    for(int i = 0; i < period; i++) {
        sma += prices[i];
    }
    sma /= period;
    
    // Calcular desvio padrão
    double sumSquaredDiff = 0.0;
    for(int i = 0; i < period; i++) {
        double diff = prices[i] - sma;
        sumSquaredDiff += diff * diff;
    }
    double stdDev = MathSqrt(sumSquaredDiff / period);
    
    // Calcular bandas
    double upperBand = sma + (deviation * stdDev);
    double lowerBand = sma - (deviation * stdDev);
    
    // Atualizar arrays
    ArrayResize(upper, 1);
    ArrayResize(middle, 1);
    ArrayResize(lower, 1);
    
    upper[0] = upperBand;
    middle[0] = sma;
    lower[0] = lowerBand;
}

// Funções de cálculo de métricas de desempenho
double CalculateSharpeRatio(const double& returns[],
                           const double& riskFreeRate) {
    if(ArraySize(returns) < 2) return 0.0;
    
    // Calcular retorno médio
    double avgReturn = 0.0;
    for(int i = 0; i < ArraySize(returns); i++) {
        avgReturn += returns[i];
    }
    avgReturn /= ArraySize(returns);
    
    // Calcular desvio padrão
    double sumSquaredDiff = 0.0;
    for(int i = 0; i < ArraySize(returns); i++) {
        double diff = returns[i] - avgReturn;
        sumSquaredDiff += diff * diff;
    }
    double stdDev = MathSqrt(sumSquaredDiff / ArraySize(returns));
    
    if(stdDev == 0) return 0.0;
    
    return (avgReturn - riskFreeRate) / stdDev;
}

double CalculateSortinoRatio(const double& returns[],
                            const double& riskFreeRate) {
    if(ArraySize(returns) < 2) return 0.0;
    
    // Calcular retorno médio
    double avgReturn = 0.0;
    for(int i = 0; i < ArraySize(returns); i++) {
        avgReturn += returns[i];
    }
    avgReturn /= ArraySize(returns);
    
    // Calcular desvio padrão negativo
    double sumSquaredNegativeDiff = 0.0;
    int negativeCount = 0;
    
    for(int i = 0; i < ArraySize(returns); i++) {
        if(returns[i] < 0) {
            double diff = returns[i] - avgReturn;
            sumSquaredNegativeDiff += diff * diff;
            negativeCount++;
        }
    }
    
    if(negativeCount == 0) return 0.0;
    
    double negativeStdDev = MathSqrt(sumSquaredNegativeDiff / negativeCount);
    
    if(negativeStdDev == 0) return 0.0;
    
    return (avgReturn - riskFreeRate) / negativeStdDev;
}

double CalculateCalmarRatio(const double& returns[],
                           const double& maxDrawdown) {
    if(ArraySize(returns) < 2 || maxDrawdown == 0) return 0.0;
    
    // Calcular retorno anualizado
    double totalReturn = 1.0;
    for(int i = 0; i < ArraySize(returns); i++) {
        totalReturn *= (1.0 + returns[i]);
    }
    totalReturn -= 1.0;
    
    // Calcular retorno anualizado
    double annualizedReturn = MathPow(1.0 + totalReturn, 252.0 / ArraySize(returns)) - 1.0;
    
    return annualizedReturn / maxDrawdown;
}

// Funções de manipulação de datas
datetime AddMinutes(const datetime& time, const int& minutes) {
    return time + (minutes * 60);
}

datetime AddHours(const datetime& time, const int& hours) {
    return time + (hours * 3600);
}

datetime AddDays(const datetime& time, const int& days) {
    return time + (days * 86400);
}

// Funções de formatação
string FormatPrice(const double& price) {
    return DoubleToString(price, _Digits);
}

string FormatVolume(const double& volume) {
    return DoubleToString(volume, 2);
}

string FormatPercentage(const double& percentage) {
    return DoubleToString(percentage * 100.0, 2) + "%";
}

// Funções de validação
bool IsValidPrice(const double& price) {
    return price > 0 && price < 1000000;
}

bool IsValidVolume(const double& volume) {
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    return volume >= minLot && 
           volume <= maxLot && 
           MathMod(volume, lotStep) == 0;
}

bool IsValidTimeframe(const int& timeframe) {
    int validTimeframes[] = {
        SKYLER_TIMEFRAME_M1,
        SKYLER_TIMEFRAME_M5,
        SKYLER_TIMEFRAME_M15,
        SKYLER_TIMEFRAME_H1,
        SKYLER_TIMEFRAME_H4,
        SKYLER_TIMEFRAME_D1,
        SKYLER_TIMEFRAME_W1,
        SKYLER_TIMEFRAME_MN
    };
    
    for(int i = 0; i < ArraySize(validTimeframes); i++) {
        if(timeframe == validTimeframes[i]) {
            return true;
        }
    }
    
    return false;
} 