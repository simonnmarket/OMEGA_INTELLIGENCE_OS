//+------------------------------------------------------------------+
//|                                                Apollo11.mq5 |
//|                                  Copyright 2024, Quantum Sensory   |
//|                                             https://www.quantumsensory.com |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "1.00"
#property strict

// Estruturas e enums
enum ENUM_MARKET_STATE {
    MARKET_STATE_RANGE,
    MARKET_STATE_TREND,
    MARKET_STATE_VOLATILE
};

enum ENUM_DIRECTION {
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_SIDEWAYS
};

struct IntegratedSensoryData {
    double visualConfidence;
    double auditoryConfidence;
    double tactileConfidence;
    double olfactoryConfidence;
    double gustatoryConfidence;
    double overallPerception;
    double sensoryCoherence;
    double marketStrength;
    double trendStrength;
    double gravForce;
    double rotationFactor;
};

// Classe do Sistema de Visão Quântica
class CQuantumVisionSystem {
private:
    bool isInitialized;
    double lastPrice;
    double lastVolume;
    
public:
    CQuantumVisionSystem() : isInitialized(false), lastPrice(0), lastVolume(0) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação da visão quântica
        lastPrice = iClose(_Symbol, PERIOD_CURRENT, 0);
        lastVolume = iVolume(_Symbol, PERIOD_CURRENT, 0);
    }
    
    double GetVisualConfidence() {
        return 0.8; // Exemplo
    }
};

// Classe do Sistema de Audição de Mercado
class CMarketHearingSystem {
private:
    bool isInitialized;
    
public:
    CMarketHearingSystem() : isInitialized(false) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação da audição de mercado
    }
    
    double GetAuditoryConfidence() {
        return 0.7; // Exemplo
    }
};

// Classe do Sistema de Tato de Mercado
class CMarketTouchSystem {
private:
    bool isInitialized;
    
public:
    CMarketTouchSystem() : isInitialized(false) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação do tato de mercado
    }
    
    double GetTactileConfidence() {
        return 0.75; // Exemplo
    }
};

// Classe do Sistema de Olfato de Risco
class CRiskSmellingSystem {
private:
    bool isInitialized;
    
public:
    CRiskSmellingSystem() : isInitialized(false) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação do olfato de risco
    }
    
    double GetOlfactoryConfidence() {
        return 0.65; // Exemplo
    }
};

// Classe do Sistema de Paladar de Mercado
class CMarketTasteSystem {
private:
    bool isInitialized;
    
public:
    CMarketTasteSystem() : isInitialized(false) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação do paladar de mercado
    }
    
    double GetGustatoryConfidence() {
        return 0.7; // Exemplo
    }
};

// Classe de Integração Sensorial
class CSensoryIntegration {
private:
    bool isInitialized;
    IntegratedSensoryData currentPerception;
    
public:
    CSensoryIntegration() : isInitialized(false) {}
    
    void ProcessSensoryInput(CQuantumVisionSystem* vision, CMarketHearingSystem* hearing,
                           CMarketTouchSystem* touch, CRiskSmellingSystem* smell,
                           CMarketTasteSystem* taste) {
        if(!isInitialized) return;
        
        currentPerception.visualConfidence = vision.GetVisualConfidence();
        currentPerception.auditoryConfidence = hearing.GetAuditoryConfidence();
        currentPerception.tactileConfidence = touch.GetTactileConfidence();
        currentPerception.olfactoryConfidence = smell.GetOlfactoryConfidence();
        currentPerception.gustatoryConfidence = taste.GetGustatoryConfidence();
        
        // Cálculo da percepção geral
        currentPerception.overallPerception = (currentPerception.visualConfidence +
                                             currentPerception.auditoryConfidence +
                                             currentPerception.tactileConfidence +
                                             currentPerception.olfactoryConfidence +
                                             currentPerception.gustatoryConfidence) / 5.0;
    }
    
    IntegratedSensoryData GetCurrentPerception() {
        return currentPerception;
    }
};

