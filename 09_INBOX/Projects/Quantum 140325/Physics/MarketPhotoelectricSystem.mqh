#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"

// Estrutura para trigger de mercado
struct MarketTrigger {
    string   symbol;
    string   type;           // "VOLUME", "VOLATILITY", "PRICE"
    datetime timestamp;
    double   threshold;      // Valor limite que ativou o trigger
    double   currentValue;   // Valor atual
    double   deviation;      // Desvio do normal
    bool     isActive;       // Se o trigger está ativo
    string   description;    // Descrição do evento
};

// Estrutura para nível de energia
struct EnergyLevel {
    string   symbol;
    double   price;
    string   type;          // "SUPPORT", "RESISTANCE", "BREAKOUT"
    double   strength;      // 0-1
    int      touches;       // Número de toques no nível
    datetime lastTouch;     // Último toque
    bool     isActive;      // Se o nível está ativo
};

// Estrutura para configuração do sistema
struct PhotoelectricConfig {
    double   volumeThreshold;    // Multiplicador do volume normal (2.0 = 2x)
    double   volatilityThreshold;// Multiplicador da volatilidade normal (1.5 = 1.5x)
    int      reactionTime;       // Tempo de reação em milissegundos
    int      historyPeriod;     // Períodos para análise histórica
    bool     useVolume;         // Usar triggers de volume
    bool     useVolatility;     // Usar triggers de volatilidade
    bool     usePrice;          // Usar triggers de preço
};

//+------------------------------------------------------------------+
//| Classe MarketPhotoelectricSystem                                   |
//+------------------------------------------------------------------+
class CMarketPhotoelectricSystem {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    PhotoelectricConfig m_config;
    
    // Cache de dados
    MarketTrigger      m_triggers[];
    EnergyLevel       m_levels[];
    
    // Estado do sistema
    bool              m_isInitialized;
    datetime          m_lastUpdate;
    
    // Configurações
    int               m_maxTriggers;
    int               m_maxLevels;
    
    // Métodos privados
    bool              ValidateTrigger(const MarketTrigger &trigger);
    bool              ValidateEnergyLevel(const EnergyLevel &level);
    void              CleanupOldTriggers();
    void              UpdateEnergyLevels();
    double            CalculateNormalVolume(string symbol);
    double            CalculateNormalVolatility(string symbol);
    bool              IsSignificantLevel(double price, string symbol);
    
public:
                      CMarketPhotoelectricSystem();
                     ~CMarketPhotoelectricSystem();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Update();
    
    // Métodos de análise
    bool              CheckVolumeTrigger(string symbol);
    bool              CheckVolatilityTrigger(string symbol);
    bool              CheckPriceTrigger(string symbol);
    bool              IdentifyEnergyLevels(string symbol);
    
    // Métodos de consulta
    MarketTrigger    *GetActiveTriggers();
    EnergyLevel     *GetActiveEnergyLevels(string symbol);
    bool             IsTriggerActive(string symbol, string type);
    
