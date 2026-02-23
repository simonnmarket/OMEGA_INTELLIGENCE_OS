#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "4.0"
#property strict

#include <Trade\Trade.mqh>

// --- Configurações e Estruturas ---
struct IntegratedSensoryData {
    double visualConfidence;
    double auditoryConfidence;
    double tactileConfidence;
    double olfactoryConfidence;
    double gustatoryConfidence;
    double overallPerception;
    double sensoryCoherence;
};

struct GlobalConfig {
    const static double MinimumConfidence;
    const static double CoherenceThreshold;
    const static int AnalysisDepth;
};
const double GlobalConfig::MinimumConfidence = 0.3;
const double GlobalConfig::CoherenceThreshold = 0.55; // Reduzido de 0.65
const int GlobalConfig::AnalysisDepth = 100;

struct VisionConfig {
    const static double PatternConfidence;
    static double VolumeThreshold;
};
const double VisionConfig::PatternConfidence = 0.75;
double VisionConfig::VolumeThreshold = 2.5;

struct HearingConfig {
    const static double NoiseThreshold;
    const static double SignalStrength;
};
const double HearingConfig::NoiseThreshold = 0.2;
const double HearingConfig::SignalStrength = 0.7;

struct TouchConfig {
    const static double ResistanceThreshold;
    const static double PressureThreshold;
};
const double TouchConfig::ResistanceThreshold = 0.6;
const double TouchConfig::PressureThreshold = 0.7;

struct SmellConfig {
    const static double RiskThreshold;
    const static double DangerThreshold;
};
const double SmellConfig::RiskThreshold = 0.65;
const double SmellConfig::DangerThreshold = 1.5;

struct TasteConfig {
    const static double ProfitThreshold;
    const static double QualityThreshold;
};
const double TasteConfig::ProfitThreshold = 0.7;
const double TasteConfig::QualityThreshold = 0.8;

// --- Classes Sensoriais ---
class CSensoryBase {
protected:
    double confidence;
    bool isInitialized;
    
public:
    CSensoryBase() : confidence(0), isInitialized(false) {}
    virtual ~CSensoryBase() {}
    
    double GetConfidence() const { return confidence; }
    bool IsInitialized() const { return isInitialized; }
    
    virtual bool Initialize() {
        isInitialized = true;
        return true;
    }
};

class CQuantumVisionSystem : public CSensoryBase {
private:
    double lastVolume;
    double averageVolume;
    int volumeMA;
    
public:
    CQuantumVisionSystem() : lastVolume(0), averageVolume(0) {
        volumeMA = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, VOLUME_TICK);
    }
    
    ~CQuantumVisionSystem() {
        if(volumeMA != INVALID_HANDLE) IndicatorRelease(volumeMA);
    }
    
    bool Initialize() override {
        if(volumeMA == INVALID_HANDLE) return false;
        isInitialized = true;
        return true;
    }
    
    void ProcessMarketView() {
        lastVolume = (double)iVolume(_Symbol, PERIOD_CURRENT, 0);
        averageVolume = CalculateAverageVolume(20);
        confidence = CalculateConfidence();
    }
    
    bool DetectarBlocosPesados() {
        return (lastVolume > averageVolume * VisionConfig::VolumeThreshold / 2);
    }
    
    double AnalyzeOrderFlow() {
        double close[];
        ArraySetAsSeries(close, true);
        if(CopyClose(_Symbol, PERIOD_CURRENT, 0, 2, close) < 2) return 0;
        double priceChange = close[0] - close[1];
        double volume = iVolume(_Symbol, PERIOD_CURRENT, 0);
        if(volume == 0) return 0;
        return priceChange / volume;
    }
    
    double GetLastVolume() const { return lastVolume; }
    double GetAverageVolume(int period) { return CalculateAverageVolume(period); }

private:
    double CalculateAverageVolume(int period) {
        long volumes[];
        ArraySetAsSeries(volumes, true);
        datetime startTime = iTime(_Symbol, PERIOD_CURRENT, period - 1);
        if(CopyTickVolume(_Symbol, PERIOD_CURRENT, startTime, period, volumes) > 0) {
            double sum = 0;
            for(int i = 0; i < ArraySize(volumes); i++) {
                sum += (double)volumes[i];
            }
            return sum / ArraySize(volumes);
        }
        return 1; // Evitar divisão por zero
    }
    
    double CalculateConfidence() {
        if(averageVolume == 0) return 0;
        return MathMin(lastVolume / averageVolume, 1.0);
    }
};

