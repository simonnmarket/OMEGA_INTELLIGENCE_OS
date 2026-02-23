#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\DealInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include "..\Core\TimeframeHierarchy.mqh"
#include "..\Core\VolatilityAnalysis.mqh"

class StealthManager {
private:
    CTrade m_trade;
    string m_symbol;
    int m_magic;
    double m_min_lot;
    double m_max_lot;
    double m_lot_step;
    int m_max_slices;
    int m_min_delay;
    int m_max_delay;
    double m_max_spread;
    double m_volume_threshold;
    long m_magic_number;
    double m_volume;
    double m_sl;
    double m_tp;
    ENUM_ORDER_TYPE m_type;
    string m_log_file;
    
    // Estrutura para ordens stealth
    struct StealthOrder {
        int ticket;
        double total_lots;
        double remaining_lots;
        int direction;
        double entry_price;
        double target_price;
        double stop_loss;
        double take_profit;
        datetime last_execution;
        int slice_count;
    };
    
    StealthOrder m_orders[];
    
    // Métodos privados
    bool ValidateLotSize(double lot) {
        if(lot < m_min_lot || lot > m_max_lot) return false;
        if(MathMod(lot, m_lot_step) != 0) return false;
        return true;
    }
    
    double NormalizeLotSize(double lot) {
        lot = MathFloor(lot / m_lot_step) * m_lot_step;
        lot = MathMax(m_min_lot, MathMin(m_max_lot, lot));
        return lot;
    }
    
    double CalculateSliceSize(double remaining_lots, int slice_count) {
        double slice = remaining_lots / (m_max_slices - slice_count);
        return NormalizeLotSize(slice);
    }
    
    int CalculateDelay() {
        return m_min_delay + MathRand() % (m_max_delay - m_min_delay);
    }
    
    bool CheckVolumeProfile() {
        double volume = iVolume(m_symbol, PERIOD_M1, 0);
        double avg_volume = 0;
        
        for(int i=1; i<=20; i++) {
            avg_volume += iVolume(m_symbol, PERIOD_M1, i);
        }
        avg_volume /= 20.0;
        
        return volume < avg_volume * m_volume_threshold;
    }
    
    void CleanupCompletedOrders() {
        for(int i=ArraySize(m_orders)-1; i>=0; i--) {
            if(m_orders[i].remaining_lots <= 0) {
                ArrayRemove(m_orders, i, 1);
            }
        }
    }
    
    void Log(string message, string severity = "INFO") {
        int handle = FileOpen(m_log_file, FILE_WRITE|FILE_TXT|FILE_COMMON, ';');
        if(handle != INVALID_HANDLE) {
            string log_entry = StringFormat("[%s][%s] %s", 
                TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), 
                severity, 
                message);
            FileWrite(handle, log_entry);
            FileClose(handle);
        }
    }
    
    bool ValidateOrder() {
        if(m_volume <= 0) {
            Log("Volume inválido", "ERROR");
            return false;
        }
        
        if(!SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE)) {
            Log("Símbolo inválido: " + m_symbol, "ERROR");
            return false;
        }
        
        return true;
    }