// Classe do Motor de Física
class CPhysicsEngine {
private:
    bool isInitialized;
    double resultantForce;
    double linearMomentum;
    double angularMomentum;
    double kineticEnergy;
    double potentialEnergy;
    double totalEnergy;
    double torque;
    double inertia;
    double centerOfMass;
    int quantumState;
    
public:
    CPhysicsEngine() : isInitialized(false), resultantForce(0), linearMomentum(0),
                      angularMomentum(0), kineticEnergy(0), potentialEnergy(0),
                      totalEnergy(0), torque(0), inertia(0), centerOfMass(0),
                      quantumState(0) {}
    
    bool Initialize() {
        isInitialized = true;
        return true;
    }
    
    void Process() {
        if(!isInitialized) return;
        
        // Implementação do motor de física
        resultantForce = CalculateResultantForce();
        linearMomentum = CalculateLinearMomentum();
        angularMomentum = CalculateAngularMomentum();
        kineticEnergy = CalculateKineticEnergy();
        potentialEnergy = CalculatePotentialEnergy();
        totalEnergy = kineticEnergy + potentialEnergy;
        torque = CalculateTorque();
        inertia = CalculateInertia();
        centerOfMass = CalculateCenterOfMass();
        quantumState = CalculateQuantumState();
    }
    
    double GetResultantForce() { return resultantForce; }
    double GetLinearMomentum() { return linearMomentum; }
    double GetAngularMomentum() { return angularMomentum; }
    double GetKineticEnergy() { return kineticEnergy; }
    double GetPotentialEnergy() { return potentialEnergy; }
    double GetTotalEnergy() { return totalEnergy; }
    double GetTorque() { return torque; }
    double GetInertia() { return inertia; }
    double GetCenterOfMass() { return centerOfMass; }
    int GetQuantumState() { return quantumState; }
    
private:
    double CalculateResultantForce() {
        // Implementação do cálculo da força resultante
        return 0.5; // Exemplo
    }
    
    double CalculateLinearMomentum() {
        // Implementação do cálculo do momento linear
        return 0.6; // Exemplo
    }
    
    double CalculateAngularMomentum() {
        // Implementação do cálculo do momento angular
        return 0.4; // Exemplo
    }
    
    double CalculateKineticEnergy() {
        // Implementação do cálculo da energia cinética
        return 0.7; // Exemplo
    }
    
    double CalculatePotentialEnergy() {
        // Implementação do cálculo da energia potencial
        return 0.3; // Exemplo
    }
    
    double CalculateTorque() {
        // Implementação do cálculo do torque
        return 0.5; // Exemplo
    }
    
    double CalculateInertia() {
        // Implementação do cálculo da inércia
        return 0.6; // Exemplo
    }
    
    double CalculateCenterOfMass() {
        // Implementação do cálculo do centro de massa
        return 0.5; // Exemplo
    }
    
    int CalculateQuantumState() {
        // Implementação do cálculo do estado quântico
        return 1; // Exemplo
    }
};

// Classe do Analisador de Mercado
class CMarketAnalyzer {
private:
    bool isInitialized;
    ENUM_TIMEFRAMES timeframe;
    int lookbackPeriod;
    ENUM_MARKET_STATE marketState;
    double trendStrength;
    
public:
    CMarketAnalyzer() : isInitialized(false), timeframe(PERIOD_CURRENT),
                       lookbackPeriod(20), marketState(MARKET_STATE_RANGE),
                       trendStrength(0) {}
    
    void SetTimeframe(ENUM_TIMEFRAMES tf) { timeframe = tf; }
    void SetLookbackPeriod(int period) { lookbackPeriod = period; }
    
    void AnalyzeTrend() {
        // Implementação da análise de tendência
        trendStrength = CalculateTrendStrength();
    }
    
    double CalculateVolatility() {
        // Implementação do cálculo de volatilidade
        return 0.5; // Exemplo
    }
    
    double CalculateMomentum() {
        // Implementação do cálculo de momentum
        return 0.6; // Exemplo
    }
    
    double AnalyzeVolume() {
        // Implementação da análise de volume
        return 0.7; // Exemplo
    }
    
    double FindSupport() {
        // Implementação da busca de suporte
        return 0.0; // Exemplo
    }
    