class CMarketHearingSystem : public CSensoryBase {
private:
    double noiseLevel;
    double signalStrength;
    int rsiHandle;
    
public:
    CMarketHearingSystem() : noiseLevel(0), signalStrength(0) {
        rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
    }
    
    ~CMarketHearingSystem() {
        if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
    }
    
    bool Initialize() override {
        if(rsiHandle == INVALID_HANDLE) return false;
        isInitialized = true;
        return true;
    }
    
    void ProcessMarketSounds() {
        noiseLevel = CalculateNoiseLevel();
        signalStrength = CalculateSignalStrength();
        confidence = CalculateConfidence();
    }
    
    bool AnalisarImpulsoForte() {
        return (signalStrength > HearingConfig::SignalStrength / 2);
    }
    
    double GetMarketNoise() {
        return noiseLevel;
    }
    
private:
    double CalculateNoiseLevel() {
        double rsi[];
        ArraySetAsSeries(rsi, true);
        if(CopyBuffer(rsiHandle, 0, 0, 2, rsi) > 0) {
            return MathAbs(rsi[0] - rsi[1]) / 100.0;
        }
        return 1.0;
    }
    
    double CalculateSignalStrength() {
        double rsi[];
        ArraySetAsSeries(rsi, true);
        if(CopyBuffer(rsiHandle, 0, 0, 1, rsi) > 0) {
            return MathAbs(50 - rsi[0]) / 50.0;
        }
        return 0;
    }
    
    double CalculateConfidence() {
        return 1.0 - noiseLevel;
    }
};

class CMarketTouchSystem : public CSensoryBase {
private:
    double pressure;
    double resistance;
    int maHandle;
    
public:
    CMarketTouchSystem() : pressure(0), resistance(0) {
        maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
    }
    
    ~CMarketTouchSystem() {
        if(maHandle != INVALID_HANDLE) IndicatorRelease(maHandle);
    }
    
    bool Initialize() override {
        if(maHandle == INVALID_HANDLE) return false;
        isInitialized = true;
        return true;
    }
    
    void ProcessMarketTouch() {
        pressure = CalculatePressure();
        resistance = CalculateResistance();
        confidence = CalculateConfidence();
    }
    
    bool VerificarAbsorcao() {
        return (resistance > TouchConfig::ResistanceThreshold / 2);
    }
    
    double GetMarketPressure() {
        return pressure;
    }
    
private:
    double CalculatePressure() {
        double ma[];
        ArraySetAsSeries(ma, true);
        if(CopyBuffer(maHandle, 0, 0, 2, ma) > 0) {
            return MathAbs((ma[0] - ma[1]) / ma[1]); // Ajustado para valor absoluto
        }
        return 0.5; // Valor padrão mais alto
    }
    
    double CalculateResistance() {
        MqlTick tick;
        if(!SymbolInfoTick(_Symbol, tick)) return 0;
        double range = tick.ask - tick.bid;
        double avgRange = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 20;
        return MathMin(range / avgRange, 1.0);
    }
    
    double CalculateConfidence() {
        return MathMax((pressure + resistance) / 2, 0.3); // Garantir mínimo de 0.3
    }
};

class CRiskSmellingSystem : public CSensoryBase {
private:
    double riskLevel;
    double marketStress;
    int atrHandle;
    
public:
    CRiskSmellingSystem() : riskLevel(0), marketStress(0) {
        atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
    }
    
    ~CRiskSmellingSystem() {
        if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
    }
    
    bool Initialize() override {
        if(atrHandle == INVALID_HANDLE) return false;
        isInitialized = true;
        return true;
    }
    
    void ProcessMarketSmell() {
        riskLevel = CalculateRiskLevel();
        marketStress = CalculateMarketStress();
        confidence = CalculateConfidence();
    }
    
    bool AvaliarSentimento() {
        return (marketStress < SmellConfig::DangerThreshold);
    }
    
    double GetRiskLevel() {
        return riskLevel;
    }
    
private:
    double CalculateRiskLevel() {
        double atr[];
        ArraySetAsSeries(atr, true);
        if(CopyBuffer(atrHandle, 0, 0, 2, atr) > 0) {
            return MathMin(atr[0] / atr[1], 1.0); // Limitado a 1.0
        }
        return 0.5; // Valor padrão mais alto
    }
    
