//+------------------------------------------------------------------+
//|                           Numeia_v5_0_Passive_Portfolio_EA.mq5 |
//|                              Copyright 2025, Numeia Trading System |
//|                                                  Numeia v5.0 GO |
//+------------------------------------------------------------------+
#property copyright "Numeia Trading System v5.0"
#property link      "https://numeia.com"
#property version   "5.00"
#property description "PASSIVE PORTFOLIO: 80% ACWI + 15% AGG + 5% CASH"
#property description "FILOSOFIA: Executar e Monitorar. Não otimizar. Não interferir."
#property description "BASEADO EM EVIDÊNCIA: Diretiva v4.1 (Sharpe 0.384)"

//--- Includes
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| INPUTS - CONFIGURAÇÃO DO PORTFOLIO                              |
//+------------------------------------------------------------------+
input group "=== Portfolio Target (IMUTÁVEL) ==="
input string   InpSymbol1 = "SPX500";            // Símbolo 1: S&P 500 (Mercado Global)
input double   InpWeight1 = 80.0;                // Peso 1: 80% (IMUTÁVEL)

input string   InpSymbol2 = "XAUUSD";            // Símbolo 2: Gold (Hedge)
input double   InpWeight2 = 15.0;                // Peso 2: 15% (IMUTÁVEL)

input double   InpCashWeight = 5.0;              // Cash: 5% (IMUTÁVEL)

input group "=== Rebalanceamento ==="
input int      InpRebalanceDays = 90;            // Rebalancear a cada X dias (90 = trimestral)
input double   InpDeviationThreshold = 5.0;      // Threshold de desvio para rebalancear (%)

input group "=== Segurança ==="
input double   InpMaxDrawdown = 30.0;            // Kill-Switch: Drawdown máximo (%)
input ulong    InpMagicNumber = 50000;           // Magic Number (Numeia v5.0)

input group "=== Comunicação com Python ==="
input bool     InpEnablePythonControl = true;    // Habilitar controle via Python
input int      InpCheckInterval = 60;            // Intervalo de verificação (segundos)

//+------------------------------------------------------------------+
//| VARIÁVEIS GLOBAIS                                                |
//+------------------------------------------------------------------+
CTrade trade;
datetime g_lastRebalanceTime = 0;
double g_initialBalance = 0.0;
bool g_killSwitchActive = false;
bool g_portfolioInitialized = false;

// Estrutura de posição alvo
struct TargetPosition
{
   string symbol;
   double weight;
   double currentValue;
   double targetValue;
   double deviation;
};