    double FindResistance() {
        // Implementação da busca de resistência
        return 0.0; // Exemplo
    }
    
    ENUM_MARKET_STATE GetMarketState() { return marketState; }
    double GetTrendStrength() { return trendStrength; }
    
private:
    double CalculateTrendStrength() {
        // Implementação do cálculo da força da tendência
        return 0.7; // Exemplo
    }
};

// Classe do Analisador de Trajetória
class CTrajectoryAnalyzer {
private:
    bool isInitialized;
    ENUM_DIRECTION direction;
    double velocity;
    double acceleration;
    double inertia;
    double resistance;
    double momentum;
    double energy;
    double stability;
    
public:
    CTrajectoryAnalyzer() : isInitialized(false), direction(DIRECTION_SIDEWAYS),
                           velocity(0), acceleration(0), inertia(0), resistance(0),
                           momentum(0), energy(0), stability(0) {}
    
    void AnalyzeTrajectory() {
        if(!isInitialized) return;
        
        // Implementação da análise de trajetória
        direction = CalculateDirection();
        velocity = CalculateVelocity();
        acceleration = CalculateAcceleration();
        inertia = CalculateInertia();
        resistance = CalculateResistance();
        momentum = CalculateMomentum();
        energy = CalculateEnergy();
        stability = CalculateStability();
    }
    
    ENUM_DIRECTION GetDirection() { return direction; }
    double GetVelocity() { return velocity; }
    double GetAcceleration() { return acceleration; }
    double GetInertia() { return inertia; }
    double GetResistance() { return resistance; }
    double GetMomentum() { return momentum; }
    double GetEnergy() { return energy; }
    double GetStability() { return stability; }
    
private:
    ENUM_DIRECTION CalculateDirection() {
        // Implementação do cálculo da direção
        return DIRECTION_UP; // Exemplo
    }
    
    double CalculateVelocity() {
        // Implementação do cálculo da velocidade
        return 0.6; // Exemplo
    }
    
    double CalculateAcceleration() {
        // Implementação do cálculo da aceleração
        return 0.5; // Exemplo
    }
    
    double CalculateInertia() {
        // Implementação do cálculo da inércia
        return 0.7; // Exemplo
    }
    
    double CalculateResistance() {
        // Implementação do cálculo da resistência
        return 0.4; // Exemplo
    }
    
    double CalculateMomentum() {
        // Implementação do cálculo do momento
        return 0.6; // Exemplo
    }
    
    double CalculateEnergy() {
        // Implementação do cálculo da energia
        return 0.8; // Exemplo
    }
    
    double CalculateStability() {
        // Implementação do cálculo da estabilidade
        return 0.7; // Exemplo
    }
};

// Classe do Gerenciador de Risco
class CRiskManager {
private:
    bool isInitialized;
    double maxRiskPercent;
    double maxDrawdown;
    double currentRisk;
    double currentDrawdown;
    
public:
    CRiskManager() : isInitialized(false), maxRiskPercent(2.0), maxDrawdown(10.0),
                    currentRisk(0), currentDrawdown(0) {}
    
    void SetMaxRiskPercent(double percent) { maxRiskPercent = percent; }
    void SetMaxDrawdown(double percent) { maxDrawdown = percent; }
    
    bool CanOpenPosition() {
        return currentRisk < maxRiskPercent && currentDrawdown < maxDrawdown;
    }
    
    double CalculatePositionSize() {
        // Implementação do cálculo do tamanho da posição
        return 0.1; // Exemplo
    }
    
    double CalculateStopLoss() {
        // Implementação do cálculo do stop loss
        return 0.0; // Exemplo
    }
    
    double CalculateTakeProfit() {
        // Implementação do cálculo do take profit
        return 0.0; // Exemplo
    }
    
    double GetCurrentRisk() { return currentRisk; }
    double GetCurrentDrawdown() { return currentDrawdown; }
};

// Classe do Radar Institucional
class CInstitutionalRadar {
private:
    bool isInitialized;
    double volumeThreshold;
    double priceImpactThreshold;
    int lookbackPeriod;
    
public:
    CInstitutionalRadar() : isInitialized(false), volumeThreshold(1000),
                           priceImpactThreshold(0.5), lookbackPeriod(20) {}
    