    double CalculateMarketStress() {
        double atr[];
        ArraySetAsSeries(atr, true);
        if(CopyBuffer(atrHandle, 0, 0, 20, atr) > 0) {
            double maxAtr = atr[ArrayMaximum(atr, 0, 20)];
            double suddenSpike = atr[0] / atr[1];
            return (suddenSpike > 2.0) ? 1.0 : atr[0] / maxAtr;
        }
        return 0;
    }
    
    double CalculateConfidence() {
        return MathMax(1.0 - (riskLevel + marketStress) / 2, 0.3); // Garantir mínimo de 0.3
    }
};

class CMarketTasteSystem : public CSensoryBase {
private:
    double profitPotential;
    double marketQuality;
    int stochHandle;
    
public:
    CMarketTasteSystem() : profitPotential(0), marketQuality(0) {
        stochHandle = iStochastic(_Symbol, PERIOD_CURRENT, 5, 3, 3, MODE_SMA, STO_LOWHIGH);
    }
    
    ~CMarketTasteSystem() {
        if(stochHandle != INVALID_HANDLE) IndicatorRelease(stochHandle);
    }
    
    bool Initialize() override {
        if(stochHandle == INVALID_HANDLE) return false;
        isInitialized = true;
        return true;
    }
    
    void ProcessMarketTaste() {
        profitPotential = CalculateProfitPotential();
        marketQuality = CalculateMarketQuality();
        confidence = CalculateConfidence();
    }
    
    bool AnalisarQualidadeFluxo() {
        return (marketQuality > TasteConfig::QualityThreshold);
    }
    
    double GetMarketQuality() {
        return marketQuality;
    }
    
private:
    double CalculateProfitPotential() {
        double stoch[];
        ArraySetAsSeries(stoch, true);
        if(CopyBuffer(stochHandle, 0, 0, 1, stoch) > 0) {
            return stoch[0] / 100.0;
        }
        return 0.5;
    }
    
    double CalculateMarketQuality() {
        double stoch[];
        ArraySetAsSeries(stoch, true);
        if(CopyBuffer(stochHandle, 0, 0, 20, stoch) > 0) {
            double sum = 0;
            for(int i = 0; i < 20; i++) {
                sum += MathAbs(50 - stoch[i]);
            }
            return 1.0 - (sum / (20 * 50));
        }
        return 0.5;
    }
    
    double CalculateConfidence() {
        return (profitPotential + marketQuality) / 2;
    }
};

class CSensoryIntegration {
private:
    IntegratedSensoryData currentPerception;
    double sensoryWeights[5];
    
public:
    CSensoryIntegration() {
        ZeroMemory(currentPerception);
        ArrayInitialize(sensoryWeights, 0.2);
    }
    
    void ProcessSensoryInput(CQuantumVisionSystem* vision, CMarketHearingSystem* hearing, 
                           CMarketTouchSystem* touch, CRiskSmellingSystem* smell, 
                           CMarketTasteSystem* taste) {
        currentPerception.visualConfidence = vision.GetConfidence();
        currentPerception.auditoryConfidence = hearing.GetConfidence();
        currentPerception.tactileConfidence = touch.GetConfidence();
        currentPerception.olfactoryConfidence = smell.GetConfidence();
        currentPerception.gustatoryConfidence = taste.GetConfidence();

        double atr = GetMarketVolatility();
        AdjustWeights(atr);

        currentPerception.overallPerception = (
            currentPerception.visualConfidence * sensoryWeights[0] +
            currentPerception.auditoryConfidence * sensoryWeights[1] +
            currentPerception.tactileConfidence * sensoryWeights[2] +
            currentPerception.olfactoryConfidence * sensoryWeights[3] +
            currentPerception.gustatoryConfidence * sensoryWeights[4]
        );

        double confidences[] = {
            currentPerception.visualConfidence, currentPerception.auditoryConfidence,
            currentPerception.tactileConfidence, currentPerception.olfactoryConfidence,
            currentPerception.gustatoryConfidence
        };
        double mean = currentPerception.overallPerception;
        double variance = 0;
        for(int i = 0; i < 5; i++) {
            variance += MathPow(confidences[i] - mean, 2);
        }
        currentPerception.sensoryCoherence = 1.0 - MathSqrt(variance / 10); // Reduzido impacto da variância
    }
    
