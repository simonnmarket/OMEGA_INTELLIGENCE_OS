//+------------------------------------------------------------------+
//| Quantum Trading System                                           |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Quantum"
#property link      "https://www.quantumtrading.com"
#property version   "3.0"
#property strict

//--- Inputs
input double RiskPercent = 0.1; // Risco máximo por operação (0.1% do equity)
input int StopLossPips = 15;    // Stop loss em pips
input int TakeProfitPips = 30;  // Take profit em pips
input bool FilterNews = false;  // Desativar filtro de notícias para teste
input int EmaPeriod = 20;       // Período da EMA
input int RsiPeriod = 14;       // Período do RSI

//--- Variáveis Globais
int rsiHandle = 0;
int emaHandle = 0;
double rsiValue = 0.0;
double emaValue = 0.0;
double pointValue = 0.0;
double tickValue = 0.0;
long contractSize = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Inicializar indicadores
    rsiHandle = iRSI(_Symbol, PERIOD_M5, RsiPeriod, PRICE_CLOSE);
    emaHandle = iMA(_Symbol, PERIOD_M5, EmaPeriod, 0, MODE_SMA, PRICE_CLOSE);

    if (rsiHandle == INVALID_HANDLE || emaHandle == INVALID_HANDLE)
    {
        Print("Erro: Indicadores não inicializados!");
        return INIT_FAILED;
    }

    // Obter dados do símbolo
    pointValue = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

    // Obter tamanho mínimo do lote (contract size)
    long minVolume;
    if (!SymbolInfoInteger(_Symbol, SYMBOL_VOLUME_MIN, minVolume)) // Correção: Usar a assinatura com referência
    {
        Print("Falha ao obter o volume mínimo para ", _Symbol);
        return INIT_FAILED;
    }

    contractSize = minVolume; // Armazenar o volume mínimo

    // Verificar se o tamanho do contrato foi inicializado
    if (contractSize <= 0)
    {
        Print("Tamanho do contrato inválido para ", _Symbol);
        return INIT_FAILED;
    }

    Print("Inicialização bem-sucedida.");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    IndicatorRelease(rsiHandle);
    IndicatorRelease(emaHandle);
    Print("Desinicialização completa.");
}

//+------------------------------------------------------------------+
//| Calcular lote dinâmico                                           |
//+------------------------------------------------------------------+
double CalculateDynamicLot(double price)
{
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double riskPerTrade = equity * (RiskPercent / 100);

    // Calcular lote com base no stop loss e spread
    double lot = (riskPerTrade / (StopLossPips * tickValue)) / (pointValue * contractSize);

    // Limitar o lote a micro-lotes para segurança
    if (lot > 0.03) lot = 0.03;

    return NormalizeDouble(lot, 2);
}

//+------------------------------------------------------------------+
//| Verificar margem suficiente                                      |
//+------------------------------------------------------------------+
bool CheckMargin(double volume, ENUM_ORDER_TYPE type)
{
    double requiredMargin;
    if (!OrderCalcMargin(type, _Symbol, volume, SymbolInfoDouble(_Symbol, SYMBOL_BID), requiredMargin))
    {
        Print("Falha ao calcular margem necessária!");
        return false;
    }

    double freeMargin = AccountInfoDouble(ACCOUNT_FREEMARGIN);
    return (freeMargin > requiredMargin);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Copiar valores dos indicadores
    double buffer[];
    if (CopyBuffer(rsiHandle, 0, 0, 1, buffer) > 0) rsiValue = buffer[0];
    if (CopyBuffer(emaHandle, 0, 0, 1, buffer) > 0) emaValue = buffer[0];

    // Obter preço atual
    double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

    // Calcular lote dinâmico
    double lots = CalculateDynamicLot(price);

    // Condições de entrada simplificadas para teste
    if (price > emaValue && rsiValue < 25) // Compra (RSI oversold)
    {
        if (CheckMargin(lots, ORDER_TYPE_BUY))
            OpenOrder(ORDER_TYPE_BUY, lots, price);
    }

    if (price < emaValue && rsiValue > 75) // Venda (RSI overbought)
    {
        if (CheckMargin(lots, ORDER_TYPE_SELL))
            OpenOrder(ORDER_TYPE_SELL, lots, price);
    }
}

//+------------------------------------------------------------------+
//| Abrir ordem                                                     |
//+------------------------------------------------------------------+
void OpenOrder(ENUM_ORDER_TYPE type, double volume, double price)
{
    MqlTradeRequest request = {};
    MqlTradeResult result = {};

    request.action = TRADE_ACTION_DEAL;
    request.symbol = _Symbol;
    request.volume = volume;
    request.price = price;
    request.type = type;

    // Configurar stop loss e take profit
    if (type == ORDER_TYPE_BUY)
    {
        request.sl = NormalizeDouble(price - StopLossPips * pointValue, Digits());
        request.tp = NormalizeDouble(price + TakeProfitPips * pointValue, Digits());
    }
    else if (type == ORDER_TYPE_SELL)
    {
        request.sl = NormalizeDouble(price + StopLossPips * pointValue, Digits());
        request.tp = NormalizeDouble(price - TakeProfitPips * pointValue, Digits());
    }

    // Configurações adicionais
    request.magic = 12345;
    request.deviation = 5;
    request.type_filling = ORDER_FILLING_RETURN; // Modo padrão de preenchimento
    request.type_time = ORDER_TIME_GTC;          // Validade até cancelamento

    // Enviar solicitação de ordem
    if (OrderSend(request, result))
    {
        PrintFormat("Ordem %s %s %f aberta em %.5f",
                   type == ORDER_TYPE_BUY ? "COMPRA" : "VENDA",
                   _Symbol,
                   volume,
                   price);
    }
    else
    {
        PrintFormat("Erro ao abrir ordem: #%d (%s)",
                   result.retcode,
                   result.comment);
    }
}