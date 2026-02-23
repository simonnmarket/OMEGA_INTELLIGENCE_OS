#!/usr/bin/env python3
"""
Verificar Códigos de Retorno do MT5
"""

import MetaTrader5 as mt5

mt5.initialize()

print("=" * 70)
print("CÓDIGOS DE RETORNO DO MT5")
print("=" * 70)
print()

retcodes = [
    mt5.TRADE_RETCODE_REQUOTE,
    mt5.TRADE_RETCODE_REJECT,
    mt5.TRADE_RETCODE_CANCEL,
    mt5.TRADE_RETCODE_PLACED,
    mt5.TRADE_RETCODE_DONE,
    mt5.TRADE_RETCODE_DONE_PARTIAL,
    mt5.TRADE_RETCODE_ERROR,
    mt5.TRADE_RETCODE_TIMEOUT,
    mt5.TRADE_RETCODE_INVALID,
    mt5.TRADE_RETCODE_INVALID_VOLUME,
    mt5.TRADE_RETCODE_INVALID_PRICE,
    mt5.TRADE_RETCODE_INVALID_STOPS,
    mt5.TRADE_RETCODE_TRADE_DISABLED,
    mt5.TRADE_RETCODE_MARKET_CLOSED,
    mt5.TRADE_RETCODE_NO_MONEY,
    mt5.TRADE_RETCODE_PRICE_CHANGED,
    mt5.TRADE_RETCODE_PRICE_OFF,
    mt5.TRADE_RETCODE_INVALID_EXPIRATION,
    mt5.TRADE_RETCODE_ORDER_CHANGED,
    mt5.TRADE_RETCODE_TOO_MANY_REQUESTS,
    mt5.TRADE_RETCODE_NO_CHANGES,
    mt5.TRADE_RETCODE_SERVER_DISABLES_AT,
    mt5.TRADE_RETCODE_CLIENT_DISABLES_AT,
    mt5.TRADE_RETCODE_LOCKED,
    mt5.TRADE_RETCODE_FROZEN,
    mt5.TRADE_RETCODE_INVALID_FILL,
    mt5.TRADE_RETCODE_CONNECTION,
    mt5.TRADE_RETCODE_ONLY_REAL,
    mt5.TRADE_RETCODE_LIMIT_ORDERS,
    mt5.TRADE_RETCODE_LIMIT_VOLUME,
    mt5.TRADE_RETCODE_INVALID_ORDER,
    mt5.TRADE_RETCODE_POSITION_CLOSED,
]

print("Códigos de retorno:")
for code in retcodes:
    print(f"  {code}: {repr(code)}")

print()
print("Códigos de sucesso comuns:")
print(f"  TRADE_RETCODE_DONE: {mt5.TRADE_RETCODE_DONE}")
print(f"  TRADE_RETCODE_DONE_PARTIAL: {mt5.TRADE_RETCODE_DONE_PARTIAL}")
print(f"  TRADE_RETCODE_PLACED: {mt5.TRADE_RETCODE_PLACED}")
print()

# Verificar o que é 10009
print("Verificando código 10009...")
if hasattr(mt5, 'TRADE_RETCODE'):
    print(f"  TRADE_RETCODE constante: {mt5.TRADE_RETCODE}")
    
# Testar ordem
symbol = "EURUSD"
tick = mt5.symbol_info_tick(symbol)
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": 0.01,
    "type": mt5.ORDER_TYPE_BUY,
    "price": tick.ask,
    "deviation": 20,
    "magic": 123456,
    "comment": "TESTE_RETCODE",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

result = mt5.order_send(request)
if result:
    print()
    print(f"Resultado do teste:")
    print(f"  Retcode: {result.retcode}")
    print(f"  Deal: {result.deal}")
    print(f"  Volume: {result.volume}")
    print(f"  Comment: {result.comment}")
    
    # Verificar se retcode 10009 é sucesso
    if result.retcode == 10009:
        print()
        print("⚠️  Retcode 10009 - 'Request executed'")
        print("   Este código parece ser sucesso mas não está em success_codes")

mt5.shutdown()

