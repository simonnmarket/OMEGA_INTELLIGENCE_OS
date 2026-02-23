//+------------------------------------------------------------------+
//|       Galex Quantum EA - Multi-Indicadores e Adaptativo          |
//+------------------------------------------------------------------+
#property copyright "GALEX Trading System"
#property version   "5.3"
#property strict

#include <Trade\Trade.mqh>
CTrade trade;

//================== INPUTS ==================
input double   LotSize           = 0.1;
input int      StopLoss          = 300;
input int      TakeProfit        = 600;
input int      ATR_Period        = 14;
input int      ATR_MA_Period     = 100;
input double   ATR_Multiplier    = 1.0;
input int      MaxTradesPerDay   = 5;
input int      TradingStartHour  = 0;       // Hora de início do trading (0-23)
input int      TradingEndHour    = 23;      // Hora de fim do trading (0-23)
input double   MaxDailyLossPct   = 3.0;
input double   MaxDailyProfitPct = 8.0;
input double   TrendThreshold    = 0.3;     // Reduzido para ser mais sensível
input double   RSI_Buy           = 45.0;    // Aumentado para ser mais sensível
input double   RSI_Sell          = 55.0;    // Reduzido para ser mais sensível
input int      MagicNumber       = 202531;
input bool     OnlyOnNewBar      = false;   // Desativado para permitir mais sinais
input bool     DebugMode         = true;    // Modo de depuração com logs detalhados
input bool     TestMode          = true;    // Modo de teste - força sinais para validação

// Parâmetros do modo de teste
input int      TestSignalInterval = 50;     // Intervalo em ticks para gerar sinais de teste
input bool     TestBuySignals     = true;   // Gerar sinais de compra em modo de teste
input bool     TestSellSignals    = true;   // Gerar sinais de venda em modo de teste

//================== VARIÁVEIS ==================
int      trades_today = 0;
datetime last_trade_day = 0;
double   daily_profit = 0.0, daily_loss = 0.0;
bool     trading_paused = false;
datetime last_bar_time = 0;
datetime last_signal_check_time = 0;
bool     force_signal_check = false;
int      test_tick_counter = 0;

// Handles para indicadores
int handle_ma_fast_M5 = INVALID_HANDLE;
int handle_ma_slow_M5 = INVALID_HANDLE;
int handle_ma_fast_H1 = INVALID_HANDLE;
int handle_ma_slow_H1 = INVALID_HANDLE;
int handle_rsi = INVALID_HANDLE;
int handle_atr = INVALID_HANDLE;
int handle_roc = INVALID_HANDLE;
int handle_ha_open = INVALID_HANDLE;
int handle_ha_close = INVALID_HANDLE;
int handle_ha_high = INVALID_HANDLE;
int handle_ha_low = INVALID_HANDLE;

// Estrutura de sinal
struct SignalData {
   double trend_score;
   double trend_score_h1;
   double rsi;
   double atr;
   double atr_ma;
   double roc;
   double ha_direction; // +1 bullish, -1 bearish
   int    direction;    // 1=buy, -1=sell, 0=none
   bool   is_test_signal; // Indica se o sinal foi gerado pelo modo de teste
};
SignalData g_signal;

//================== FUNÇÕES AUXILIARES ==================
double GetATR(int period) {
   if(handle_atr == INVALID_HANDLE)
      handle_atr = iATR(_Symbol, PERIOD_CURRENT, period);
   
   if(handle_atr == INVALID_HANDLE) {
      if(DebugMode) Print("Erro ao criar handle ATR: ", GetLastError());
      return 0.0;
   }
   
   double buff[];
   if(CopyBuffer(handle_atr, 0, 0, 2, buff) > 0)
      return buff[0];
   
   if(DebugMode) Print("Erro ao copiar buffer ATR: ", GetLastError());
   return 0.0;
}

double GetATR_MA(int period, int ma_period) {
   if(handle_atr == INVALID_HANDLE)
      handle_atr = iATR(_Symbol, PERIOD_CURRENT, period);
   
   if(handle_atr == INVALID_HANDLE) {
      if(DebugMode) Print("Erro ao criar handle ATR para MA: ", GetLastError());
      return 0.0;
   }
   
   double buff[];
   if(CopyBuffer(handle_atr, 0, 0, ma_period, buff) > 0) {
      double sum = 0;
      for(int i=0; i<ma_period; i++) sum += buff[i];
      return sum/ma_period;
   }
   
   if(DebugMode) Print("Erro ao copiar buffer ATR para MA: ", GetLastError());
   return 0.0;
}

