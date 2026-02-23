//+------------------------------------------------------------------+
//| HUDManager.mqh - Sistema de Visualização Quântica Institucional  |
//| v15.0 - Painel de Controle com Realidade Aumentada               |
//+------------------------------------------------------------------+

#include "VectorDisplay.mqh"
#include "..\Core\QuantumState.mqh"
#include <Canvas\Canvas.mqh>

class HUDManager {
private:
   VectorDisplay* m_displays[10];       // Suporte para até 10 ativos
   CCanvas        m_quantum_canvas;     // Canvas para visualização quântica
   int            m_width;              // Largura do display
   int            m_height;             // Altura do display
   color          m_bull_color;         // Cor para tendência de alta
   color          m_bear_color;         // Cor para tendência de baixa
   color          m_neutral_color;      // Cor para estado neutro
   bool           m_3d_mode;            // Modo de visualização 3D
   double         m_quantum_scale;      // Escala de visualização quântica

   // Estrutura para dados de ativo
   struct AssetDisplay {
      string symbol;
      int signal;
      double weight;
      string status;
      QuantumState state;
   } m_assets[10];

   // Inicializa o canvas quântico
   void InitQuantumCanvas() {
      if(!m_quantum_canvas.CreateBitmapLabel("QuantumCanvas", 100, 100, m_width, m_height, COLOR_FORMAT_ARGB_NORMALIZE)) {
         Print("Falha ao criar canvas quântico");
      }
      m_quantum_canvas.Erase(ColorToARGB(clrBlack, 0));
   }

   // Renderiza o estado quântico no canvas
   void RenderQuantumState(int index) {
      if(index < 0 || index >= 10) return;
      
      complex wave = m_assets[index].state.GetWaveFunction();
      double prob = m_assets[index].state.Probability();
      
      // Configura cores baseadas no estado
      color base_color = (m_assets[index].signal == 1) ? m_bull_color : 
                        (m_assets[index].signal == -1) ? m_bear_color : m_neutral_color;
      
      // Renderiza função de onda
      int center_x = m_width / 2;
      int center_y = m_height / 2;
      double scale = m_quantum_scale * prob * 50;
      
      for(int x=0; x<m_width; x++) {
         double x_val = (x - center_x) / 10.0;
         double y_val = wave.re * MathExp(-MathPow(x_val,2)) * scale;
         int y = (int)(center_y - y_val);
         
         if(y >=0 && y < m_height) {
            m_quantum_canvas.PixelSet(x, y, ColorToARGB(base_color, 255));
         }
      }
      
      // Renderiza parte imaginária
      for(int x=0; x<m_width; x++) {
         double x_val = (x - center_x) / 10.0;
         double y_val = wave.im * MathExp(-MathPow(x_val,2)) * scale;
         int y = (int)(center_y - y_val);
         
         if(y >=0 && y < m_height) {
            m_quantum_canvas.PixelSet(x, y, ColorToARGB(base_color, 150));
         }
      }
   }

public:
   HUDManager(int width=800, int height=600) : m_width(width), m_height(height) {
      m_bull_color = C'0,255,0';      // Verde para alta
      m_bear_color = C'255,0,0';      // Vermelho para baixa
      m_neutral_color = C'200,200,200'; // Cinza para neutro
      m_3d_mode = false;
      m_quantum_scale = 1.0;
      
      for(int i=0; i<10; i++) {
         m_displays[i] = new VectorDisplay("Asset_"+IntegerToString(i), 50, 70 + i*25);
         m_displays[i]->Create(0, 0, 50, 70 + i*25);
         m_assets[i].symbol = "";
         m_assets[i].signal = 0;
         m_assets[i].weight = 0.0;
      }
      
      Init();
      InitQuantumCanvas();
   }

   ~HUDManager() {
      for(int i=0; i<10; i++)
         delete m_displays[i];
      m_quantum_canvas.Destroy();
   }

   // Inicialização avançada da interface
   void Init() {
      // Cria título com estilo profissional
      VectorDisplay title("Title", m_width/2, 30);
      title.Create(0, 0, m_width/2, 30);
      title.SetFont("Arial", 12, FW_BOLD);
      title.Update("🌠 GALEX QUANTUM TRADING SYSTEM v15.0 | " + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS));
      
      // Cria legendas de status
      VectorDisplay legend("Legend", m_width-150, 30);
      legend.Create(m_width-150, 0, m_width, 30);
      legend.Update("🔴 High Risk | 🟡 Medium | 🟢 Low");
   }

   // Atualização completa do display
   void Update(string symbol, int signal, string status, const QuantumState& state) {
      int index = SymbolToIndex(symbol);
      if(index >= 0 && index < 10) {
         m_assets[index].symbol = symbol;
         m_assets[index].signal = signal;
         m_assets[index].status = status;
         m_assets[index].state = state;
         
         // Atualiza display tradicional
         string display_text = StringFormat("%-8s %s %-15s W:%.2f | P:%.2f", 
                                           symbol, 
                                           SignalToIcon(signal), 
                                           status,
                                           SignalToWeight(signal),
                                           state.Probability());
         
         m_displays[index]->Update(display_text);
         
         // Atualiza visualização quântica
         RenderQuantumState(index);
      }
   }

   // Mapeamento de símbolo para índice (expandido)
   int SymbolToIndex(string symbol) {
      string major_symbols[] = {"EURUSD","GBPUSD","USDJPY","XAUUSD","BTCUSD","US30","DAX","NAS100","OIL","BUND"};
      for(int i=0; i<10; i++) {
         if(symbol == major_symbols[i]) return i;
      }
      return -1;
   }

   // Conversão de sinal para ícones avançados
   string SignalToIcon(int signal) {
      if(signal > 0) {
         if(signal == 1) return "▲";
         return "▲▲"; // Sinal forte
      }
      else if(signal < 0) {
         if(signal == -1) return "▼";
         return "▼▼"; // Sinal forte
      }
      return "■";
   }

   // Cálculo de peso visual com efeito quântico
   double SignalToWeight(int signal) {
      return (signal != 0) ? MathAbs(signal * 0.8) + 0.2 * MathRand()/32767.0 : 0.0;
   }

   // Configuração de cores
   void SetColorScheme(color bull, color bear, color neutral) {
      m_bull_color = bull;
      m_bear_color = bear;
      m_neutral_color = neutral;
   }

   // Ativa/desativa modo 3D
   void Set3DMode(bool enable) {
      m_3d_mode = enable;
      // Lógica adicional para 3D seria implementada aqui
   }

   // Gera relatório completo
   string GenerateReport() const {
      string report = "=== GALEX QUANTUM TRADING REPORT ===\n";
      report += "Time: " + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\n";
      report += "Symbol | Signal | Weight | Probability\n";
      
      for(int i=0; i<10; i++) {
         if(m_assets[i].symbol != "") {
            report += StringFormat("%-6s | %-6s | %-6.2f | %-6.2f\n",
                                 m_assets[i].symbol,
                                 SignalToString(m_assets[i].signal),
                                 m_assets[i].weight,
                                 m_assets[i].state.Probability());
         }
      }
      
      return report;
   }
};