    IntegratedSensoryData GetCurrentPerception() const {
        return currentPerception;
    }

private:
    double GetMarketVolatility() {
        int atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
        double atr[];
        ArraySetAsSeries(atr, true);
        if(CopyBuffer(atrHandle, 0, 0, 1, atr) > 0) {
            IndicatorRelease(atrHandle);
            return atr[0];
        }
        IndicatorRelease(atrHandle);
        return 0.01;
    }

    void AdjustWeights(double atr) {
        double totalWeight = 0;
        sensoryWeights[0] = 0.3 + (atr * 0.1);
        sensoryWeights[1] = 0.2;
        sensoryWeights[2] = 0.25 + (atr * 0.05);
        sensoryWeights[3] = 0.15 - (atr * 0.05);
        sensoryWeights[4] = 0.15 - (atr * 0.05);
        
        for(int i = 0; i < 5; i++) totalWeight += sensoryWeights[i];
        for(int i = 0; i < 5; i++) sensoryWeights[i] /= totalWeight;
    }
};

class CSensoryOptimizer {
private:
    double bestScore;
    double bestThreshold;

public:
    CSensoryOptimizer() : bestScore(0), bestThreshold(0) {}
    
    bool OptimizeSensorySystem(CSensoryIntegration* system, CQuantumVisionSystem* vision) {
        if(system == NULL || vision == NULL) return false;
        
        bestThreshold = VisionConfig::VolumeThreshold;
        for(double threshold = 1.5; threshold <= 3.5; threshold += 0.5) {
            double score = SimulatePerformance(threshold, vision);
            if(score > bestScore) {
                bestScore = score;
                bestThreshold = threshold;
            }
        }
        VisionConfig::VolumeThreshold = bestThreshold;
        Print("Novo VolumeThreshold otimizado: ", bestThreshold);
        return true;
    }

private:
    double SimulatePerformance(double threshold, CQuantumVisionSystem* vision) {
        vision.ProcessMarketView();
        double successRate = (vision.GetLastVolume() > threshold * vision.GetAverageVolume(20)) ? 1.0 : 0.5;
        return successRate * (1.0 - MathAbs(threshold - VisionConfig::VolumeThreshold));
    }
};

// --- Lógica do EA ---
enum ENUM_TRADING_MODE {
    MODE_CONSERVATIVE = 0,
    MODE_MODERATE = 1,
    MODE_AGGRESSIVE = 2
};

input group "Configurações Gerais"
input ENUM_TRADING_MODE InpTradingMode = MODE_MODERATE;
input ENUM_TIMEFRAMES  InpTimeframe   = PERIOD_M5;
input double          InpLotSize      = 0.1;
input double          InpRiskPercent  = 2.0;
input int             InpMaxDailyLoss = -500;
input int             InpMaxDailyTrades = 10;

input group "Configurações de Proteção"
input bool           InpUseBreakEven   = true;
input int            InpBreakEvenPoints = 100;
input bool           InpUseTrailingStop = true;
input int            InpTrailingPoints  = 50;

CTrade trade;
CQuantumVisionSystem* Vision = NULL;
CMarketHearingSystem* Hearing = NULL;
CMarketTouchSystem* Touch = NULL;
CRiskSmellingSystem* Smell = NULL;
CMarketTasteSystem* Taste = NULL;
CSensoryIntegration* SensorySystem = NULL;
CSensoryOptimizer* Optimizer = NULL;

int dailyTrades = 0;
double dailyProfit = 0;
datetime lastTradeTime = 0;
bool isNewDay = false;

int OnInit() {
    Vision = new CQuantumVisionSystem();
    Hearing = new CMarketHearingSystem();
    Touch = new CMarketTouchSystem();
    Smell = new CRiskSmellingSystem();
    Taste = new CMarketTasteSystem();
    SensorySystem = new CSensoryIntegration();
    Optimizer = new CSensoryOptimizer();
    
    if(!Vision || !Vision.Initialize() || !Hearing || !Hearing.Initialize() ||
       !Touch || !Touch.Initialize() || !Smell || !Smell.Initialize() ||
       !Taste || !Taste.Initialize() || !SensorySystem || !Optimizer) {
        Print("Erro na inicialização do sistema");
        return INIT_FAILED;
    }
    
    trade.SetExpertMagicNumber(123456);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(Symbol());
    
    CreateDashboard();
    Print("Quantum Sensory Trading System iniciado com sucesso");
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    delete Vision;
    delete Hearing;
    delete Touch;
    delete Smell;
    delete Taste;
    delete SensorySystem;
    delete Optimizer;
    ObjectsDeleteAll(0, "Sensory_");
    Print("Quantum Sensory Trading System finalizado");
}

