//+------------------------------------------------------------------+
//|                                              EA_RaioX_Universal.mq5 |
//|                                  Copyright 2024, RaioX Trading      |
//|                                             https://raiox.com.br   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, RaioX Trading"
#property link      "https://raiox.com.br"
#property version   "1.00"
#property strict

// Parâmetros de entrada
input double LotSize = 0.01;          // Tamanho inicial do lote (reduzido para 0.01)
input double MaxLotSize = 0.1;        // Tamanho máximo do lote (reduzido para 0.1)
input int MaxPositions = 5;           // Número máximo de posições (aumentado para 5)
input double RiskPercent = 1.0;       // Percentual de risco (reduzido para 1%)
input double StopLoss = 30;           // Stop Loss em pontos (reduzido para 30)
input double TakeProfit = 60;         // Take Profit em pontos (reduzido para 60)
input bool UseTrailingStop = true;    // Usar trailing stop
input int TrailingStart = 15;         // Início do trailing stop em pontos (reduzido para 15)
input int TrailingStep = 5;           // Step do trailing stop em pontos (reduzido para 5)
input int MaxSpread = 100;            // Spread máximo permitido (aumentado para 100)
input bool UseNewsFilter = false;     // Usar filtro de notícias (desativado)
input bool UseTrendFilter = true;     // Usar filtro de tendência
input int TrendPeriod = 14;           // Período da média móvel (reduzido para 14)
input bool UseMultiTimeframe = true;  // Usar análise multi-timeframe
input double MinimumConfidence = 0.4; // Confiança mínima para operar (reduzido para 0.4)
input double CoherenceThreshold = 0.5; // Limiar de coerência entre timeframes (reduzido para 0.5)
input double VolumeMinimo = 0.01;     // Volume Mínimo (0.01 = 1 micro lote)
input double VolumeMaximo = 0.1;      // Volume Máximo (0.1 = 1 mini lote)
input double TrendWeight = 0.3;        // Peso da tendência
input double MomentumWeight = 0.25;    // Peso do momentum
input double VolumeWeight = 0.25;      // Peso do volume
input double VolatilityWeight = 0.2;   // Peso da volatilidade
input double MinimumScore = 0.6;       // Pontuação mínima para operar
input double ATRMultiplier = 1.5;      // Multiplicador do ATR para Stop Loss
input double VolatilityFactor = 0.5;   // Fator de redução do lote em alta volatilidade
input double MinStopLoss = 20;         // Stop Loss mínimo em pontos
input double MaxStopLoss = 50;         // Stop Loss máximo em pontos
input ENUM_TIMEFRAMES Timeframe1 = PERIOD_H1;    // Timeframe 1
input ENUM_TIMEFRAMES Timeframe2 = PERIOD_H4;    // Timeframe 2
input ENUM_TIMEFRAMES Timeframe3 = PERIOD_D1;    // Timeframe 3
input double TimeframeWeight1 = 0.4;             // Peso Timeframe 1
input double TimeframeWeight2 = 0.4;             // Peso Timeframe 2
input double TimeframeWeight3 = 0.2;             // Peso Timeframe 3

// Parâmetros para análise dinâmica de volume
input int VolumePeriod = 20;          // Período para análise de volume
input double VolumeThreshold = 0.5;    // Limiar de volume relativo à média

// Parâmetros para controle dinâmico de volume
input double VolumeMinimoPadrao = 500.0;    // Volume mínimo padrão
input double VolumeMinimoNoturno = 200.0;    // Volume mínimo para período noturno
input int HoraInicioNoturno = 22;            // Hora início período noturno
input int HoraFimNoturno = 4;                // Hora fim período noturno
input double BufferVolume = 0.7;             // Buffer de volume (70% do mínimo)

// Enums
enum MarketCondition
{
    MARKET_CONDITION_NORMAL,
    MARKET_CONDITION_TSUNAMI,
    MARKET_CONDITION_UNKNOWN
};

// Estruturas
struct MarketStats
{
    double avgVolume;
    double volumeStdDev;
    double avgRange;
    double rangeStdDev;
    double momentum;
    double volatility;
    double correlation;
    
    void Init()
    {
        avgVolume = 0;
        volumeStdDev = 0;
        avgRange = 0;
        rangeStdDev = 0;
        momentum = 0;
        volatility = 0;
        correlation = 0;
    }
};

struct PositionInfo
{
    ulong ticket;
    double volume;
    double openPrice;
    double currentPrice;
    double stopLoss;
    double takeProfit;
    datetime openTime;
    bool isLong;
    
    void Init()
    {
        ticket = 0;
        volume = 0;
        openPrice = 0;
        currentPrice = 0;
        stopLoss = 0;
        takeProfit = 0;
        openTime = 0;
        isLong = false;
    }
};

struct TimeframeAnalysis
{
    ENUM_TIMEFRAMES timeframe;
    double trend;
    double strength;
    double volatility;
    double volume;
    datetime lastUpdate;
    
    void Init()
    {
        timeframe = PERIOD_CURRENT;
        trend = 0;
        strength = 0;
        volatility = 0;
        volume = 0;
        lastUpdate = 0;
    }
};

// Estrutura para eventos de notícias
struct NewsEvent
{
    datetime time;
    string description;
};

// Array global para eventos de notícias
NewsEvent g_newsEvents[];

// Estrutura para pontuação de trade
struct TradeScore
{
    double trendScore;      // Pontuação da tendência (0-1)
    double momentumScore;   // Pontuação do momentum (0-1)
    double volumeScore;     // Pontuação do volume (0-1)
    double volatilityScore; // Pontuação da volatilidade (0-1)
    double totalScore;      // Pontuação total
    
    void Init()
    {
        trendScore = 0;
        momentumScore = 0;
        volumeScore = 0;
        volatilityScore = 0;
        totalScore = 0;
    }
};

// Classe de Logging
class CLogger
{
private:
    string m_name;
    
public:
    CLogger(string name)
    {
        m_name = name;
    }
    
    void Info(string message)
    {
        Print("[", m_name, "] INFO: ", message);
    }
    
    void Warning(string message)
    {
        Print("[", m_name, "] WARNING: ", message);
    }
    
