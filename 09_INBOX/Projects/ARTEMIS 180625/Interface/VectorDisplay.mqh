//+------------------------------------------------------------------+
//| VectorDisplay.mqh - Quantum State Visualization                  |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "TextObject.mqh"

class VectorDisplay
{
private:
   long m_chart_id;
   TextObject* m_vector;
   TextObject* m_magnitude;
   bool m_is_created;
   
public:
   VectorDisplay(long chart_id)
   {
      m_chart_id = chart_id;
      m_vector = NULL;
      m_magnitude = NULL;
      m_is_created = false;
   }
   
   ~VectorDisplay()
   {
      Delete();
   }
   
   bool Create(string vector_text, string magnitude_text, int x, int y)
   {
      if(m_is_created)
      {
         Print("Vector Display já existe");
         return false;
      }
      
      // Criar vetor
      m_vector = new TextObject(m_chart_id, "Vector_Text");
      if(!m_vector.Create(m_chart_id, x, y, vector_text))
      {
         Print("Erro ao criar texto do vetor");
         delete m_vector;
         m_vector = NULL;
         return false;
      }
      
      // Configurar vetor
      if(!m_vector.Color(clrWhite))
      {
         Print("Erro ao configurar cor do vetor");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         return false;
      }
      
      if(!m_vector.FontSize(12))
      {
         Print("Erro ao configurar tamanho da fonte do vetor");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         return false;
      }
      
      if(!m_vector.Align(TEXT_ALIGN_LEFT))
      {
         Print("Erro ao configurar alinhamento do vetor");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         return false;
      }
      
      // Criar magnitude
      m_magnitude = new TextObject(m_chart_id, "Vector_Magnitude");
      if(!m_magnitude.Create(m_chart_id, x, y + 20, magnitude_text))
      {
         Print("Erro ao criar texto da magnitude");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         delete m_magnitude;
         m_magnitude = NULL;
         return false;
      }
      
      // Configurar magnitude
      if(!m_magnitude.Color(clrYellow))
      {
         Print("Erro ao configurar cor da magnitude");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         m_magnitude.Delete();
         delete m_magnitude;
         m_magnitude = NULL;
         return false;
      }
      
      if(!m_magnitude.FontSize(10))
      {
         Print("Erro ao configurar tamanho da fonte da magnitude");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         m_magnitude.Delete();
         delete m_magnitude;
         m_magnitude = NULL;
         return false;
      }
      
      if(!m_magnitude.Align(TEXT_ALIGN_LEFT))
      {
         Print("Erro ao configurar alinhamento da magnitude");
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
         m_magnitude.Delete();
         delete m_magnitude;
         m_magnitude = NULL;
         return false;
      }
      
      m_is_created = true;
      return true;
   }
   
   bool Delete()
   {
      if(!m_is_created) return false;
      
      if(m_vector != NULL)
      {
         m_vector.Delete();
         delete m_vector;
         m_vector = NULL;
      }
      
      if(m_magnitude != NULL)
      {
         m_magnitude.Delete();
         delete m_magnitude;
         m_magnitude = NULL;
      }
      
      m_is_created = false;
      return true;
   }
   
   bool UpdateVector(string vector_text)
   {
      if(!m_is_created || m_vector == NULL) return false;
      return m_vector.Text(vector_text);
   }
   
   bool UpdateMagnitude(string magnitude_text)
   {
      if(!m_is_created || m_magnitude == NULL) return false;
      return m_magnitude.Text(magnitude_text);
   }
   
   bool UpdatePosition(int x, int y)
   {
      if(!m_is_created) return false;
      
      if(m_vector != NULL)
      {
         if(!m_vector.Move(x, y)) return false;
      }
      
      if(m_magnitude != NULL)
      {
         if(!m_magnitude.Move(x, y + 20)) return false;
      }
      
      return true;
   }
   
   bool IsCreated() const
   {
      return m_is_created;
   }
}; 