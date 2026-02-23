//+------------------------------------------------------------------+
//|                      Gravitational Sphere Module                    |
//|                      Copyright 2024, Quantum Sensory                |
//|                      https://www.quantumsensory.com                |
//+------------------------------------------------------------------+
#property copyright "Quantum Sensory Trading System - Enhanced with Apollo11"
#property link      "https://www.quantumsensory.com"
#property version   "4.7"
#property strict

//+------------------------------------------------------------------+
//| Estrutura do Canal Dimensional                                    |
//+------------------------------------------------------------------+
struct DimensionalChannel {
    double top;          // Topo do canal
    double bottom;       // Fundo do canal
    double poc;          // Point of Control
    double node;         // Nó do Market Profile
    double energy;       // Energia do canal
    datetime startTime;  // Início do canal
    datetime endTime;    // Fim do canal
};

//+------------------------------------------------------------------+
//| Estrutura da Linha Gravitacional                                  |
//+------------------------------------------------------------------+
struct GravitationalLine {
    double startPrice;   // Preço inicial
    double endPrice;     // Preço final
    datetime startTime;  // Tempo inicial
    datetime endTime;    // Tempo final
    double force;        // Força da linha
    double angle;        // Ângulo da linha
};

//+------------------------------------------------------------------+
//| Gravitational Sphere Class                                         |
//+------------------------------------------------------------------+
class CGravitationalSphere {
private:
    double volumeForce;
    double gravForce;
    double sphereEnergy;
    double sphereEnergyLast;
    double POC;
    int rotationFactor;
    datetime lastTime;
    datetime lastResetTime;
    int plotCounter;
    
    // ATR handles for different timeframes
    int atr41Handle;
    int atr20Handle;
    int atrW1Handle;
    int atrM1Handle;
    
    // ATR arrays
    double ATR41[];
    double ATR20[];
    double ATRW1[];
    double ATRM1[];
    
    // Channel levels
    double monthlyHigh;
    double monthlyLow;
    double weeklyHigh;
    double weeklyLow;
    
    // Configuration
    string resetInterval;
    
    // Big Player Detection
    double volumeThreshold;
    double priceImpactThreshold;
    int lookbackPeriod;
    double lastBigPlayerVolume;
    datetime lastBigPlayerTime;
    
    // Canal Dimensional
    DimensionalChannel currentChannel;
    DimensionalChannel previousChannel;
    GravitationalLine currentLine;
    GravitationalLine previousLine;
    
    // Configuração do Canal
    int channelPeriod;           // Período para formação do canal
    double channelDeviation;     // Desvio permitido para o canal
    double minChannelWidth;      // Largura mínima do canal
    
public:
    CGravitationalSphere() {
        volumeForce = 0.0;
        gravForce = 0.0;
        sphereEnergy = 0.0;
        sphereEnergyLast = 0.0;
        POC = 0.0;
        rotationFactor = 0;
        lastTime = 0;
        lastResetTime = 0;
        plotCounter = 0;
        resetInterval = "D1";
        
        // Big Player Detection Parameters
        volumeThreshold = 2.5;      // Volume 2.5x maior que a média
        priceImpactThreshold = 0.1; // Impacto de 0.1% no preço
        lookbackPeriod = 20;        // Período de análise
        lastBigPlayerVolume = 0.0;
        lastBigPlayerTime = 0;
        
        // Initialize ATR handles
        atr41Handle = iATR(_Symbol, PERIOD_CURRENT, 41);
        atr20Handle = iATR(_Symbol, PERIOD_CURRENT, 20);
        atrW1Handle = iATR(_Symbol, PERIOD_W1, 41);
        atrM1Handle = iATR(_Symbol, PERIOD_M1, 41);
        
        // Set arrays as series
        ArraySetAsSeries(ATR41, true);
        ArraySetAsSeries(ATR20, true);
        ArraySetAsSeries(ATRW1, true);
        ArraySetAsSeries(ATRM1, true);
        
        // Inicialização do Canal
        channelPeriod = 20;      // 20 períodos para formação do canal
        channelDeviation = 0.002; // 0.2% de desvio
        minChannelWidth = 0.001;  // 0.1% de largura mínima
        
        // Inicialização das estruturas
        currentChannel = {};
        previousChannel = {};
        currentLine = {};
        previousLine = {};
    }
    
    ~CGravitationalSphere() {
        // Release ATR handles
        if(atr41Handle != INVALID_HANDLE) IndicatorRelease(atr41Handle);
        if(atr20Handle != INVALID_HANDLE) IndicatorRelease(atr20Handle);
        if(atrW1Handle != INVALID_HANDLE) IndicatorRelease(atrW1Handle);
        if(atrM1Handle != INVALID_HANDLE) IndicatorRelease(atrM1Handle);
        
        // Clean up objects
        ObjectsDeleteAll(0, "GravChannel_");
        ObjectsDeleteAll(0, "SphereEnergy_");
        ObjectsDeleteAll(0, "GravPulse_");
    }
    