    bool DetectInstitutionalActivity() {
        if(!isInitialized) return false;
        
        // Implementação da detecção de atividade institucional
        return AnalyzeVolumeActivity() && AnalyzePriceImpact();
    }
    
    double GetVolumeActivity() {
        // Implementação do cálculo da atividade de volume
        return 0.7; // Exemplo
    }
    
    double GetPriceImpact() {
        // Implementação do cálculo do impacto de preço
        return 0.6; // Exemplo
    }
    
    int GetLookbackPeriod() { return lookbackPeriod; }
    
private:
    bool AnalyzeVolumeActivity() {
        // Implementação da análise de atividade de volume
        return true; // Exemplo
    }
    
    bool AnalyzePriceImpact() {
        // Implementação da análise de impacto de preço
        return true; // Exemplo
    }
};

// Classe do Logger
class CLogger {
private:
    bool isInitialized;
    string logFileName;
    
public:
    CLogger() : isInitialized(false) {
        logFileName = "Apollo11_" + TimeToString(TimeCurrent(), TIME_DATE) + ".log";
    }
    
    bool Initialize() {
        int handle = FileOpen(logFileName, FILE_WRITE|FILE_READ|FILE_TXT);
        if(handle == INVALID_HANDLE) {
            Print("Erro ao abrir arquivo de log: ", GetLastError());
            return false;
        }
        FileClose(handle);
        isInitialized = true;
        return true;
    }
    
    void Log(string message, bool printToConsole = true) {
        if(!isInitialized) return;
        
        string logMessage = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + " - " + message;
        
        int handle = FileOpen(logFileName, FILE_WRITE|FILE_READ|FILE_TXT);
        if(handle != INVALID_HANDLE) {
            FileSeek(handle, 0, FILE_END);
            FileWrite(handle, logMessage);
            FileClose(handle);
        }
        
        if(printToConsole) Print(logMessage);
    }
    
    void LogError(string message, int errorCode) {
        Log("ERRO: " + message + " (Código: " + IntegerToString(errorCode) + ")", true);
    }
    
    void LogTrade(string type, double lotSize, double stopLoss, double takeProfit) {
        Log("TRADE: " + type + " - Lote: " + DoubleToString(lotSize, 2) +
            " SL: " + DoubleToString(stopLoss, 5) +
            " TP: " + DoubleToString(takeProfit, 5), true);
    }
    
    void LogPositionClosed(string type, double profit) {
        Log("POSIÇÃO FECHADA: " + type + " - Lucro: " + DoubleToString(profit, 2), true);
    }
};

// Parâmetros de entrada
input double   RiskPercent = 2.0;        // Risco por operação (%)
input double   MaxDrawdown = 10.0;       // Drawdown máximo (%)
input int      LookbackPeriod = 20;      // Período de análise
input bool     UseInstitutionalRadar = true; // Usar radar institucional

// Instâncias dos módulos
CQuantumVisionSystem* Vision = NULL;
CMarketHearingSystem* Hearing = NULL;
CMarketTouchSystem* Touch = NULL;
CRiskSmellingSystem* Smell = NULL;
CMarketTasteSystem* Taste = NULL;
CSensoryIntegration* SensorySystem = NULL;
CPhysicsEngine* Physics = NULL;
CMarketAnalyzer* Market = NULL;
CTrajectoryAnalyzer* Trajectory = NULL;
CRiskManager* Risk = NULL;
CInstitutionalRadar* Radar = NULL;
CLogger* Logger = NULL;

