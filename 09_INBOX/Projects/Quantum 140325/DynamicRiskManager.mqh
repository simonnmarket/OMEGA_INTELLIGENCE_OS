#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.0"
#property strict

// Estrutura para parâmetros de risco
struct RiskParameters {
    double maxRiskPerTrade;     // Risco máximo por operação (%)
    double portfolioHeat;       // Calor do portfólio (%)
    double initialStopLoss;     // Stop loss inicial (%)
    double trailingFactor;      // Fator de trailing stop (%)
};

// Classe para gestão de risco dinâmica
class CDynamicRiskManager {
private:
    // Estado
    bool m_isInitialized;
    RiskParameters m_params;
    double m_currentStopLoss;
    double m_highestPrice;
    double m_lowestPrice;
    
    // Métodos privados
    double CalculatePositionSize(const string& symbol, double stopLoss) {
        if(!m_isInitialized) return 0;
        
        double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        double riskAmount = accountBalance * m_params.maxRiskPerTrade / 100;
        
        double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        
        // Calcular tamanho do lote baseado no risco
        double lotSize = riskAmount / (stopLoss * tickValue / tickSize);
        
        // Ajustar para limites do símbolo
        lotSize = MathFloor(lotSize / lotStep) * lotStep;
        lotSize = MathMax(minLot, MathMin(maxLot, lotSize));
        
        return lotSize;
    }
    
    double CalculateTrailingStop(const string& symbol, double currentPrice, bool isLong) {
        if(!m_isInitialized) return 0;
        
        if(isLong) {
            // Atualizar preço mais alto
            m_highestPrice = MathMax(m_highestPrice, currentPrice);
            
            // Calcular novo stop loss
            double newStopLoss = m_highestPrice * (1 - m_params.trailingFactor / 100);
            
            // Só atualizar se for maior que o stop loss atual
            if(newStopLoss > m_currentStopLoss) {
                m_currentStopLoss = newStopLoss;
            }
        }
        else {
            // Atualizar preço mais baixo
            m_lowestPrice = MathMin(m_lowestPrice, currentPrice);
            
            // Calcular novo stop loss
            double newStopLoss = m_lowestPrice * (1 + m_params.trailingFactor / 100);
            
            // Só atualizar se for menor que o stop loss atual
            if(newStopLoss < m_currentStopLoss) {
                m_currentStopLoss = newStopLoss;
            }
        }
        
        return m_currentStopLoss;
    }
    
public:
    // Construtor
    CDynamicRiskManager() {
        m_isInitialized = false;
        m_params.maxRiskPerTrade = 2.0;    // 2% por operação
        m_params.portfolioHeat = 15.0;     // 15% do portfólio
        m_params.initialStopLoss = 2.0;    // 2% stop loss inicial
        m_params.trailingFactor = 2.0;     // 2% trailing stop
        m_currentStopLoss = 0;
        m_highestPrice = 0;
        m_lowestPrice = 0;
    }
    
    // Destrutor
    ~CDynamicRiskManager() {
        // Limpar recursos
    }
    
    // Inicialização
    bool Initialize() {
        m_isInitialized = true;
        return true;
    }
    
    // Calcular tamanho da posição
    double CalculatePositionSize(const string& symbol) {
        if(!m_isInitialized) return 0;
        
        double currentPrice = SymbolInfoDouble(symbol, SYMBOL_ASK);
        double stopLoss = currentPrice * (1 - m_params.initialStopLoss / 100);
        
        return CalculatePositionSize(symbol, stopLoss);
    }
    
    // Atualizar stop loss
    double UpdateStopLoss(const string& symbol, bool isLong) {
        if(!m_isInitialized) return 0;
        
        double currentPrice = isLong ? 
            SymbolInfoDouble(symbol, SYMBOL_BID) : 
            SymbolInfoDouble(symbol, SYMBOL_ASK);
            
        return CalculateTrailingStop(symbol, currentPrice, isLong);
    }
    
    // Verificar calor do portfólio
    bool IsPortfolioHeatAcceptable() {
        if(!m_isInitialized) return false;
        
        double totalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        double usedMargin = AccountInfoDouble(ACCOUNT_MARGIN);
        double heat = (usedMargin / totalEquity) * 100;
        
        return heat <= m_params.portfolioHeat;
    }
    
    // Configurações
    void SetRiskParameters(const RiskParameters& params) {
        m_params = params;
    }
    
    // Acesso
    bool IsInitialized() const {
        return m_isInitialized;
    }
    
    RiskParameters GetRiskParameters() const {
        return m_params;
    }
    
    double GetCurrentStopLoss() const {
        return m_currentStopLoss;
    }
    
    // Métricas
    void PrintMetrics() {
        Print("Dynamic Risk Manager Metrics:");
        Print("Initialized: ", m_isInitialized);
        Print("Max Risk Per Trade: ", m_params.maxRiskPerTrade, "%");
        Print("Portfolio Heat: ", m_params.portfolioHeat, "%");
        Print("Initial Stop Loss: ", m_params.initialStopLoss, "%");
        Print("Trailing Factor: ", m_params.trailingFactor, "%");
        Print("Current Stop Loss: ", m_currentStopLoss);
    }
}; 