    bool Initialize() {
        if(atr41Handle == INVALID_HANDLE || atr20Handle == INVALID_HANDLE || 
           atrW1Handle == INVALID_HANDLE || atrM1Handle == INVALID_HANDLE) {
            Print("Erro ao inicializar indicadores ATR");
            return false;
        }
        return true;
    }
    
    void Update() {
        UpdateMarketData();
        DetectBigPlayerActivity();
        CalculatePhysics();
        UpdateRotationFactor();
        UpdateChannel();
        
        plotCounter++;
        if(plotCounter % 5 == 0) {
            double poc = POC;
            TraceReferenceLines(poc);
            PlotSphereEnergy(sphereEnergy);
            PlotGravitationalPulse();
        }
    }
    
    double GetGravitationalForce() const { return gravForce; }
    double GetSphereEnergy() const { return sphereEnergy; }
    double GetPOC() const { return POC; }
    int GetRotationFactor() const { return rotationFactor; }
    
    void UpdateChannel() {
        // Atualiza o canal dimensional
        UpdateChannelLevels();
        UpdateGravitationalLines();
        PlotChannel();
    }
    
private:
    void UpdateMarketData() {
        long volumeArray[];
        ArraySetAsSeries(volumeArray, true);
        if(CopyTickVolume(_Symbol, 0, 0, lookbackPeriod, volumeArray) > 0) {
            double volumeAvg = 0;
            for(int i = 0; i < lookbackPeriod; i++) volumeAvg += (double)volumeArray[i];
            volumeAvg /= lookbackPeriod;
            double currentVolume = (double)volumeArray[0];
            volumeForce = currentVolume / volumeAvg;
            
            // Ajuste dinâmico do threshold baseado na volatilidade
            double atr[];
            ArraySetAsSeries(atr, true);
            int atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
            if(CopyBuffer(atrHandle, 0, 0, 1, atr) > 0) {
                double volatilityFactor = atr[0] / ATR20[0];
                volumeThreshold = 2.5 * volatilityFactor;
                IndicatorRelease(atrHandle);
            }
            
            Print("volumeForce atualizado: ", volumeForce, " Threshold: ", volumeThreshold);
        } else {
            Print("Erro ao copiar volume de ticks em UpdateMarketData: ", GetLastError());
        }
    }
    
    void DetectBigPlayerActivity() {
        if(volumeForce > volumeThreshold) {
            double priceImpact = MathAbs(iClose(_Symbol, PERIOD_CURRENT, 0) - iClose(_Symbol, PERIOD_CURRENT, 1)) / iClose(_Symbol, PERIOD_CURRENT, 1);
            
            if(priceImpact > priceImpactThreshold) {
                lastBigPlayerVolume = volumeForce;
                lastBigPlayerTime = TimeCurrent();
                
                // Ajusta a força gravitacional baseado na atividade do Big Player
                gravForce *= 1.5;
                sphereEnergy *= 1.2;
                
                Print("Big Player detectado! Volume: ", volumeForce, " Impacto: ", priceImpact);
                PlotBigPlayerActivity();
            }
        }
    }
    
    void CalculatePhysics() {
        // Cálculo base da força gravitacional
        double baseForce = volumeForce * (rotationFactor != 0 ? MathAbs(rotationFactor) * 1000 : 1000);
        
        // Ajuste baseado na atividade recente de Big Players
        if(TimeCurrent() - lastBigPlayerTime < 3600) { // Última hora
            baseForce *= 1.2;
        }
        
        // Ajuste baseado na volatilidade
        double volatilityFactor = ATR20[0] / ATR41[0];
        gravForce = baseForce * volatilityFactor;
        
        // Cálculo da energia da esfera
        sphereEnergy = volumeForce * 2.0 * (1 + MathAbs(rotationFactor) * 0.1);
        POC = iClose(_Symbol, PERIOD_CURRENT, 1);
        
        Print("Physics: gravForce=", gravForce, " sphereEnergy=", sphereEnergy, " VolatilityFactor=", volatilityFactor);
    }
    
