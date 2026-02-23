#property copyright "Quantum Trading System"
#property link      "https://www.quantumtrading.com"
#property version   "1.0"
#property strict

// Inclusões necessárias
#include "../Core/QuantumCore.mqh"
#include "../Data/DataCollection.mqh"
#include <Trade/Trade.mqh>

//+------------------------------------------------------------------+
//| Classe StoDefenseStrategy                                         |
//+------------------------------------------------------------------+
class CStoDefenseStrategy {
private:
    // Componentes principais
    CQuantumCore*      m_core;
    CTrade            m_trade;
    
    // Estruturas
    struct DefenseLevels {
        double top;
        double bottom;
        datetime lastUpdate;
        double volumeTop;
        double volumeBottom;
    };
    
    struct StrategyConfig {
        double lotSize;
        int lossPoints;
        int gainPoints;
        int swingPeriod;
        double minVolume;
        int maxSpread;
        bool enableWeekend;
    };
    
    // Dados
    DefenseLevels     m_defense;
    StrategyConfig    m_config;
    bool             m_positionOpen;
    
    // Métodos privados
    void              CalculateDefenseLevels();
    bool              IsMarketConditionGood();
    bool              CheckMargin(double lotSize, double price);
    void              ManagePositions(double currentPrice);
    void              UpdateDefenseLevels();
    double            CalculatePOC(const double &prices[], const double &volumes[], int count);
    
public:
                      CStoDefenseStrategy();
                     ~CStoDefenseStrategy();
    
    // Métodos principais
    bool              Initialize(CQuantumCore* core);
    bool              Update();
    
    // Configuração
    void              SetLotSize(double size);
    void              SetLossPoints(int points);
    void              SetGainPoints(int points);
    void              SetSwingPeriod(int period);
    void              SetMinVolume(double volume);
    void              SetMaxSpread(int spread);
    void              EnableWeekend(bool enable);
    
    // Métodos de consulta
    DefenseLevels*    GetDefenseLevels() { return &m_defense; }
    bool              IsPositionOpen() { return m_positionOpen; }
    double            GetCurrentLotSize() { return m_config.lotSize; }
};

//+------------------------------------------------------------------+
//| Construtor                                                         |
//+------------------------------------------------------------------+
CStoDefenseStrategy::CStoDefenseStrategy() {
    m_core = NULL;
    m_positionOpen = false;
    
    // Configurações padrão
    m_config.lotSize = 0.1;
    m_config.lossPoints = 250;
    m_config.gainPoints = 100;
    m_config.swingPeriod = 20;
    m_config.minVolume = 100;
    m_config.maxSpread = 50;
    m_config.enableWeekend = false;
    
    // Inicializa níveis de defesa
    m_defense.top = 0.0;
    m_defense.bottom = 0.0;
    m_defense.lastUpdate = 0;
    m_defense.volumeTop = 0.0;
    m_defense.volumeBottom = 0.0;
}

//+------------------------------------------------------------------+
//| Destrutor                                                          |
//+------------------------------------------------------------------+
CStoDefenseStrategy::~CStoDefenseStrategy() {
    // Fecha todas as posições abertas
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelect(PositionGetString(ticket, POSITION_SYMBOL)) {
            m_trade.PositionClose(ticket);
        }
    }
}

