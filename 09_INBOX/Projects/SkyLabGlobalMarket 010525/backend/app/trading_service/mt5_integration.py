# backend/app/trading_service.py
import MetaTrader5 as mt5

def execute_order(symbol, lot, side):
    if not mt5.initialize():
        return {"error": "Falha na conexão com MetaTrader 5"}

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return {"error": f"Símbolo {symbol} não encontrado."}

    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)

    price = symbol_info.ask if side == "buy" else symbol_info.bid
    order_type = mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": 0.0,
        "tp": 0.0,
        "deviation": 10,
        "magic": 10032024,
        "comment": "Ordem Automatizada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return {
            "status": "failed",
            "retcode": result.retcode,
            "comment": result.comment,
            "request": request
        }

    return {
        "status": "success",
        "order": result.order,
        "price": result.price,
        "symbol": symbol,
        "volume": lot
    } 