#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para partícula de preço
struct PriceParticle {
    string   symbol;
    datetime timestamp;
    double   price;
    double   velocity;      // Velocidade de mudança
    double   acceleration;  // Aceleração da mudança
    double   momentum;      // Momentum do movimento
    double   energy;        // Energia cinética
};

// Estrutura para difusão de preço
struct PriceDiffusion {
    string   symbol;
    datetime startTime;
    datetime endTime;
    double   startPrice;
    double   endPrice;
    double   meanPath;      // Caminho médio
    double   variance;      // Variância do movimento
    double   drift;         // Tendência
    double   diffusion;     // Coeficiente de difusão
};

// Estrutura para configuração do sistema
struct BrownianConfig {
    int      historyPeriod;     // Períodos para análise histórica
    int      diffusionPeriod;   // Períodos para cálculo de difusão
    double   noiseThreshold;    // Limite para filtrar ruído (0-1)
    double   driftThreshold;    // Limite para detectar tendência
    bool     useKalmanFilter;   // Usar filtro de Kalman
    bool     useWienerProcess;  // Usar processo de Wiener
};

//+------------------------------------------------------------------+
//| Classe BrownianMarketSystem                                        |
//+------------------------------------------------------------------+
class CBrownianMarketSystem {
private:
    // Componentes principais
    CQuantumCore*    m_core;
    BrownianConfig   m_config;
    
    // Cache de dados
    PriceParticle    m_particles[];
    PriceDiffusion   m_diffusions[];
    
    // Estado do sistema
    bool             m_isInitialized;
    datetime         m_lastUpdate;
    
    // Configurações
    int              m_maxParticles;
    int              m_maxDiffusions;
    
    // Filtro de Kalman
    double           m_kalmanGain;
    double           m_estimateError;
    double           m_measurementNoise;
    
    // Métodos privados
    void             UpdateParticles(string symbol);
    void             UpdateDiffusion(string symbol);
    double           CalculateVelocity(double price1, double price2, int timeDiff);
    double           CalculateAcceleration(double vel1, double vel2, int timeDiff);
    double           CalculateMomentum(double velocity, double price);
    double           CalculateEnergy(double velocity, double price);
    double           ApplyKalmanFilter(double measurement, double &estimate);
    double           CalculateWienerProcess(double drift, double diffusion, double timeStep);
    void             CleanupOldData();
    
public:
                     CBrownianMarketSystem();
                    ~CBrownianMarketSystem();
    
    // Métodos principais
    bool             Initialize(CQuantumCore* core);
    bool             Update();
    
    // Métodos de análise
    bool             AnalyzeParticle(string symbol, PriceParticle &particle);
    bool             AnalyzeDiffusion(string symbol, PriceDiffusion &diffusion);
    bool             PredictNextMove(string symbol, double &prediction, double &probability);
    
    // Métodos de consulta
    PriceParticle   *GetLatestParticle(string symbol);
    PriceDiffusion  *GetLatestDiffusion(string symbol);
    double           GetDiffusionCoefficient(string symbol);
    double           GetDriftCoefficient(string symbol);
    