TargetPosition g_positions[2];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("========================================");
   Print("NUMEIA v5.0 - PASSIVE PORTFOLIO");
   Print("Filosofia: Executar e Monitorar");
   Print("========================================");
   
   // Configurar magic number
   trade.SetExpertMagicNumber(InpMagicNumber);
   
   // Registrar balanço inicial
   g_initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   Print("Balanço Inicial: ", g_initialBalance);
   
   // Validar pesos (devem somar 95% - 5% é cash)
   double totalWeight = InpWeight1 + InpWeight2 + InpCashWeight;
   if(MathAbs(totalWeight - 100.0) > 0.1)
   {
      Print("ERRO: Pesos devem somar 100%. Atual: ", totalWeight);
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Inicializar estrutura de posições
   g_positions[0].symbol = InpSymbol1;
   g_positions[0].weight = InpWeight1 / 100.0;
   
   g_positions[1].symbol = InpSymbol2;
   g_positions[1].weight = InpWeight2 / 100.0;
   
   // Verificar se símbolos existem
   if(!SymbolSelect(InpSymbol1, true))
   {
      Print("ERRO: Símbolo ", InpSymbol1, " não encontrado");
      return INIT_FAILED;
   }
   
   if(!SymbolSelect(InpSymbol2, true))
   {
      Print("ERRO: Símbolo ", InpSymbol2, " não encontrado");
      return INIT_FAILED;
   }
   
   Print("Portfolio configurado:");
   Print("  ", InpSymbol1, ": ", InpWeight1, "%");
   Print("  ", InpSymbol2, ": ", InpWeight2, "%");
   Print("  CASH: ", InpCashWeight, "%");
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
   Print("NUMEIA v5.0 - Desligando");
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
         Print("🚨 KILL-SWITCH ATIVADO! Drawdown > ", InpMaxDrawdown, "%");
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
         Print("✅ Portfolio inicializado com sucesso");
      }
      return;
   }
   
   // 3. Verificar se precisa rebalancear
   if(ShouldRebalance())
   {
      Print("🔄 Iniciando rebalanceamento...");
      RebalancePortfolio();
      g_lastRebalanceTime = TimeCurrent();
   }
   
   // 4. Verificar comandos Python (se habilitado)
   if(InpEnablePythonControl)
   {
      static datetime lastCheck = 0;
      if(TimeCurrent() - lastCheck > InpCheckInterval)
      {
         CheckPythonCommands();
         lastCheck = TimeCurrent();
      }
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
//| Inicializar Portfolio (primeira compra)                          |
//+------------------------------------------------------------------+
bool InitializePortfolio()
{
   Print("Inicializando portfolio...");
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   Print("Balanço disponível: ", balance);
   
   // Calcular valores alvo
   for(int i = 0; i < 2; i++)
   {
      g_positions[i].targetValue = balance * g_positions[i].weight;
      Print("Target ", g_positions[i].symbol, ": ", g_positions[i].targetValue);
   }
   
   // Executar compras iniciais
   bool success = true;
   
   for(int i = 0; i < 2; i++)
   {
      if(!BuyPosition(g_positions[i].symbol, g_positions[i].targetValue))
      {
         Print("ERRO ao comprar ", g_positions[i].symbol);
         success = false;
      }
   }
   
   return success;
}

//+------------------------------------------------------------------+
//| Comprar posição                                                  |
//+------------------------------------------------------------------+
bool BuyPosition(string symbol, double targetValue)
{
   double price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   if(price <= 0)
   {
      Print("ERRO: Preço inválido para ", symbol);
      return false;
   }
   
   // Calcular lotes
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double lotSize = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   
   // Volume baseado no valor alvo
   double volume = NormalizeVolume(symbol, targetValue / price);
   
   if(volume < lotSize)
   {
      Print("Volume muito baixo para ", symbol, ": ", volume);
      return false;
   }
   
   Print("Comprando ", symbol, ": ", volume, " lotes a ", price);
   
   bool result = trade.Buy(volume, symbol, price, 0, 0, "Numeia v5.0 Initial");
   
   if(result)
   {
      Print("✅ Compra executada: ", symbol);
   }
   else
   {
      Print("❌ Falha na compra: ", symbol, " - Erro: ", GetLastError());
   }
   
   return result;
}

//+------------------------------------------------------------------+
//| Verificar se deve rebalancear                                    |
//+------------------------------------------------------------------+
bool ShouldRebalance()
{
   // Verificar tempo desde último rebalanceamento
   datetime currentTime = TimeCurrent();
   int daysSinceRebalance = (int)((currentTime - g_lastRebalanceTime) / 86400);
   
   if(daysSinceRebalance < InpRebalanceDays)
      return false;
   
   // Calcular desvios atuais
   UpdateCurrentPositions();
   
   // Verificar se algum desvio excede threshold
   for(int i = 0; i < 2; i++)
   {
      if(MathAbs(g_positions[i].deviation) > InpDeviationThreshold)
      {
         Print("Desvio detectado em ", g_positions[i].symbol, ": ", 
               g_positions[i].deviation, "%");
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
   
   for(int i = 0; i < 2; i++)
   {
      g_positions[i].currentValue = GetPositionValue(g_positions[i].symbol);
      g_positions[i].targetValue = totalEquity * g_positions[i].weight;
      
      double currentWeight = g_positions[i].currentValue / totalEquity * 100.0;
      double targetWeight = g_positions[i].weight * 100.0;
      
      g_positions[i].deviation = currentWeight - targetWeight;
   }
}

//+------------------------------------------------------------------+
//| Obter valor atual de uma posição                                 |
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
            value += PositionGetDouble(POSITION_VOLUME) * 
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
   Print("REBALANCEAMENTO TRIMESTRAL");
   Print("========================================");
   
   for(int i = 0; i < 2; i++)
   {
      Print(g_positions[i].symbol, ":");
      Print("  Atual: ", g_positions[i].currentValue);
      Print("  Alvo: ", g_positions[i].targetValue);
      Print("  Desvio: ", g_positions[i].deviation, "%");
      
      double diff = g_positions[i].targetValue - g_positions[i].currentValue;
      
      if(MathAbs(diff) > 10) // Apenas se diferença > 10 EUR
      {
         if(diff > 0)
         {
            // Comprar mais
            BuyPosition(g_positions[i].symbol, diff);
         }
         else
         {
            // Vender parte
            SellPosition(g_positions[i].symbol, MathAbs(diff));
         }
      }
   }
   
   Print("========================================");
}

//+------------------------------------------------------------------+
//| Vender posição parcial                                           |
//+------------------------------------------------------------------+
bool SellPosition(string symbol, double valueToSell)
{
   double price = SymbolInfoDouble(symbol, SYMBOL_BID);
   double volumeToSell = NormalizeVolume(symbol, valueToSell / price);
   
   // Encontrar posição
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
         if(PositionGetString(POSITION_SYMBOL) == symbol &&
            PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            double currentVolume = PositionGetDouble(POSITION_VOLUME);
            double sellVol = MathMin(volumeToSell, currentVolume);
            
            Print("Vendendo ", sellVol, " de ", symbol);
            
            return trade.PositionClosePartial(ticket, sellVol);
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
   
   if(volume < minVol) return minVol;
   if(volume > maxVol) return maxVol;
   
   return MathFloor(volume / stepVol) * stepVol;
}

//+------------------------------------------------------------------+
//| Fechar todas as posições (Kill-Switch)                           |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   Print("🚨 Fechando todas as posições (KILL-SWITCH)");
   
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
//| Verificar comandos Python                                        |
//+------------------------------------------------------------------+
void CheckPythonCommands()
{
   // Verificar arquivo de comando
   string filename = "NumeiaCommand.json";
   int handle = FileOpen(filename, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   
   if(handle == INVALID_HANDLE)
      return; // Sem comandos
   
   string content = "";
   while(!FileIsEnding(handle))
   {
      content += FileReadString(handle);
   }
   FileClose(handle);
   
   // Deletar arquivo (comando consumido)
   FileDelete(filename, FILE_COMMON);
   
   // Processar comando (exemplo: force rebalance)
   if(StringFind(content, "REBALANCE") >= 0)
   {
      Print("📥 Comando Python recebido: REBALANCE");
      RebalancePortfolio();
      g_lastRebalanceTime = TimeCurrent();
   }
}

//+------------------------------------------------------------------+

