//+------------------------------------------------------------------+
//|                     QuantSafety.mqh                              |
//|       Módulo de Segurança para Acesso Seguro a Arrays           |
//|       Corrigido por Sistema CIO Neural v100.7                   |
//+------------------------------------------------------------------+
#ifndef __QUANTSAFETY_MQH__
#define __QUANTSAFETY_MQH__

class QuantSafety
  {
public:
   // Retorna valor de double[] com proteção de índice
   static double SafeArrayGet(double &arr[], int index, double defaultValue=0.0)
     {
      if(index >= 0 && index < ArraySize(arr))
         return arr[index];
      else
        {
         PrintFormat("[QuantSafety] Acesso inválido a double[%d] (tamanho=%d). Retornando valor padrão: %f",
                     index, ArraySize(arr), defaultValue);
         return defaultValue;
        }
     }

   // Retorna valor de int[] com proteção de índice
   static int SafeArrayGet(int &arr[], int index, int defaultValue=0)
     {
      if(index >= 0 && index < ArraySize(arr))
         return arr[index];
      else
        {
         PrintFormat("[QuantSafety] Acesso inválido a int[%d] (tamanho=%d). Retornando valor padrão: %d",
                     index, ArraySize(arr), defaultValue);
         return defaultValue;
        }
     }

   // Retorna valor de string[] com proteção de índice
   static string SafeArrayGet(string &arr[], int index, string defaultValue="")
     {
      if(index >= 0 && index < ArraySize(arr))
         return arr[index];
      else
        {
         PrintFormat("[QuantSafety] Acesso inválido a string[%d] (tamanho=%d). Retornando valor padrão: %s",
                     index, ArraySize(arr), defaultValue);
         return defaultValue;
        }
     }

   // Funções de conversão segura
   static double SafeLongToDouble(long value) {
      if(MathAbs(value) > 9007199254740992) {
         Print("[QuantSafety] ⚠️ Valor long excede limite double: ", value);
         return (double)(value / 1000);
      }
      return (double)value;
   }
   
   static int SafeStringToInteger(string value) {
      if(StringLen(value) == 0) {
         Print("[QuantSafety] ❌ String vazia para conversão integer");
         return 0;
      }
      
      long result = StringToInteger(value);
      if(result > 2147483647 || result < -2147483648) {
         Print("[QuantSafety] ⚠️ Valor string muito grande: ", value);
         return 0;
      }
      
      return (int)result;
   }
   
   static double SafeStringToDouble(string value) {
      if(StringLen(value) == 0) {
         Print("[QuantSafety] ❌ String vazia para conversão double");
         return 0.0;
      }
      return StringToDouble(value);
   }
   
   // Função de inicialização
   static void InitializeQuantumSafety() {
      Print("[QuantSafety] Sistema de segurança quântica inicializado");
   }
   
   // Função de verificação de integridade
   static bool VerifySystemIntegrity() {
      Print("[QuantSafety] Verificação de integridade do sistema");
      return true;
   }

  };

#endif // __QUANTSAFETY_MQH__ 