//+------------------------------------------------------------------+
//| Inicialização                                                      |
//+------------------------------------------------------------------+
bool CStoDefenseStrategy::Initialize(CQuantumCore* core) {
    if(core == NULL) return false;
    
    m_core = core;
    m_trade.SetExpertMagicNumber(m_core.GetMagicNumber());
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza estratégia                                                |
//+------------------------------------------------------------------+
bool CStoDefenseStrategy::Update() {
    if(!m_core || !IsMarketConditionGood()) return false;
    
    string symbol = m_core.GetCurrentSymbol();
    double price = SymbolInfoDouble(symbol, SYMBOL_LAST);
    
    // Atualiza níveis de defesa se necessário
    if(TimeCurrent() - m_defense.lastUpdate > 60) {  // Atualiza a cada minuto
        UpdateDefenseLevels();
    }
    
    // Verifica sinais de entrada
    if(!m_positionOpen) {
        if(price > m_defense.bottom && CheckMargin(m_config.lotSize, price)) {
            if(m_trade.Buy(m_config.lotSize, symbol, price, 
                          price - m_config.lossPoints * _Point,
                          price + m_config.gainPoints * _Point,
                          "STO DEFENSE Buy")) {
                m_positionOpen = true;
                Print(StringFormat("%s: Compra executada. Preço = %.5f",
                      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
                      price));
            }
        }
        else if(price < m_defense.top && CheckMargin(m_config.lotSize, price)) {
            if(m_trade.Sell(m_config.lotSize, symbol, price,
                           price + m_config.lossPoints * _Point,
                           price - m_config.gainPoints * _Point,
                           "STO DEFENSE Sell")) {
                m_positionOpen = true;
                Print(StringFormat("%s: Venda executada. Preço = %.5f",
                      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
                      price));
            }
        }
    }
    
    // Gerencia posições abertas
    ManagePositions(price);
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula níveis de defesa                                           |
//+------------------------------------------------------------------+
void CStoDefenseStrategy::CalculateDefenseLevels() {
    string symbol = m_core.GetCurrentSymbol();
    
    // Arrays para armazenar dados
    double highs[], lows[], volumes[];
    ArrayResize(highs, m_config.swingPeriod);
    ArrayResize(lows, m_config.swingPeriod);
    ArrayResize(volumes, m_config.swingPeriod);
    
    // Obtém dados históricos
    for(int i = 0; i < m_config.swingPeriod; i++) {
        highs[i] = iHigh(symbol, PERIOD_M5, i);
        lows[i] = iLow(symbol, PERIOD_M5, i);
        volumes[i] = iVolume(symbol, PERIOD_M5, i);
    }
    
    // Calcula POC para topo e fundo
    m_defense.top = CalculatePOC(highs, volumes, m_config.swingPeriod);
    m_defense.bottom = CalculatePOC(lows, volumes, m_config.swingPeriod);
    
    // Atualiza volumes
    m_defense.volumeTop = 0;
    m_defense.volumeBottom = 0;
    for(int i = 0; i < m_config.swingPeriod; i++) {
        if(highs[i] == m_defense.top) {
            m_defense.volumeTop += volumes[i];
        }
        if(lows[i] == m_defense.bottom) {
            m_defense.volumeBottom += volumes[i];
        }
    }
    
    m_defense.lastUpdate = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Calcula POC (Point of Control)                                     |
//+------------------------------------------------------------------+
double CStoDefenseStrategy::CalculatePOC(
    const double &prices[],
    const double &volumes[],
    int count
) {
    double totalVolume = 0;
    double weightedPrice = 0;
    
    for(int i = 0; i < count; i++) {
        totalVolume += volumes[i];
        weightedPrice += prices[i] * volumes[i];
    }
    
    return totalVolume > 0 ? weightedPrice / totalVolume : 0;
}

//+------------------------------------------------------------------+
//| Atualiza níveis de defesa                                          |
//+------------------------------------------------------------------+
void CStoDefenseStrategy::UpdateDefenseLevels() {
    CalculateDefenseLevels();
    
    Print(StringFormat("DEFENSE Top = %.5f, DEFENSE Bottom = %.5f",
          m_defense.top,
          m_defense.bottom));
}

//+------------------------------------------------------------------+
//| Verifica condições de mercado                                      |
//+------------------------------------------------------------------+
bool CStoDefenseStrategy::IsMarketConditionGood() {
    MqlDateTime timeStruct;
    TimeToStruct(TimeCurrent(), timeStruct);
    
    if(!m_config.enableWeekend && timeStruct.day_of_week >= 6) {
        return false;
    }
    
    string symbol = m_core.GetCurrentSymbol();
    double spread = SymbolInfoInteger(symbol, SYMBOL_SPREAD);
    double volume = iVolume(symbol, PERIOD_M5, 0);
    
    return (spread < m_config.maxSpread && volume > m_config.minVolume);
}

//+------------------------------------------------------------------+
//| Verifica margem                                                    |
//+------------------------------------------------------------------+
bool CStoDefenseStrategy::CheckMargin(double lotSize, double price) {
    double marginRequired = 0.0;
    if(!OrderCalcMargin(ORDER_TYPE_BUY, m_core.GetCurrentSymbol(),
                       lotSize, price, marginRequired)) {
        Print("Erro ao calcular margem necessária.");
        return false;
    }
    
    double freeMargin = AccountInfoDouble(ACCOUNT_FREEMARGIN);
    if(marginRequired > freeMargin) {
        Print(StringFormat("Margem insuficiente (%.2f > %.2f)",
              marginRequired, freeMargin));
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Gerencia posições                                                  |
//+------------------------------------------------------------------+
void CStoDefenseStrategy::ManagePositions(double currentPrice) {
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelect(PositionGetString(ticket, POSITION_SYMBOL)) {
            double openPrice = PositionGetDouble(ticket, POSITION_PRICE_OPEN);
            int type = PositionGetInteger(ticket, POSITION_TYPE);
            
            if(type == ORDER_TYPE_BUY) {
                if((currentPrice - openPrice) / _Point >= m_config.gainPoints) {
                    m_trade.PositionClose(ticket);
                    Print(StringFormat("Compra fechada por ganho (%.5f)",
                          currentPrice));
                    m_positionOpen = false;
                }
                else if((openPrice - currentPrice) / _Point >= m_config.lossPoints) {
                    m_trade.PositionClose(ticket);
                    Print(StringFormat("Compra fechada por perda (%.5f)",
                          currentPrice));
                    m_positionOpen = false;
                }
            }
            else if(type == ORDER_TYPE_SELL) {
                if((openPrice - currentPrice) / _Point >= m_config.gainPoints) {
                    m_trade.PositionClose(ticket);
                    Print(StringFormat("Venda fechada por ganho (%.5f)",
                          currentPrice));
                    m_positionOpen = false;
                }
                else if((currentPrice - openPrice) / _Point >= m_config.lossPoints) {
                    m_trade.PositionClose(ticket);
                    Print(StringFormat("Venda fechada por perda (%.5f)",
                          currentPrice));
                    m_positionOpen = false;
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Configurações                                                      |
//+------------------------------------------------------------------+
void CStoDefenseStrategy::SetLotSize(double size) {
    m_config.lotSize = size;
}

void CStoDefenseStrategy::SetLossPoints(int points) {
    m_config.lossPoints = points;
}

void CStoDefenseStrategy::SetGainPoints(int points) {
    m_config.gainPoints = points;
}

void CStoDefenseStrategy::SetSwingPeriod(int period) {
    m_config.swingPeriod = period;
}

void CStoDefenseStrategy::SetMinVolume(double volume) {
    m_config.minVolume = volume;
}

void CStoDefenseStrategy::SetMaxSpread(int spread) {
    m_config.maxSpread = spread;
}

void CStoDefenseStrategy::EnableWeekend(bool enable) {
    m_config.enableWeekend = enable;
} 