// Função de inicialização
int OnInit() {
    Print("Inicializando Apollo11...");
    
    // Inicializando os sistemas sensoriais
    Vision = new CQuantumVisionSystem();
    Hearing = new CMarketHearingSystem();
    Touch = new CMarketTouchSystem();
    Smell = new CRiskSmellingSystem();
    Taste = new CMarketTasteSystem();
    SensorySystem = new CSensoryIntegration();
    
    // Inicializando os sistemas
    if(!Vision.Initialize() || !Hearing.Initialize() || !Touch.Initialize() ||
       !Smell.Initialize() || !Taste.Initialize()) {
        Print("Erro na inicialização dos sistemas sensoriais");
        return INIT_FAILED;
    }
    
    // Inicializando o motor de física
    Physics = new CPhysicsEngine();
    if(!Physics.Initialize()) {
        Print("Erro na inicialização do PhysicsEngine");
        return INIT_FAILED;
    }
    
    // Inicializando o analisador de mercado
    Market = new CMarketAnalyzer();
    Market.SetTimeframe(PERIOD_CURRENT);
    Market.SetLookbackPeriod(LookbackPeriod);
    
    // Inicializando o analisador de trajetória
    Trajectory = new CTrajectoryAnalyzer();
    
    // Inicializando o gerenciador de risco
    Risk = new CRiskManager();
    Risk.SetMaxRiskPercent(RiskPercent);
    Risk.SetMaxDrawdown(MaxDrawdown);
    
    // Inicializando o radar institucional
    if(UseInstitutionalRadar) {
        Radar = new CInstitutionalRadar();
    }
    
    // Inicializando o logger
    Logger = new CLogger();
    Logger.Initialize();
    
    Logger.Log("Apollo11 inicializado com sucesso");
    return INIT_SUCCEEDED;
}

// Função de finalização
void OnDeinit(const int reason) {
    if(Vision != NULL) { delete Vision; Vision = NULL; }
    if(Hearing != NULL) { delete Hearing; Hearing = NULL; }
    if(Touch != NULL) { delete Touch; Touch = NULL; }
    if(Smell != NULL) { delete Smell; Smell = NULL; }
    if(Taste != NULL) { delete Taste; Taste = NULL; }
    if(SensorySystem != NULL) { delete SensorySystem; SensorySystem = NULL; }
    if(Physics != NULL) { delete Physics; Physics = NULL; }
    if(Market != NULL) { delete Market; Market = NULL; }
    if(Trajectory != NULL) { delete Trajectory; Trajectory = NULL; }
    if(Risk != NULL) { delete Risk; Risk = NULL; }
    if(Radar != NULL) { delete Radar; Radar = NULL; }
    if(Logger != NULL) { delete Logger; Logger = NULL; }
}

// Função principal de processamento
void OnTick() {
    static datetime lastBar;
    datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBar == lastBar) return;
    lastBar = currentBar;
    
    // Processando sistemas sensoriais
    Vision.Process();
    Hearing.Process();
    Touch.Process();
    Smell.Process();
    Taste.Process();
    
    // Integrando percepções sensoriais
    SensorySystem.ProcessSensoryInput(Vision, Hearing, Touch, Smell, Taste);
    IntegratedSensoryData perception = SensorySystem.GetCurrentPerception();
    
    // Processando simulação física
    Physics.Process();
    
    // Analisando mercado
    Market.AnalyzeTrend();
    Market.CalculateVolatility();
    Market.CalculateMomentum();
    Market.AnalyzeVolume();
    
    // Analisando trajetória
    Trajectory.AnalyzeTrajectory();
    
    // Verificando atividade institucional
    bool institutionalActivity = false;
    if(UseInstitutionalRadar && Radar != NULL) {
        institutionalActivity = Radar.DetectInstitutionalActivity();
    }
    
    // Verificando condições de entrada
    if(ShouldEnterLong(perception, institutionalActivity)) {
        EnterLongPosition();
    }
    else if(ShouldEnterShort(perception, institutionalActivity)) {
        EnterShortPosition();
    }
    
    // Gerenciando posições abertas
    ManageOpenPositions();
}

