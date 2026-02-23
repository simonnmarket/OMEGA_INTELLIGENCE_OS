//+------------------------------------------------------------------+
//|                      Numeia_v5_1_Multi_Asset_Portfolio_EA.mq5 |
//|                              Copyright 2025, Numeia Trading System |
//|                                    v5.1 - DIVERSIFICAÇÃO MÁXIMA |
//+------------------------------------------------------------------+
#property copyright "Numeia Trading System v5.1"
#property version   "5.10"
#property description "MULTI-ASSET PORTFOLIO: 10 ativos, 5 classes"
#property description "ÍNDICES: SPX500 (20%), DAX40 (15%), NIKKEI (15%)"
#property description "COMMODITIES: XAUUSD (15%), XAGUSD (5%), UKOIL (5%), COPPER (5%)"
#property description "FOREX: EURUSD (7.5%), GBPUSD (7.5%)"
#property description "CASH: 5%"
#property description "FILOSOFIA: Executar e Monitorar. Não otimizar. Não interferir."

//--- Includes
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| INPUTS - CONFIGURAÇÃO DO PORTFOLIO (10 ATIVOS)                  |
//+------------------------------------------------------------------+
input group "=== ÍNDICES (50% - Crescimento) ==="
input string   InpIndex1 = "US500";              // Índice 1: S&P 500 (EUA)
input double   InpWeight1 = 20.0;                // Peso: 20%

input string   InpIndex2 = "GER40";              // Índice 2: Germany 40 (Europa)
input double   InpWeight2 = 15.0;                // Peso: 15%

input string   InpIndex3 = "UK100";              // Índice 3: FTSE 100 (Reino Unido)
input double   InpWeight3 = 15.0;                // Peso: 15%

input group "=== COMMODITIES (25% - Hedge Inflação) ==="
input string   InpComm1 = "XAUUSD";              // Commodity 1: Gold
input double   InpWeightC1 = 15.0;               // Peso: 15%

input string   InpComm2 = "XAGUSD";              // Commodity 2: Silver
input double   InpWeightC2 = 5.0;                // Peso: 5%

input string   InpComm3 = "UKOIL+";              // Commodity 3: Oil Brent
input double   InpWeightC3 = 5.0;                // Peso: 5%

input group "=== FOREX (20% - Dollar Hedge) ==="
input string   InpForex1 = "EURUSD";             // Forex 1: EUR/USD
input double   InpWeightF1 = 7.0;                // Peso: 7%

input string   InpForex2 = "GBPUSD";             // Forex 2: GBP/USD
input double   InpWeightF2 = 7.0;                // Peso: 7%

input string   InpForex3 = "USDJPY";             // Forex 3: USD/JPY
input double   InpWeightF3 = 6.0;                // Peso: 6%

input group "=== CASH & REBALANCEAMENTO ==="
input double   InpCashWeight = 5.0;              // Cash: 5%
input int      InpRebalanceDays = 90;            // Rebalancear a cada X dias
input double   InpDeviationThreshold = 5.0;      // Threshold de desvio (%)

input group "=== SEGURANÇA ==="
input double   InpMaxDrawdown = 30.0;            // Kill-Switch: Drawdown máximo (%)
input ulong    InpMagicNumber = 50010;           // Magic Number (v5.1)

//+------------------------------------------------------------------+
//| ESTRUTURA DE ATIVO                                               |
//+------------------------------------------------------------------+
struct Asset
{
   string symbol;
   double targetWeight;
   double currentValue;
   double targetValue;
   double deviation;
   bool initialized;
};

//+------------------------------------------------------------------+
//| VARIÁVEIS GLOBAIS                                                |
//+------------------------------------------------------------------+
CTrade trade;
datetime g_lastRebalanceTime = 0;
double g_initialBalance = 0.0;
bool g_killSwitchActive = false;
bool g_portfolioInitialized = false;

