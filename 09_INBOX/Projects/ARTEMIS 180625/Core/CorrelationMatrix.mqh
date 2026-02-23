//+------------------------------------------------------------------+
//| CorrelationMatrix.mqh - Análise de Correlação entre Ativos       |
//| Inspirado em: Markowitz, Sharpe, Lintner                         |
//+------------------------------------------------------------------+
#include <Math\Alglib\alglib.mqh>
#include <Trade\Trade.mqh>
#include "..\Math\Statistics.mqh"

class CorrelationMatrix
{
private:
   double m_correlation_matrix[][];  // Matriz de correlação quântica
   int m_size;                       // Tamanho da matriz
   string m_symbols[];               // Símbolos correlacionados
   
public:
   // Construtor
   CorrelationMatrix()
   {
      m_size = 0;
      ArrayResize(m_symbols, 0);
      ArrayResize(m_correlation_matrix, 0, 0);
   }
   
   // Inicialização da matriz
   bool Initialize(const string &symbols[])
   {
      m_size = ArraySize(symbols);
      if(m_size == 0) return false;
      
      // Redimensionar arrays
      ArrayResize(m_symbols, m_size);
      ArrayResize(m_correlation_matrix, m_size, m_size);
      
      // Copiar símbolos
      ArrayCopy(m_symbols, symbols);
      
      // Inicializar matriz com zeros
      for(int i = 0; i < m_size; i++)
      {
         for(int j = 0; j < m_size; j++)
         {
            m_correlation_matrix[i][j] = 0.0;
         }
      }
      
      return true;
   }
   
   // Atualizar correlação
   bool UpdateCorrelation(const int i, const int j, const double correlation)
   {
      if(i < 0 || i >= m_size || j < 0 || j >= m_size)
         return false;
         
      m_correlation_matrix[i][j] = correlation;
      m_correlation_matrix[j][i] = correlation;  // Matriz simétrica
      
      return true;
   }
   
   // Obter correlação
   double GetCorrelation(const int i, const int j) const
   {
      if(i < 0 || i >= m_size || j < 0 || j >= m_size)
         return 0.0;
         
      return m_correlation_matrix[i][j];
   }
   
   // Obter símbolo
   string GetSymbol(const int index) const
   {
      if(index < 0 || index >= m_size)
         return "";
         
      return m_symbols[index];
   }
   
   // Obter tamanho
   int GetSize() const
   {
      return m_size;
   }
   
   // Validar matriz
   bool ValidateMatrix() const
   {
      if(m_size == 0) return false;
      
      // Verificar simetria
      for(int i = 0; i < m_size; i++)
      {
         for(int j = 0; j < m_size; j++)
         {
            if(MathAbs(m_correlation_matrix[i][j] - m_correlation_matrix[j][i]) > 0.0001)
               return false;
         }
      }
      
      return true;
   }
}; 