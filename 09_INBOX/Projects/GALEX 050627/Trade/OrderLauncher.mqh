//+------------------------------------------------------------------+
//| OrderLauncher.mqh - Sistema de Execução Institucional Avançado   |
//| v17.0 - Execução Algorítmica com Controle de Impacto de Mercado  |
//+------------------------------------------------------------------+

#include <Trade\Trade.mqh>
#include <Math\Alglib\alglib.mqh>

class OrderLauncher {
private:
   CTrade m_trade;
   int m_magic;
   double m_max_slippage;
   double m_max_impact;
   bool m_use_vwap;
   bool m_use_twap;
   double m_order_size_limit;
   
   // Estrutura para métricas de execução
   struct ExecutionMetrics {
      double avg_fill_price;
      double slippage;
      double market_impact;
      datetime execution_time;
   } m_last_execution;
   
   // Calcula impacto de mercado estimado
   double EstimateMarketImpact(string symbol, double volume) {
      double daily_volume = iVolume(symbol, PERIOD_D1, 0);
      return (volume / daily_volume) * 100; // % do volume diário
   }
   
   // Execução TWAP (Time Weighted Average Price)
   bool ExecuteTWAP(string symbol, int direction, double total_lots, int duration_sec, double sl, double tp) {
      int slices = (int)(duration_sec / 30); // Slice a cada 30 segundos
      double slice_lot = total_lots / slices;
      datetime end_time = TimeCurrent() + duration_sec;
      
      while(TimeCurrent() < end_time && !IsStopped()) {
         if(SendOrder(symbol, direction, slice_lot, 0, sl, tp, "TWAP Execution")) {
            Sleep(30000); // Espera 30s entre execuções
         } else {
            Print("Falha na execução TWAP para ", symbol);
            return false;
         }
      }
      return true;
   }
   