    // Configuração
    void             SetConfig(const PhotoelectricConfig &config);
    PhotoelectricConfig GetConfig() const { return m_config; }
    bool             IsInitialized() const { return m_isInitialized; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CMarketPhotoelectricSystem::CMarketPhotoelectricSystem() {
    m_core = NULL;
    m_isInitialized = false;
    m_lastUpdate = 0;
    
    // Configurações padrão
    m_config.volumeThreshold = 2.0;
    m_config.volatilityThreshold = 1.5;
    m_config.reactionTime = 50;
    m_config.historyPeriod = 100;
    m_config.useVolume = true;
    m_config.useVolatility = true;
    m_config.usePrice = true;
    
    m_maxTriggers = 1000;
    m_maxLevels = 100;
    
    ArrayResize(m_triggers, 0);
    ArrayResize(m_levels, 0);
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CMarketPhotoelectricSystem::~CMarketPhotoelectricSystem() {
    ArrayFree(m_triggers);
    ArrayFree(m_levels);
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    m_core = core;
    
    m_isInitialized = true;
    m_lastUpdate = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza sistema                                                   |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::Update() {
    if(!m_isInitialized || !m_core) return false;
    
    // Limpa triggers antigos
    CleanupOldTriggers();
    
    // Atualiza níveis de energia
    UpdateEnergyLevels();
    
    m_lastUpdate = TimeCurrent();
    return true;
}

//+------------------------------------------------------------------+
//| Verifica trigger de volume                                        |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::CheckVolumeTrigger(string symbol) {
    if(!m_isInitialized || !m_config.useVolume) return false;
    
    // Obtém volume atual
    double currentVolume = m_core.GetAnalysis().CalculateVolume(symbol);
    double normalVolume = CalculateNormalVolume(symbol);
    
    // Verifica se excede o threshold
    if(currentVolume > normalVolume * m_config.volumeThreshold) {
        // Cria novo trigger
        MarketTrigger trigger;
        trigger.symbol = symbol;
        trigger.type = "VOLUME";
        trigger.timestamp = TimeCurrent();
        trigger.threshold = normalVolume * m_config.volumeThreshold;
        trigger.currentValue = currentVolume;
        trigger.deviation = (currentVolume - normalVolume) / normalVolume;
        trigger.isActive = true;
        trigger.description = StringFormat("Volume spike: %.2fx normal volume", 
            currentVolume / normalVolume);
        
        // Valida e adiciona trigger
        if(ValidateTrigger(trigger)) {
            int size = ArraySize(m_triggers);
            ArrayResize(m_triggers, size + 1);
            m_triggers[size] = trigger;
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Verifica trigger de volatilidade                                  |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::CheckVolatilityTrigger(string symbol) {
    if(!m_isInitialized || !m_config.useVolatility) return false;
    
    // Obtém volatilidade atual
    double currentVolatility = m_core.GetAnalysis().CalculateVolatility(symbol);
    double normalVolatility = CalculateNormalVolatility(symbol);
    
    // Verifica se excede o threshold
    if(currentVolatility > normalVolatility * m_config.volatilityThreshold) {
        // Cria novo trigger
        MarketTrigger trigger;
        trigger.symbol = symbol;
        trigger.type = "VOLATILITY";
        trigger.timestamp = TimeCurrent();
        trigger.threshold = normalVolatility * m_config.volatilityThreshold;
        trigger.currentValue = currentVolatility;
        trigger.deviation = (currentVolatility - normalVolatility) / normalVolatility;
        trigger.isActive = true;
        trigger.description = StringFormat("Volatility spike: %.2fx normal volatility",
            currentVolatility / normalVolatility);
        
        // Valida e adiciona trigger
        if(ValidateTrigger(trigger)) {
            int size = ArraySize(m_triggers);
            ArrayResize(m_triggers, size + 1);
            m_triggers[size] = trigger;
            return true;
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Verifica trigger de preço                                         |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::CheckPriceTrigger(string symbol) {
    if(!m_isInitialized || !m_config.usePrice) return false;
    
    // Obtém preço atual
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick)) return false;
    
    // Verifica níveis de energia ativos
    for(int i = 0; i < ArraySize(m_levels); i++) {
        if(m_levels[i].symbol == symbol && m_levels[i].isActive) {
            // Verifica se o preço cruzou o nível
            if(MathAbs(tick.last - m_levels[i].price) < Point()) {
                // Cria novo trigger
                MarketTrigger trigger;
                trigger.symbol = symbol;
                trigger.type = "PRICE";
                trigger.timestamp = TimeCurrent();
                trigger.threshold = m_levels[i].price;
                trigger.currentValue = tick.last;
                trigger.deviation = 0;
                trigger.isActive = true;
                trigger.description = StringFormat("Price reached %s level: %.5f",
                    m_levels[i].type, m_levels[i].price);
                
                // Valida e adiciona trigger
                if(ValidateTrigger(trigger)) {
                    int size = ArraySize(m_triggers);
                    ArrayResize(m_triggers, size + 1);
                    m_triggers[size] = trigger;
                    return true;
                }
            }
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Identifica níveis de energia                                      |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::IdentifyEnergyLevels(string symbol) {
    if(!m_isInitialized || !m_config.usePrice) return false;
    
    // Obtém dados históricos
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    
    int copied = CopyRates(symbol, PERIOD_CURRENT, 0, m_config.historyPeriod, rates);
    if(copied != m_config.historyPeriod) return false;
    
    // Encontra níveis significativos
    for(int i = 1; i < copied - 1; i++) {
        // Verifica pivôs de alta
        if(rates[i].high > rates[i-1].high && rates[i].high > rates[i+1].high) {
            if(IsSignificantLevel(rates[i].high, symbol)) {
                EnergyLevel level;
                level.symbol = symbol;
                level.price = rates[i].high;
                level.type = "RESISTANCE";
                level.strength = 0.8;
                level.touches = 1;
                level.lastTouch = rates[i].time;
                level.isActive = true;
                
                if(ValidateEnergyLevel(level)) {
                    int size = ArraySize(m_levels);
                    ArrayResize(m_levels, size + 1);
                    m_levels[size] = level;
                }
            }
        }
        
        // Verifica pivôs de baixa
        if(rates[i].low < rates[i-1].low && rates[i].low < rates[i+1].low) {
            if(IsSignificantLevel(rates[i].low, symbol)) {
                EnergyLevel level;
                level.symbol = symbol;
                level.price = rates[i].low;
                level.type = "SUPPORT";
                level.strength = 0.8;
                level.touches = 1;
                level.lastTouch = rates[i].time;
                level.isActive = true;
                
                if(ValidateEnergyLevel(level)) {
                    int size = ArraySize(m_levels);
                    ArrayResize(m_levels, size + 1);
                    m_levels[size] = level;
                }
            }
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Obtém triggers ativos                                             |
//+------------------------------------------------------------------+
MarketTrigger *CMarketPhotoelectricSystem::GetActiveTriggers() {
    static MarketTrigger activeTriggers[];
    ArrayResize(activeTriggers, 0);
    
    for(int i = 0; i < ArraySize(m_triggers); i++) {
        if(m_triggers[i].isActive) {
            int size = ArraySize(activeTriggers);
            ArrayResize(activeTriggers, size + 1);
            activeTriggers[size] = m_triggers[i];
        }
    }
    
    return activeTriggers;
}

//+------------------------------------------------------------------+
//| Obtém níveis de energia ativos                                    |
//+------------------------------------------------------------------+
EnergyLevel *CMarketPhotoelectricSystem::GetActiveEnergyLevels(string symbol) {
    static EnergyLevel activeLevels[];
    ArrayResize(activeLevels, 0);
    
    for(int i = 0; i < ArraySize(m_levels); i++) {
        if(m_levels[i].symbol == symbol && m_levels[i].isActive) {
            int size = ArraySize(activeLevels);
            ArrayResize(activeLevels, size + 1);
            activeLevels[size] = m_levels[i];
        }
    }
    
    return activeLevels;
}

//+------------------------------------------------------------------+
//| Verifica se trigger está ativo                                    |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::IsTriggerActive(string symbol, string type) {
    for(int i = 0; i < ArraySize(m_triggers); i++) {
        if(m_triggers[i].symbol == symbol && 
           m_triggers[i].type == type &&
           m_triggers[i].isActive) {
            return true;
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Define configuração                                               |
//+------------------------------------------------------------------+
void CMarketPhotoelectricSystem::SetConfig(const PhotoelectricConfig &config) {
    m_config = config;
}

//+------------------------------------------------------------------+
//| Valida trigger                                                    |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::ValidateTrigger(const MarketTrigger &trigger) {
    if(trigger.symbol == "") return false;
    if(trigger.timestamp == 0) return false;
    if(trigger.currentValue <= 0) return false;
    if(trigger.threshold <= 0) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Valida nível de energia                                          |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::ValidateEnergyLevel(const EnergyLevel &level) {
    if(level.symbol == "") return false;
    if(level.price <= 0) return false;
    if(level.strength <= 0 || level.strength > 1) return false;
    if(level.touches <= 0) return false;
    if(level.lastTouch == 0) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Limpa triggers antigos                                            |
//+------------------------------------------------------------------+
void CMarketPhotoelectricSystem::CleanupOldTriggers() {
    datetime current = TimeCurrent();
    
    // Remove triggers antigos (mais de 1 hora)
    for(int i = ArraySize(m_triggers) - 1; i >= 0; i--) {
        if(current - m_triggers[i].timestamp > 3600) {
            for(int j = i; j < ArraySize(m_triggers) - 1; j++) {
                m_triggers[j] = m_triggers[j + 1];
            }
            ArrayResize(m_triggers, ArraySize(m_triggers) - 1);
        }
    }
    
    // Se ainda exceder o máximo, remove os mais antigos
    while(ArraySize(m_triggers) > m_maxTriggers) {
        for(int i = 0; i < ArraySize(m_triggers) - 1; i++) {
            m_triggers[i] = m_triggers[i + 1];
        }
        ArrayResize(m_triggers, ArraySize(m_triggers) - 1);
    }
}

//+------------------------------------------------------------------+
//| Atualiza níveis de energia                                        |
//+------------------------------------------------------------------+
void CMarketPhotoelectricSystem::UpdateEnergyLevels() {
    datetime current = TimeCurrent();
    
    // Atualiza força dos níveis baseado em toques recentes
    for(int i = 0; i < ArraySize(m_levels); i++) {
        // Reduz força se não houver toques recentes
        if(current - m_levels[i].lastTouch > 24 * 3600) {
            m_levels[i].strength *= 0.9;
        }
        
        // Desativa níveis fracos
        if(m_levels[i].strength < 0.2) {
            m_levels[i].isActive = false;
        }
    }
    
    // Remove níveis inativos se exceder o máximo
    while(ArraySize(m_levels) > m_maxLevels) {
        bool removed = false;
        for(int i = 0; i < ArraySize(m_levels); i++) {
            if(!m_levels[i].isActive) {
                for(int j = i; j < ArraySize(m_levels) - 1; j++) {
                    m_levels[j] = m_levels[j + 1];
                }
                ArrayResize(m_levels, ArraySize(m_levels) - 1);
                removed = true;
                break;
            }
        }
        if(!removed) break;
    }
}

//+------------------------------------------------------------------+
//| Calcula volume normal                                             |
//+------------------------------------------------------------------+
double CMarketPhotoelectricSystem::CalculateNormalVolume(string symbol) {
    if(!m_core) return 0.0;
    
    // Calcula média móvel do volume
    return m_core.GetAnalysis().CalculateAverageVolume(
        symbol,
        m_config.historyPeriod
    );
}

//+------------------------------------------------------------------+
//| Calcula volatilidade normal                                       |
//+------------------------------------------------------------------+
double CMarketPhotoelectricSystem::CalculateNormalVolatility(string symbol) {
    if(!m_core) return 0.0;
    
    // Calcula média móvel da volatilidade
    return m_core.GetAnalysis().CalculateAverageVolatility(
        symbol,
        m_config.historyPeriod
    );
}

//+------------------------------------------------------------------+
//| Verifica se nível é significativo                                 |
//+------------------------------------------------------------------+
bool CMarketPhotoelectricSystem::IsSignificantLevel(double price, string symbol) {
    // Verifica se já existe um nível próximo
    for(int i = 0; i < ArraySize(m_levels); i++) {
        if(m_levels[i].symbol == symbol && m_levels[i].isActive) {
            if(MathAbs(m_levels[i].price - price) < Point() * 10) {
                // Atualiza nível existente
                m_levels[i].touches++;
                m_levels[i].lastTouch = TimeCurrent();
                m_levels[i].strength = MathMin(1.0, m_levels[i].strength + 0.1);
                return false;
            }
        }
    }
    
    return true;
} 