    void Error(string message)
    {
        Print("[", m_name, "] ERROR: ", message);
    }
};

// Classe principal
class CRaioX
{
private:
    // Parâmetros de risco
    double m_lotSize;
    double m_maxLotSize;
    int m_maxPositions;
    double m_riskPercent;
    double m_stopLoss;
    double m_takeProfit;
    bool m_useTrailingStop;
    int m_trailingStart;
    int m_trailingStep;
    
    // Arrays
    PositionInfo m_positions[];
    TimeframeAnalysis m_analysis[];
    double m_priceBuffer[];
    long m_volumeBuffer[];
    double m_highBuffer[];
    double m_lowBuffer[];
    
    // Handles
    int m_atrHandle;
    int m_rsiHandle;
    int m_maHandle;
    
    // Estatísticas
    MarketStats m_stats;
    
    // Logger
    CLogger* m_logger;
    
    // Métodos privados
    bool InitializeBuffers();
    bool InitializeIndicators();
    bool UpdateTimeframeAnalysis(const ENUM_TIMEFRAMES timeframe);
    double CalculateTrend(const ENUM_TIMEFRAMES timeframe);
    double CalculateStrength(const ENUM_TIMEFRAMES timeframe);
    double CalculateVolatility(const ENUM_TIMEFRAMES timeframe);
    double CalculateVolume(const ENUM_TIMEFRAMES timeframe);
    bool ClosePosition(ulong ticket);
    bool ModifyPosition(ulong ticket, double stopLoss, double takeProfit);
    void UpdatePositions();
    bool DetectTsunami();
    void CalculateMarketStats();
    bool CheckVolume();
    bool CheckBasicConditions();
    bool CheckSpread();
    bool CheckNews();
    bool CheckTrend();
    bool CheckConfidence();
    bool CheckCoherence();
    bool CheckPositions();
    
public:
    CRaioX();
    ~CRaioX();
    
    bool Init(double lotSize, double maxLotSize, int maxPositions,
              double riskPercent, double stopLoss, double takeProfit,
              bool useTrailingStop, int trailingStart, int trailingStep,
              const ENUM_TIMEFRAMES &timeframes[]);
              
    void ManagePositions();
    MarketCondition AnalyzeMarket();
    void ExecuteStrategy();
    void ExecuteTsunamiStrategy();
    void ExecuteNormalStrategy();
    bool UpdateAnalysis();
    
    // Métodos públicos adicionados
    bool OpenPosition(bool isLong, double volume);
    double CalculatePositionSize();
    double CalculateSignal();
};

//+------------------------------------------------------------------+
//| Inicializa buffers                                                 |
//+------------------------------------------------------------------+
bool CRaioX::InitializeBuffers()
{
    // Redimensiona arrays
    ArrayResize(m_priceBuffer, 100);
    ArrayResize(m_volumeBuffer, 100);
    ArrayResize(m_highBuffer, 100);
    ArrayResize(m_lowBuffer, 100);
    
    // Configura arrays como séries
    ArraySetAsSeries(m_priceBuffer, true);
    ArraySetAsSeries(m_volumeBuffer, true);
    ArraySetAsSeries(m_highBuffer, true);
    ArraySetAsSeries(m_lowBuffer, true);
    
    return true;
}

