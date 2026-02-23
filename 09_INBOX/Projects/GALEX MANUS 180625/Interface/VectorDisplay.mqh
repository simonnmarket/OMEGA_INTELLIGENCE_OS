//+------------------------------------------------------------------+
//| VectorDisplay.mqh - Sistema de Visualização Vetorial Avançado    |
//| v16.0 - Visualização Holográfica de Campo Financeiro             |
//+------------------------------------------------------------------+

#include <Canvas\Canvas.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>

class VectorDisplay {
private:
   string            m_name;
   int               m_x;
   int               m_y;
   int               m_width;
   int               m_height;
   color             m_base_color;
   CCanvas           m_canvas;
   CChartObjectLabel m_label;
   CChartObjectRect  m_background;
   bool              m_3d_enabled;
   double            m_quantum_scale;

   // Estrutura para vetores financeiros
   struct FinancialVector {
      double magnitude;
      double direction;
      color  vector_color;
      string description;
   } m_vectors[5]; // Suporte para 5 vetores simultâneos

   // Renderiza vetor no canvas
   void RenderVector(int index) {
      if(index < 0 || index >= 5) return;
      
      double angle = m_vectors[index].direction * M_PI / 180.0;
      int end_x = (int)(m_width/2 + m_vectors[index].magnitude * MathCos(angle) * m_quantum_scale);
      int end_y = (int)(m_height/2 - m_vectors[index].magnitude * MathSin(angle) * m_quantum_scale);
      
      // Desenha linha do vetor
      m_canvas.Line(m_width/2, m_height/2, end_x, end_y, m_vectors[index].vector_color);
      
      // Desenha cabeça da seta
      DrawArrowHead(end_x, end_y, angle, m_vectors[index].vector_color);
   }

   // Desenha ponta de seta
   void DrawArrowHead(int x, int y, double angle, color clr) {
      double arrow_size = 10.0 * m_quantum_scale;
      double angle1 = angle + M_PI * 0.8;
      double angle2 = angle - M_PI * 0.8;
      
      int x1 = (int)(x + arrow_size * MathCos(angle1));
      int y1 = (int)(y - arrow_size * MathSin(angle1));
      int x2 = (int)(x + arrow_size * MathCos(angle2));
      int y2 = (int)(y - arrow_size * MathSin(angle2));
      
      m_canvas.Line(x, y, x1, y1, clr);
      m_canvas.Line(x, y, x2, y2, clr);
   }

public:
   VectorDisplay(string name = "vector", int x = 0, int y = 0, int width = 200, int height = 200) : 
      m_name(name), m_x(x), m_y(y), m_width(width), m_height(height) {
      m_base_color = clrDodgerBlue;
      m_3d_enabled = false;
      m_quantum_scale = 1.0;
      ArrayInitialize(m_vectors, 0);
   }

   ~VectorDisplay() {
      m_canvas.Destroy();
      m_label.Delete();
      m_background.Delete();
   }

   // Criação do display com múltiplos elementos
   bool Create(long chart_id = 0, int sub_window = 0, int x = 0, int y = 0) {
      // Configura posição
      m_x = x;
      m_y = y;
      
      // Cria background
      if(!m_background.Create(chart_id, m_name+"_BG", sub_window, m_x, m_y, m_x+m_width, m_y+m_height)) {
         Print("Falha ao criar background");
         return false;
      }
      m_background.ColorBackground(clrBlack);
      m_background.ColorBorder(clrGray);
      m_background.BorderType(BORDER_FLAT);
      
      // Cria label de título
      if(!m_label.Create(chart_id, m_name+"_Label", sub_window, m_x+10, m_y+10)) {
         Print("Falha ao criar label");
         return false;
      }
      m_label.Description(m_name);
      m_label.Font("Arial");
      m_label.FontSize(10);
      m_label.Color(clrWhite);
      
      // Cria canvas para renderização vetorial
      if(!m_canvas.CreateBitmapLabel(m_name+"_Canvas", m_x+5, m_y+30, m_width-10, m_height-35, COLOR_FORMAT_ARGB_NORMALIZE)) {
         Print("Falha ao criar canvas");
         return false;
      }
      
      return true;
   }

   // Atualização completa do display
   void Update(const string text, const FinancialVector &vectors[], int vector_count) {
      // Atualiza texto
      m_label.Description(text);
      
      // Limpa canvas
      m_canvas.Erase(ColorToARGB(clrBlack, 0));
      
      // Atualiza e renderiza vetores
      int count = MathMin(vector_count, 5);
      for(int i=0; i<count; i++) {
         m_vectors[i] = vectors[i];
         RenderVector(i);
      }
      
      // Adiciona grade de referência
      DrawReferenceGrid();
      
      // Atualiza canvas
      m_canvas.Update();
   }

   // Desenha grade de referência
   void DrawReferenceGrid() {
      // Eixos centrais
      m_canvas.Line(m_width/2, 0, m_width/2, m_height, clrGray);
      m_canvas.Line(0, m_height/2, m_width, m_height/2, clrGray);
      
      // Círculos concêntricos
      for(int r=1; r<=3; r++) {
         int radius = (int)(m_width/2 * r/3.0);
         m_canvas.Circle(m_width/2, m_height/2, radius, clrDarkGray);
      }
   }

   // Configuração de cores
   void SetBaseColor(color base_color) {
      m_base_color = base_color;
      m_background.ColorBackground(ColorToARGB(base_color, 50));
   }

   // Ativa/desativa modo 3D
   void Set3DMode(bool enable) {
      m_3d_enabled = enable;
      // Lógica adicional para efeitos 3D
   }

   // Ajusta escala quântica
   void SetQuantumScale(double scale) {
      m_quantum_scale = MathMax(0.1, MathMin(5.0, scale));
   }

   // Métodos para adicionar vetores individuais
   void AddVector(int index, double magnitude, double direction, string description="", color clr=clrNONE) {
      if(index >=0 && index <5) {
         m_vectors[index].magnitude = magnitude;
         m_vectors[index].direction = direction;
         m_vectors[index].description = description;
         m_vectors[index].vector_color = (clr == clrNONE) ? m_base_color : clr;
      }
   }

   // Gera imagem do canvas
   void SaveToFile(string filename) {
      m_canvas.SaveToImage(filename+".png");
   }
};