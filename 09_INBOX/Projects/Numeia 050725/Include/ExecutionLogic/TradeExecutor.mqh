//+------------------------------------------------------------------+
//| TradeExecutor.mqh - Módulo de Execução Inteligente de Ordens    |
//+------------------------------------------------------------------+
#pragma once

#include "../../Config/GlobalConfig.mqh"
#include "../../Config/RiskConfig.mqh"
#include "../../Utils/Log.mqh"
#include "../../Utils/PriceUtils.mqh"
#include "../../Utils/TimeUtils.mqh"

class TradeExecutor {
private:
    double baseLot;
    double stopLossPoints;
    double takeProfitPoints;
    bool enableTrailing;
    bool enableBreakEven;

public:
    void Initialize() {
        baseLot           = GlobalConfig::BaseLot;
        stopLossPoints    = GlobalConfig::StopLossPoints;
        takeProfitPoints  = GlobalConfig::TakeProfitPoints;
        enableTrailing    = GlobalConfig::EnableTrailingStop;
        enableBreakEven   = GlobalConfig::EnableBreakEven;

        Log("🧠 TradeExecutor inicializado com parâmetros globais.");
    }

    void ExecuteOrder(string symbol, ENUM_ORDER_TYPE type, double lotMultiplier = 1.0) {
        double lot     = NormalizeDouble(baseLot * lotMultiplier, 2);
        double price   = (type == ORDER_TYPE_BUY) ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
        double slPrice = (type == ORDER_TYPE_BUY) ? price - stopLossPoints * _Point : price + stopLossPoints * _Point;
        double tpPrice = (type == ORDER_TYPE_BUY) ? price + takeProfitPoints * _Point : price - takeProfitPoints * _Point;

        MqlTradeRequest request;
        MqlTradeResult result;
        ZeroMemory(request);
        ZeroMemory(result);

        request.action   = TRADE_ACTION_DEAL;
        request.symbol   = symbol;
        request.volume   = lot;
        request.type     = type;
        request.price    = price;
        request.sl       = slPrice;
        request.tp       = tpPrice;
        request.deviation= 10;
        request.magic    = GlobalConfig::MagicNumber;
        request.comment  = "Numeia Execução Inteligente";

        if(!OrderSend(request, result)) {
            Log("❌ Falha ao enviar ordem. Erro: " + IntegerToString(GetLastError()));
            return;
        }

        if(result.retcode != TRADE_RETCODE_DONE) {
            Log("⚠️ Ordem não executada corretamente. Código: " + IntegerToString(result.retcode));
        } else {
            Log("✅ Ordem executada com sucesso. Ticket: " + IntegerToString(result.order));
        }
    }

    void ManageTrailingStop(string symbol, ulong ticket) {
        if (!enableTrailing) return;

        double trailingStart = RiskConfig::TrailingStartPoints * _Point;
        double trailingStep  = RiskConfig::TrailingStepPoints * _Point;

        double price = SymbolInfoDouble(symbol, SYMBOL_BID);
        double stopLossNew;

        if (PositionGetTicket(ticket) && PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
            double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            stopLossNew = price - trailingStart;

            if ((price - openPrice) > trailingStart) {
                ModifyPositionSLTP(ticket, stopLossNew, 0.0);
            }
        }

        // Implementação para SELL se necessário...
    }

    void ApplyBreakEven(string symbol, ulong ticket) {
        if (!enableBreakEven) return;

        if (PositionGetTicket(ticket) && PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
            double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            double price     = SymbolInfoDouble(symbol, SYMBOL_BID);
            double distance  = price - openPrice;

            if (distance > RiskConfig::BreakEvenTriggerPoints * _Point) {
                ModifyPositionSLTP(ticket, openPrice + RiskConfig::BreakEvenOffsetPoints * _Point, 0.0);
                Log("🎯 Break-even aplicado com sucesso.");
            }
        }

        // Implementação para SELL se necessário...
    }

private:
    void ModifyPositionSLTP(ulong ticket, double newSL, double newTP) {
        MqlTradeRequest request;
        MqlTradeResult result;
        ZeroMemory(request);
        ZeroMemory(result);

        request.action = TRADE_ACTION_SLTP;
        request.position = ticket;
        request.sl = NormalizeDouble(newSL, _Digits);
        request.tp = (newTP > 0.0) ? NormalizeDouble(newTP, _Digits) : 0.0;

        if(!OrderSend(request, result)) {
            Log("❌ Erro ao modificar SL/TP. Código: " + IntegerToString(GetLastError()));
        } else {
            Log("🔄 SL/TP atualizados para o ticket: " + IntegerToString(ticket));
        }
    }
};
