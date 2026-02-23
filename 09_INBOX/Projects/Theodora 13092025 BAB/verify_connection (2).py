import json
import sys
import os
import traceback

def main():
    try:
        import MetaTrader5 as mt5
    except Exception as e:
        print("ERROR: Failed to import MetaTrader5. Install with: pip install MetaTrader5")
        print(f"DETAILS: {e}")
        sys.exit(2)

    cfg_path = os.path.join("Backend", "config.json")
    if not os.path.isfile(cfg_path):
        print(f"ERROR: Config file not found: {cfg_path}")
        sys.exit(2)

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read config: {e}")
        sys.exit(2)

    account = int(cfg.get("mt5_account", 0) or 0)
    password = str(cfg.get("mt5_password", ""))
    server = str(cfg.get("mt5_server", ""))
    symbols = cfg.get("symbols", ["EURUSD"]) or ["EURUSD"]

    print("=== MT5 CONNECTION VERIFY ===")
    print(f"Account: {account}")
    print(f"Server:  {server}")
    print(f"Symbols: {symbols}")

    # Initialize
    if not mt5.initialize():
        print(f"INIT FAIL: last_error={mt5.last_error()}")
        sys.exit(1)
    print("INIT OK")

    # Login
    if not mt5.login(account, password, server):
        print(f"LOGIN FAIL: last_error={mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)
    print("LOGIN OK")

    try:
        print(f"VERSION: {mt5.version()}")
        ti = mt5.terminal_info()
        ai = mt5.account_info()
        print(f"TERMINAL: build={getattr(ti,'build',None)} company={getattr(ti,'company',None)}")
        print(f"ACCOUNT:  name={getattr(ai,'name',None)} balance={getattr(ai,'balance',None)} leverage={getattr(ai,'leverage',None)}")

        sym = str(symbols[0])
        print(f"TEST SYMBOL: {sym}")
        if not mt5.symbol_select(sym, True):
            print(f"SYMBOL SELECT FAIL: {sym}")
        tick = mt5.symbol_info_tick(sym)
        print(f"TICK: {tick}")
        rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M1, 0, 10)
        print(f"RATES M1 x10: count={0 if rates is None else len(rates)}")

        if rates is None or len(rates) == 0:
            print("DATA WARN: No rates returned. Market closed or symbol unavailable or connection issue.")

        print("RESULT: OK")
    except Exception as e:
        print("ERROR during data test:")
        traceback.print_exc()
        mt5.shutdown()
        sys.exit(1)

    mt5.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    # Optional quick check function (as requested)
    try:
        import MetaTrader5 as mt5
    except Exception:
        mt5 = None

    def check_mt5_connection(account, password, server):
        try:
            if mt5 is None:
                print("❌ MetaTrader5 module not available")
                return False
            if not mt5.initialize():
                print("❌ MT5 não está inicializado")
                return False
            if not mt5.login(account, password, server):
                print("❌ Falha no login - Verifique:")
                print(f"   Conta: {account}")
                print(f"   Servidor: {server}")
                print(f"   Erro: {mt5.last_error()}")
                return False
            print("✅ MT5 conectado com sucesso!")
            info = mt5.account_info()
            if info:
                print(f"   Conta: {info.login}")
                print(f"   Corretora: {getattr(info,'company',None)}")
                print(f"   Saldo: {info.balance}")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False

    # Run standard verifier
    main()


