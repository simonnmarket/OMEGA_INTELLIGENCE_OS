#property copyright "Risk Management System"
#property strict

class CRiskManager {
private:
    double maxRiskPercent;
    double maxDrawdownPercent;
    double minVolumeForce;
    double maxPositions;
    double currentDrawdown;
    double accountBalance;
    double accountEquity;
    int currentPositions;
    
    // Handles para indicadores
    int atrHandle;
    int volumeHandle;
    
public:
    CRiskManager(double riskPercent = 2.0, double drawdownPercent = 10.0, 
                double minVolForce = 0.5, double maxPos = 3) {
        maxRiskPercent = riskPercent;
        maxDrawdownPercent = drawdownPercent;
        minVolumeForce = minVolForce;
        maxPositions = maxPos;
        currentDrawdown = 0.0;
        accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        currentPositions = 0;
        
        atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
        volumeHandle = iVolumes(_Symbol, PERIOD_CURRENT, VOLUME_TICK);
    }
    
    ~CRiskManager() {
        if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
        if(volumeHandle != INVALID_HANDLE) IndicatorRelease(volumeHandle);
    }
    
    bool Initialize() {
        if(atrHandle == INVALID_HANDLE || volumeHandle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores em CRiskManager");
            return false;
        }
        return true;
    }
    
    void Process() {
        // Atualiza informações da conta
        accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        accountEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        
        // Calcula drawdown atual
        if(accountBalance > 0) {
            currentDrawdown = (accountBalance - accountEquity) / accountBalance * 100.0;
        }
        
        // Atualiza número de posições
        currentPositions = PositionsTotal();
        
        Print("Gerenciamento de Risco:",
              "\nDrawdown: ", currentDrawdown, "%",
              "\nPosições Atuais: ", currentPositions,
              "\nSaldo: ", accountBalance,
              "\nEquidade: ", accountEquity);
    }
    
    bool IsRiskAcceptable() {
        // Verifica drawdown máximo
        if(currentDrawdown >= maxDrawdownPercent) {
            Print("Drawdown máximo excedido: ", currentDrawdown, "%");
            return false;
        }
        
        // Verifica número máximo de posições
        if(currentPositions >= maxPositions) {
            Print("Número máximo de posições excedido: ", currentPositions);
            return false;
        }
        
        // Verifica força do volume
        double volumeForce = CalculateVolumeForce();
        if(volumeForce < minVolumeForce) {
            Print("Força do volume insuficiente: ", volumeForce);
            return false;
        }
        
        return true;
    }
    
    double CalculatePositionSize(double stopLoss) {
        if(!IsRiskAcceptable()) return 0.0;
        
        // Calcula tamanho da posição baseado no risco
        double riskAmount = accountBalance * (maxRiskPercent / 100.0);
        double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        
        if(tickSize == 0 || tickValue == 0) return 0.0;
        
        double positionSize = riskAmount / (stopLoss * tickValue / tickSize);
        
        // Ajusta para o tamanho mínimo e máximo permitido
        double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
        
        positionSize = MathMax(minLot, MathMin(maxLot, positionSize));
        
        return positionSize;
    }
    
    double CalculateVolumeForce() {
        double volume[];
        ArraySetAsSeries(volume, true);
        if(CopyBuffer(volumeHandle, 0, 0, 20, volume) <= 0) return 0.0;
        
        double avgVolume = 0.0;
        for(int i = 0; i < 20; i++) {
            avgVolume += volume[i];
        }
        avgVolume /= 20.0;
        
        return volume[0] / avgVolume;
    }
    
    double GetCurrentDrawdown() {
        return currentDrawdown;
    }
    
    int GetCurrentPositions() {
        return currentPositions;
    }
}; 