    void UpdateRotationFactor() {
        datetime currentResetTime = iTime(_Symbol, StringToPeriod(resetInterval), 0);
        if(currentResetTime == 0) {
            Print("Erro ao obter tempo para reset em UpdateRotationFactor: ", GetLastError());
            return;
        }
        bool reset = currentResetTime != lastResetTime;
        lastResetTime = currentResetTime;

        double high = iHigh(_Symbol, PERIOD_CURRENT, 0);
        double low = iLow(_Symbol, PERIOD_CURRENT, 0);
        double highPrev = iHigh(_Symbol, PERIOD_CURRENT, 1);
        double lowPrev = iLow(_Symbol, PERIOD_CURRENT, 1);

        int one = (high > highPrev && low > lowPrev) ? 2 : 0;
        int two = (high < highPrev && low < lowPrev) ? -2 : 0;
        int three = (high > highPrev && low < lowPrev) ? 0 : 0;
        int four = (high < highPrev && low > lowPrev) ? 0 : 0;
        int five = (high == highPrev && low > lowPrev) ? 1 : 0;
        int six = (high > highPrev && low == lowPrev) ? 1 : 0;
        int seven = (high < highPrev && low == lowPrev) ? -1 : 0;
        int eight = (high == highPrev && low < lowPrev) ? -1 : 0;

        if (reset) rotationFactor = one + two + three + four + five + six + seven + eight;
        else rotationFactor += one + two + three + four + five + six + seven + eight;

        Print("Rotation Factor atualizado: ", rotationFactor);
    }
    