// Função para verificar condições de entrada long
bool ShouldEnterLong(IntegratedSensoryData &perception, bool institutionalActivity) {
    // Verificando se pode abrir posição
    if(!Risk.CanOpenPosition()) return false;
    
    // Verificando condições sensoriais
    if(perception.overallPerception < 0.7) return false;
    if(perception.sensoryCoherence < 0.8) return false;
    
    // Verificando condições de mercado
    if(Market.GetMarketState() != MARKET_STATE_TREND) return false;
    if(Market.GetTrendStrength() < 0.6) return false;
    
    // Verificando condições físicas
    if(Physics.GetResultantForce() < 0.5) return false;
    if(Physics.GetLinearMomentum() < 0.5) return false;
    
    // Verificando trajetória
    if(Trajectory.GetDirection() != DIRECTION_UP) return false;
    if(Trajectory.GetStability() < 0.7) return false;
    
    // Verificando atividade institucional
    if(UseInstitutionalRadar && !institutionalActivity) return false;
    
    return true;
}

// Função para verificar condições de entrada short
bool ShouldEnterShort(IntegratedSensoryData &perception, bool institutionalActivity) {
    // Verificando se pode abrir posição
    if(!Risk.CanOpenPosition()) return false;
    
    // Verificando condições sensoriais
    if(perception.overallPerception > -0.7) return false;
    if(perception.sensoryCoherence < 0.8) return false;
    
    // Verificando condições de mercado
    if(Market.GetMarketState() != MARKET_STATE_TREND) return false;
    if(Market.GetTrendStrength() < 0.6) return false;
    
    // Verificando condições físicas
    if(Physics.GetResultantForce() > -0.5) return false;
    if(Physics.GetLinearMomentum() > -0.5) return false;
    
    // Verificando trajetória
    if(Trajectory.GetDirection() != DIRECTION_DOWN) return false;
    if(Trajectory.GetStability() < 0.7) return false;
    
    // Verificando atividade institucional
    if(UseInstitutionalRadar && !institutionalActivity) return false;
    
    return true;
}

// Função para entrar em posição long
void EnterLongPosition() {
    double lotSize = Risk.CalculatePositionSize();
    double stopLoss = Risk.CalculateStopLoss();
    double takeProfit = Risk.CalculateTakeProfit();
    
    if(OrderSend(_Symbol, ORDER_TYPE_BUY, lotSize, Ask, 10, stopLoss, takeProfit, "Apollo11 Long", 0, 0, clrGreen)) {
        Logger.LogTrade("Entrada Long", lotSize, stopLoss, takeProfit);
    }
}

// Função para entrar em posição short
void EnterShortPosition() {
    double lotSize = Risk.CalculatePositionSize();
    double stopLoss = Risk.CalculateStopLoss();
    double takeProfit = Risk.CalculateTakeProfit();
    
    if(OrderSend(_Symbol, ORDER_TYPE_SELL, lotSize, Bid, 10, stopLoss, takeProfit, "Apollo11 Short", 0, 0, clrRed)) {
        Logger.LogTrade("Entrada Short", lotSize, stopLoss, takeProfit);
    }
}

// Função para gerenciar posições abertas
void ManageOpenPositions() {
    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionSelectByTicket(PositionGetTicket(i))) {
            // Verificando condições de saída
            if(ShouldExitPosition()) {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                    if(OrderClose(PositionGetTicket(i), PositionGetDouble(POSITION_VOLUME), Bid, 10, clrRed)) {
                        Logger.LogPositionClosed("Saída Long", PositionGetDouble(POSITION_PROFIT));
                    }
                }
                else {
                    if(OrderClose(PositionGetTicket(i), PositionGetDouble(POSITION_VOLUME), Ask, 10, clrRed)) {
                        Logger.LogPositionClosed("Saída Short", PositionGetDouble(POSITION_PROFIT));
                    }
                }
            }
        }
    }
}

// Função para verificar condições de saída
bool ShouldExitPosition() {
    // Verificando condições sensoriais
    IntegratedSensoryData perception = SensorySystem.GetCurrentPerception();
    if(perception.overallPerception < 0.3 || perception.overallPerception > -0.3) return true;
    
    // Verificando condições de mercado
    if(Market.GetMarketState() == MARKET_STATE_RANGE) return true;
    if(Market.GetTrendStrength() < 0.3) return true;
    
    // Verificando condições físicas
    if(MathAbs(Physics.GetResultantForce()) < 0.3) return true;
    
    // Verificando trajetória
    if(Trajectory.GetStability() < 0.3) return true;
    
    return false;
} 