double GetROC(int period) {
   if(Bars(_Symbol, PERIOD_CURRENT) <= period) return 0.0;
   
   double close[];
   if(CopyClose(_Symbol, PERIOD_CURRENT, 0, period+1, close) <= 0) {
      if(DebugMode) Print("Erro ao copiar preços de fechamento para ROC: ", GetLastError());
      return 0.0;
   }
   
   if(close[period] == 0) return 0.0;
   return ((close[0] - close[period]) / close[period]) * 100.0;
}

double GetHeikinAshiDirection() {
   // Verificar se os handles são válidos e criá-los se necessário
   if(handle_ha_open == INVALID_HANDLE || handle_ha_close == INVALID_HANDLE) {
      // Tentar criar os handles
      handle_ha_open  = iCustom(_Symbol, PERIOD_CURRENT, "Heiken_Ashi", 0);
      handle_ha_close = iCustom(_Symbol, PERIOD_CURRENT, "Heiken_Ashi", 1);
      handle_ha_high  = iCustom(_Symbol, PERIOD_CURRENT, "Heiken_Ashi", 2);
      handle_ha_low   = iCustom(_Symbol, PERIOD_CURRENT, "Heiken_Ashi", 3);
      
      // Verificar se os handles foram criados com sucesso
      if(handle_ha_open == INVALID_HANDLE || handle_ha_close == INVALID_HANDLE) {
         if(DebugMode) Print("Erro ao criar handles Heikin Ashi: ", GetLastError());
         
         // Alternativa: usar velas normais se Heikin Ashi não estiver disponível
         double open = iOpen(_Symbol, PERIOD_CURRENT, 0);
         double close = iClose(_Symbol, PERIOD_CURRENT, 0);
         
         if(close > open) return 1.0; // bullish
         else if(close < open) return -1.0; // bearish
         return 0.0;
      }
   }
   
   // Tentar copiar os buffers
   double ha_open[], ha_close[];
   if(CopyBuffer(handle_ha_open, 0, 0, 1, ha_open) > 0 &&
      CopyBuffer(handle_ha_close, 0, 0, 1, ha_close) > 0) {
      if(ha_close[0] > ha_open[0]) return 1.0; // bullish
      else if(ha_close[0] < ha_open[0]) return -1.0; // bearish
   } else {
      if(DebugMode) Print("Erro ao copiar buffers Heikin Ashi: ", GetLastError());
      
      // Alternativa: usar velas normais
      double open = iOpen(_Symbol, PERIOD_CURRENT, 0);
      double close = iClose(_Symbol, PERIOD_CURRENT, 0);
      
      if(close > open) return 1.0; // bullish
      else if(close < open) return -1.0; // bearish
   }
   
   return 0.0;
}

int GetDay(datetime dt) {
   MqlDateTime tm;
   TimeToStruct(dt, tm);
   return tm.day;
}

int GetHour(datetime dt) {
   MqlDateTime tm;
   TimeToStruct(dt, tm);
   return tm.hour;
}

int TradesToday() {
   int today = GetDay(TimeCurrent());
   if (today != GetDay(last_trade_day)) {
      trades_today = 0;
      daily_profit = 0.0;
      daily_loss = 0.0;
      last_trade_day = TimeCurrent();
      if(DebugMode) Print("Novo dia de trading, contadores resetados.");
   }
   return trades_today;
}

void RegisterTrade(double profit) {
   trades_today++;
   if (profit > 0) daily_profit += profit;
   else daily_loss += profit;
   if(DebugMode) Print("Trade registrado. Total hoje: ", trades_today);
}

