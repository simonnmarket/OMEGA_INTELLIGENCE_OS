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

class IcebergExecutor {
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
    
    // Estrutura para armazenar ordens iceberg
    struct IcebergOrder {
        int ticket;
        double total_lots;
        double remaining_lots;
        int direction;
        double price;
        double stop_loss;
        double take_profit;
        datetime last_execution;
    };
    
    IcebergOrder m_orders[];
    
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
    
    string GetOrderSymbol(int ticket) {
        for(int i=0; i<OrdersTotal(); i++) {
            if(OrderSelect(i, SELECT_BY_POS)) {
                if(OrderTicket() == ticket) {
                    return OrderSymbol();
                }
            }
        }
        return "";
    }
    
    void CleanupCompletedOrders() {
        for(int i=ArraySize(m_orders)-1; i>=0; i--) {
            if(m_orders[i].remaining_lots <= 0) {
                ArrayRemove(m_orders, i, 1);
            }
        }
    }
    
public:
    IcebergExecutor(string symbol, int magic, int max_slices=5, int min_delay=30, int max_delay=120, double max_spread=3.0) 
        : m_symbol(symbol), m_magic(magic), m_max_slices(max_slices), m_min_delay(min_delay), m_max_delay(max_delay), m_max_spread(max_spread) {
        
        // Configuração do objeto de trading
        m_trade.SetExpertMagicNumber(magic);
        
        // Obtém parâmetros de lotagem do símbolo
        m_min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        m_max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        m_lot_step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
    }
    
    bool ExecuteIcebergOrder(int direction, double total_lots, double stop_loss=0, double take_profit=0) {
        if(!ValidateLotSize(total_lots)) return false;
        
        // Calcula tamanho de cada slice
        int slices = MathMin(m_max_slices, (int)MathCeil(total_lots / m_min_lot));
        double slice_lot = NormalizeLotSize(total_lots / slices);
        
        // Cria nova ordem iceberg
        IcebergOrder order;
        order.ticket = 0;
        order.total_lots = total_lots;
        order.remaining_lots = total_lots;
        order.direction = direction;
        order.price = (direction == OP_BUY) ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) : SymbolInfoDouble(m_symbol, SYMBOL_BID);
        order.stop_loss = stop_loss;
        order.take_profit = take_profit;
        order.last_execution = 0;
        
        // Executa primeira parte da ordem
        if(!ExecuteIcebergPart(order, slice_lot)) return false;
        
        // Adiciona ordem à lista
        ArrayResize(m_orders, ArraySize(m_orders) + 1);
        m_orders[ArraySize(m_orders)-1] = order;
        
        return true;
    }
    
    void UpdateIcebergOrders() {
        for(int i=0; i<ArraySize(m_orders); i++) {
            if(m_orders[i].remaining_lots > 0) {
                // Verifica se já passou tempo suficiente desde última execução
                if(TimeCurrent() - m_orders[i].last_execution >= m_min_delay) {
                    // Calcula próximo slice
                    double slice_lot = NormalizeLotSize(m_orders[i].remaining_lots / 2);
                    
                    // Executa próximo slice
                    if(ExecuteIcebergPart(m_orders[i], slice_lot)) {
                        m_orders[i].last_execution = TimeCurrent();
                    }
                }
            }
        }
        
        // Limpa ordens completadas
        CleanupCompletedOrders();
    }
    
    bool ExecuteIcebergPart(IcebergOrder &order, double slice_lot) {
        // Verifica spread
        if(SymbolInfoInteger(m_symbol, SYMBOL_SPREAD) > m_max_spread) return false;
        
        // Executa ordem
        bool result = false;
        if(order.direction == OP_BUY) {
            result = m_trade.Buy(slice_lot, m_symbol, 0, order.stop_loss, order.take_profit, "Iceberg Buy");
        } else {
            result = m_trade.Sell(slice_lot, m_symbol, 0, order.stop_loss, order.take_profit, "Iceberg Sell");
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
    
    bool ExecuteOrder() {
        if(!ValidateOrder()) return false;
        
        // Verifica se já existe uma ordem iceberg ativa
        for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(OrderSelect(i, SELECT_BY_POS)) {
                ulong ticket = OrderGetTicket(i);
                if(OrderGetString(ORDER_SYMBOL) == m_symbol && 
                   OrderGetInteger(ORDER_MAGIC) == m_magic) {
                    Log("Já existe uma ordem iceberg ativa", "WARNING");
                    return false;
                }
            }
        }
        
        // Executa a ordem principal
        CTrade trade;
        trade.SetExpertMagicNumber(m_magic);
        
        double price = m_type == ORDER_TYPE_BUY ? SymbolInfoDouble(m_symbol, SYMBOL_ASK) 
                                              : SymbolInfoDouble(m_symbol, SYMBOL_BID);
        
        if(!trade.OrderOpen(m_symbol, m_type, m_volume, price, 0, 0)) {
            Log("Erro ao abrir ordem principal: " + IntegerToString(trade.ResultRetcode()), "ERROR");
            return false;
        }
        
        // Executa as ordens iceberg
        for(int i = 0; i < m_iceberg_count; i++) {
            if(!trade.OrderOpen(m_symbol, m_type, m_iceberg_volume, price, 0, 0)) {
                Log("Erro ao abrir ordem iceberg " + IntegerToString(i+1) + 
                    ": " + IntegerToString(trade.ResultRetcode()), "ERROR");
                return false;
            }
        }
        
        return true;
    }
    
    bool ModifyOrder() {
        if(!ValidateOrder()) return false;
        
        CTrade trade;
        trade.SetExpertMagicNumber(m_magic);
        
        for(int i = OrdersTotal() - 1; i >= 0; i--) {
            if(OrderSelect(i, SELECT_BY_POS)) {
                ulong ticket = OrderGetTicket(i);
                if(OrderGetString(ORDER_SYMBOL) == m_symbol && 
                   OrderGetInteger(ORDER_MAGIC) == m_magic) {
                    
                    if(!trade.OrderModify(ticket, OrderGetDouble(ORDER_PRICE_OPEN), 
                                        m_sl, m_tp)) {
                        Log("Erro ao modificar ordem: " + IntegerToString(trade.ResultRetcode()), "ERROR");
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
}; 