void OnTick() {
    CheckNewTradingDay();
    if(!IsTradeAllowed()) return;
    
    ProcessSensoryInputs();
    AnalyzeMarketConditions();
    ManageOpenPositions();
    UpdateDashboard();
}

void ProcessSensoryInputs() {
    Vision.ProcessMarketView();
    Hearing.ProcessMarketSounds();
    Touch.ProcessMarketTouch();
    Smell.ProcessMarketSmell();
    Taste.ProcessMarketTaste();
    SensorySystem.ProcessSensoryInput(Vision, Hearing, Touch, Smell, Taste);
}

void AnalyzeMarketConditions() {
    IntegratedSensoryData perception = SensorySystem.GetCurrentPerception();
    
    Print("Overall Perception: ", perception.overallPerception, 
          " | Sensory Coherence: ", perception.sensoryCoherence);
    Print("Sensor Values: Visual=", perception.visualConfidence, 
          " Auditory=", perception.auditoryConfidence, 
          " Tactile=", perception.tactileConfidence, 
          " Olfactory=", perception.olfactoryConfidence, 
          " Gustatory=", perception.gustatoryConfidence);
    
    if(perception.overallPerception > GlobalConfig::MinimumConfidence && 
       perception.sensoryCoherence > GlobalConfig::CoherenceThreshold) {
        
        Print("Condições de percepção atendidas");
        if(DetectarFluxoInstitucional()) {
            Print("Fluxo institucional detectado");
            if(IsLongOpportunity(perception)) {
                Print("Oportunidade de compra detectada");
                OpenLongPosition();
            }
            else if(IsShortOpportunity(perception)) {
                Print("Oportunidade de venda detectada");
                OpenShortPosition();
            }
            else {
                Print("Nenhuma oportunidade específica detectada");
            }
        }
        else {
            Print("Fluxo institucional não detectado");
        }
    }
    else {
        Print("Condições de percepção não atendidas");
    }
    
    if(isNewDay) {
        Optimizer.OptimizeSensorySystem(SensorySystem, Vision);
        isNewDay = false;
    }
}

bool DetectarFluxoInstitucional() {
    bool fluxoVisual = Vision.DetectarBlocosPesados();
    bool fluxoAuditivo = Hearing.AnalisarImpulsoForte();
    bool fluxoTatil = Touch.VerificarAbsorcao();
    bool fluxoOlfativo = Smell.AvaliarSentimento();
    bool fluxoGustativo = Taste.AnalisarQualidadeFluxo();
    
    double orderFlow = Vision.AnalyzeOrderFlow();
    double deltaVolume = (Vision.GetLastVolume() - Vision.GetAverageVolume(20)) / Vision.GetAverageVolume(20);
    double marketStress = Smell.GetRiskLevel();

    int confirmations = fluxoVisual + fluxoAuditivo + fluxoTatil + fluxoOlfativo + fluxoGustativo;
    double flowStrength = MathAbs(orderFlow) * (1 + deltaVolume);
    
    Print("Fluxo: Visual=", fluxoVisual, " Auditivo=", fluxoAuditivo, 
          " Tatil=", fluxoTatil, " Olfativo=", fluxoOlfativo, 
          " Gustativo=", fluxoGustativo);
    Print("OrderFlow=", orderFlow, " DeltaVolume=", deltaVolume, 
          " MarketStress=", marketStress, " Confirmations=", confirmations, 
          " FlowStrength=", flowStrength);
    
    return (confirmations >= 1) && (flowStrength > 0.1) && (marketStress < SmellConfig::DangerThreshold);
}

bool IsLongOpportunity(const IntegratedSensoryData& perception) {
    if(perception.visualConfidence < VisionConfig::PatternConfidence) return false;
    if(perception.tactileConfidence < TouchConfig::ResistanceThreshold) return false;
    
    double orderFlow = Vision.AnalyzeOrderFlow();
    double pressure = Touch.GetMarketPressure();
    double noise = Hearing.GetMarketNoise();
    
    Print("Long Check: OrderFlow=", orderFlow, " Pressure=", pressure, " Noise=", noise);
    return (orderFlow > 0 && pressure > 0 && noise < HearingConfig::NoiseThreshold);
}