//+------------------------------------------------------------------+
//| Inicializa indicadores                                            |
//+------------------------------------------------------------------+
bool CRaioX::InitializeIndicators()
{
    // Inicializa ATR
    m_atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
    if(m_atrHandle == INVALID_HANDLE)
    {
        m_logger.Error("Erro ao criar handle do ATR");
        return false;
    }
    
    // Inicializa RSI
    m_rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
    if(m_rsiHandle == INVALID_HANDLE)
    {
        m_logger.Error("Erro ao criar handle do RSI");
        return false;
    }
    
    // Inicializa MA
    m_maHandle = iMA(_Symbol, PERIOD_CURRENT, 20, 0, MODE_SMA, PRICE_CLOSE);
    if(m_maHandle == INVALID_HANDLE)
    {
        m_logger.Error("Erro ao criar handle da MA");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza análise do timeframe                                     |
//+------------------------------------------------------------------+
bool CRaioX::UpdateTimeframeAnalysis(const ENUM_TIMEFRAMES timeframe)
{
    if(!ArrayResize(m_analysis, 3)) return false;
    
    // Atualiza análise para cada timeframe
    m_analysis[0].timeframe = Timeframe1;
    m_analysis[1].timeframe = Timeframe2;
    m_analysis[2].timeframe = Timeframe3;
    
    for(int i = 0; i < 3; i++)
    {
        m_analysis[i].trend = CalculateTrend(m_analysis[i].timeframe);
        m_analysis[i].strength = CalculateStrength(m_analysis[i].timeframe);
        m_analysis[i].volatility = CalculateVolatility(m_analysis[i].timeframe);
        m_analysis[i].volume = CalculateVolume(m_analysis[i].timeframe);
        m_analysis[i].lastUpdate = TimeCurrent();
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Calcula estatísticas do mercado                                    |
//+------------------------------------------------------------------+
void CRaioX::CalculateMarketStats()
{
    // Calcula média e desvio padrão do volume
    double volumeSum = 0;
    double volumeSumSquared = 0;
    for(int i = 0; i < 20; i++)
    {
        double volume = (double)m_volumeBuffer[i];
        volumeSum += volume;
        volumeSumSquared += volume * volume;
    }
    m_stats.avgVolume = volumeSum / 20;
    m_stats.volumeStdDev = MathSqrt(volumeSumSquared / 20 - m_stats.avgVolume * m_stats.avgVolume);
    
    // Calcula média e desvio padrão do range
    double rangeSum = 0;
    double rangeSumSquared = 0;
    for(int i = 0; i < 20; i++)
    {
        double range = m_highBuffer[i] - m_lowBuffer[i];
        rangeSum += range;
        rangeSumSquared += range * range;
    }
    m_stats.avgRange = rangeSum / 20;
    m_stats.rangeStdDev = MathSqrt(rangeSumSquared / 20 - m_stats.avgRange * m_stats.avgRange);
    
    // Calcula momentum
    m_stats.momentum = (m_priceBuffer[0] - m_priceBuffer[20]) / m_priceBuffer[20] * 100;
    
    // Calcula volatilidade
    m_stats.volatility = CalculateVolatility(PERIOD_CURRENT);
    
    // Calcula correlação
    double priceVolumeSum = 0;
    double priceSum = 0;
    double correlationVolumeSum = 0;
    double priceSquaredSum = 0;
    double volumeSquaredSum = 0;
    
    for(int i = 0; i < 20; i++)
    {
        double price = m_priceBuffer[i];
        double volume = (double)m_volumeBuffer[i];
        
        priceVolumeSum += price * volume;
        priceSum += price;
        correlationVolumeSum += volume;
        priceSquaredSum += price * price;
        volumeSquaredSum += volume * volume;
    }
    
    double numerator = 20 * priceVolumeSum - priceSum * correlationVolumeSum;
    double denominator = MathSqrt((20 * priceSquaredSum - priceSum * priceSum) * (20 * volumeSquaredSum - correlationVolumeSum * correlationVolumeSum));
    
    m_stats.correlation = denominator != 0 ? numerator / denominator : 0;
    
    m_logger.Info("Estatísticas atualizadas - Volume: " + DoubleToString(m_stats.avgVolume, 2) + 
                  ", Range: " + DoubleToString(m_stats.avgRange, 2) + 
                  ", Momentum: " + DoubleToString(m_stats.momentum, 2));
}

//+------------------------------------------------------------------+
//| Calcula tendência do timeframe                                    |
//+------------------------------------------------------------------+
double CRaioX::CalculateTrend(const ENUM_TIMEFRAMES timeframe)
{
    double maValues[];
    ArraySetAsSeries(maValues, true);
    
    // Calcula tendência usando múltiplas médias móveis
    int ma20Handle = iMA(_Symbol, timeframe, 20, 0, MODE_SMA, PRICE_CLOSE);
    int ma50Handle = iMA(_Symbol, timeframe, 50, 0, MODE_SMA, PRICE_CLOSE);
    int ma200Handle = iMA(_Symbol, timeframe, 200, 0, MODE_SMA, PRICE_CLOSE);
    
    if(ma20Handle == INVALID_HANDLE || ma50Handle == INVALID_HANDLE || ma200Handle == INVALID_HANDLE)
        return 0;
        
    double ma20[], ma50[], ma200[];
    ArraySetAsSeries(ma20, true);
    ArraySetAsSeries(ma50, true);
    ArraySetAsSeries(ma200, true);
    
    if(CopyBuffer(ma20Handle, 0, 0, 1, ma20) <= 0 ||
       CopyBuffer(ma50Handle, 0, 0, 1, ma50) <= 0 ||
       CopyBuffer(ma200Handle, 0, 0, 1, ma200) <= 0)
        return 0;
        
    // Calcula tendência ponderada
    double trend = 0;
    if(ma20[0] > ma50[0] && ma50[0] > ma200[0])
        trend = 1.0;
    else if(ma20[0] < ma50[0] && ma50[0] < ma200[0])
        trend = -1.0;
    else
        trend = 0.5 * (ma20[0] > ma50[0] ? 1.0 : -1.0);
        
    return trend;
}

//+------------------------------------------------------------------+
//| Calcula força do timeframe                                        |
//+------------------------------------------------------------------+
double CRaioX::CalculateStrength(const ENUM_TIMEFRAMES timeframe)
{
    double rsiBuffer[];
    ArraySetAsSeries(rsiBuffer, true);
    
    if(CopyBuffer(m_rsiHandle, 0, 0, 1, rsiBuffer) <= 0)
        return 0;
        
    return rsiBuffer[0];
}

//+------------------------------------------------------------------+
//| Calcula volatilidade do timeframe                                 |
//+------------------------------------------------------------------+
double CRaioX::CalculateVolatility(const ENUM_TIMEFRAMES timeframe)
{
    double atrBuffer[];
    ArraySetAsSeries(atrBuffer, true);
    
    if(CopyBuffer(m_atrHandle, 0, 0, 1, atrBuffer) <= 0)
        return 0;
        
    return atrBuffer[0];
}

//+------------------------------------------------------------------+
//| Calcula volume do timeframe                                       |
//+------------------------------------------------------------------+
double CRaioX::CalculateVolume(const ENUM_TIMEFRAMES timeframe)
{
    double sumVolume = 0;
    for(int i = 0; i < 20; i++)
        sumVolume += (double)m_volumeBuffer[i];
        
    return sumVolume / 20;
}

//+------------------------------------------------------------------+
//| Abre uma nova posição                                             |
//+------------------------------------------------------------------+
bool CRaioX::OpenPosition(bool isLong, double volume)
{
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // Log dos parâmetros
    m_logger.Info("Tentando abrir posição - Direção: " + (isLong ? "Long" : "Short") + 
                  ", Volume: " + DoubleToString(volume, 2));
    
    // Verifica se o volume é válido
    if(volume <= 0)
    {
        m_logger.Error("Volume inválido: " + DoubleToString(volume, 2));
        return false;
    }
    
    // Verifica se o símbolo está ativo
    if(!SymbolSelect(_Symbol, true))
    {
        m_logger.Error("Erro ao selecionar símbolo: " + IntegerToString(GetLastError()));
        return false;
    }
    
    // Verifica se o mercado está aberto
    if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE))
    {
        m_logger.Error("Mercado fechado para " + _Symbol);
        return false;
    }
    
    // Verifica se o trading está permitido
    if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
    {
        m_logger.Error("Trading não permitido no terminal");
        return false;
    }
    
    // Verifica se o EA está permitido para trading
    if(!MQLInfoInteger(MQL_TRADE_ALLOWED))
    {
        m_logger.Error("Trading não permitido para EAs");
        return false;
    }
    
    request.action = TRADE_ACTION_DEAL;
    request.symbol = _Symbol;
    request.volume = volume;
    request.type = isLong ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    request.price = isLong ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    request.deviation = 10;
    request.magic = 123456;
    request.comment = "RaioX Trade";
    request.type_filling = ORDER_FILLING_FOK;
    
    // Log dos preços
    m_logger.Info("Preços - Ask: " + DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_ASK), _Digits) + 
                  ", Bid: " + DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_BID), _Digits));
    
    // Calcula stop loss e take profit
    if(isLong)
    {
        request.sl = request.price - m_stopLoss * _Point;
        request.tp = request.price + m_takeProfit * _Point;
    }
    else
    {
        request.sl = request.price + m_stopLoss * _Point;
        request.tp = request.price - m_takeProfit * _Point;
    }
    
    // Log dos níveis
    m_logger.Info("Níveis - SL: " + DoubleToString(request.sl, _Digits) + 
                  ", TP: " + DoubleToString(request.tp, _Digits));
    
    // Executa ordem
    if(!OrderSend(request, result))
    {
        m_logger.Error("Erro ao enviar ordem: " + IntegerToString(GetLastError()));
        return false;
    }
    
    // Verifica resultado
    if(result.retcode != TRADE_RETCODE_DONE)
    {
        m_logger.Error("Erro na execução da ordem: " + IntegerToString(result.retcode));
        return false;
    }
    
    // Log do sucesso
    m_logger.Info("Ordem executada com sucesso - Ticket: " + IntegerToString(result.order));
    
    // Adiciona posição ao array
    int size = ArraySize(m_positions);
    ArrayResize(m_positions, size + 1);
    
    m_positions[size].ticket = result.order;
    m_positions[size].volume = volume;
    m_positions[size].openPrice = request.price;
    m_positions[size].currentPrice = request.price;
    m_positions[size].stopLoss = request.sl;
    m_positions[size].takeProfit = request.tp;
    m_positions[size].openTime = TimeCurrent();
    m_positions[size].isLong = isLong;
    
    return true;
}