    void TraceReferenceLines(double pocLevel) {
        double range = ATRW1[0];
        string nameTop = "GravChannel_Top_" + DoubleToString(pocLevel, 5);
        string nameBottom = "GravChannel_Bottom_" + DoubleToString(pocLevel, 5);
        if (ObjectFind(0, nameTop) < 0) {
            ObjectCreate(0, nameTop, OBJ_HLINE, 0, 0, weeklyHigh);
            ObjectCreate(0, nameBottom, OBJ_HLINE, 0, 0, weeklyLow);
            ObjectSetInteger(0, nameTop, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, nameBottom, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, nameTop, OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, nameBottom, OBJPROP_STYLE, STYLE_DASH);
            string label = "POC_" + DoubleToString(pocLevel, 5);
            ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), pocLevel);
            ObjectSetString(0, label, OBJPROP_TEXT, "POC: " + DoubleToString(pocLevel, 5));
            ObjectSetInteger(0, label, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
            Print("Canal Gravitacional: ", pocLevel);
        }
    }
    
    void PlotSphereEnergy(double energy) {
        if (TimeCurrent() != lastTime) {
            string name = "SphereEnergy_" + TimeToString(TimeCurrent());
            ObjectCreate(0, name, OBJ_TREND, 0, lastTime, sphereEnergyLast, TimeCurrent(), energy);
            ObjectSetInteger(0, name, OBJPROP_COLOR, clrBlue);
            string label = "Energy_" + TimeToString(TimeCurrent());
            ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), energy);
            ObjectSetString(0, label, OBJPROP_TEXT, "Energia: " + DoubleToString(energy, 2));
            ObjectSetInteger(0, label, OBJPROP_COLOR, clrBlue);
            ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
            lastTime = TimeCurrent();
            sphereEnergyLast = energy;
            Print("Energia plotada: ", energy);
        }
    }
    
    void PlotGravitationalPulse() {
        if (gravForce > 500) {
            string name = "GravPulse_" + TimeToString(TimeCurrent());
            if (ObjectFind(0, name) < 0) {
                ObjectCreate(0, name, OBJ_VLINE, 0, TimeCurrent(), 0);
                ObjectSetInteger(0, name, OBJPROP_COLOR, clrRed);
                string label = "Pulse_" + TimeToString(TimeCurrent());
                ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), iHigh(_Symbol, PERIOD_CURRENT, 0));
                ObjectSetString(0, label, OBJPROP_TEXT, "Força: " + DoubleToString(gravForce / 1000, 2) + "G");
                ObjectSetInteger(0, label, OBJPROP_COLOR, clrRed);
                ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
                Print("Pulso Gravitacional: ", gravForce);
            }
        }
    }
    
    void PlotBigPlayerActivity() {
        string name = "BigPlayer_" + TimeToString(TimeCurrent());
        if(ObjectFind(0, name) < 0) {
            ObjectCreate(0, name, OBJ_ARROW_BUY, 0, TimeCurrent(), iLow(_Symbol, PERIOD_CURRENT, 0));
            ObjectSetInteger(0, name, OBJPROP_COLOR, clrGreen);
            ObjectSetInteger(0, name, OBJPROP_ARROWCODE, 233);
            ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
            
            string label = "BP_" + TimeToString(TimeCurrent());
            ObjectCreate(0, label, OBJ_TEXT, 0, TimeCurrent(), iLow(_Symbol, PERIOD_CURRENT, 0));
            ObjectSetString(0, label, OBJPROP_TEXT, "BP: " + DoubleToString(volumeForce, 1) + "x");
            ObjectSetInteger(0, label, OBJPROP_COLOR, clrGreen);
            ObjectSetInteger(0, label, OBJPROP_FONTSIZE, 8);
        }
    }
    
    void UpdateChannelLevels() {
        // Calcula os níveis do canal
        double highs[], lows[];
        ArraySetAsSeries(highs, true);
        ArraySetAsSeries(lows, true);
        
        if(CopyHigh(_Symbol, PERIOD_CURRENT, 0, channelPeriod, highs) > 0 &&
           CopyLow(_Symbol, PERIOD_CURRENT, 0, channelPeriod, lows) > 0) {
            
            // Encontra topo e fundo
            currentChannel.top = highs[ArrayMaximum(highs)];
            currentChannel.bottom = lows[ArrayMinimum(lows)];
            
            // Calcula POC (preço médio)
            currentChannel.poc = (currentChannel.top + currentChannel.bottom) / 2;
            
            // Calcula nó do Market Profile
            currentChannel.node = CalculateMarketProfileNode();
            
            // Atualiza energia do canal
            currentChannel.energy = CalculateChannelEnergy();
            
            // Atualiza tempos
            currentChannel.startTime = iTime(_Symbol, PERIOD_CURRENT, channelPeriod-1);
            currentChannel.endTime = TimeCurrent();
        }
    }
    
    void UpdateGravitationalLines() {
        // Atualiza as linhas gravitacionais
        if(previousChannel.top != 0 && previousChannel.bottom != 0) {
            // Cria linha do topo anterior ao topo atual
            currentLine.startPrice = previousChannel.top;
            currentLine.endPrice = currentChannel.top;
            currentLine.startTime = previousChannel.endTime;
            currentLine.endTime = currentChannel.endTime;
            currentLine.force = CalculateLineForce();
            currentLine.angle = CalculateLineAngle();
        }
    }
    
    void PlotChannel() {
        // Plota o canal dimensional
        string channelName = "DimensionalChannel_" + TimeToString(TimeCurrent());
        if(ObjectFind(0, channelName) < 0) {
            // Linhas do canal
            ObjectCreate(0, channelName + "_Top", OBJ_TREND, 0, 
                        currentChannel.startTime, currentChannel.top,
                        currentChannel.endTime, currentChannel.top);
            ObjectCreate(0, channelName + "_Bottom", OBJ_TREND, 0,
                        currentChannel.startTime, currentChannel.bottom,
                        currentChannel.endTime, currentChannel.bottom);
            
            // POC
            ObjectCreate(0, channelName + "_POC", OBJ_TREND, 0,
                        currentChannel.startTime, currentChannel.poc,
                        currentChannel.endTime, currentChannel.poc);
            
            // Configuração visual
            ObjectSetInteger(0, channelName + "_Top", OBJPROP_COLOR, clrBlue);
            ObjectSetInteger(0, channelName + "_Bottom", OBJPROP_COLOR, clrBlue);
            ObjectSetInteger(0, channelName + "_POC", OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, channelName + "_Top", OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, channelName + "_Bottom", OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, channelName + "_POC", OBJPROP_STYLE, STYLE_SOLID);
        }
    }
    
    double CalculateMarketProfileNode() {
        // Implementação do cálculo do nó do Market Profile
        // TODO: Implementar lógica específica
        return currentChannel.poc;
    }
    
    double CalculateChannelEnergy() {
        // Calcula a energia do canal baseado na largura e força gravitacional
        double width = currentChannel.top - currentChannel.bottom;
        return (width / _Point) * gravForce;
    }
    
    double CalculateLineForce() {
        // Calcula a força da linha gravitacional
        double priceChange = currentLine.endPrice - currentLine.startPrice;
        double timeChange = (double)(currentLine.endTime - currentLine.startTime) / PeriodSeconds(PERIOD_CURRENT);
        return MathAbs(priceChange / timeChange) * volumeForce;
    }
    
    double CalculateLineAngle() {
        // Calcula o ângulo da linha gravitacional
        double priceChange = currentLine.endPrice - currentLine.startPrice;
        double timeChange = (double)(currentLine.endTime - currentLine.startTime) / PeriodSeconds(PERIOD_CURRENT);
        return MathArctan(priceChange / timeChange) * 180 / M_PI;
    }
    
    ENUM_TIMEFRAMES StringToPeriod(string timeframeStr) {
        if(timeframeStr == "D1") return PERIOD_D1;
        if(timeframeStr == "H4") return PERIOD_H4;
        if(timeframeStr == "H1") return PERIOD_H1;
        if(timeframeStr == "M15") return PERIOD_M15;
        if(timeframeStr == "M5") return PERIOD_M5;
        if(timeframeStr == "M1") return PERIOD_M1;
        return PERIOD_CURRENT;
    }
}; 