bool CanTrade() {
   if (trading_paused) {
      if(DebugMode) Print("Trading pausado. Não é possível abrir novas ordens.");
      return false;
   }
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   if (daily_loss <= -MaxDailyLossPct/100.0 * balance) { 
      trading_paused = true; 
      if(DebugMode) Print("Limite de perda diária atingido. Trading pausado.");
      return false; 
   }
   
   if (daily_profit >= MaxDailyProfitPct/100.0 * balance) { 
      trading_paused = true; 
      if(DebugMode) Print("Objetivo de lucro diário atingido. Trading pausado.");
      return false; 
   }
   
   if (TradesToday() >= MaxTradesPerDay) {
      if(DebugMode) Print("Número máximo de trades diários atingido: ", MaxTradesPerDay);
      return false;
   }
   
   int hour = GetHour(TimeCurrent());
   if (hour < TradingStartHour || hour > TradingEndHour) {
      if(DebugMode) Print("Fora do horário de trading: ", hour, ". Permitido: ", TradingStartHour, "-", TradingEndHour);
      return false;
   }
   
   // Verificar se o trading automático está habilitado
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED)) {
      if(DebugMode) Print("Trading automático não está habilitado no terminal");
      return false;
   }
   
   // Verificar se o trading está habilitado para o símbolo
   if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE)) {
      if(DebugMode) Print("Trading não está habilitado para o símbolo ", _Symbol);
      return false;
   }
   
   // Verificar se o EA tem permissão para trading
   if(!AccountInfoInteger(ACCOUNT_TRADE_EXPERT)) {
      if(DebugMode) Print("Trading por EAs não está habilitado na conta");
      return false;
   }
   
   // Verificar se o mercado está aberto
   if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE)) {
      if(DebugMode) Print("Mercado fechado para o símbolo ", _Symbol);
      return false;
   }
   
   if(DebugMode) Print("Trading permitido. Verificações passaram.");
   return true;
}