#define NUM_ASSETS 9
Asset g_assets[NUM_ASSETS];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("NUMEIA v5.1 - MULTI-ASSET PORTFOLIO");
   Print("10 Ativos, 5 Classes de Ativos");
   Print("Diversificação Máxima");
   Print("========================================");
   
   trade.SetExpertMagicNumber(InpMagicNumber);
   
   g_initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   Print("Balanço Inicial: ", g_initialBalance);
   
   // Configurar assets (9 ativos)
   g_assets[0].symbol = InpIndex1;    g_assets[0].targetWeight = InpWeight1 / 100.0;
   g_assets[1].symbol = InpIndex2;    g_assets[1].targetWeight = InpWeight2 / 100.0;
   g_assets[2].symbol = InpIndex3;    g_assets[2].targetWeight = InpWeight3 / 100.0;
   g_assets[3].symbol = InpComm1;     g_assets[3].targetWeight = InpWeightC1 / 100.0;
   g_assets[4].symbol = InpComm2;     g_assets[4].targetWeight = InpWeightC2 / 100.0;
   g_assets[5].symbol = InpComm3;     g_assets[5].targetWeight = InpWeightC3 / 100.0;
   g_assets[6].symbol = InpForex1;    g_assets[6].targetWeight = InpWeightF1 / 100.0;
   g_assets[7].symbol = InpForex2;    g_assets[7].targetWeight = InpWeightF2 / 100.0;
   g_assets[8].symbol = InpForex3;    g_assets[8].targetWeight = InpWeightF3 / 100.0;
   
   // Validar pesos (devem somar 95%)
   double totalWeight = 0;
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      totalWeight += g_assets[i].targetWeight * 100.0;
   }
   totalWeight += InpCashWeight;
   
   if(MathAbs(totalWeight - 100.0) > 0.1)
   {
      Print("ERRO: Pesos devem somar 100%. Atual: ", totalWeight);
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Verificar se símbolos existem
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      if(!SymbolSelect(g_assets[i].symbol, true))
      {
         Print("AVISO: Símbolo ", g_assets[i].symbol, " não encontrado no Market Watch");
         Print("  Tentando adicionar automaticamente...");
         
         if(!SymbolSelect(g_assets[i].symbol, true))
         {
            Print("ERRO: Não foi possível adicionar ", g_assets[i].symbol);
            Print("  AÇÃO: Adicione manualmente no Market Watch ou ajuste o nome");
            return INIT_FAILED;
         }
      }
      
      g_assets[i].initialized = false;
      Print("? ", g_assets[i].symbol, ": ", g_assets[i].targetWeight * 100, "%");
   }
   
   Print("CASH: ", InpCashWeight, "%");
   Print("Rebalanceamento: A cada ", InpRebalanceDays, " dias");
   Print("========================================");
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("========================================");
   Print("NUMEIA v5.1 - Desligando");
   Print("Razão: ", reason);
   Print("========================================");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Verificar Kill-Switch
   if(CheckKillSwitch())
   {
      if(!g_killSwitchActive)
      {
         Print("?? KILL-SWITCH ATIVADO! Drawdown > ", InpMaxDrawdown, "%");
         g_killSwitchActive = true;
         CloseAllPositions();
      }
      return;
   }
   
   // 2. Inicializar portfolio (primeira vez)
   if(!g_portfolioInitialized)
   {
      if(InitializePortfolio())
      {
         g_portfolioInitialized = true;
         g_lastRebalanceTime = TimeCurrent();
         Print("? Portfolio multi-asset inicializado com sucesso");
      }
      return;
   }
   
   // 3. Verificar se precisa rebalancear
   if(ShouldRebalance())
   {
      Print("?? Iniciando rebalanceamento...");
      RebalancePortfolio();
      g_lastRebalanceTime = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Verificar Kill-Switch                                            |
//+------------------------------------------------------------------+
bool CheckKillSwitch()
{
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double drawdown = (g_initialBalance - currentBalance) / g_initialBalance * 100.0;
   
   return (drawdown > InpMaxDrawdown);
}

//+------------------------------------------------------------------+
//| Inicializar Portfolio                                            |
//+------------------------------------------------------------------+
bool InitializePortfolio()
{
   Print("Inicializando portfolio multi-asset...");
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double cashReserve = balance * (InpCashWeight / 100.0);
   double investibleCash = balance - cashReserve;
   
   Print("Balanço: ", balance);
   Print("Cash Reserve (5%): ", cashReserve);
   Print("Disponível para investir: ", investibleCash);
   
   // Calcular valores alvo para cada ativo
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      g_assets[i].targetValue = balance * g_assets[i].targetWeight;
      Print("Target ", g_assets[i].symbol, ": ", g_assets[i].targetValue);
   }
   
   // Executar compras
   bool allSuccess = true;
   int successCount = 0;
   
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      if(BuyAsset(g_assets[i].symbol, g_assets[i].targetValue))
      {
         g_assets[i].initialized = true;
         successCount++;
      }
      else
      {
         Print("?? Falha ao comprar ", g_assets[i].symbol);
         allSuccess = false;
      }
      
      Sleep(500); // Pausa entre ordens
   }
   
   Print("========================================");
   Print("Inicialização concluída: ", successCount, "/", NUM_ASSETS, " ativos");
   Print("========================================");
   
   return (successCount >= NUM_ASSETS - 1); // Aceitar se 90%+ funcionar
}

//+------------------------------------------------------------------+
//| Comprar ativo                                                    |
//+------------------------------------------------------------------+
bool BuyAsset(string symbol, double targetValue)
{
   double price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   if(price <= 0)
   {
      Print("ERRO: Preço inválido para ", symbol);
      return false;
   }
   
   double contractSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   if(contractSize == 0) contractSize = 1.0;
   
   // Para Forex: volume em lotes
   // Para Índices/Commodities: volume baseado em contract size
   double volume = targetValue / (price * contractSize);
   volume = NormalizeVolume(symbol, volume);
   
   double minVol = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   if(volume < minVol)
   {
      Print("Volume muito baixo para ", symbol, ": ", volume, " (min: ", minVol, ")");
      return false;
   }
   
   Print("Comprando ", symbol, ": ", volume, " lotes a ", price);
   
   bool result = trade.Buy(volume, symbol, 0, 0, 0, "Numeia v5.1 Multi-Asset");
   
   if(result)
   {
      Print("? Compra executada: ", symbol);
   }
   else
   {
      Print("? Falha: ", symbol, " - Erro: ", GetLastError());
   }
   
   return result;
}

