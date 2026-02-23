#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para configurações de visualização
struct VisualizationSettings {
    color buyColor;        // Cor para sinais de compra
    color sellColor;       // Cor para sinais de venda
    color slColor;         // Cor para stop loss
    color tpColor;         // Cor para take profit
    int arrowSize;         // Tamanho das setas
    int lineWidth;         // Largura das linhas
    bool showLabels;       // Mostrar rótulos
    bool showLevels;       // Mostrar níveis
};

// Classe para visualização gráfica
class CChartVisualizer {
private:
    // Configurações
    VisualizationSettings m_settings;
    
    // Estado
    bool m_isInitialized;
    string m_prefix;       // Prefixo para objetos gráficos
    
    // Métodos privados
    string GenerateObjectName(const string& type) {
        return m_prefix + "_" + type + "_" + IntegerToString(TimeCurrent());
    }
    
    void DrawArrow(const datetime& time, const double& price, bool isBuy) {
        string name = GenerateObjectName("Arrow");
        color arrowColor = isBuy ? m_settings.buyColor : m_settings.sellColor;
        
        ObjectCreate(0, name, OBJ_ARROW, 0, time, price);
        ObjectSetInteger(0, name, OBJPROP_ARROWCODE, isBuy ? 233 : 234);
        ObjectSetInteger(0, name, OBJPROP_COLOR, arrowColor);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, m_settings.arrowSize);
    }
    
    void DrawLine(const string& name, const datetime& time1, const double& price1,
                 const datetime& time2, const double& price2, color lineColor) {
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
        ObjectSetInteger(0, name, OBJPROP_COLOR, lineColor);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, m_settings.lineWidth);
    }
    
    void DrawLabel(const string& name, const datetime& time, const double& price,
                  const string& text, color textColor) {
        ObjectCreate(0, name, OBJ_TEXT, 0, time, price);
        ObjectSetString(0, name, OBJPROP_TEXT, text);
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, 8);
    }
    
public:
    // Construtor
    CChartVisualizer() {
        // Configurações padrão
        m_settings.buyColor = clrLime;
        m_settings.sellColor = clrRed;
        m_settings.slColor = clrRed;
        m_settings.tpColor = clrLime;
        m_settings.arrowSize = 2;
        m_settings.lineWidth = 1;
        m_settings.showLabels = true;
        m_settings.showLevels = true;
        
        m_isInitialized = false;
        m_prefix = "Skyler_";
    }
    
    // Destrutor
    ~CChartVisualizer() {
        // Limpar objetos gráficos
        ObjectsDeleteAll(0, m_prefix);
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Marcar sinal
    void MarkSignal(const datetime& time, const double& price, bool isBuy) {
        if(!m_isInitialized) return;
        
        // Desenhar seta
        DrawArrow(time, price, isBuy);
        
        // Adicionar rótulo se habilitado
        if(m_settings.showLabels) {
            string labelName = GenerateObjectName("Label");
            string labelText = isBuy ? "BUY" : "SELL";
            color labelColor = isBuy ? m_settings.buyColor : m_settings.sellColor;
            
            DrawLabel(labelName, time, price, labelText, labelColor);
        }
    }
    
    // Mostrar níveis
    void ShowLevels(const double& entry, const double& sl, const double& tp) {
        if(!m_isInitialized || !m_settings.showLevels) return;
        
        datetime currentTime = TimeCurrent();
        datetime futureTime = currentTime + 24 * 3600; // 24 horas no futuro
        
        // Linha de entrada
        string entryName = GenerateObjectName("Entry");
        DrawLine(entryName, currentTime, entry, futureTime, entry, clrYellow);
        
        // Linha de stop loss
        string slName = GenerateObjectName("SL");
        DrawLine(slName, currentTime, sl, futureTime, sl, m_settings.slColor);
        
        // Linha de take profit
        string tpName = GenerateObjectName("TP");
        DrawLine(tpName, currentTime, tp, futureTime, tp, m_settings.tpColor);
        
        // Adicionar rótulos se habilitado
        if(m_settings.showLabels) {
            DrawLabel(GenerateObjectName("EntryLabel"), currentTime, entry, "Entry", clrYellow);
            DrawLabel(GenerateObjectName("SLLabel"), currentTime, sl, "SL", m_settings.slColor);
            DrawLabel(GenerateObjectName("TPLabel"), currentTime, tp, "TP", m_settings.tpColor);
        }
    }
    
    // Limpar visualização
    void Clear() {
        ObjectsDeleteAll(0, m_prefix);
    }
    
    // Configurações
    void SetSettings(const VisualizationSettings& settings) {
        m_settings = settings;
    }
    
    // Acesso
    VisualizationSettings GetSettings() const {
        return m_settings;
    }
    
    // Métricas
    void UpdateMetrics() {
        Print("Chart Visualizer Metrics:");
        Print("Total Objects: ", ObjectsTotal(0));
        Print("Show Labels: ", m_settings.showLabels);
        Print("Show Levels: ", m_settings.showLevels);
    }
}; 