//================== ATUALIZAÇÃO DO SINAL ==================
void UpdateSignal() {
   // Verificar se já passou tempo suficiente desde a última verificação
   datetime current_time = TimeCurrent();
   if(!force_signal_check && current_time - last_signal_check_time < 5) {
      return; // Evitar verificações muito frequentes
   }
   
   last_signal_check_time = current_time;
   force_signal_check = false;
   
   // Inicializa handles se necessário
   if(handle_ma_fast_M5 == INVALID_HANDLE) {
      handle_ma_fast_M5 = iMA(_Symbol, PERIOD_M5, 12, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_ma_fast_M5 == INVALID_HANDLE && DebugMode)
         Print("Erro ao criar handle MA rápida M5: ", GetLastError());
   }
   
   if(handle_ma_slow_M5 == INVALID_HANDLE) {
      handle_ma_slow_M5 = iMA(_Symbol, PERIOD_M5, 48, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_ma_slow_M5 == INVALID_HANDLE && DebugMode)
         Print("Erro ao criar handle MA lenta M5: ", GetLastError());
   }
   
   if(handle_ma_fast_H1 == INVALID_HANDLE) {
      handle_ma_fast_H1 = iMA(_Symbol, PERIOD_H1, 12, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_ma_fast_H1 == INVALID_HANDLE && DebugMode)
         Print("Erro ao criar handle MA rápida H1: ", GetLastError());
   }
   
   if(handle_ma_slow_H1 == INVALID_HANDLE) {
      handle_ma_slow_H1 = iMA(_Symbol, PERIOD_H1, 48, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_ma_slow_H1 == INVALID_HANDLE && DebugMode)
         Print("Erro ao criar handle MA lenta H1: ", GetLastError());
   }
   
   if(handle_rsi == INVALID_HANDLE) {
      handle_rsi = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
      if(handle_rsi == INVALID_HANDLE && DebugMode)
         Print("Erro ao criar handle RSI: ", GetLastError());
   }

   // Copia buffers
   double ma_fast_M5[1], ma_slow_M5[1], ma_fast_H1[1], ma_slow_H1[1], rsi_buff[1];
   bool data_ok = true;
   
   if(handle_ma_fast_M5 != INVALID_HANDLE && CopyBuffer(handle_ma_fast_M5, 0, 0, 1, ma_fast_M5) <= 0) {
      if(DebugMode) Print("Erro ao copiar buffer MA rápida M5: ", GetLastError());
      data_ok = false;
   }
   
   if(handle_ma_slow_M5 != INVALID_HANDLE && CopyBuffer(handle_ma_slow_M5, 0, 0, 1, ma_slow_M5) <= 0) {
      if(DebugMode) Print("Erro ao copiar buffer MA lenta M5: ", GetLastError());
      data_ok = false;
   }
   
   if(handle_ma_fast_H1 != INVALID_HANDLE && CopyBuffer(handle_ma_fast_H1, 0, 0, 1, ma_fast_H1) <= 0) {
      if(DebugMode) Print("Erro ao copiar buffer MA rápida H1: ", GetLastError());
      data_ok = false;
   }
   
   if(handle_ma_slow_H1 != INVALID_HANDLE && CopyBuffer(handle_ma_slow_H1, 0, 0, 1, ma_slow_H1) <= 0) {
      if(DebugMode) Print("Erro ao copiar buffer MA lenta H1: ", GetLastError());
      data_ok = false;
   }
   
   if(handle_rsi != INVALID_HANDLE && CopyBuffer(handle_rsi, 0, 0, 1, rsi_buff) <= 0) {
      if(DebugMode) Print("Erro ao copiar buffer RSI: ", GetLastError());
      data_ok = false;
   }

   // Se não conseguiu obter todos os dados, mantém o sinal anterior
   if(!data_ok) {
      if(DebugMode) Print("Falha ao obter dados dos indicadores. Mantendo sinal anterior.");
      return;
   }

   // Calcula scores
   double trend_M5 = 0.0;
   if(handle_ma_fast_M5 != INVALID_HANDLE && handle_ma_slow_M5 != INVALID_HANDLE) {
      trend_M5 = (ma_fast_M5[0] - ma_slow_M5[0]) / _Point / 100.0;
   }
   
   double trend_H1 = 0.0;
   if(handle_ma_fast_H1 != INVALID_HANDLE && handle_ma_slow_H1 != INVALID_HANDLE) {
      trend_H1 = (ma_fast_H1[0] - ma_slow_H1[0]) / _Point / 100.0;
   }
   
   double rsi = (handle_rsi != INVALID_HANDLE) ? rsi_buff[0] : 50.0;
   double atr = GetATR(ATR_Period);
   double atr_ma = GetATR_MA(ATR_Period, ATR_MA_Period);
   double roc = GetROC(12);
   double ha_dir = GetHeikinAshiDirection();

   g_signal.trend_score = trend_M5;
   g_signal.trend_score_h1 = trend_H1;
   g_signal.rsi = rsi;
   g_signal.atr = atr;
   g_signal.atr_ma = atr_ma;
   g_signal.roc = roc;
   g_signal.ha_direction = ha_dir;
   
   // Salvar direção anterior para log
   int previous_direction = g_signal.direction;
   g_signal.direction = 0;
   g_signal.is_test_signal = false;

   // Lógica combinada - mais flexível para gerar sinais
   if(atr > atr_ma * ATR_Multiplier * 0.5) { // Reduzido o multiplicador para ser mais sensível
      if(trend_M5 > TrendThreshold && rsi < RSI_Buy && (roc > 0 || ha_dir > 0)) {
         g_signal.direction = 1;
         if(DebugMode) Print("Sinal de COMPRA gerado!");
      }
      else if(trend_M5 < -TrendThreshold && rsi > RSI_Sell && (roc < 0 || ha_dir < 0)) {
         g_signal.direction = -1;
         if(DebugMode) Print("Sinal de VENDA gerado!");
      }
   }
   
   // Modo de teste - gerar sinais forçados
   if(TestMode && g_signal.direction == 0) {
      test_tick_counter++;
      
      if(test_tick_counter >= TestSignalInterval) {
         test_tick_counter = 0;
         
         // Alternar entre sinais de compra e venda
         static bool last_was_buy = false;
         
         if(!last_was_buy && TestBuySignals) {
            g_signal.direction = 1;
            g_signal.is_test_signal = true;
            last_was_buy = true;
            if(DebugMode) Print("MODO DE TESTE: Sinal de COMPRA forçado!");
         }
         else if(last_was_buy && TestSellSignals) {
            g_signal.direction = -1;
            g_signal.is_test_signal = true;
            last_was_buy = false;
            if(DebugMode) Print("MODO DE TESTE: Sinal de VENDA forçado!");
         }
         else if(TestBuySignals) {
            g_signal.direction = 1;
            g_signal.is_test_signal = true;
            last_was_buy = true;
            if(DebugMode) Print("MODO DE TESTE: Sinal de COMPRA forçado!");
         }
         else if(TestSellSignals) {
            g_signal.direction = -1;
            g_signal.is_test_signal = true;
            last_was_buy = false;
            if(DebugMode) Print("MODO DE TESTE: Sinal de VENDA forçado!");
         }
      }
   }
   
   // Log detalhado se a direção mudou
   if(previous_direction != g_signal.direction && DebugMode) {
      Print("Mudança de sinal: ", previous_direction, " -> ", g_signal.direction, 
            (g_signal.is_test_signal ? " (TESTE)" : ""));
      Print("Detalhes: Trend M5=", trend_M5, " Trend H1=", trend_H1, 
            " RSI=", rsi, " ATR=", atr, " ATR MA=", atr_ma, 
            " ROC=", roc, " HA Dir=", ha_dir);
   }
}

