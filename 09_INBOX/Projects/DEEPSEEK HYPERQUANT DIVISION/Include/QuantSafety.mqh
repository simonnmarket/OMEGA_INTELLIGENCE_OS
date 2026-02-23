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

  };

#endif // __QUANTSAFETY_MQH__ 