    // Configuração
    void             SetConfig(const BrownianConfig &config);
    BrownianConfig   GetConfig() const { return m_config; }
    bool             IsInitialized() const { return m_isInitialized; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CBrownianMarketSystem::CBrownianMarketSystem() {
    m_core = NULL;
    m_isInitialized = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_config.historyPeriod = 1000;
    m_config.diffusionPeriod = 100;
    m_config.noiseThreshold = 0.1;
    m_config.driftThreshold = 0.001;
    m_config.useKalmanFilter = true;
    m_config.useWienerProcess = true;
    
    m_maxParticles = 5000;
    m_maxDiffusions = 1000;
    
    // Configurações do filtro de Kalman
    m_kalmanGain = 0.0;
    m_estimateError = 1.0;
    m_measurementNoise = 0.1;
    
    ArrayResize(m_particles, 0);
    ArrayResize(m_diffusions, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CBrownianMarketSystem::~CBrownianMarketSystem() {
    ArrayFree(m_particles);
    ArrayFree(m_diffusions);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CBrownianMarketSystem::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isInitialized = true;
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CBrownianMarketSystem::Update() {
    if(!m_isInitialized || !m_core) return false;
    
    string symbols[];
    m_core.GetSymbols(symbols);
    
    for(int i = 0; i < ArraySize(symbols); i++) {
        UpdateParticles(symbols[i]);
        UpdateDiffusion(symbols[i]);
    }
    
    CleanupOldData();
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza partículas                                               |
//+------------------------------------------------------------------+
void CBrownianMarketSystem::UpdateParticles(string symbol) {
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) return;
    
    // Cria nova partícula
    PriceParticle particle;
    if(!AnalyzeParticle(symbol, particle)) return;
    
    // Adiciona ao array
    int size = ArraySize(m_particles);
    ArrayResize(m_particles, size + 1);
    m_particles[size] = particle;
}

//+------------------------------------------------------------------+
//| Atualiza difusão                                                  |
//+------------------------------------------------------------------+
void CBrownianMarketSystem::UpdateDiffusion(string symbol) {
    // Cria nova análise de difusão
    PriceDiffusion diffusion;
    if(!AnalyzeDiffusion(symbol, diffusion)) return;
    
    // Adiciona ao array
    int size = ArraySize(m_diffusions);
    ArrayResize(m_diffusions, size + 1);
    m_diffusions[size] = diffusion;
}

//+------------------------------------------------------------------+
//| Analisa partícula                                                 |
//+------------------------------------------------------------------+
bool CBrownianMarketSystem::AnalyzeParticle(
    string symbol,
    PriceParticle &particle
) {
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) return false;
    
    // Obtém partícula anterior
    PriceParticle* prev = GetLatestParticle(symbol);
    
    // Preenche dados da partícula
    particle.symbol = symbol;
    particle.timestamp = tick.time;
    particle.price = tick.last;
    
    if(prev != NULL) {
        int timeDiff = (int)(particle.timestamp - prev.timestamp);
        if(timeDiff > 0) {
            particle.velocity = CalculateVelocity(prev.price, particle.price, timeDiff);
            particle.acceleration = CalculateAcceleration(prev.velocity, particle.velocity, timeDiff);
            particle.momentum = CalculateMomentum(particle.velocity, particle.price);
            particle.energy = CalculateEnergy(particle.velocity, particle.price);
            
            // Aplica filtro de Kalman se configurado
            if(m_config.useKalmanFilter) {
                double estimate = prev.price;
                particle.price = ApplyKalmanFilter(particle.price, estimate);
            }
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Analisa difusão                                                   |
//+------------------------------------------------------------------+
bool CBrownianMarketSystem::AnalyzeDiffusion(
    string symbol,
    PriceDiffusion &diffusion
) {
    // Obtém dados históricos
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, m_config.diffusionPeriod, rates);
    if(copied != m_config.diffusionPeriod) return false;
    
    // Preenche dados básicos
    diffusion.symbol = symbol;
    diffusion.startTime = rates[copied-1].time;
    diffusion.endTime = rates[0].time;
    diffusion.startPrice = rates[copied-1].close;
    diffusion.endPrice = rates[0].close;
    
    // Calcula caminho médio
    double sumPath = 0;
    for(int i = 1; i < copied; i++) {
        sumPath += MathAbs(rates[i].close - rates[i-1].close);
    }
    diffusion.meanPath = sumPath / (copied - 1);
    
    // Calcula variância
    double sumSquares = 0;
    double mean = (diffusion.endPrice - diffusion.startPrice) / copied;
    
    for(int i = 1; i < copied; i++) {
        double diff = (rates[i].close - rates[i-1].close) - mean;
        sumSquares += diff * diff;
    }
    diffusion.variance = sumSquares / (copied - 1);
    
    // Calcula drift (tendência)
    diffusion.drift = (diffusion.endPrice - diffusion.startPrice) / copied;
    
    // Calcula coeficiente de difusão
    diffusion.diffusion = diffusion.variance / (2 * copied);
    
    return true;
}

//+------------------------------------------------------------------+
//| Prediz próximo movimento                                          |
//+------------------------------------------------------------------+
bool CBrownianMarketSystem::PredictNextMove(
    string symbol,
    double &prediction,
    double &probability
) {
    PriceDiffusion* diff = GetLatestDiffusion(symbol);
    if(diff == NULL) return false;
    
    // Obtém última partícula
    PriceParticle* particle = GetLatestParticle(symbol);
    if(particle == NULL) return false;
    
    // Calcula previsão usando processo de Wiener se configurado
    if(m_config.useWienerProcess) {
        double timeStep = 1.0;  // Um período à frente
        double wienerComponent = CalculateWienerProcess(
            diff.drift,
            diff.diffusion,
            timeStep
        );
        
        prediction = particle.price + wienerComponent;
        
        // Calcula probabilidade baseada na distribuição normal
        double stdDev = MathSqrt(diff.variance);
        double zScore = MathAbs(wienerComponent) / (stdDev * MathSqrt(timeStep));
        probability = 1.0 - NormalCDF(zScore);
    }
    else {
        // Previsão simples baseada em momentum
        prediction = particle.price + particle.velocity + 
                    (particle.acceleration * 0.5);
        probability = 0.5;  // Probabilidade neutra
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém última partícula                                            |
//+------------------------------------------------------------------+
PriceParticle* CBrownianMarketSystem::GetLatestParticle(string symbol) {
    for(int i = ArraySize(m_particles) - 1; i >= 0; i--) {
        if(m_particles[i].symbol == symbol) {
            return &m_particles[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém última difusão                                              |
//+------------------------------------------------------------------+
PriceDiffusion* CBrownianMarketSystem::GetLatestDiffusion(string symbol) {
    for(int i = ArraySize(m_diffusions) - 1; i >= 0; i--) {
        if(m_diffusions[i].symbol == symbol) {
            return &m_diffusions[i];
        }
    }
    return NULL;
}

//+------------------------------------------------------------------+
//| Obtém coeficiente de difusão                                      |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::GetDiffusionCoefficient(string symbol) {
    PriceDiffusion* diff = GetLatestDiffusion(symbol);
    if(diff != NULL) {
        return diff.diffusion;
    }
    return 0.0;
}

//+------------------------------------------------------------------+
//| Obtém coeficiente de drift                                        |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::GetDriftCoefficient(string symbol) {
    PriceDiffusion* diff = GetLatestDiffusion(symbol);
    if(diff != NULL) {
        return diff.drift;
    }
    return 0.0;
}

//+------------------------------------------------------------------+
//| Define configuração                                               |
//+------------------------------------------------------------------+
void CBrownianMarketSystem::SetConfig(const BrownianConfig &config) {
    m_config = config;
}

//+------------------------------------------------------------------+
//| Calcula velocidade                                                |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::CalculateVelocity(
    double price1,
    double price2,
    int timeDiff
) {
    if(timeDiff <= 0) return 0.0;
    return (price2 - price1) / timeDiff;
}

//+------------------------------------------------------------------+
//| Calcula aceleração                                               |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::CalculateAcceleration(
    double vel1,
    double vel2,
    int timeDiff
) {
    if(timeDiff <= 0) return 0.0;
    return (vel2 - vel1) / timeDiff;
}

//+------------------------------------------------------------------+
//| Calcula momentum                                                  |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::CalculateMomentum(
    double velocity,
    double price
) {
    return velocity * price;
}

//+------------------------------------------------------------------+
//| Calcula energia                                                   |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::CalculateEnergy(
    double velocity,
    double price
) {
    return 0.5 * price * velocity * velocity;
}

//+------------------------------------------------------------------+
//| Aplica filtro de Kalman                                          |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::ApplyKalmanFilter(
    double measurement,
    double &estimate
) {
    // Predição
    double predictedEstimate = estimate;
    double predictedError = m_estimateError + m_measurementNoise;
    
    // Atualização
    m_kalmanGain = predictedError / (predictedError + m_measurementNoise);
    estimate = predictedEstimate + m_kalmanGain * (measurement - predictedEstimate);
    m_estimateError = (1 - m_kalmanGain) * predictedError;
    
    return estimate;
}

//+------------------------------------------------------------------+
//| Calcula processo de Wiener                                        |
//+------------------------------------------------------------------+
double CBrownianMarketSystem::CalculateWienerProcess(
    double drift,
    double diffusion,
    double timeStep
) {
    // Gera número aleatório normal
    double z = MathRandomNormal(0.0, 1.0);
    
    // Aplica fórmula do processo de Wiener
    return drift * timeStep + MathSqrt(2.0 * diffusion * timeStep) * z;
}

//+------------------------------------------------------------------+
//| Limpa dados antigos                                               |
//+------------------------------------------------------------------+
void CBrownianMarketSystem::CleanupOldData() {
    datetime current = TimeCurrent();
    
    // Remove partículas antigas
    for(int i = ArraySize(m_particles) - 1; i >= 0; i--) {
        if(current - m_particles[i].timestamp > m_config.historyPeriod * 60) {
            for(int j = i; j < ArraySize(m_particles) - 1; j++) {
                m_particles[j] = m_particles[j + 1];
            }
            ArrayResize(m_particles, ArraySize(m_particles) - 1);
        }
    }
    
    // Remove difusões antigas
    for(int i = ArraySize(m_diffusions) - 1; i >= 0; i--) {
        if(current - m_diffusions[i].endTime > m_config.diffusionPeriod * 60) {
            for(int j = i; j < ArraySize(m_diffusions) - 1; j++) {
                m_diffusions[j] = m_diffusions[j + 1];
            }
            ArrayResize(m_diffusions, ArraySize(m_diffusions) - 1);
        }
    }
    
    // Limita tamanho dos arrays
    while(ArraySize(m_particles) > m_maxParticles) {
        for(int i = 0; i < ArraySize(m_particles) - 1; i++) {
            m_particles[i] = m_particles[i + 1];
        }
        ArrayResize(m_particles, ArraySize(m_particles) - 1);
    }
    
    while(ArraySize(m_diffusions) > m_maxDiffusions) {
        for(int i = 0; i < ArraySize(m_diffusions) - 1; i++) {
            m_diffusions[i] = m_diffusions[i + 1];
        }
        ArrayResize(m_diffusions, ArraySize(m_diffusions) - 1);
    }
} 