bool IsShortOpportunity(const IntegratedSensoryData& perception) {
    if(perception.visualConfidence < VisionConfig::PatternConfidence) return false;
    if(perception.tactileConfidence < TouchConfig::ResistanceThreshold) return false;
    
    double orderFlow = Vision.AnalyzeOrderFlow();
    double pressure = Touch.GetMarketPressure();
    double noise = Hearing.GetMarketNoise();
    
    Print("Short Check: OrderFlow=", orderFlow, " Pressure=", pressure, " Noise=", noise);
    return (orderFlow < 0 && pressure < 0 && noise < HearingConfig::NoiseThreshold);
}

void OpenLongPosition() {
    if(dailyTrades >= InpMaxDailyTrades) {
        Print("Limite diário de trades atingido");
        return;
    }
    
    double sl = CalculateStopLoss(true);
    double tp = CalculateTakeProfit(true);
    double lots = CalculateLotSize(sl);
    
    if(trade.Buy(lots, Symbol(), 0, sl, tp, "Quantum Sensory Long")) {
        dailyTrades++;
        lastTradeTime = TimeCurrent();
        Print("Compra aberta: Lote=", lots, " SL=", sl, " TP=", tp);
    } else {
        Print("Falha ao abrir compra: Erro=", GetLastError());
    }
}

void OpenShortPosition() {
    if(dailyTrades >= InpMaxDailyTrades) {
        Print("Limite diário de trades atingido");
        return;
    }
    
    double sl = CalculateStopLoss(false);
    double tp = CalculateTakeProfit(false);
    double lots = CalculateLotSize(sl);
    
    if(trade.Sell(lots, Symbol(), 0, sl, tp, "Quantum Sensory Short")) {
        dailyTrades++;
        lastTradeTime = TimeCurrent();
        Print("Venda aberta: Lote=", lots, " SL=", sl, " TP=", tp);
    } else {
        Print("Falha ao abrir venda: Erro=", GetLastError());
    }
}

double CalculateLotSize(double stopLoss) {
    double riskAmount = AccountInfoDouble(ACCOUNT_BALANCE) * InpRiskPercent / 100;
    double tickValue = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_SIZE);
    
    double stopPoints = MathAbs(stopLoss - SymbolInfoDouble(Symbol(), SYMBOL_ASK)) / tickSize;
    if(stopPoints == 0) return InpLotSize;
    double lots = NormalizeDouble(riskAmount / (stopPoints * tickValue), 2);
    lots = MathMin(lots, SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX));
    lots = MathMax(lots, SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN));
    
    return NormalizeDouble(lots, 2);
}

double CalculateStopLoss(bool isLong) {
    int atrHandle = iATR(Symbol(), PERIOD_CURRENT, 14);
    double atrBuffer[];
    ArraySetAsSeries(atrBuffer, true);
    if(CopyBuffer(atrHandle, 0, 0, 1, atrBuffer) <= 0) {
        IndicatorRelease(atrHandle);
        return 0;
    }
    double atr = atrBuffer[0];
    IndicatorRelease(atrHandle);
    
    double multiplier = Smell.GetRiskLevel();
    if(isLong) {
        return SymbolInfoDouble(Symbol(), SYMBOL_BID) - (atr * multiplier);
    } else {
        return SymbolInfoDouble(Symbol(), SYMBOL_ASK) + (atr * multiplier);
    }
}

double CalculateTakeProfit(bool isLong) {
    int atrHandle = iATR(Symbol(), PERIOD_CURRENT, 14);
    double atrBuffer[];
    ArraySetAsSeries(atrBuffer, true);
    if(CopyBuffer(atrHandle, 0, 0, 1, atrBuffer) <= 0) {
        IndicatorRelease(atrHandle);
        return 0;
    }
    double atr = atrBuffer[0];
    IndicatorRelease(atrHandle);
    
    double multiplier = Taste.GetMarketQuality() * 2;
    if(isLong) {
        return SymbolInfoDouble(Symbol(), SYMBOL_ASK) + (atr * multiplier);
    } else {
        return SymbolInfoDouble(Symbol(), SYMBOL_BID) - (atr * multiplier);
    }
}