   // Execução VWAP (Volume Weighted Average Price)
   bool ExecuteVWAP(string symbol, int direction, double total_lots, int duration_min, double sl, double tp) {
      // Implementação simplificada - versão real usaria book de ofertas
      int slices = duration_min * 2; // Slice a cada 30s
      double slice_lot = total_lots / slices;
      datetime end_time = TimeCurrent() + duration_min * 60;
      
      while(TimeCurrent() < end_time && !IsStopped()) {
         double volume_factor = 1.0 + (iVolume(symbol, PERIOD_M1, 0) / iVolume(symbol, PERIOD_M5, 0);
         double adjusted_lot = slice_lot * volume_factor;
         
         if(SendOrder(symbol, direction, adjusted_lot, 0, sl, tp, "VWAP Execution")) {
            Sleep(30000);
         } else {
            Print("Falha na execução VWAP para ", symbol);
            return false;
         }
      }
      return true;
   }

public:
   OrderLauncher(int magic = 20250601, double max_slippage = 3.0, double max_impact = 0.5) : 
      m_magic(magic), m_max_slippage(max_slippage), m_max_impact(max_impact) {
      m_trade.SetExpertMagicNumber(magic);
      m_use_vwap = false;
      m_use_twap = false;
      m_order_size_limit = 50.0; // 50 lotes por padrão
      ArrayInitialize(m_last_execution, 0);
   }
   
   // Configura método de execução
   void SetExecutionMethod(bool use_vwap, bool use_twap) {
      m_use_vwap = use_vwap;
      m_use_twap = use_twap;
      
      if(m_use_vwap && m_use_twap) {
         m_use_twap = false; // Precedência para VWAP
         Print("AVISO: Configurado apenas VWAP (precedência sobre TWAP)");
      }
   }
   
   // Envia ordem com validação avançada
   bool SendOrder(string symbol, int direction, double lot, double price = 0, double sl = 0, double tp = 0, string comment = "") {
      // 1. Validação básica
      if(!SymbolSelect(symbol, true)) {
         Print("Erro: Símbolo ", symbol, " não disponível");
         return false;
      }
      
      // 2. Verifica limite de tamanho
      if(lot > m_order_size_limit) {
         Print("Erro: Tamanho da ordem ", lot, " excede limite de ", m_order_size_limit);
         return false;
      }
      
      // 3. Calcula impacto de mercado
      double impact = EstimateMarketImpact(symbol, lot);
      if(impact > m_max_impact) {
         Print("AVISO: Impacto de mercado ", DoubleToString(impact,2), "% excede limite");
         if(!m_use_vwap && !m_use_twap) {
            Print("Convertendo para execução TWAP");
            return ExecuteTWAP(symbol, direction, lot, 300, sl, tp); // 5 minutos
         }
      }
      
      // 4. Execução direta ou algorítmica
      if(m_use_vwap) {
         return ExecuteVWAP(symbol, direction, lot, 5, sl, tp); // 5 minutos
      }
      else if(m_use_twap) {
         return ExecuteTWAP(symbol, direction, lot, 300, sl, tp); // 5 minutos
      }
      else {
         // Execução imediata
         double entry_price = (price == 0) ? GetEntryPrice(symbol, direction) : price;
         double expected_slippage = CalculateExpectedSlippage(symbol, lot);
         
         if(expected_slippage > m_max_slippage) {
            Print("AVISO: Slippage esperado ", DoubleToString(expected_slippage,1), " pips excede limite");
            return false;
         }
         
         bool result = (direction == 1) 
            ? m_trade.Buy(lot, symbol, entry_price, sl, tp, comment)
            : m_trade.Sell(lot, symbol, entry_price, sl, tp, comment);
         
         if(result) {
            // Atualiza métricas de execução
            m_last_execution.avg_fill_price = m_trade.ResultPrice();
            m_last_execution.slippage = MathAbs(entry_price - m_trade.ResultPrice()) / _Point;
            m_last_execution.market_impact = impact;
            m_last_execution.execution_time = TimeCurrent();
         }
         
         return result;
      }
   }
   
   // Cálculo de slippage esperado
   double CalculateExpectedSlippage(string symbol, double volume) {
      double spread = SymbolInfoDouble(symbol, SYMBOL_ASK) - SymbolInfoDouble(symbol, SYMBOL_BID);
      double liquidity_factor = iVolume(symbol, PERIOD_M1, 0) / (volume * 100000 + 1e-8);
      return spread * (1.0 + 1.0/liquidity_factor) / _Point;
   }
   
   // Fechamento inteligente de posições
   void ClosePositionsSmart(string symbol, int direction = 0) {
      for(int i = PositionsTotal() - 1; i >= 0; i--) {
         if(PositionGetSymbol(i) == symbol && 
            (direction == 0 || PositionGetInteger(POSITION_TYPE) == direction) &&
            PositionGetInteger(POSITION_MAGIC) == m_magic) {
            
            if(EstimateMarketImpact(symbol, PositionGetDouble(POSITION_VOLUME)) > m_max_impact * 0.5) {
               // Fechamento TWAP para grandes posições
               ExecuteTWAP(symbol, -PositionGetInteger(POSITION_TYPE), 
                          PositionGetDouble(POSITION_VOLUME), 180, 0, 0); // 3 minutos
            } else {
               // Fechamento imediato
               m_trade.PositionClose(PositionGetTicket(i));
            }
         }
      }
   }
   
   // Métricas da última execução
   const ExecutionMetrics& GetLastExecutionMetrics() const {
      return m_last_execution;
   }
   
   // Configura limite de tamanho de ordem
   void SetOrderSizeLimit(double max_lots) {
      m_order_size_limit = max_lots;
   }
   
   // Obtém o ticket da última ordem executada
   ulong GetLastOrderTicket() const {
      return m_trade.ResultOrder();
   }
   
   // Obtém o preço médio de preenchimento
   double GetLastFillPrice() const {
      return m_trade.ResultPrice();
   }
};