//================== EXECUÇÃO DE ORDENS ==================
void ExecuteSignal() {
   if (!CanTrade() || g_signal.direction == 0) {
      if(DebugMode && g_signal.direction != 0) 
         Print("Sinal disponível mas trading não permitido.");
      return;
   }
   
   if (OnlyOnNewBar && last_bar_time == iTime(_Symbol, PERIOD_CURRENT, 0)) {
      if(DebugMode) Print("Aguardando nova barra para executar sinal.");
      return;
   }

   double price = (g_signal.direction == 1) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl = (g_signal.direction == 1) ? price - StopLoss * _Point : price + StopLoss * _Point;
   double tp = (g_signal.direction == 1) ? price + TakeProfit * _Point : price - TakeProfit * _Point;

   if(DebugMode) {
      Print("Tentando executar ordem: ", (g_signal.direction == 1 ? "COMPRA" : "VENDA"), 
            (g_signal.is_test_signal ? " (TESTE)" : ""));
      Print("Preço: ", price, " SL: ", sl, " TP: ", tp, " Lote: ", LotSize);
   }

   // Configurar o magic number
   trade.SetExpertMagicNumber(MagicNumber);
   
   bool trade_ok = false;
   if (g_signal.direction == 1) {
      trade_ok = trade.Buy(LotSize, _Symbol, price, sl, tp, "Galex Quantum BUY" + (g_signal.is_test_signal ? " TEST" : ""));
   } else if (g_signal.direction == -1) {
      trade_ok = trade.Sell(LotSize, _Symbol, price, sl, tp, "Galex Quantum SELL" + (g_signal.is_test_signal ? " TEST" : ""));
   }

   if (trade_ok) {
      RegisterTrade(0.0);
      Print("Ordem aberta com sucesso. Ticket: ", trade.ResultOrder(), 
            (g_signal.is_test_signal ? " (TESTE)" : ""));
   } else {
      int error = GetLastError();
      Print("Falha ao abrir ordem. Erro:", error, " - ", ErrorDescription(error));
      ResetLastError();
   }
   
   last_bar_time = iTime(_Symbol, PERIOD_CURRENT, 0);
}

//================== DASHBOARD ==================
void ShowDashboard() {
   string test_mode_str = TestMode ? "ATIVADO" : "Desativado";
   string next_test_signal = TestMode ? StringFormat(" (Próximo em %d ticks)", TestSignalInterval - test_tick_counter) : "";
   
   string dash = StringFormat(
      "Galex Quantum EA v5.3\n\n"
      "Trend M5: %.2f | Trend H1: %.2f | RSI: %.2f\n"
      "ATR: %.5f | ATR MA: %.5f | ROC: %.2f | HA Dir: %.0f\n"
      "Sinal: %s%s\n\n"
      "Trades Hoje: %d | P&L Diário: %.2f | Pausado: %s\n"
      "Horário de Trading: %d-%d | Max Trades: %d\n\n"
      "Modo de Teste: %s%s",
      g_signal.trend_score,
      g_signal.trend_score_h1,
      g_signal.rsi,
      g_signal.atr,
      g_signal.atr_ma,
      g_signal.roc,
      g_signal.ha_direction,
      (g_signal.direction == 1 ? "COMPRA" : (g_signal.direction == -1 ? "VENDA" : "NENHUM")),
      (g_signal.is_test_signal ? " (TESTE)" : ""),
      trades_today,
      daily_profit + daily_loss,
      (trading_paused ? "SIM" : "NÃO"),
      TradingStartHour, TradingEndHour, MaxTradesPerDay,
      test_mode_str, next_test_signal
   );
   Comment(dash);
}