//+------------------------------------------------------------------+
//| Verificar se deve rebalancear                                    |
//+------------------------------------------------------------------+
bool ShouldRebalance()
{
   datetime currentTime = TimeCurrent();
   int daysSinceRebalance = (int)((currentTime - g_lastRebalanceTime) / 86400);
   
   if(daysSinceRebalance < InpRebalanceDays)
      return false;
   
   UpdateCurrentPositions();
   
   // Verificar desvios
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      if(MathAbs(g_assets[i].deviation) > InpDeviationThreshold)
      {
         Print("Desvio em ", g_assets[i].symbol, ": ", g_assets[i].deviation, "%");
         return true;
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Atualizar posições atuais                                        |
//+------------------------------------------------------------------+
void UpdateCurrentPositions()
{
   double totalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      g_assets[i].currentValue = GetPositionValue(g_assets[i].symbol);
      g_assets[i].targetValue = totalEquity * g_assets[i].targetWeight;
      
      double currentWeight = g_assets[i].currentValue / totalEquity * 100.0;
      double targetWeight = g_assets[i].targetWeight * 100.0;
      
      g_assets[i].deviation = currentWeight - targetWeight;
   }
}

//+------------------------------------------------------------------+
//| Obter valor de posição                                           |
//+------------------------------------------------------------------+
double GetPositionValue(string symbol)
{
   double value = 0.0;
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionSelectByTicket(PositionGetTicket(i)))
      {
         if(PositionGetString(POSITION_SYMBOL) == symbol &&
            PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            value += PositionGetDouble(POSITION_PROFIT) + 
                     PositionGetDouble(POSITION_VOLUME) * 
                     SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE) *
                     SymbolInfoDouble(symbol, SYMBOL_BID);
         }
      }
   }
   
   return value;
}

//+------------------------------------------------------------------+
//| Rebalancear portfolio                                            |
//+------------------------------------------------------------------+
void RebalancePortfolio()
{
   UpdateCurrentPositions();
   
   Print("========================================");
   Print("REBALANCEAMENTO TRIMESTRAL - 10 ATIVOS");
   Print("========================================");
   
   for(int i = 0; i < NUM_ASSETS; i++)
   {
      Print(g_assets[i].symbol, ":");
      Print("  Atual: ", g_assets[i].currentValue, " (", 
            (g_assets[i].currentValue / AccountInfoDouble(ACCOUNT_EQUITY) * 100), "%)");
      Print("  Alvo: ", g_assets[i].targetValue, " (", 
            g_assets[i].targetWeight * 100, "%)");
      Print("  Desvio: ", g_assets[i].deviation, "%");
      
      double diff = g_assets[i].targetValue - g_assets[i].currentValue;
      
      if(MathAbs(diff) > 10) // Apenas se diferença significativa
      {
         if(diff > 0)
         {
            BuyAsset(g_assets[i].symbol, diff);
         }
         else
         {
            SellAsset(g_assets[i].symbol, MathAbs(diff));
         }
         
         Sleep(500); // Pausa entre ordens
      }
   }
   
   Print("========================================");
}

//+------------------------------------------------------------------+
//| Vender ativo parcialmente                                        |
//+------------------------------------------------------------------+
bool SellAsset(string symbol, double valueToSell)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL) == symbol &&
            PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            double currentVolume = PositionGetDouble(POSITION_VOLUME);
            double price = SymbolInfoDouble(symbol, SYMBOL_BID);
            double contractSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
            if(contractSize == 0) contractSize = 1.0;
            
            double volumeToSell = valueToSell / (price * contractSize);
            volumeToSell = NormalizeVolume(symbol, volumeToSell);
            volumeToSell = MathMin(volumeToSell, currentVolume);
            
            Print("Vendendo ", volumeToSell, " de ", symbol);
            
            return trade.PositionClosePartial(ticket, volumeToSell);
         }
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Normalizar volume                                                |
//+------------------------------------------------------------------+
double NormalizeVolume(string symbol, double volume)
{
   double minVol = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxVol = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double stepVol = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   if(minVol == 0) minVol = 0.01;
   if(stepVol == 0) stepVol = 0.01;
   
   if(volume < minVol) return minVol;
   if(maxVol > 0 && volume > maxVol) return maxVol;
   
   return MathFloor(volume / stepVol) * stepVol;
}

//+------------------------------------------------------------------+
//| Fechar todas as posições                                         |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   Print("?? Fechando todas as posições (KILL-SWITCH)");
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            trade.PositionClose(ticket);
         }
      }
   }
}
//+------------------------------------------------------------------+