//+------------------------------------------------------------------+
//| Fecha uma posição existente                                       |
//+------------------------------------------------------------------+
bool CRaioX::ClosePosition(ulong ticket)
{
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // Busca posição
    if(!PositionSelectByTicket(ticket))
    {
        m_logger.Error("Posição não encontrada: " + IntegerToString(ticket));
        return false;
    }
    
    request.action = TRADE_ACTION_DEAL;
    request.symbol = _Symbol;
    request.volume = PositionGetDouble(POSITION_VOLUME);
    request.type = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
    request.price = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    request.deviation = 10;
    request.magic = 123456;
    request.comment = "RaioX Close";
    request.type_filling = ORDER_FILLING_FOK;
    
    // Executa ordem
    if(!OrderSend(request, result))
    {
        m_logger.Error("Erro ao enviar ordem de fechamento: " + IntegerToString(GetLastError()));
        return false;
    }
    
    // Verifica resultado
    if(result.retcode != TRADE_RETCODE_DONE)
    {
        m_logger.Error("Erro na execução da ordem de fechamento: " + IntegerToString(result.retcode));
        return false;
    }
    
    // Remove posição do array
    for(int i = 0; i < ArraySize(m_positions); i++)
    {
        if(m_positions[i].ticket == ticket)
        {
            for(int j = i; j < ArraySize(m_positions) - 1; j++)
                m_positions[j] = m_positions[j + 1];
            ArrayResize(m_positions, ArraySize(m_positions) - 1);
            break;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Modifica uma posição existente                                    |
//+------------------------------------------------------------------+
bool CRaioX::ModifyPosition(ulong ticket, double stopLoss, double takeProfit)
{
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // Busca posição
    if(!PositionSelectByTicket(ticket))
    {
        m_logger.Error("Posição não encontrada: " + IntegerToString(ticket));
        return false;
    }
    
    request.action = TRADE_ACTION_SLTP;
    request.symbol = _Symbol;
    request.sl = stopLoss;
    request.tp = takeProfit;
    
    // Executa ordem
    if(!OrderSend(request, result))
    {
        m_logger.Error("Erro ao enviar ordem de modificação: " + IntegerToString(GetLastError()));
        return false;
    }
    
    // Verifica resultado
    if(result.retcode != TRADE_RETCODE_DONE)
    {
        m_logger.Error("Erro na execução da ordem de modificação: " + IntegerToString(result.retcode));
        return false;
    }
    
    // Atualiza array
    for(int i = 0; i < ArraySize(m_positions); i++)
    {
        if(m_positions[i].ticket == ticket)
        {
            m_positions[i].stopLoss = stopLoss;
            m_positions[i].takeProfit = takeProfit;
            break;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Atualiza informações das posições                                 |
//+------------------------------------------------------------------+
void CRaioX::UpdatePositions()
{
    // Atualiza estatísticas do mercado
    CalculateMarketStats();
    
    // Ajusta tamanho do lote baseado na volatilidade
    double atrValues[];
    ArraySetAsSeries(atrValues, true);
    CopyBuffer(m_atrHandle, 0, 0, 1, atrValues);
    
    double volatilityRatio = atrValues[0] / (StopLoss * Point());
    double adjustedLotSize = LotSize;
    
    if(volatilityRatio > 1.0)
    {
        adjustedLotSize *= (1.0 - (volatilityRatio - 1.0) * VolatilityFactor);
        adjustedLotSize = MathMax(adjustedLotSize, VolumeMinimo);
    }
    
    // Ajusta Stop Loss baseado no ATR
    double atrStopLoss = atrValues[0] * ATRMultiplier / Point();
    atrStopLoss = MathMin(MathMax(atrStopLoss, MinStopLoss), MaxStopLoss);
    
    // Atualiza posições existentes
    for(int i = 0; i < ArraySize(m_positions); i++)
    {
        if(m_positions[i].ticket > 0)
        {
            // Atualiza preço atual
            if(!PositionSelectByTicket(m_positions[i].ticket))
                continue;
                
            m_positions[i].currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
            
            // Ajusta Stop Loss se necessário
            if(m_useTrailingStop)
            {
                double newStopLoss = 0.0;
                
                // Calcula novo stop loss baseado na direção da posição
                if(m_positions[i].isLong)
                {
                    newStopLoss = m_positions[i].currentPrice - atrStopLoss * Point();
                    if(newStopLoss > m_positions[i].stopLoss)
                    {
                        ModifyPosition(m_positions[i].ticket, newStopLoss, m_positions[i].takeProfit);
                    }
                }
                else
                {
                    newStopLoss = m_positions[i].currentPrice + atrStopLoss * Point();
                    if(newStopLoss < m_positions[i].stopLoss)
                    {
                        ModifyPosition(m_positions[i].ticket, newStopLoss, m_positions[i].takeProfit);
                    }
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Calcula tamanho da posição                                        |
//+------------------------------------------------------------------+
double CRaioX::CalculatePositionSize()
{
    double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = accountBalance * m_riskPercent / 100;
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    
    double volume = NormalizeDouble(riskAmount / (m_stopLoss * tickValue / tickSize), 2);
    volume = MathMin(volume, m_maxLotSize);
    volume = MathMax(volume, m_lotSize);
    
    return volume;
}

//+------------------------------------------------------------------+
//| Detecta formação de tsunami                                       |
//+------------------------------------------------------------------+
bool CRaioX::DetectTsunami()
{
    m_logger.Info("Iniciando detecção de tsunami");
    
    // Verifica volume
    double currentVolume = (double)m_volumeBuffer[0];
    double volumeZScore = (currentVolume - m_stats.avgVolume) / m_stats.volumeStdDev;
    
    m_logger.Info("Volume Z-Score: " + DoubleToString(volumeZScore, 2));
    
    // Verifica momentum
    m_logger.Info("Momentum: " + DoubleToString(m_stats.momentum, 2));
    
    // Verifica volatilidade
    double volatilityRatio = m_stats.volatility / m_stats.avgRange;
    m_logger.Info("Razão de Volatilidade: " + DoubleToString(volatilityRatio, 2));
    
    // Condições ainda mais simplificadas para tsunami
    bool isTsunami = MathAbs(volumeZScore) > 0.05 || MathAbs(m_stats.momentum) > 0.05 || volatilityRatio > 0.05;
    
    if(isTsunami)
    {
        m_logger.Info("Tsunami detectado! - Volume Z-Score: " + DoubleToString(volumeZScore, 2) + 
                      ", Momentum: " + DoubleToString(m_stats.momentum, 2) + 
                      ", Volatilidade: " + DoubleToString(volatilityRatio, 2));
    }
    else
    {
        m_logger.Info("Tsunami não detectado - Volume Z-Score: " + DoubleToString(volumeZScore, 2) + 
                      ", Momentum: " + DoubleToString(m_stats.momentum, 2) + 
                      ", Volatilidade: " + DoubleToString(volatilityRatio, 2));
    }
    
    return isTsunami;
}

//+------------------------------------------------------------------+
//| Construtor da classe CRaioX                                        |
//+------------------------------------------------------------------+
CRaioX::CRaioX()
{
    m_lotSize = 0.01;
    m_maxLotSize = 0.1;
    m_maxPositions = 5;
    m_riskPercent = 1.0;
    m_stopLoss = 30;
    m_takeProfit = 60;
    m_useTrailingStop = true;
    m_trailingStart = 15;
    m_trailingStep = 5;
    
    m_atrHandle = INVALID_HANDLE;
    m_rsiHandle = INVALID_HANDLE;
    m_maHandle = INVALID_HANDLE;
    
    m_stats.Init();
    m_logger = new CLogger("RaioX");
}

//+------------------------------------------------------------------+
//| Destrutor da classe CRaioX                                         |
//+------------------------------------------------------------------+
CRaioX::~CRaioX()
{
    if(m_atrHandle != INVALID_HANDLE)
        IndicatorRelease(m_atrHandle);
        
    if(m_rsiHandle != INVALID_HANDLE)
        IndicatorRelease(m_rsiHandle);
        
    if(m_maHandle != INVALID_HANDLE)
        IndicatorRelease(m_maHandle);
        
    if(m_logger != NULL)
    {
        delete m_logger;
        m_logger = NULL;
    }
}

//+------------------------------------------------------------------+
//| Inicializa o EA                                                    |
//+------------------------------------------------------------------+
bool CRaioX::Init(double lotSize, double maxLotSize, int maxPositions,
                  double riskPercent, double stopLoss, double takeProfit,
                  bool useTrailingStop, int trailingStart, int trailingStep,
                  const ENUM_TIMEFRAMES &timeframes[])
{
    // Valida parâmetros
    if(lotSize <= 0 || maxLotSize <= 0 || maxPositions <= 0)
    {
        m_logger.Error("Parâmetros inválidos");
        return false;
    }
    
    // Configura parâmetros
    m_lotSize = lotSize;
    m_maxLotSize = maxLotSize;
    m_maxPositions = maxPositions;
    m_riskPercent = riskPercent;
    m_stopLoss = stopLoss;
    m_takeProfit = takeProfit;
    m_useTrailingStop = useTrailingStop;
    m_trailingStart = trailingStart;
    m_trailingStep = trailingStep;
    
    // Inicializa array de análise
    ArrayResize(m_analysis, ArraySize(timeframes));
    for(int i = 0; i < ArraySize(timeframes); i++)
    {
        m_analysis[i].timeframe = timeframes[i];
        m_analysis[i].Init();
    }
    
    // Inicializa buffers
    if(!InitializeBuffers())
    {
        m_logger.Error("Erro ao inicializar buffers");
        return false;
    }
    
    // Inicializa indicadores
    if(!InitializeIndicators())
    {
        m_logger.Error("Erro ao inicializar indicadores");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Gerencia posições existentes                                       |
//+------------------------------------------------------------------+
void CRaioX::ManagePositions()
{
    // Atualiza informações das posições
    UpdatePositions();
    
    // Gerencia trailing stop
    if(m_useTrailingStop)
    {
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            if(m_positions[i].ticket == 0) continue;
            
            double newStopLoss = 0;
            bool shouldModify = false;
            
            if(m_positions[i].isLong)
            {
                double profit = m_positions[i].currentPrice - m_positions[i].openPrice;
                if(profit > m_trailingStart * _Point)
                {
                    newStopLoss = m_positions[i].currentPrice - m_trailingStep * _Point;
                    if(newStopLoss > m_positions[i].stopLoss)
                        shouldModify = true;
                }
            }
            else
            {
                double profit = m_positions[i].openPrice - m_positions[i].currentPrice;
                if(profit > m_trailingStart * _Point)
                {
                    newStopLoss = m_positions[i].currentPrice + m_trailingStep * _Point;
                    if(newStopLoss < m_positions[i].stopLoss)
                        shouldModify = true;
                }
            }
            
            if(shouldModify)
                ModifyPosition(m_positions[i].ticket, newStopLoss, m_positions[i].takeProfit);
        }
    }
}

//+------------------------------------------------------------------+
//| Analisa condição do mercado                                        |
//+------------------------------------------------------------------+
MarketCondition CRaioX::AnalyzeMarket()
{
    // Atualiza análise de timeframes
    if(!UpdateAnalysis())
    {
        m_logger.Error("Erro ao atualizar análise");
        return MARKET_CONDITION_UNKNOWN;
    }
    
    // Detecta tsunami
    if(DetectTsunami())
    {
        return MARKET_CONDITION_TSUNAMI;
    }
    
    return MARKET_CONDITION_NORMAL;
}

//+------------------------------------------------------------------+
//| Executa estratégia                                                 |
//+------------------------------------------------------------------+
void CRaioX::ExecuteStrategy()
{
    MarketCondition condition = AnalyzeMarket();
    
    switch(condition)
    {
        case MARKET_CONDITION_TSUNAMI:
            ExecuteTsunamiStrategy();
            break;
            
        case MARKET_CONDITION_NORMAL:
            ExecuteNormalStrategy();
            break;
            
        default:
            m_logger.Warning("Condição de mercado desconhecida");
            break;
    }
}

//+------------------------------------------------------------------+
//| Executa estratégia de tsunami                                      |
//+------------------------------------------------------------------+
void CRaioX::ExecuteTsunamiStrategy()
{
    m_logger.Info("Iniciando execução da estratégia de tsunami");
    
    // Verifica número máximo de posições
    int currentPositions = ArraySize(m_positions);
    m_logger.Info("Posições atuais: " + IntegerToString(currentPositions) + 
                  ", Máximo permitido: " + IntegerToString(m_maxPositions));
                  
    if(currentPositions >= m_maxPositions)
    {
        m_logger.Warning("Número máximo de posições atingido: " + IntegerToString(currentPositions));
        return;
    }
    
    // Calcula tamanho da posição
    double volume = CalculatePositionSize();
    m_logger.Info("Tamanho da posição calculado: " + DoubleToString(volume, 2));
    
    // Verifica se o volume é válido
    if(volume <= 0)
    {
        m_logger.Error("Volume calculado inválido: " + DoubleToString(volume, 2));
        return;
    }
    
    // Verifica tendência
    double trend = CalculateTrend(PERIOD_CURRENT);
    m_logger.Info("Tendência atual: " + DoubleToString(trend, 2));
    
    // Verifica força do mercado
    double strength = CalculateStrength(PERIOD_CURRENT);
    m_logger.Info("Força do mercado: " + DoubleToString(strength, 2));
    
    // Condições ainda mais simplificadas para ordens
    bool longConditions = trend > 0 && strength > 10;  // Reduzido para 10
    m_logger.Info("Condições para ordem longa: " + (longConditions ? "OK" : "NÃO OK") + 
                  " (Trend > 0: " + (trend > 0 ? "Sim" : "Não") + 
                  ", Strength > 10: " + (strength > 10 ? "Sim" : "Não") + ")");
    
    bool shortConditions = trend < 0 && strength < 90;  // Aumentado para 90
    m_logger.Info("Condições para ordem curta: " + (shortConditions ? "OK" : "NÃO OK") + 
                  " (Trend < 0: " + (trend < 0 ? "Sim" : "Não") + 
                  ", Strength < 90: " + (strength < 90 ? "Sim" : "Não") + ")");
    
    // Abre posição longa se tendência for positiva
    if(longConditions)
    {
        m_logger.Info("Tentando abrir posição longa - Tendência: " + DoubleToString(trend, 2) + 
                      ", Força: " + DoubleToString(strength, 2));
                      
        if(!OpenPosition(true, volume))
        {
            m_logger.Error("Falha ao abrir posição longa");
        }
    }
    // Abre posição curta se tendência for negativa
    else if(shortConditions)
    {
        m_logger.Info("Tentando abrir posição curta - Tendência: " + DoubleToString(trend, 2) + 
                      ", Força: " + DoubleToString(strength, 2));
                      
        if(!OpenPosition(false, volume))
        {
            m_logger.Error("Falha ao abrir posição curta");
        }
    }
    else
    {
        m_logger.Info("Condições não favoráveis para abrir posição - Tendência: " + DoubleToString(trend, 2) + 
                      ", Força: " + DoubleToString(strength, 2));
    }
}

//+------------------------------------------------------------------+
//| Executa estratégia normal                                          |
//+------------------------------------------------------------------+
void CRaioX::ExecuteNormalStrategy()
{
    // Implementar estratégia normal
    // TODO: Implementar lógica de análise e execução para condições normais
}

//+------------------------------------------------------------------+
//| Atualiza análise                                                   |
//+------------------------------------------------------------------+
bool CRaioX::UpdateAnalysis()
{
    for(int i = 0; i < ArraySize(m_analysis); i++)
    {
        if(!UpdateTimeframeAnalysis(m_analysis[i].timeframe))
        {
            m_logger.Error("Erro ao atualizar análise do timeframe: " + IntegerToString(m_analysis[i].timeframe));
            return false;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    // Configura timeframes
    ENUM_TIMEFRAMES timeframes[] = {PERIOD_CURRENT};  // Simplificado para usar apenas o timeframe atual
    
    // Inicializa EA
    if(!g_raioX.Init(LotSize, MaxLotSize, MaxPositions, RiskPercent, StopLoss, TakeProfit,
                     UseTrailingStop, TrailingStart, TrailingStep, timeframes))
    {
        Print("Erro ao inicializar EA");
        return INIT_FAILED;
    }
    
    Print("EA inicializado com sucesso");
    Print("Parâmetros: LotSize=", LotSize, ", MaxLotSize=", MaxLotSize, ", MaxPositions=", MaxPositions);
    Print("StopLoss=", StopLoss, ", TakeProfit=", TakeProfit);
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Limpa recursos
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
{
    // Verifica se é uma nova barra
    if(!IsNewBar()) return;
    
    // Verifica condições básicas
    if(!CheckBasicConditions())
    {
        Print("Condições básicas não atendidas");
        return;
    }
    
    // Verifica volume
    if(!CheckVolume())
    {
        Print("Volume insuficiente para operar");
        return;
    }
    
    // Verifica spread
    if(!CheckSpread())
    {
        Print("Spread muito alto: ", SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point);
        return;
    }
    
    // Verifica notícias
    if(!CheckNews())
    {
        Print("Período de notícias - operações desativadas");
        return;
    }
    
    // Verifica tendência
    if(!CheckTrend())
    {
        Print("Tendência não favorável");
        return;
    }
    
    // Verifica confiança
    if(!CheckConfidence())
    {
        Print("Confiança insuficiente para operar");
        return;
    }
    
    // Verifica coerência
    if(!CheckCoherence())
    {
        Print("Coerência insuficiente entre timeframes");
        return;
    }
    
    // Verifica posições existentes
    if(!CheckPositions())
    {
        Print("Número máximo de posições atingido");
        return;
    }
    
    // Calcula sinais usando o objeto g_raioX
    double signal = g_raioX.CalculateSignal();
    Print("Sinal calculado: ", signal);
    
    // Executa operações
    if(signal > 0)
    {
        g_raioX.OpenPosition(true, g_raioX.CalculatePositionSize());
    }
    else if(signal < 0)
    {
        g_raioX.OpenPosition(false, g_raioX.CalculatePositionSize());
    }
    
    // Gerencia posições existentes
    g_raioX.ManagePositions();
}

// Variáveis globais
CRaioX g_raioX;

bool CheckBasicConditions()
{
    if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
    {
        Print("Trading não permitido");
        return false;
    }
    
    if(!MQLInfoInteger(MQL_TRADE_ALLOWED))
    {
        Print("Expert Advisor desativado");
        return false;
    }
    
    if(!TerminalInfoInteger(TERMINAL_CONNECTED))
    {
        Print("Não conectado ao servidor");
        return false;
    }
    
    return true;
}

bool CheckSpread()
{
    long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
    double spreadPoints = spread * _Point;
    Print("Spread atual: ", spread, " (", DoubleToString(spreadPoints, 5), ") - Máximo permitido: ", MaxSpread);
    
    if(spread > MaxSpread)
    {
        Print("Spread muito alto: ", spread, " (", DoubleToString(spreadPoints, 5), ")");
        return false;
    }
    return true;
}

bool CheckNews()
{
    if(!UseNewsFilter) return true;
    
    datetime currentTime = TimeCurrent();
    for(int i = 0; i < ArraySize(g_newsEvents); i++)
    {
        if(currentTime >= g_newsEvents[i].time - 30*60 && 
           currentTime <= g_newsEvents[i].time + 30*60)
        {
            Print("Período de notícias: ", g_newsEvents[i].description);
            return false;
        }
    }
    return true;
}

bool CheckTrend()
{
    if(!UseTrendFilter) return true;
    
    int maHandle = iMA(_Symbol, PERIOD_CURRENT, TrendPeriod, 0, MODE_SMA, PRICE_CLOSE);
    if(maHandle == INVALID_HANDLE) return false;
    
    double maBuffer[];
    ArraySetAsSeries(maBuffer, true);
    
    if(CopyBuffer(maHandle, 0, 0, 1, maBuffer) <= 0) return false;
    
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    
    if(currentPrice > maBuffer[0])
    {
        Print("Tendência de alta confirmada");
        return true;
    }
    else if(currentPrice < maBuffer[0])
    {
        Print("Tendência de baixa confirmada");
        return true;
    }
    
    Print("Tendência indefinida");
    return false;
}

bool CheckConfidence()
{
    // Implementa cálculo de confiança baseado em indicadores
    int rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
    if(rsiHandle == INVALID_HANDLE) return false;
    
    double rsiBuffer[];
    ArraySetAsSeries(rsiBuffer, true);
    
    if(CopyBuffer(rsiHandle, 0, 0, 1, rsiBuffer) <= 0) return false;
    
    // Cálculo simplificado de confiança
    double rsiValue = rsiBuffer[0];
    double rsiDistance = MathAbs(50.0 - rsiValue);
    double rsiRatio = (rsiDistance / 50.0);
    double confidence = (1.0 - rsiRatio);
    
    Print("Confiança calculada: ", DoubleToString(confidence, 4), " - Mínimo: ", MinimumConfidence);
    
    return (confidence >= MinimumConfidence);
}

bool CheckCoherence()
{
    if(!UseMultiTimeframe) return true;
    
    double coherence = 0.0;
    // Implementa cálculo de coerência entre timeframes
    int maHandle = iMA(_Symbol, PERIOD_CURRENT, TrendPeriod, 0, MODE_SMA, PRICE_CLOSE);
    if(maHandle == INVALID_HANDLE) return false;
    
    double maBuffer[];
    ArraySetAsSeries(maBuffer, true);
    
    if(CopyBuffer(maHandle, 0, 0, 1, maBuffer) <= 0) return false;
    
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    
    // Calcula coerência baseada na distância do preço à média móvel
    coherence = 1.0 - MathAbs(currentPrice - maBuffer[0]) / (maBuffer[0] * 0.01);
    
    Print("Coerência calculada: ", DoubleToString(coherence, 4), " - Limiar: ", CoherenceThreshold);
    
    if(coherence < CoherenceThreshold)
    {
        Print("Coerência insuficiente entre timeframes: ", DoubleToString(coherence, 4));
        return false;
    }
    return true;
}

bool CheckPositions()
{
    int totalPositions = PositionsTotal();
    if(totalPositions >= MaxPositions)
    {
        Print("Número máximo de posições atingido: ", totalPositions);
        return false;
    }
    return true;
}

double CRaioX::CalculateSignal()
{
    TradeScore score;
    score.Init();
    
    // Calcula pontuação da tendência
    double trend = CalculateTrend(PERIOD_CURRENT);
    score.trendScore = MathAbs(trend);
    
    // Calcula pontuação do momentum
    double rsiValues[];
    ArraySetAsSeries(rsiValues, true);
    CopyBuffer(m_rsiHandle, 0, 0, 2, rsiValues);
    score.momentumScore = MathAbs(rsiValues[0] - 50) / 50;
    
    // Calcula pontuação do volume
    long volumeBuffer[];
    ArraySetAsSeries(volumeBuffer, true);
    if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, 1, volumeBuffer) > 0)
    {
        double currentVolume = (double)volumeBuffer[0];
        double avgVolume = 0.0;
        for(int i = 0; i < VolumePeriod; i++)
        {
            if(CopyTickVolume(_Symbol, PERIOD_CURRENT, i, 1, volumeBuffer) > 0)
            {
                avgVolume += (double)volumeBuffer[0];
            }
        }
        avgVolume /= VolumePeriod;
        score.volumeScore = MathMin(currentVolume / avgVolume, 1.0);
    }
    
    // Calcula pontuação da volatilidade
    double atrValues[];
    ArraySetAsSeries(atrValues, true);
    CopyBuffer(m_atrHandle, 0, 0, 1, atrValues);
    score.volatilityScore = MathMin(atrValues[0] / (StopLoss * Point()), 1.0);
    
    // Calcula pontuação total
    score.totalScore = (score.trendScore * TrendWeight +
                       score.momentumScore * MomentumWeight +
                       score.volumeScore * VolumeWeight +
                       score.volatilityScore * VolatilityWeight);
    
    // Log das pontuações
    m_logger.Info(StringFormat("Pontuações - Tendência: %.2f, Momentum: %.2f, Volume: %.2f, Volatilidade: %.2f, Total: %.2f",
                              score.trendScore, score.momentumScore, score.volumeScore, score.volatilityScore, score.totalScore));
    
    // Retorna sinal baseado na pontuação total
    if(score.totalScore >= MinimumScore)
    {
        return trend > 0 ? 1.0 : -1.0;
    }
    
    return 0.0;
}

bool IsNewBar()
{
    static datetime lastBarTime = 0;
    datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
    
    if(lastBarTime == currentBarTime)
    {
        return false;
    }
    
    lastBarTime = currentBarTime;
    Print("Nova barra - Time: ", TimeToString(currentBarTime));
    return true;
}

bool CheckVolume()
{
    long volumeBuffer[];
    ArraySetAsSeries(volumeBuffer, true);
    
    // Obtém dados de volume das últimas N barras
    if(CopyTickVolume(_Symbol, PERIOD_CURRENT, 0, VolumePeriod, volumeBuffer) <= 0) {
        Print("Erro ao obter volume: ", GetLastError());
        return false;
    }
    
    // Calcula volume atual e médias
    double currentVolume = (double)volumeBuffer[0];
    double avgVolume = 0.0;
    double volumeStdDev = 0.0;
    
    // Calcula média
    for(int i = 0; i < VolumePeriod; i++) {
        avgVolume += (double)volumeBuffer[i];
    }
    avgVolume /= VolumePeriod;
    
    // Calcula desvio padrão
    for(int i = 0; i < VolumePeriod; i++) {
        volumeStdDev += MathPow((double)volumeBuffer[i] - avgVolume, 2);
    }
    volumeStdDev = MathSqrt(volumeStdDev / VolumePeriod);
    
    // Calcula Z-score do volume atual
    double volumeZScore = (currentVolume - avgVolume) / volumeStdDev;
    
    // Log detalhado
    Print("Análise de Volume:");
    Print("Volume Atual: ", currentVolume);
    Print("Média de Volume: ", avgVolume);
    Print("Desvio Padrão: ", volumeStdDev);
    Print("Z-Score: ", volumeZScore);
    
    // Verifica se o volume está significativamente abaixo da média
    if(currentVolume < avgVolume * VolumeThreshold) {
        Print("Volume abaixo do limiar relativo à média");
        return false;
    }
    
    // Verifica se o volume está muito baixo em relação ao histórico
    if(volumeZScore < -2.0) {
        Print("Volume significativamente abaixo do histórico (Z-Score < -2)");
        return false;
    }
    
    return true;
}

double GetMarketVolume()
{
    double volume = 0;
    
    // Calcula o volume médio das últimas 24 horas
    for(int i = 0; i < 24; i++)
    {
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyRates(_Symbol, PERIOD_H1, i, 1, rates) > 0)
        {
            volume += (double)rates[0].tick_volume; // Conversão explícita para double
        }
    }
    
    volume = volume / 24.0; // Volume médio por hora
    
    // Adiciona log detalhado do volume
    Print("Volume atual do mercado: ", DoubleToString(volume, 2));
    Print("Volume mínimo necessário: ", DoubleToString(VolumeMinimo, 2));
    
    return volume;
}

// Função para verificar se está no período noturno
bool IsPeriodoNoturno()
{
    datetime horaAtual = TimeCurrent();
    MqlDateTime dt;
    TimeToStruct(horaAtual, dt);
    
    return (dt.hour >= HoraInicioNoturno || dt.hour < HoraFimNoturno);
}

// Função para calcular volume mínimo dinâmico
double CalcularVolumeMinimo()
{
    if(IsPeriodoNoturno())
    {
        return VolumeMinimoNoturno;
    }
    return VolumeMinimoPadrao;
}

// Função para verificar volume com buffer
bool VerificarVolume(double volumeAtual)
{
    double volumeMinimo = CalcularVolumeMinimo();
    double volumeComBuffer = volumeMinimo * BufferVolume;
    
    if(volumeAtual >= volumeMinimo)
        return true;
        
    if(volumeAtual >= volumeComBuffer && IsPeriodoNoturno())
    {
        Print("Volume abaixo do ideal mas dentro do buffer permitido para período noturno");
        return true;
    }
    
    return false;
} 