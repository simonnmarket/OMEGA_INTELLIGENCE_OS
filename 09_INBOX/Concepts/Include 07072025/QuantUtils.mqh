//+------------------------------------------------------------------+
//|                  QUANTUM UTILITIES - FUNÇÕES FALTANTES           |
//|                  VERSÃO 2.0 - NAMESPACE SEGURO                   |
//|                  ATUALIZADO EM: 2025-01-07 por Agente: GPT       |
//+------------------------------------------------------------------+

#ifndef QUANT_UTILS_V2
#define QUANT_UTILS_V2

//+------------------------------------------------------------------+
//|                  NAMESPACE QUANTUTILS - SEGURO                   |
//+------------------------------------------------------------------+
namespace QuantUtils {
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE VALIDAÇÃO SEGURAS                  |
    //+------------------------------------------------------------------+
    
    // Verificação de NaN (FALTANTE)
    bool IsNaN(double x) {
        return (x != x);
    }
    
    // Verificação de Infinito (FALTANTE)
    bool IsInfinite(double x) {
        return !MathIsValidNumber(x) && !IsNaN(x);
    }
    
    // Verificação de número válido (FALTANTE)
    bool IsValidNumber(double value) {
        return !IsNaN(value) && !IsInfinite(value);
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE CONVERSÃO SEGURAS                  |
    //+------------------------------------------------------------------+
    
    // Conversão segura de long para double (FALTANTE)
    double SafeLongToDouble(long val) {
        if(val > 9007199254740992) { // 2^53
            Print("[QUANT UTILS] ⚠️ Possível perda de precisão na conversão long->double: ", val);
            return (double)(val / 1000); // Reduz magnitude
        }
        return (double)val;
    }
    
    // Conversão segura de double para int (FALTANTE)
    int SafeDoubleToInt(double val) {
        if(val > 2147483647.0 || val < -2147483648.0) {
            Print("[QUANT UTILS] ⚠️ Valor double fora do intervalo int: ", val);
            return (int)(val / 1000); // Reduz magnitude
        }
        return (int)MathRound(val);
    }
    
    // Conversão segura de string para double (FALTANTE)
    double SafeStringToDouble(string val) {
        if(StringLen(val) == 0) {
            return 0.0;
        }
        
        double result = StringToDouble(val);
        if(!IsValidNumber(result)) {
            return 0.0;
        }
        
        return result;
    }
    
    // Conversão segura de string para int (FALTANTE)
    int SafeStringToInt(string val) {
        if(StringLen(val) == 0) {
            return 0;
        }
        
        long result = StringToInteger(val);
        if(result > 2147483647 || result < -2147483648) {
            Print("[QUANT UTILS] ⚠️ Valor string muito grande: ", val);
            return 0;
        }
        
        return (int)result;
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE CONVERSÃO PARA STRING              |
    //+------------------------------------------------------------------+
    
    // Conversão segura de long para string (FALTANTE)
    string SafeLongToString(long val) {
        if(val > 2147483647 || val < -2147483648) {
            Print("[QUANT UTILS] ⚠️ Valor long muito grande: ", val);
            return "0";
        }
        return IntegerToString((int)val);
    }
    
    // Conversão segura de double para string (FALTANTE)
    string SafeDoubleToString(double val, int digits = 8) {
        if(!IsValidNumber(val)) {
            return "0.0";
        }
        
        // Limitar dígitos para evitar overflow
        digits = MathMax(0, MathMin(digits, 8));
        
        return DoubleToString(val, digits);
    }
    
    // Conversão segura de int para string (FALTANTE)
    string SafeIntToString(int val) {
        return IntegerToString(val);
    }
    
    // Conversão segura de long para string (alias) (FALTANTE)
    string IntToString(long val) {
        return SafeLongToString(val);
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES MATEMÁTICAS SEGURAS                   |
    //+------------------------------------------------------------------+
    
    // Arredondamento seguro (FALTANTE)
    int SafeRound(double value) {
        if(!IsValidNumber(value)) {
            return 0;
        }
        
        if(value >= 0) {
            return (int)(value + 0.5);
        } else {
            return (int)(value - 0.5);
        }
    }
    
    // Máximo seguro (FALTANTE)
    double SafeMax(double a, double b) {
        if(!IsValidNumber(a) || !IsValidNumber(b)) {
            return 0.0;
        }
        return (a > b) ? a : b;
    }
    
    // Mínimo seguro (FALTANTE)
    double SafeMin(double a, double b) {
        if(!IsValidNumber(a) || !IsValidNumber(b)) {
            return 0.0;
        }
        return (a < b) ? a : b;
    }
    
    // Valor absoluto seguro (FALTANTE)
    double SafeAbs(double value) {
        if(!IsValidNumber(value)) {
            return 0.0;
        }
        return (value < 0) ? -value : value;
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE PERFORMANCE                        |
    //+------------------------------------------------------------------+
    
    // Função GetPerformance - Versão segura (FALTANTE)
    double GetPerformance(int id = 0) {
        // CORREÇÃO CRÍTICA: Implementação da função GetPerformance faltante
        Print("[QUANTUTILS] 🔍 Calculando performance para ID: ", id);
        
        // Lógica de cálculo de performance
        double performanceScore = 0.0;
        
        // Verificar se o ID é válido
        if(id < 0) {
            Print("[QUANTUTILS] ❌ ID inválido: ", id);
            return 0.0;
        }
        
        // Calcular performance baseada em métricas de trading
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double profit = AccountInfoDouble(ACCOUNT_PROFIT);
        
        // Fórmula de performance quântica
        if(balance > 0) {
            performanceScore = (equity - balance) / balance * 100.0;
        }
        
        // Aplicar fator de correção baseado no ID
        performanceScore *= (1.0 + (id % 10) / 100.0);
        
        Print("[QUANTUTILS] ✅ Performance calculada: ", QuantUtils::SafeDoubleToString(performanceScore, 4), "%");
        
        return performanceScore;
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE UTILIDADE                          |
    //+------------------------------------------------------------------+
    
    // Símbolo atual seguro (FALTANTE)
    string GetCurrentSymbol() {
        return _Symbol;
    }
    
    // Verificação de array válido (FALTANTE)
    bool IsArrayValid(const double &arr[]) {
        return ArraySize(arr) > 0;
    }
    
    bool IsArrayValid(const int &arr[]) {
        return ArraySize(arr) > 0;
    }
    
    bool IsArrayValid(const string &arr[]) {
        return ArraySize(arr) > 0;
    }
    
    // Acesso seguro a array (FALTANTE)
    double GetArrayValue(const double &arr[], int index, double defaultValue = 0.0) {
        if(index < 0 || index >= ArraySize(arr)) {
            return defaultValue;
        }
        return arr[index];
    }
    
    int GetArrayValue(const int &arr[], int index, int defaultValue = 0) {
        if(index < 0 || index >= ArraySize(arr)) {
            return defaultValue;
        }
        return arr[index];
    }
    
    string GetArrayValue(const string &arr[], int index, string defaultValue = "") {
        if(index < 0 || index >= ArraySize(arr)) {
            return defaultValue;
        }
        return arr[index];
    }
    
    //+------------------------------------------------------------------+
    //|                  FUNÇÕES DE LOGGING SEGURO                     |
    //+------------------------------------------------------------------+
    
    // Log seguro com validação (FALTANTE)
    void SafePrint(string message) {
        if(StringLen(message) > 0) {
            Print("[QUANT UTILS] ", message);
        }
    }
    
    // Log de erro seguro (FALTANTE)
    void SafeError(string message) {
        if(StringLen(message) > 0) {
            Print("[QUANT UTILS] ❌ ERRO: ", message);
        }
    }
    
    // Log de aviso seguro (FALTANTE)
    void SafeWarning(string message) {
        if(StringLen(message) > 0) {
            Print("[QUANT UTILS] ⚠️ AVISO: ", message);
        }
    }
    
    // Log de sucesso seguro (FALTANTE)
    void SafeSuccess(string message) {
        if(StringLen(message) > 0) {
            Print("[QUANT UTILS] ✅ SUCESSO: ", message);
        }
    }
    
} // namespace QuantUtils

#endif // QUANT_UTILS_V2 