void ManageOpenPositions() {
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(ticket <= 0) continue;
        
        if(InpUseBreakEven) CheckBreakEven(ticket);
        if(InpUseTrailingStop) UpdateTrailingStop(ticket);
    }
}

void CheckBreakEven(ulong ticket) {
    if(!PositionSelectByTicket(ticket)) return;
    
    double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
    double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
    double stopLoss = PositionGetDouble(POSITION_SL);
    
    if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
        if(currentPrice >= openPrice + InpBreakEvenPoints * Point()) {
            if(stopLoss < openPrice) {
                trade.PositionModify(ticket, openPrice, PositionGetDouble(POSITION_TP));
            }
        }
    } else {
        if(currentPrice <= openPrice - InpBreakEvenPoints * Point()) {
            if(stopLoss > openPrice) {
                trade.PositionModify(ticket, openPrice, PositionGetDouble(POSITION_TP));
            }
        }
    }
}

void UpdateTrailingStop(ulong ticket) {
    if(!PositionSelectByTicket(ticket)) return;
    
    double stopLoss = PositionGetDouble(POSITION_SL);
    double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
    
    if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
        double newStopLoss = currentPrice - InpTrailingPoints * Point();
        if(newStopLoss > stopLoss) {
            trade.PositionModify(ticket, newStopLoss, PositionGetDouble(POSITION_TP));
        }
    } else {
        double newStopLoss = currentPrice + InpTrailingPoints * Point();
        if(newStopLoss < stopLoss || stopLoss == 0) {
            trade.PositionModify(ticket, newStopLoss, PositionGetDouble(POSITION_TP));
        }
    }
}

void CheckNewTradingDay() {
    MqlDateTime now;
    TimeToStruct(TimeCurrent(), now);
    static int lastDay = -1;
    if(lastDay != now.day) {
        lastDay = now.day;
        dailyTrades = 0;
        dailyProfit = 0;
        isNewDay = true;
    }
}

bool IsTradeAllowed() {
    if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) {
        Print("Trading não permitido pelo terminal");
        return false;
    }
    if(!MQLInfoInteger(MQL_TRADE_ALLOWED)) {
        Print("Trading não permitido pelo MQL");
        return false;
    }
    if(dailyTrades >= InpMaxDailyTrades) {
        Print("Limite diário de trades atingido");
        return false;
    }
    if(dailyProfit <= InpMaxDailyLoss) {
        Print("Limite diário de perda atingido");
        return false;
    }
    return true;
}

void CreateDashboard() {
    CreateLabel("Sensory_Status", "Sistema Sensorial: Ativo", 10, 10);
    CreateLabel("Sensory_Visual", "Visão: 0.00", 10, 30);
    CreateLabel("Sensory_Hearing", "Audição: 0.00", 10, 50);
    CreateLabel("Sensory_Touch", "Tato: 0.00", 10, 70);
    CreateLabel("Sensory_Smell", "Olfato: 0.00", 10, 90);
    CreateLabel("Sensory_Taste", "Paladar: 0.00", 10, 110);
    CreateLabel("Sensory_Integration", "Integração: 0.00", 10, 130);
}

void CreateLabel(string name, string text, int x, int y) {
    ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
    ObjectSetString(0, name, OBJPROP_TEXT, text);
    ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
    ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
    ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
    ObjectSetInteger(0, name, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
}

void UpdateDashboard() {
    IntegratedSensoryData perception = SensorySystem.GetCurrentPerception();
    
    ObjectSetString(0, "Sensory_Visual", OBJPROP_TEXT, 
        "Visão: " + DoubleToString(Vision.GetConfidence(), 2));
    ObjectSetString(0, "Sensory_Hearing", OBJPROP_TEXT, 
        "Audição: " + DoubleToString(Hearing.GetConfidence(), 2));
    ObjectSetString(0, "Sensory_Touch", OBJPROP_TEXT, 
        "Tato: " + DoubleToString(Touch.GetConfidence(), 2));
    ObjectSetString(0, "Sensory_Smell", OBJPROP_TEXT, 
        "Olfato: " + DoubleToString(Smell.GetConfidence(), 2));
    ObjectSetString(0, "Sensory_Taste", OBJPROP_TEXT, 
        "Paladar: " + DoubleToString(Taste.GetConfidence(), 2));
    ObjectSetString(0, "Sensory_Integration", OBJPROP_TEXT, 
        "Integração: " + DoubleToString(perception.overallPerception, 2));
}