public:
    StealthManager(string symbol, double volume, double sl, double tp, 
                  ENUM_ORDER_TYPE type, long magic_number = 123456) 
        : m_symbol(symbol), m_volume(volume), m_sl(sl), m_tp(tp),
          m_type(type), m_magic_number(magic_number) {
        m_log_file = "StealthManager_Log_" + IntegerToString(GetTickCount()) + ".txt";
        
        // Configuração do objeto de trading
        m_trade.SetExpertMagicNumber(magic_number);
        
        // Obtém parâmetros de lotagem do símbolo
        m_min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        m_max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        m_lot_step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
    }
    
    bool ExecuteOrder() {
        if(!ValidateOrder()) return false;
        
        CTrade trade;
        trade.SetExpertMagicNumber(m_magic_number);
        
        double price = m_type == ORDER_TYPE_BUY ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) 
                                               : SymbolInfoDouble(m_symbol, SYMBOL_BID);
        
        if(!trade.OrderOpen(m_symbol, m_type, m_volume, price, m_sl, m_tp)) {
            Log("Erro ao abrir ordem: " + IntegerToString((int)trade.ResultRetcode()), "ERROR");
            return false;
        }
        
        return true;
    }
    
    bool ModifyOrder() {
        if(!ValidateOrder()) return false;
        
        CTrade trade;
        trade.SetExpertMagicNumber(m_magic_number);
        
        for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(OrderSelect(i, SELECT_BY_POS)) {
                ulong ticket = OrderGetTicket(i);
                if(OrderGetString(ORDER_SYMBOL) == m_symbol && 
                   OrderGetInteger(ORDER_MAGIC) == m_magic_number) {
                    
                    if(!trade.OrderModify(ticket, OrderGetDouble(ORDER_PRICE_OPEN), 
                                        m_sl, m_tp)) {
                        Log("Erro ao modificar ordem: " + IntegerToString((int)trade.ResultRetcode()), "ERROR");
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
    
    bool ExecuteStealthOrder(int direction, double total_lots, double stop_loss=0, double take_profit=0) {
        if(!ValidateLotSize(total_lots)) return false;
        
        // Verifica condições de mercado
        if(SymbolInfoInteger(m_symbol, SYMBOL_SPREAD) > m_max_spread) return false;
        if(!CheckVolumeProfile()) return false;
        
        // Calcula preço alvo
        double entry_price = (direction == ORDER_TYPE_BUY) ? 
            SymbolInfoDouble(m_symbol, SYMBOL_ASK) : 
            SymbolInfoDouble(m_symbol, SYMBOL_BID);
            
        double target_price = entry_price + (direction * 10 * SymbolInfoDouble(m_symbol, SYMBOL_POINT));
        
        // Cria nova ordem stealth
        StealthOrder order;
        order.ticket = 0;
        order.total_lots = total_lots;
        order.remaining_lots = total_lots;
        order.direction = direction;
        order.entry_price = entry_price;
        order.target_price = target_price;
        order.stop_loss = stop_loss;
        order.take_profit = take_profit;
        order.last_execution = 0;
        order.slice_count = 0;
        
        // Executa primeira parte da ordem
        double first_slice = CalculateSliceSize(total_lots, 0);
        if(!ExecuteStealthSlice(order, first_slice)) return false;
        
        // Adiciona ordem à lista
        ArrayResize(m_orders, ArraySize(m_orders) + 1);
        m_orders[ArraySize(m_orders)-1] = order;
        
        return true;
    }
    
    void UpdateStealthOrders() {
        for(int i=0; i<ArraySize(m_orders); i++) {
            if(m_orders[i].remaining_lots > 0) {
                // Verifica se já passou tempo suficiente desde última execução
                if(TimeCurrent() - m_orders[i].last_execution >= m_min_delay) {
                    // Verifica condições de mercado
                    if(SymbolInfoInteger(m_symbol, SYMBOL_SPREAD) <= m_max_spread && 
                       CheckVolumeProfile()) {
                        
                        // Calcula próximo slice
                        double slice_lot = CalculateSliceSize(m_orders[i].remaining_lots, 
                                                            m_orders[i].slice_count);
                        
                        // Executa próximo slice
                        if(ExecuteStealthSlice(m_orders[i], slice_lot)) {
                            m_orders[i].last_execution = TimeCurrent();
                            m_orders[i].slice_count++;
                        }
                    }
                }
            }
        }
        
        // Limpa ordens completadas
        CleanupCompletedOrders();
    }
    
    bool ExecuteStealthSlice(StealthOrder &order, double slice_lot) {
        // Verifica se o preço atual está próximo do alvo
        double current_price = (order.direction == ORDER_TYPE_BUY) ? 
            SymbolInfoDouble(m_symbol, SYMBOL_ASK) : 
            SymbolInfoDouble(m_symbol, SYMBOL_BID);
            
        if(MathAbs(current_price - order.target_price) > 
           SymbolInfoDouble(m_symbol, SYMBOL_POINT) * 5) {
            return false;
        }
        
        // Executa ordem com delay aleatório
        Sleep(CalculateDelay());
        
        bool result = false;
        if(order.direction == ORDER_TYPE_BUY) {
            result = m_trade.Buy(slice_lot, m_symbol, 0, order.stop_loss, order.take_profit, "Stealth Buy");
        } else {
            result = m_trade.Sell(slice_lot, m_symbol, 0, order.stop_loss, order.take_profit, "Stealth Sell");
        }
        
        if(result) {
            order.remaining_lots -= slice_lot;
            if(order.ticket == 0) {
                order.ticket = m_trade.ResultOrder();
            }
        }
        
        return result;
    }
    
    int GetActiveOrdersCount() {
        return ArraySize(m_orders);
    }
    
    double GetRemainingLots(int ticket) {
        for(int i=0; i<ArraySize(m_orders); i++) {
            if(m_orders[i].ticket == ticket) {
                return m_orders[i].remaining_lots;
            }
        }
        return 0;
    }
    
    void SetVolumeThreshold(double threshold) {
        m_volume_threshold = threshold;
    }
    
    double GetVolumeThreshold() {
        return m_volume_threshold;
    }
}; 