//================== CICLO PRINCIPAL ==================
int OnInit() {
   Print("Galex Quantum EA Multi-Indicadores v5.3 iniciado.");
   
   if(TestMode) {
      Print("AVISO: Modo de teste ATIVADO. Sinais serão gerados automaticamente a cada ", 
            TestSignalInterval, " ticks.");
   }
   
   // Configurar o objeto de trade
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(10);
   
   // Inicializar variáveis
   last_bar_time = iTime(_Symbol, PERIOD_CURRENT, 0);
   force_signal_check = true; // Forçar verificação de sinal no início
   
   // Verificar se o trading automático está habilitado
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED)) {
      Print("AVISO: Trading automático não está habilitado no terminal!");
   }
   
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
   Comment("");
   Print("Galex Quantum EA Multi-Indicadores v5.3 finalizado.");
   
   // Liberar handles de indicadores
   if(handle_ma_fast_M5 != INVALID_HANDLE) IndicatorRelease(handle_ma_fast_M5);
   if(handle_ma_slow_M5 != INVALID_HANDLE) IndicatorRelease(handle_ma_slow_M5);
   if(handle_ma_fast_H1 != INVALID_HANDLE) IndicatorRelease(handle_ma_fast_H1);
   if(handle_ma_slow_H1 != INVALID_HANDLE) IndicatorRelease(handle_ma_slow_H1);
   if(handle_rsi != INVALID_HANDLE) IndicatorRelease(handle_rsi);
   if(handle_atr != INVALID_HANDLE) IndicatorRelease(handle_atr);
   if(handle_ha_open != INVALID_HANDLE) IndicatorRelease(handle_ha_open);
   if(handle_ha_close != INVALID_HANDLE) IndicatorRelease(handle_ha_close);
   if(handle_ha_high != INVALID_HANDLE) IndicatorRelease(handle_ha_high);
   if(handle_ha_low != INVALID_HANDLE) IndicatorRelease(handle_ha_low);
}

void OnTick() {
   UpdateSignal();
   ExecuteSignal();
   ShowDashboard();
}

//================== FUNÇÕES AUXILIARES ADICIONAIS ==================
string ErrorDescription(int error_code) {
   string error_string;
   
   switch(error_code) {
      case 0:     error_string = "Operação concluída com sucesso"; break;
      case 4001:  error_string = "Erro interno inesperado"; break;
      case 4002:  error_string = "Parâmetro interno incorreto"; break;
      case 4003:  error_string = "Parâmetro inválido"; break;
      case 4004:  error_string = "Memória insuficiente"; break;
      case 4005:  error_string = "Estrutura contém objetos de strings e/ou arrays e/ou classes"; break;
      case 4006:  error_string = "Array inválido"; break;
      case 4007:  error_string = "Erro ao redimensionar array"; break;
      case 4008:  error_string = "Erro ao redimensionar string"; break;
      case 4009:  error_string = "String não inicializada"; break;
      case 4010:  error_string = "Data e/ou hora inválida"; break;
      case 4011:  error_string = "Tamanho de array solicitado excede 2GB"; break;
      case 4012:  error_string = "Ponteiro inválido"; break;
      case 4013:  error_string = "Tipo de ponteiro inválido"; break;
      case 4014:  error_string = "Função do sistema não permitida"; break;
      
      // Erros de gráfico
      case 4101:  error_string = "ID de gráfico incorreto"; break;
      case 4102:  error_string = "Gráfico não responde"; break;
      case 4103:  error_string = "Gráfico não encontrado"; break;
      case 4104:  error_string = "Gráfico não tem Expert Advisor"; break;
      case 4105:  error_string = "Falha ao abrir gráfico"; break;
      case 4106:  error_string = "Falha ao alterar gráfico"; break;
      
      // Erros de trading
      case 4751:  error_string = "Trading desabilitado"; break;
      case 4752:  error_string = "Posição não encontrada"; break;
      case 4753:  error_string = "Ordem não encontrada"; break;
      case 4754:  error_string = "Deal não encontrado"; break;
      case 4755:  error_string = "Ordem bloqueada"; break;
      case 4756:  error_string = "Apenas ordens de compra permitidas"; break;
      case 4757:  error_string = "Número de ordens excedido"; break;
      case 4758:  error_string = "Subsistema de trading ocupado"; break;
      case 4759:  error_string = "Expiração de ordem negada"; break;
      case 4760:  error_string = "Muitas requisições"; break;
      case 4761:  error_string = "Hedge proibido"; break;
      case 4762:  error_string = "Proibido por regra FIFO"; break;
      
      default: error_string = "Erro desconhecido " + IntegerToString(error_code);
   }
   
   return error_string;
}
